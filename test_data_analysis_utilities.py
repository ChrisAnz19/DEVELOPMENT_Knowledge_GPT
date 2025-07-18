#!/usr/bin/env python3
"""
Tests for Data Analysis and Correction Utilities
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import the modules to test
from data_analysis_utilities import (
    DataIntegrityAnalyzer,
    DataCorrectionUtilities,
    DataIntegrityMonitor,
    analyze_database_integrity,
    correct_null_prompt,
    get_integrity_status
)


class TestDataIntegrityAnalyzer(unittest.TestCase):
    """Test cases for DataIntegrityAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = DataIntegrityAnalyzer()
    
    @patch('data_analysis_utilities.supabase')
    def test_analyze_null_prompt_records_success(self, mock_supabase):
        """Test successful analysis of null prompt records."""
        # Mock database response
        mock_result = Mock()
        mock_result.data = [
            {
                'id': 1,
                'request_id': 'req-1',
                'prompt': 'Valid prompt',
                'status': 'completed',
                'created_at': '2024-01-01T10:00:00',
                'completed_at': '2024-01-01T10:05:00',
                'error': None
            },
            {
                'id': 2,
                'request_id': 'req-2',
                'prompt': None,  # Null prompt
                'status': 'completed',
                'created_at': '2024-01-01T11:00:00',
                'completed_at': '2024-01-01T11:05:00',
                'error': None
            },
            {
                'id': 3,
                'request_id': 'req-3',
                'prompt': '',  # Empty prompt
                'status': 'failed',
                'created_at': '2024-01-01T12:00:00',
                'completed_at': None,
                'error': 'Processing failed'
            }
        ]
        
        mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_result
        
        # Run analysis
        result = self.analyzer.analyze_null_prompt_records(limit=10)
        
        # Verify results
        assert result['total_records'] == 3
        assert result['null_prompt_count'] == 2
        assert result['null_prompt_percentage'] == 66.67
        assert 'completed' in result['status_distribution']
        assert 'failed' in result['status_distribution']
        assert result['null_prompts_by_status']['completed'] == 1
        assert result['null_prompts_by_status']['failed'] == 1
        assert len(result['recommendations']) > 0
    
    @patch('data_analysis_utilities.supabase')
    def test_analyze_null_prompt_records_no_data(self, mock_supabase):
        """Test analysis when no records are found."""
        mock_result = Mock()
        mock_result.data = []
        
        mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_result
        
        result = self.analyzer.analyze_null_prompt_records()
        
        assert result['total_records'] == 0
        assert result['null_prompt_count'] == 0
    
    @patch('data_analysis_utilities.DATABASE_AVAILABLE', False)
    def test_analyze_null_prompt_records_no_database(self):
        """Test analysis when database is not available."""
        result = self.analyzer.analyze_null_prompt_records()
        
        assert 'error' in result
        assert result['error'] == 'Database not available'
    
    def test_generate_recommendations_no_nulls(self):
        """Test recommendation generation when no null prompts found."""
        recommendations = self.analyzer._generate_recommendations(0, 100, {})
        
        assert len(recommendations) == 1
        assert "No null prompt records found" in recommendations[0]
    
    def test_generate_recommendations_high_priority(self):
        """Test recommendation generation for high priority issues."""
        recommendations = self.analyzer._generate_recommendations(15, 100, {'completed': 5})
        
        assert any("HIGH PRIORITY" in rec for rec in recommendations)
        assert any("completed searches with null prompts" in rec for rec in recommendations)
    
    def test_identify_recoverable_records(self):
        """Test identification of recoverable records."""
        # Set up analysis results
        self.analyzer.analysis_results = {
            'null_prompt_records': [
                {
                    'id': 1,
                    'request_id': 'req-1',
                    'status': 'processing',
                    'completed_at': None,
                    'error': None
                },
                {
                    'id': 2,
                    'request_id': 'req-2',
                    'status': 'failed',
                    'completed_at': None,
                    'error': 'Validation failed'
                }
            ]
        }
        
        recoverable = self.analyzer.identify_recoverable_records()
        
        assert len(recoverable) == 1  # Only processing record should be recoverable
        assert recoverable[0]['request_id'] == 'req-1'
        assert recoverable[0]['recovery_method'] == 'restart_processing'
    
    def test_assess_recovery_potential_processing(self):
        """Test recovery assessment for processing records."""
        record = {
            'status': 'processing',
            'completed_at': None,
            'error': None
        }
        
        assessment = self.analyzer._assess_recovery_potential(record)
        
        assert assessment['recoverable'] is True
        assert assessment['method'] == 'restart_processing'
        assert assessment['confidence'] == 'medium'
    
    def test_assess_recovery_potential_failed(self):
        """Test recovery assessment for failed records."""
        record = {
            'status': 'failed',
            'error': 'Processing error',
            'completed_at': None
        }
        
        assessment = self.analyzer._assess_recovery_potential(record)
        
        assert assessment['recoverable'] is False
        assert assessment['reason'] == 'Failed with error'


