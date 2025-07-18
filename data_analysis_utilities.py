#!/usr/bin/env python3
"""
Data Analysis and Correction Utilities for Knowledge_GPT
Provides utilities to analyze existing null prompt records and implement correction mechanisms
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database utilities
try:
    from database import get_search_from_database, update_search_in_database
    from supabase_client import supabase
    DATABASE_AVAILABLE = True
except ImportError:
    logger.warning("Database utilities not available")
    DATABASE_AVAILABLE = False
    supabase = None

# Import logging utilities
try:
    from search_data_logger import log_data_flow, track_prompt_presence
    LOGGING_AVAILABLE = True
except ImportError:
    logger.warning("Enhanced logging not available")
    LOGGING_AVAILABLE = False
    def log_data_flow(*args, **kwargs):
        pass
    def track_prompt_presence(*args, **kwargs):
        pass


class DataIntegrityAnalyzer:
    """Analyzes database records for data integrity issues, particularly null prompts."""
    
    def __init__(self):
        self.analysis_results = {}
        self.correction_log = []
    
    def analyze_null_prompt_records(self, limit: int = 100) -> Dict[str, Any]:
        """
        Analyze existing database records for null prompt patterns.
        
        Args:
            limit (int): Maximum number of records to analyze
            
        Returns:
            Dict containing analysis results
        """
        if not DATABASE_AVAILABLE:
            logger.error("Database not available for analysis")
            return {"error": "Database not available"}
        
        logger.info(f"Starting null prompt analysis with limit: {limit}")
        
        try:
            # Query recent searches to analyze
            res = supabase.table("searches").select(
                "id, request_id, prompt, status, created_at, completed_at, error"
            ).order("created_at", desc=True).limit(limit).execute()
            
            if not hasattr(res, 'data') or not res.data:
                logger.warning("No search records found for analysis")
                return {"total_records": 0, "null_prompt_count": 0}
            
            records = res.data
            total_records = len(records)
            
            # Analyze records for null prompt patterns
            null_prompt_records = []
            status_distribution = {}
            null_by_status = {}
            date_patterns = {}
            
            for record in records:
                request_id = record.get('request_id')
                prompt = record.get('prompt')
                status = record.get('status', 'unknown')
                created_at = record.get('created_at')
                
                # Track status distribution
                status_distribution[status] = status_distribution.get(status, 0) + 1
                
                # Check for null/empty prompt
                has_null_prompt = not prompt or not str(prompt).strip()
                
                if has_null_prompt:
                    null_prompt_records.append({
                        'id': record.get('id'),
                        'request_id': request_id,
                        'status': status,
                        'created_at': created_at,
                        'completed_at': record.get('completed_at'),
                        'error': record.get('error'),
                        'prompt_value': repr(prompt)
                    })
                    
                    # Track null prompts by status
                    null_by_status[status] = null_by_status.get(status, 0) + 1
                    
                    # Track date patterns for null prompts
                    if created_at:
                        date_key = created_at[:10]  # YYYY-MM-DD
                        date_patterns[date_key] = date_patterns.get(date_key, 0) + 1
                
                # Log prompt presence for tracking
                track_prompt_presence("analysis", request_id, not has_null_prompt,
                                    len(str(prompt)) if prompt else 0, "data_analysis")
            
            # Calculate analysis metrics
            null_prompt_count = len(null_prompt_records)
            null_prompt_percentage = (null_prompt_count / total_records * 100) if total_records > 0 else 0
            
            analysis_results = {
                "analysis_timestamp": datetime.now().isoformat(),
                "total_records": total_records,
                "null_prompt_count": null_prompt_count,
                "null_prompt_percentage": round(null_prompt_percentage, 2),
                "status_distribution": status_distribution,
                "null_prompts_by_status": null_by_status,
                "null_prompt_date_patterns": date_patterns,
                "null_prompt_records": null_prompt_records[:10],  # First 10 for review
                "recommendations": self._generate_recommendations(null_prompt_count, total_records, null_by_status)
            }
            
            # Store results for later use
            self.analysis_results = analysis_results
            
            # Log analysis summary
            logger.info(f"Analysis complete: {null_prompt_count}/{total_records} records have null prompts ({null_prompt_percentage:.2f}%)")
            log_data_flow("analysis_complete", "system", analysis_results, "data_integrity_analysis")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error during null prompt analysis: {e}")
            return {"error": str(e), "analysis_timestamp": datetime.now().isoformat()}
    
    def _generate_recommendations(self, null_count: int, total_count: int, null_by_status: Dict) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        if null_count == 0:
            recommendations.append("✅ No null prompt records found - data integrity is good")
            return recommendations
        
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
        
        if null_percentage > 10:
            recommendations.append("🚨 HIGH PRIORITY: Significant null prompt issue detected")
        elif null_percentage > 5:
            recommendations.append("⚠️ MEDIUM PRIORITY: Notable null prompt issue detected")
        else:
            recommendations.append("ℹ️ LOW PRIORITY: Minor null prompt issue detected")
        
        # Status-specific recommendations
        if null_by_status.get('completed', 0) > 0:
            recommendations.append("🔍 Investigate completed searches with null prompts - this indicates data loss during processing")
        
        if null_by_status.get('processing', 0) > 0:
            recommendations.append("⏸️ Review processing searches with null prompts - may indicate validation issues")
        
        if null_by_status.get('failed', 0) > 0:
            recommendations.append("❌ Failed searches with null prompts may be due to validation failures")
        
        recommendations.append("🔧 Consider running data correction utilities for recoverable records")
        recommendations.append("📊 Implement enhanced monitoring to prevent future null prompt issues")
        
        return recommendations
    
    def identify_recoverable_records(self) -> List[Dict[str, Any]]:
        """
        Identify records that might be recoverable through correction mechanisms.
        
        Returns:
            List of potentially recoverable records
        """
        if not self.analysis_results or not self.analysis_results.get('null_prompt_records'):
            logger.warning("No analysis results available. Run analyze_null_prompt_records first.")
            return []
        
        recoverable_records = []
        
        for record in self.analysis_results['null_prompt_records']:
            recovery_potential = self._assess_recovery_potential(record)
            if recovery_potential['recoverable']:
                recoverable_records.append({
                    **record,
                    'recovery_method': recovery_potential['method'],
                    'recovery_confidence': recovery_potential['confidence']
                })
        
        logger.info(f"Identified {len(recoverable_records)} potentially recoverable records")
        return recoverable_records
    
    def _assess_recovery_potential(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Assess whether a record can be recovered and how."""
        status = record.get('status')
        error = record.get('error')
        completed_at = record.get('completed_at')
        
        # Records that are unlikely to be recoverable
        if status == 'failed' and error:
            return {'recoverable': False, 'reason': 'Failed with error'}
        
        if status == 'cancelled':
            return {'recoverable': False, 'reason': 'Cancelled by user'}
        
        # Records that might be recoverable
        if status == 'processing' and not completed_at:
            return {
                'recoverable': True,
                'method': 'restart_processing',
                'confidence': 'medium',
                'reason': 'Processing incomplete, may have original prompt in logs'
            }
        
        if status == 'completed' and completed_at:
            return {
                'recoverable': True,
                'method': 'log_recovery',
                'confidence': 'low',
                'reason': 'Completed but prompt lost, check logs for recovery'
            }
        
        return {
            'recoverable': True,
            'method': 'manual_review',
            'confidence': 'low',
            'reason': 'Requires manual investigation'
        }


