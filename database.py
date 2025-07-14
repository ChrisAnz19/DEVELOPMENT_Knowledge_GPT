#!/usr/bin/env python3
"""
Database utilities for Knowledge_GPT
Handles Supabase connection and operations for storing search results and candidate data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseManager:
    """Manages database connections and operations for Knowledge_GPT"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
        # Database configuration
        self.db_config = {
            'user': os.getenv("SUPABASE_USER"),
            'password': os.getenv("SUPABASE_PASSWORD"),
            'host': os.getenv("SUPABASE_HOST"),
            'port': os.getenv("SUPABASE_PORT", "5432"),
            'dbname': os.getenv("SUPABASE_DBNAME")
        }
        
        # Validate required environment variables
        missing_vars = [key for key, value in self.db_config.items() if not value]
        if missing_vars:
            logger.warning(f"Missing database environment variables: {missing_vars}")
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connection established successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("Database connection closed.")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def create_tables(self) -> bool:
        """Create necessary tables if they don't exist"""
        try:
            # Create searches table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS searches (
                    id SERIAL PRIMARY KEY,
                    request_id VARCHAR(255) UNIQUE NOT NULL,
                    prompt TEXT NOT NULL,
                    filters JSONB,
                    behavioral_data JSONB,
                    status VARCHAR(50) DEFAULT 'processing',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    error TEXT
                );
            """)
            
            # Create candidates table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id SERIAL PRIMARY KEY,
                    search_id INTEGER REFERENCES searches(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    title VARCHAR(255),
                    company VARCHAR(255),
                    email VARCHAR(255),
                    linkedin_url TEXT,
                    profile_photo_url TEXT,
                    location VARCHAR(255),
                    accuracy INTEGER,
                    reasons JSONB,
                    linkedin_profile JSONB,
                    linkedin_posts JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.connection.commit()
            logger.info("Database tables created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            self.connection.rollback()
            return False
    
    def store_search_result(self, search_data: Dict[str, Any]) -> Optional[int]:
        """Store a search result and return the search ID"""
        try:
            # Insert search record
            self.cursor.execute("""
                INSERT INTO searches (request_id, prompt, filters, behavioral_data, status, created_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                search_data.get('request_id'),
                search_data.get('prompt'),
                json.dumps(search_data.get('filters', {})),
                json.dumps(search_data.get('behavioral_data', {})),
                search_data.get('status', 'completed'),
                search_data.get('created_at'),
                search_data.get('completed_at')
            ))
            
            search_id = self.cursor.fetchone()['id']
            
            # Store candidates if they exist
            candidates = search_data.get('candidates', [])
            for candidate in candidates:
                self.cursor.execute("""
                    INSERT INTO candidates (
                        search_id, name, title, company, email, linkedin_url, 
                        profile_photo_url, location, accuracy, reasons, 
                        linkedin_profile, linkedin_posts
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    search_id,
                    candidate.get('name'),
                    candidate.get('title'),
                    candidate.get('company'),
                    candidate.get('email'),
                    candidate.get('linkedin_url'),
                    candidate.get('profile_photo_url'),
                    candidate.get('location'),
                    candidate.get('accuracy'),
                    json.dumps(candidate.get('reasons', [])),
                    json.dumps(candidate.get('linkedin_profile', {})),
                    json.dumps(candidate.get('linkedin_posts', []))
                ))
            
            self.connection.commit()
            logger.info(f"Search result stored successfully with ID: {search_id}")
            return search_id
            
        except Exception as e:
            logger.error(f"Error storing search result: {e}")
            self.connection.rollback()
            return None
    
    def get_search_by_request_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a search result by request ID"""
        try:
            self.cursor.execute("""
                SELECT * FROM searches WHERE request_id = %s
            """, (request_id,))
            
            search = self.cursor.fetchone()
            if not search:
                return None
            
            # Get candidates for this search
            self.cursor.execute("""
                SELECT * FROM candidates WHERE search_id = %s ORDER BY accuracy DESC
            """, (search['id'],))
            
            candidates = self.cursor.fetchall()
            
            # Convert to dict and format
            search_dict = dict(search)
            search_dict['candidates'] = [dict(candidate) for candidate in candidates]
            
            return search_dict
            
        except Exception as e:
            logger.error(f"Error retrieving search result: {e}")
            return None
    
    def get_recent_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search results"""
        try:
            self.cursor.execute("""
                SELECT s.*, COUNT(c.id) as candidate_count 
                FROM searches s 
                LEFT JOIN candidates c ON s.id = c.search_id 
                GROUP BY s.id 
                ORDER BY s.created_at DESC 
                LIMIT %s
            """, (limit,))
            
            searches = self.cursor.fetchall()
            return [dict(search) for search in searches]
            
        except Exception as e:
            logger.error(f"Error retrieving recent searches: {e}")
            return []
    
    def delete_search(self, request_id: str) -> bool:
        """Delete a search result and its candidates"""
        try:
            self.cursor.execute("""
                DELETE FROM searches WHERE request_id = %s
            """, (request_id,))
            
            deleted_count = self.cursor.rowcount
            self.connection.commit()
            
            if deleted_count > 0:
                logger.info(f"Search {request_id} deleted successfully")
                return True
            else:
                logger.warning(f"Search {request_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting search: {e}")
            self.connection.rollback()
            return False

# Global database manager instance
db_manager = DatabaseManager()

def init_database() -> bool:
    """Initialize database connection and create tables"""
    if db_manager.connect():
        return db_manager.create_tables()
    return False

def store_search_to_database(search_data: Dict[str, Any]) -> Optional[int]:
    """Store search result to database"""
    return db_manager.store_search_result(search_data)

def get_search_from_database(request_id: str) -> Optional[Dict[str, Any]]:
    """Get search result from database"""
    return db_manager.get_search_by_request_id(request_id)

def get_recent_searches_from_database(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent searches from database"""
    return db_manager.get_recent_searches(limit)

def delete_search_from_database(request_id: str) -> bool:
    """Delete search from database"""
    return db_manager.delete_search(request_id)

if __name__ == "__main__":
    # Test database connection
    print("🧪 Testing Database Connection...")
    
    if init_database():
        print("✅ Database initialized successfully!")
        
        # Test a simple query
        db_manager.cursor.execute("SELECT NOW();")
        result = db_manager.cursor.fetchone()
        print(f"⏰ Current database time: {result['now']}")
        
        # Show table structure
        db_manager.cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            ORDER BY table_name, ordinal_position
        """)
        
        tables = db_manager.cursor.fetchall()
        print("\n📋 Database Tables:")
        current_table = ""
        for table in tables:
            if table['table_name'] != current_table:
                current_table = table['table_name']
                print(f"\n{table['table_name']}:")
            print(f"  - {table['column_name']}: {table['data_type']}")
        
    else:
        print("❌ Database initialization failed!")
    
    db_manager.disconnect() 