class TestDataCorrectionUtilities(unittest.TestCase):
    """Test cases for DataCorrectionUtilities class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.corrector = DataCorrectionUtilities()
    
    def test_set_dry_run_mode(self):
        """Test setting dry run mode."""
        assert self.corrector.dry_run_mode is True  # Default
        
        self.corrector.set_dry_run_mode(False)
        assert self.corrector.dry_run_mode is False
        
        self.corrector.set_dry_run_mode(True)
        assert self.corrector.dry_run_mode is True
    
    @patch('data_analysis_utilities.get_search_from_database')
    @patch('data_analysis_utilities.update_search_in_database')
    def test_correct_null_prompt_record_success(self, mock_update, mock_get):
        """Test successful correction of null prompt record."""
        # Mock current record with null prompt
        mock_get.return_value = {
            'id': 1,
            'request_id': 'req-1',
            'prompt': None,
            'status': 'completed'
        }
        mock_update.return_value = True
        
        self.corrector.set_dry_run_mode(False)
        
        result = self.corrector.correct_null_prompt_record(
            'req-1', 
            'Corrected prompt text',
            'Test correction'
        )
        
        assert result['status'] == 'success'
        assert result['request_id'] == 'req-1'
        assert result['dry_run'] is False
        assert 'Corrected prompt text' in result['corrected_prompt']
        
        # Verify database update was called
        mock_update.assert_called_once_with(
            'req-1',
            {'prompt': 'Corrected prompt text'},
            preserve_existing=True
        )
    
    @patch('data_analysis_utilities.get_search_from_database')
    def test_correct_null_prompt_record_dry_run(self, mock_get):
        """Test correction in dry run mode."""
        mock_get.return_value = {
            'id': 1,
            'request_id': 'req-1',
            'prompt': None,
            'status': 'completed'
        }
        
        # Dry run mode is default
        result = self.corrector.correct_null_prompt_record(
            'req-1',
            'Corrected prompt text'
        )
        
        assert result['status'] == 'dry_run_success'
        assert result['dry_run'] is True
    
    @patch('data_analysis_utilities.get_search_from_database')
    def test_correct_null_prompt_record_not_found(self, mock_get):
        """Test correction when record is not found."""
        mock_get.return_value = None
        
        result = self.corrector.correct_null_prompt_record('nonexistent', 'prompt')
        
        assert 'error' in result
        assert 'Record not found' in result['error']
    
    @patch('data_analysis_utilities.get_search_from_database')
    def test_correct_null_prompt_record_already_valid(self, mock_get):
        """Test correction when record already has valid prompt."""
        mock_get.return_value = {
            'id': 1,
            'request_id': 'req-1',
            'prompt': 'Existing valid prompt',
            'status': 'completed'
        }
        
        result = self.corrector.correct_null_prompt_record('req-1', 'New prompt')
        
        assert 'error' in result
        assert 'already has a valid prompt' in result['error']
    
    def test_correct_null_prompt_record_empty_prompt(self):
        """Test correction with empty corrected prompt."""
        result = self.corrector.correct_null_prompt_record('req-1', '')
        
        assert 'error' in result
        assert 'Corrected prompt cannot be empty' in result['error']
    
    @patch('data_analysis_utilities.DATABASE_AVAILABLE', False)
    def test_correct_null_prompt_record_no_database(self):
        """Test correction when database is not available."""
        result = self.corrector.correct_null_prompt_record('req-1', 'prompt')
        
        assert 'error' in result
        assert result['error'] == 'Database not available'
    
    def test_batch_correct_records(self):
        """Test batch correction of multiple records."""
        corrections = [
            {'request_id': 'req-1', 'prompt': 'Prompt 1'},
            {'request_id': 'req-2', 'prompt': 'Prompt 2'},
            {'request_id': '', 'prompt': 'Invalid'}  # Missing request_id
        ]
        
        with patch.object(self.corrector, 'correct_null_prompt_record') as mock_correct:
            mock_correct.side_effect = [
                {'status': 'dry_run_success'},
                {'status': 'dry_run_success'},
            ]
            
            result = self.corrector.batch_correct_records(corrections)
        
        assert result['total_records'] == 3
        assert result['successful_corrections'] == 2
        assert result['failed_corrections'] == 1
        assert result['success_rate'] == 66.67
    
    def test_generate_correction_report_empty(self):
        """Test report generation when no corrections performed."""
        report = self.corrector.generate_correction_report()
        
        assert 'message' in report
        assert 'No corrections have been performed' in report['message']
    
    def test_generate_correction_report_with_data(self):
        """Test report generation with correction data."""
        # Add some mock correction log entries
        self.corrector.correction_log = [
            {'status': 'success', 'request_id': 'req-1'},
            {'status': 'dry_run_success', 'request_id': 'req-2'},
            {'status': 'failed', 'request_id': 'req-3'}
        ]
        
        report = self.corrector.generate_correction_report()
        
        assert report['total_corrections_attempted'] == 3
        assert report['successful_corrections'] == 1
        assert report['dry_run_corrections'] == 1
        assert report['failed_corrections'] == 1
        assert len(report['correction_log']) == 3


class TestDataIntegrityMonitor(unittest.TestCase):
    """Test cases for DataIntegrityMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = DataIntegrityMonitor()
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring."""
        assert self.monitor.monitoring_active is False
        
        self.monitor.start_monitoring()
        assert self.monitor.monitoring_active is True
        
        self.monitor.stop_monitoring()
        assert self.monitor.monitoring_active is False
    
    def test_record_validation_attempt_inactive(self):
        """Test recording validation attempts when monitoring is inactive."""
        initial_attempts = self.monitor.metrics['validation_attempts']
        
        self.monitor.record_validation_attempt(True)
        
        # Should not record when monitoring is inactive
        assert self.monitor.metrics['validation_attempts'] == initial_attempts
    
    def test_record_validation_attempt_active(self):
        """Test recording validation attempts when monitoring is active."""
        self.monitor.start_monitoring()
        
        # Record successful validation
        self.monitor.record_validation_attempt(True)
        assert self.monitor.metrics['validation_attempts'] == 1
        assert self.monitor.metrics['validation_successes'] == 1
        assert self.monitor.metrics['validation_failures'] == 0
        
        # Record failed validation with null prompt detection
        self.monitor.record_validation_attempt(False, {'null_prompt_detected': True})
        assert self.monitor.metrics['validation_attempts'] == 2
        assert self.monitor.metrics['validation_successes'] == 1
        assert self.monitor.metrics['validation_failures'] == 1
        assert self.monitor.metrics['null_prompt_detections'] == 1
    
    def test_record_correction_attempt(self):
        """Test recording correction attempts."""
        self.monitor.start_monitoring()
        
        self.monitor.record_correction_attempt(True)
        assert self.monitor.metrics['correction_attempts'] == 1
        assert self.monitor.metrics['correction_successes'] == 1
        
        self.monitor.record_correction_attempt(False)
        assert self.monitor.metrics['correction_attempts'] == 2
        assert self.monitor.metrics['correction_successes'] == 1
    
    def test_get_integrity_metrics(self):
        """Test getting integrity metrics."""
        self.monitor.start_monitoring()
        
        # Record some test data
        self.monitor.record_validation_attempt(True)
        self.monitor.record_validation_attempt(False)
        self.monitor.record_correction_attempt(True)
        
        metrics = self.monitor.get_integrity_metrics()
        
        assert metrics['monitoring_active'] is True
        assert metrics['validation_success_rate'] == 50.0
        assert metrics['correction_success_rate'] == 100.0
        assert metrics['validation_attempts'] == 2
        assert metrics['correction_attempts'] == 1
        assert 'metrics_timestamp' in metrics
    
    def test_get_integrity_metrics_no_data(self):
        """Test getting metrics when no data recorded."""
        metrics = self.monitor.get_integrity_metrics()
        
        assert metrics['validation_success_rate'] == 0
        assert metrics['correction_success_rate'] == 0
        assert metrics['null_prompt_detection_rate'] == 0
    
    def test_reset_metrics(self):
        """Test resetting metrics."""
        self.monitor.start_monitoring()
        
        # Record some data
        self.monitor.record_validation_attempt(True)
        self.monitor.record_correction_attempt(True)
        
        # Verify data exists
        assert self.monitor.metrics['validation_attempts'] > 0
        assert self.monitor.metrics['correction_attempts'] > 0
        
        # Reset and verify
        self.monitor.reset_metrics()
        assert self.monitor.metrics['validation_attempts'] == 0
        assert self.monitor.metrics['correction_attempts'] == 0


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    @patch('data_analysis_utilities.DataIntegrityAnalyzer')
    def test_analyze_database_integrity(self, mock_analyzer_class):
        """Test analyze_database_integrity convenience function."""
        mock_analyzer = Mock()
        mock_analyzer.analyze_null_prompt_records.return_value = {'test': 'result'}
        mock_analyzer_class.return_value = mock_analyzer
        
        result = analyze_database_integrity(limit=50)
        
        mock_analyzer.analyze_null_prompt_records.assert_called_once_with(50)
        assert result == {'test': 'result'}
    
    @patch('data_analysis_utilities.DataCorrectionUtilities')
    def test_correct_null_prompt(self, mock_corrector_class):
        """Test correct_null_prompt convenience function."""
        mock_corrector = Mock()
        mock_corrector.correct_null_prompt_record.return_value = {'status': 'success'}
        mock_corrector_class.return_value = mock_corrector
        
        result = correct_null_prompt('req-1', 'prompt', dry_run=False)
        
        mock_corrector.set_dry_run_mode.assert_called_once_with(False)
        mock_corrector.correct_null_prompt_record.assert_called_once_with('req-1', 'prompt')
        assert result == {'status': 'success'}
    
    @patch('data_analysis_utilities.DataIntegrityAnalyzer')
    def test_get_integrity_status(self, mock_analyzer_class):
        """Test get_integrity_status convenience function."""
        mock_analyzer = Mock()
        mock_analyzer.analyze_null_prompt_records.return_value = {
            'null_prompt_count': 2,
            'total_records': 10,
            'null_prompt_percentage': 20.0
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        result = get_integrity_status()
        
        assert result['status'] == 'issues_detected'
        assert result['null_prompt_count'] == 2
        assert result['total_records_checked'] == 10
        assert result['integrity_percentage'] == 80.0
        assert 'last_check' in result
    
    @patch('data_analysis_utilities.DataIntegrityAnalyzer')
    def test_get_integrity_status_healthy(self, mock_analyzer_class):
        """Test get_integrity_status when database is healthy."""
        mock_analyzer = Mock()
        mock_analyzer.analyze_null_prompt_records.return_value = {
            'null_prompt_count': 0,
            'total_records': 10,
            'null_prompt_percentage': 0.0
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        result = get_integrity_status()
        
        assert result['status'] == 'healthy'
        assert result['null_prompt_count'] == 0
        assert result['integrity_percentage'] == 100.0


if __name__ == '__main__':
    unittest.main()