class DataCorrectionUtilities:
    """Utilities for correcting data integrity issues in the database."""
    
    def __init__(self):
        self.correction_log = []
        self.dry_run_mode = True  # Safety default
    
    def set_dry_run_mode(self, dry_run: bool = True):
        """Enable or disable dry run mode for safety."""
        self.dry_run_mode = dry_run
        logger.info(f"Dry run mode {'enabled' if dry_run else 'disabled'}")
    
    def correct_null_prompt_record(self, request_id: str, corrected_prompt: str, 
                                 correction_reason: str = "Manual correction") -> Dict[str, Any]:
        """
        Correct a single null prompt record.
        
        Args:
            request_id (str): The request ID to correct
            corrected_prompt (str): The corrected prompt text
            correction_reason (str): Reason for the correction
            
        Returns:
            Dict containing correction result
        """
        if not DATABASE_AVAILABLE:
            return {"error": "Database not available"}
        
        if not corrected_prompt or not corrected_prompt.strip():
            return {"error": "Corrected prompt cannot be empty"}
        
        logger.info(f"{'[DRY RUN] ' if self.dry_run_mode else ''}Correcting null prompt for request_id: {request_id}")
        
        try:
            # First, verify the record exists and has a null prompt
            current_record = get_search_from_database(request_id)
            if not current_record:
                return {"error": f"Record not found: {request_id}"}
            
            current_prompt = current_record.get('prompt')
            if current_prompt and str(current_prompt).strip():
                return {"error": f"Record already has a valid prompt: {request_id}"}
            
            correction_result = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "dry_run": self.dry_run_mode,
                "original_prompt": repr(current_prompt),
                "corrected_prompt": corrected_prompt[:100] + "..." if len(corrected_prompt) > 100 else corrected_prompt,
                "correction_reason": correction_reason,
                "status": "pending"
            }
            
            if not self.dry_run_mode:
                # Perform the actual correction
                success = update_search_in_database(
                    request_id, 
                    {"prompt": corrected_prompt},
                    preserve_existing=True
                )
                
                if success:
                    correction_result["status"] = "success"
                    logger.info(f"Successfully corrected prompt for request_id: {request_id}")
                    
                    # Log the correction
                    track_prompt_presence("corrected", request_id, True, 
                                        len(corrected_prompt), f"corrected: {correction_reason}")
                else:
                    correction_result["status"] = "failed"
                    correction_result["error"] = "Database update failed"
            else:
                correction_result["status"] = "dry_run_success"
                logger.info(f"[DRY RUN] Would correct prompt for request_id: {request_id}")
            
            # Log the correction attempt
            self.correction_log.append(correction_result)
            log_data_flow("correction_attempt", request_id, correction_result, "data_correction")
            
            return correction_result
            
        except Exception as e:
            error_result = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
            self.correction_log.append(error_result)
            logger.error(f"Error correcting record {request_id}: {e}")
            return error_result
    
    def batch_correct_records(self, corrections: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Perform batch corrections on multiple records.
        
        Args:
            corrections: List of dicts with 'request_id', 'prompt', and optional 'reason'
            
        Returns:
            Dict containing batch correction results
        """
        logger.info(f"{'[DRY RUN] ' if self.dry_run_mode else ''}Starting batch correction of {len(corrections)} records")
        
        batch_results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run_mode,
            "total_records": len(corrections),
            "successful_corrections": 0,
            "failed_corrections": 0,
            "results": []
        }
        
        for correction in corrections:
            request_id = correction.get('request_id')
            prompt = correction.get('prompt')
            reason = correction.get('reason', 'Batch correction')
            
            if not request_id or not prompt:
                batch_results["results"].append({
                    "request_id": request_id,
                    "status": "skipped",
                    "error": "Missing request_id or prompt"
                })
                batch_results["failed_corrections"] += 1
                continue
            
            result = self.correct_null_prompt_record(request_id, prompt, reason)
            batch_results["results"].append(result)
            
            if result.get("status") in ["success", "dry_run_success"]:
                batch_results["successful_corrections"] += 1
            else:
                batch_results["failed_corrections"] += 1
        
        # Calculate success rate
        success_rate = (batch_results["successful_corrections"] / batch_results["total_records"] * 100) if batch_results["total_records"] > 0 else 0
        batch_results["success_rate"] = round(success_rate, 2)
        
        logger.info(f"Batch correction complete: {batch_results['successful_corrections']}/{batch_results['total_records']} successful ({success_rate:.2f}%)")
        
        return batch_results
    
    def generate_correction_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of all correction activities."""
        if not self.correction_log:
            return {"message": "No corrections have been performed"}
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "total_corrections_attempted": len(self.correction_log),
            "successful_corrections": len([c for c in self.correction_log if c.get("status") == "success"]),
            "dry_run_corrections": len([c for c in self.correction_log if c.get("status") == "dry_run_success"]),
            "failed_corrections": len([c for c in self.correction_log if c.get("status") in ["failed", "error"]]),
            "correction_log": self.correction_log
        }
        
        return report


