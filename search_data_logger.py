#!/usr/bin/env python3
"""
Enhanced logging and data flow tracking utilities for search data operations.
Provides comprehensive logging to track prompt data throughout the pipeline.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

# Configure logging with more detailed format for data flow tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)

class SearchDataLogger:
    """Enhanced logger for tracking search data flow and prompt integrity."""
    
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)
        self.data_flow_log = []  # In-memory log for analysis
    
    def log_data_flow(self, operation: str, request_id: str, search_data: Dict[str, Any], 
                     stage: str = "unknown") -> None:
        """
        Log data flow with detailed prompt tracking.
        
        Args:
            operation: The operation being performed (e.g., 'store', 'retrieve', 'update')
            request_id: The search request ID
            search_data: The search data dictionary
            stage: The stage in the pipeline (e.g., 'api_input', 'pre_storage', 'post_retrieval')
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Extract key information for logging
        prompt_info = self._analyze_prompt_data(search_data)
        data_summary = self._create_data_summary(search_data)
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'operation': operation,
            'stage': stage,
            'request_id': request_id,
            'prompt_info': prompt_info,
            'data_summary': data_summary
        }
        
        # Add to in-memory log for analysis
        self.data_flow_log.append(log_entry)
        
        # Log based on prompt status
        if prompt_info['has_prompt']:
            self.logger.debug(
                f"DATA_FLOW [{stage}] {operation.upper()}: request_id={request_id}, "
                f"prompt_length={prompt_info['length']}, "
                f"prompt_preview='{prompt_info['preview']}', "
                f"fields={list(data_summary['fields'])}"
            )
        else:
            self.logger.warning(
                f"DATA_FLOW [{stage}] {operation.upper()}: request_id={request_id}, "
                f"⚠️  PROMPT_MISSING: {prompt_info['issue']}, "
                f"fields={list(data_summary['fields'])}"
            )
    
    def log_prompt_integrity_check(self, request_id: str, expected_prompt: Optional[str], 
                                 actual_prompt: Optional[str], operation: str) -> bool:
        """
        Log prompt integrity comparison between expected and actual values.
        
        Args:
            request_id: The search request ID
            expected_prompt: The expected prompt value
            actual_prompt: The actual prompt value found
            operation: The operation context
            
        Returns:
            bool: True if prompts match, False otherwise
        """
        timestamp = datetime.utcnow().isoformat()
        
        expected_info = self._analyze_prompt_value(expected_prompt)
        actual_info = self._analyze_prompt_value(actual_prompt)
        
        integrity_ok = (expected_info['has_value'] == actual_info['has_value'] and
                       expected_prompt == actual_prompt)
        
        log_entry = {
            'timestamp': timestamp,
            'operation': operation,
            'request_id': request_id,
            'expected_prompt_info': expected_info,
            'actual_prompt_info': actual_info,
            'integrity_ok': integrity_ok
        }
        
        self.data_flow_log.append(log_entry)
        
        if integrity_ok:
            self.logger.debug(
                f"PROMPT_INTEGRITY [{operation}] ✅ OK: request_id={request_id}, "
                f"prompt_length={actual_info['length']}"
            )
        else:
            self.logger.error(
                f"PROMPT_INTEGRITY [{operation}] ❌ MISMATCH: request_id={request_id}, "
                f"expected={expected_info}, actual={actual_info}"
            )
        
        return integrity_ok
    
    def log_database_operation(self, operation: str, table: str, request_id: str, 
                             data: Optional[Dict[str, Any]] = None, 
                             result: Optional[Any] = None, 
                             error: Optional[Exception] = None) -> None:
        """
        Log database operations with detailed prompt tracking.
        
        Args:
            operation: Database operation (select, insert, update, upsert)
            table: Database table name
            request_id: The search request ID
            data: Data being operated on (for insert/update operations)
            result: Operation result
            error: Any error that occurred
        """
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = {
            'timestamp': timestamp,
            'operation': f"db_{operation}",
            'table': table,
            'request_id': request_id,
            'success': error is None
        }
        
        # Analyze data if provided
        if data:
            prompt_info = self._analyze_prompt_data(data)
            log_entry['prompt_info'] = prompt_info
            log_entry['data_summary'] = self._create_data_summary(data)
        
        # Analyze result if provided
        if result and hasattr(result, 'data') and result.data:
            if isinstance(result.data, list) and len(result.data) > 0:
                result_prompt_info = self._analyze_prompt_data(result.data[0])
                log_entry['result_prompt_info'] = result_prompt_info
        
        if error:
            log_entry['error'] = str(error)
        
        self.data_flow_log.append(log_entry)
        
        # Log based on success/failure and prompt status
        if error:
            self.logger.error(
                f"DB_OPERATION [{operation.upper()}] ❌ FAILED: table={table}, "
                f"request_id={request_id}, error={str(error)}"
            )
        elif data and not self._analyze_prompt_data(data)['has_prompt']:
            self.logger.warning(
                f"DB_OPERATION [{operation.upper()}] ⚠️  NULL_PROMPT: table={table}, "
                f"request_id={request_id}, storing data with missing prompt"
            )
        else:
            prompt_length = 0
            if data:
                prompt_length = self._analyze_prompt_data(data)['length']
            elif result and hasattr(result, 'data') and result.data:
                if isinstance(result.data, list) and len(result.data) > 0:
                    prompt_length = self._analyze_prompt_data(result.data[0])['length']
            
            self.logger.info(
                f"DB_OPERATION [{operation.upper()}] ✅ SUCCESS: table={table}, "
                f"request_id={request_id}, prompt_length={prompt_length}"
            )
    
    def track_prompt_presence(self, operation: str, request_id: str, has_prompt: bool, 
                            prompt_length: int = 0, context: str = "") -> None:
        """
        Track prompt presence throughout operations.
        
        Args:
            operation: The operation being tracked
            request_id: The search request ID
            has_prompt: Whether prompt is present and valid
            prompt_length: Length of the prompt if present
            context: Additional context information
        """
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = {
            'timestamp': timestamp,
            'operation': f"track_{operation}",
            'request_id': request_id,
            'has_prompt': has_prompt,
            'prompt_length': prompt_length,
            'context': context
        }
        
        self.data_flow_log.append(log_entry)
        
        status_icon = "✅" if has_prompt else "❌"
        self.logger.info(
            f"PROMPT_TRACKING [{operation.upper()}] {status_icon}: request_id={request_id}, "
            f"has_prompt={has_prompt}, length={prompt_length}, context='{context}'"
        )
    
    def get_data_flow_summary(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of data flow for analysis.
        
        Args:
            request_id: Optional request ID to filter by
            
        Returns:
            Dict containing data flow summary
        """
        filtered_log = self.data_flow_log
        if request_id:
            filtered_log = [entry for entry in self.data_flow_log 
                          if entry.get('request_id') == request_id]
        
        summary = {
            'total_operations': len(filtered_log),
            'operations_by_type': {},
            'prompt_issues': [],
            'integrity_failures': [],
            'database_errors': []
        }
        
        for entry in filtered_log:
            # Count operations by type
            op_type = entry.get('operation', 'unknown')
            summary['operations_by_type'][op_type] = summary['operations_by_type'].get(op_type, 0) + 1
            
            # Track prompt issues
            if entry.get('prompt_info', {}).get('has_prompt') is False:
                summary['prompt_issues'].append({
                    'timestamp': entry['timestamp'],
                    'operation': entry['operation'],
                    'request_id': entry.get('request_id'),
                    'issue': entry.get('prompt_info', {}).get('issue')
                })
            
            # Track integrity failures
            if entry.get('integrity_ok') is False:
                summary['integrity_failures'].append({
                    'timestamp': entry['timestamp'],
                    'operation': entry['operation'],
                    'request_id': entry.get('request_id')
                })
            
            # Track database errors
            if entry.get('error'):
                summary['database_errors'].append({
                    'timestamp': entry['timestamp'],
                    'operation': entry['operation'],
                    'request_id': entry.get('request_id'),
                    'error': entry['error']
                })
        
        return summary
    
    def _analyze_prompt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze prompt data in a dictionary."""
        prompt_value = data.get('prompt')
        return self._analyze_prompt_value(prompt_value)
    
    def _analyze_prompt_value(self, prompt_value: Any) -> Dict[str, Any]:
        """Analyze a prompt value and return detailed information."""
        if prompt_value is None:
            return {
                'has_value': False,
                'has_prompt': False,
                'length': 0,
                'preview': '',
                'issue': 'null_value'
            }
        
        if not isinstance(prompt_value, str):
            return {
                'has_value': True,
                'has_prompt': False,
                'length': 0,
                'preview': str(prompt_value)[:50],
                'issue': f'wrong_type_{type(prompt_value).__name__}'
            }
        
        stripped_prompt = prompt_value.strip()
        if not stripped_prompt:
            return {
                'has_value': True,
                'has_prompt': False,
                'length': len(prompt_value),
                'preview': repr(prompt_value)[:50],
                'issue': 'empty_string'
            }
        
        return {
            'has_value': True,
            'has_prompt': True,
            'length': len(stripped_prompt),
            'preview': stripped_prompt[:50],
            'issue': None
        }
    
    def _create_data_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of data structure."""
        return {
            'fields': list(data.keys()) if isinstance(data, dict) else [],
            'total_fields': len(data) if isinstance(data, dict) else 0,
            'has_request_id': 'request_id' in data if isinstance(data, dict) else False,
            'has_status': 'status' in data if isinstance(data, dict) else False
        }


# Global logger instance for easy access
search_data_logger = SearchDataLogger('search_data_flow')


def log_data_flow(operation: str, request_id: str, search_data: Dict[str, Any], 
                 stage: str = "unknown") -> None:
    """Convenience function for logging data flow."""
    search_data_logger.log_data_flow(operation, request_id, search_data, stage)


def log_prompt_integrity_check(request_id: str, expected_prompt: Optional[str], 
                             actual_prompt: Optional[str], operation: str) -> bool:
    """Convenience function for logging prompt integrity checks."""
    return search_data_logger.log_prompt_integrity_check(
        request_id, expected_prompt, actual_prompt, operation
    )


def log_database_operation(operation: str, table: str, request_id: str, 
                         data: Optional[Dict[str, Any]] = None, 
                         result: Optional[Any] = None, 
                         error: Optional[Exception] = None) -> None:
    """Convenience function for logging database operations."""
    search_data_logger.log_database_operation(operation, table, request_id, data, result, error)


def track_prompt_presence(operation: str, request_id: str, has_prompt: bool, 
                        prompt_length: int = 0, context: str = "") -> None:
    """Convenience function for tracking prompt presence."""
    search_data_logger.track_prompt_presence(operation, request_id, has_prompt, prompt_length, context)


def get_data_flow_summary(request_id: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for getting data flow summary."""
    return search_data_logger.get_data_flow_summary(request_id)