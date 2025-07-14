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
        
        # Database configuration - using Supabase connection string format
        # For Supabase, we can use the connection string or individual parameters
        supabase_host = os.getenv("SUPABASE_HOST", "hmvcvtrucfoqxcrfinep.supabase.co")
        supabase_user = os.getenv("SUPABASE_USER", "ChrisAnz19")
        supabase_password = os.getenv("SUPABASE_PASSWORD", "2ndSight@2023")
        supabase_dbname = os.getenv("SUPABASE_DBNAME", "postgres")
        
        self.db_config = {
            'user': supabase_user,
            'password': supabase_password,
            'host': supabase_host,
            'port': os.getenv("SUPABASE_PORT", "5432"),
            'dbname': supabase_dbname
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
            
            # Create people table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS people (
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
            
            # Create people exclusions table for 30-day exclusion system
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS people_exclusions (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    excluded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
                    reason VARCHAR(255) DEFAULT 'Previously processed'
                );
            """)
            
            # Create index for faster exclusion lookups
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_people_exclusions_email 
                ON people_exclusions(email);
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_people_exclusions_expires 
                ON people_exclusions(expires_at);
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
            
            # Store people if they exist
            people = search_data.get('candidates', [])
            for person in people:
                self.cursor.execute("""
                    INSERT INTO people (
                        search_id, name, title, company, email, linkedin_url, 
                        profile_photo_url, location, accuracy, reasons, 
                        linkedin_profile, linkedin_posts
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    search_id,
                    person.get('name'),
                    person.get('title'),
                    person.get('company'),
                    person.get('email'),
                    person.get('linkedin_url'),
                    person.get('profile_photo_url'),
                    person.get('location'),
                    person.get('accuracy'),
                    json.dumps(person.get('reasons', [])),
                    json.dumps(person.get('linkedin_profile', {})),
                    json.dumps(person.get('linkedin_posts', []))
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
            
            # Get people for this search
            self.cursor.execute("""
                SELECT * FROM people WHERE search_id = %s ORDER BY accuracy DESC
            """, (search['id'],))
            
            people = self.cursor.fetchall()
            
            # Convert to dict and format
            search_dict = dict(search)
            search_dict['candidates'] = [dict(person) for person in people]
            
            return search_dict
            
        except Exception as e:
            logger.error(f"Error retrieving search result: {e}")
            return None
    
    def get_recent_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search results"""
        try:
            self.cursor.execute("""
                SELECT s.*, COUNT(p.id) as candidate_count 
                FROM searches s 
                LEFT JOIN people p ON s.id = p.search_id 
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
    
    def add_person_exclusion(self, email: str, name: str, company: str = None, reason: str = "Previously processed") -> bool:
        """Add a person to the exclusion list for 30 days"""
        try:
            if not self.connection or not self.cursor:
                self.connect()
            self.cursor.execute("""
                INSERT INTO people_exclusions (email, name, company, reason)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) 
                DO UPDATE SET 
                    excluded_at = CURRENT_TIMESTAMP,
                    expires_at = CURRENT_TIMESTAMP + INTERVAL '30 days',
                    reason = EXCLUDED.reason
            """, (email, name, company, reason))
            
            self.connection.commit()
            logger.info(f"Person {email} added to exclusion list for 30 days")
            return True
            
        except Exception as e:
            logger.error(f"Error adding person exclusion: {e}")
            self.connection.rollback()
            return False
    
    def is_person_excluded(self, email: str) -> bool:
        """Check if a person is currently excluded (within 30 days)"""
        try:
            if not self.connection or not self.cursor:
                self.connect()
            self.cursor.execute("""
                SELECT id FROM people_exclusions 
                WHERE email = %s AND expires_at > CURRENT_TIMESTAMP
            """, (email,))
            
            result = self.cursor.fetchone()
            return result is not None
            
        except Exception as e:
            logger.error(f"Error checking person exclusion: {e}")
            return False
    
    def get_excluded_people(self) -> List[Dict[str, Any]]:
        """Get all currently excluded people"""
        try:
            if not self.connection or not self.cursor:
                self.connect()
            self.cursor.execute("""
                SELECT email, name, company, excluded_at, expires_at, reason
                FROM people_exclusions 
                WHERE expires_at > CURRENT_TIMESTAMP
                ORDER BY excluded_at DESC
            """)
            
            results = self.cursor.fetchall()
            return [dict(result) for result in results]
            
        except Exception as e:
            logger.error(f"Error getting excluded people: {e}")
            return []
    
    def cleanup_expired_exclusions(self) -> int:
        """Remove expired exclusions (older than 30 days) and return count of removed records"""
        try:
            self.cursor.execute("""
                DELETE FROM people_exclusions 
                WHERE expires_at <= CURRENT_TIMESTAMP
            """)
            
            deleted_count = self.cursor.rowcount
            self.connection.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired exclusions")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired exclusions: {e}")
            self.connection.rollback()
            return 0

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

def add_person_exclusion_to_database(email: str, name: str, company: str = None, reason: str = "Previously processed") -> bool:
    """Add person to exclusion list"""
    return db_manager.add_person_exclusion(email, name, company, reason)

def is_person_excluded_in_database(email: str) -> bool:
    """Check if person is excluded"""
    return db_manager.is_person_excluded(email)

def get_excluded_people_from_database() -> List[Dict[str, Any]]:
    """Get all excluded people"""
    return db_manager.get_excluded_people()

def cleanup_expired_exclusions_in_database() -> int:
    """Clean up expired exclusions"""
    return db_manager.cleanup_expired_exclusions()

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