class DataIntegrityMonitor:
    """Monitors ongoing data integrity and provides metrics."""
    
    def __init__(self):
        self.monitoring_active = False
        self.metrics = {
            "validation_attempts": 0,
            "validation_successes": 0,
            "validation_failures": 0,
            "null_prompt_detections": 0,
            "correction_attempts": 0,
            "correction_successes": 0
        }
    
    def start_monitoring(self):
        """Start data integrity monitoring."""
        self.monitoring_active = True
        logger.info("Data integrity monitoring started")
    
    def stop_monitoring(self):
        """Stop data integrity monitoring."""
        self.monitoring_active = False
        logger.info("Data integrity monitoring stopped")
    
    def record_validation_attempt(self, success: bool, details: Optional[Dict] = None):
        """Record a validation attempt for metrics."""
        if not self.monitoring_active:
            return
        
        self.metrics["validation_attempts"] += 1
        if success:
            self.metrics["validation_successes"] += 1
        else:
            self.metrics["validation_failures"] += 1
            
        if details and details.get("null_prompt_detected"):
            self.metrics["null_prompt_detections"] += 1
    
    def record_correction_attempt(self, success: bool):
        """Record a correction attempt for metrics."""
        if not self.monitoring_active:
            return
        
        self.metrics["correction_attempts"] += 1
        if success:
            self.metrics["correction_successes"] += 1
    
    def get_integrity_metrics(self) -> Dict[str, Any]:
        """Get current data integrity metrics."""
        validation_success_rate = (
            self.metrics["validation_successes"] / self.metrics["validation_attempts"] * 100
            if self.metrics["validation_attempts"] > 0 else 0
        )
        
        correction_success_rate = (
            self.metrics["correction_successes"] / self.metrics["correction_attempts"] * 100
            if self.metrics["correction_attempts"] > 0 else 0
        )
        
        return {
            "monitoring_active": self.monitoring_active,
            "metrics_timestamp": datetime.now().isoformat(),
            "validation_success_rate": round(validation_success_rate, 2),
            "correction_success_rate": round(correction_success_rate, 2),
            "null_prompt_detection_rate": (
                self.metrics["null_prompt_detections"] / self.metrics["validation_attempts"] * 100
                if self.metrics["validation_attempts"] > 0 else 0
            ),
            **self.metrics
        }
    
    def reset_metrics(self):
        """Reset all monitoring metrics."""
        self.metrics = {key: 0 for key in self.metrics}
        logger.info("Data integrity metrics reset")


# Convenience functions for easy access
def analyze_database_integrity(limit: int = 100) -> Dict[str, Any]:
    """Convenience function to analyze database integrity."""
    analyzer = DataIntegrityAnalyzer()
    return analyzer.analyze_null_prompt_records(limit)

def correct_null_prompt(request_id: str, corrected_prompt: str, dry_run: bool = True) -> Dict[str, Any]:
    """Convenience function to correct a single null prompt record."""
    corrector = DataCorrectionUtilities()
    corrector.set_dry_run_mode(dry_run)
    return corrector.correct_null_prompt_record(request_id, corrected_prompt)

def get_integrity_status() -> Dict[str, Any]:
    """Get a quick status of data integrity."""
    analyzer = DataIntegrityAnalyzer()
    analysis = analyzer.analyze_null_prompt_records(50)  # Quick analysis
    
    return {
        "status": "healthy" if analysis.get("null_prompt_count", 0) == 0 else "issues_detected",
        "null_prompt_count": analysis.get("null_prompt_count", 0),
        "total_records_checked": analysis.get("total_records", 0),
        "integrity_percentage": 100 - analysis.get("null_prompt_percentage", 0),
        "last_check": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Example usage and testing
    print("Data Analysis and Correction Utilities")
    print("=====================================")
    
    # Quick integrity check
    status = get_integrity_status()
    print(f"Integrity Status: {status['status']}")
    print(f"Records checked: {status['total_records_checked']}")
    print(f"Null prompts found: {status['null_prompt_count']}")
    print(f"Integrity percentage: {status['integrity_percentage']:.2f}%")