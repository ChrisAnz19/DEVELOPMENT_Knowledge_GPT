#!/usr/bin/env python3
"""
Data flow monitoring utilities for analyzing search data patterns and prompt integrity.
Provides functions to monitor and analyze data flow throughout the pipeline.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from search_data_logger import search_data_logger, get_data_flow_summary
    LOGGER_AVAILABLE = True
except ImportError:
    logger.warning("Search data logger not available")
    LOGGER_AVAILABLE = False

try:
    from database import get_recent_searches_from_database
    DATABASE_AVAILABLE = True
except ImportError:
    logger.warning("Database utilities not available")
    DATABASE_AVAILABLE = False


class DataFlowMonitor:
    """Monitor and analyze data flow patterns for search operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DataFlowMonitor")
    
    def analyze_null_prompt_patterns(self, limit: int = 50) -> Dict[str, Any]:
        """
        Analyze patterns in null prompt occurrences from recent database records.
        
        Args:
            limit: Number of recent searches to analyze
            
        Returns:
            Dict containing analysis results
        """
        if not DATABASE_AVAILABLE:
            self.logger.error("Database utilities not available for analysis")
            return {"error": "database_not_available"}
        
        try:
            # Get recent searches from database
            recent_searches = get_recent_searches_from_database(limit)
            
            analysis = {
                "total_searches": len(recent_searches),
                "null_prompt_count": 0,
                "empty_prompt_count": 0,
                "valid_prompt_count": 0,
                "null_prompt_searches": [],
                "prompt_length_stats": {
                    "min": float('inf'),
                    "max": 0,
                    "avg": 0,
                    "total_length": 0
                },
                "status_distribution": {},
                "timestamp_range": {
                    "earliest": None,
                    "latest": None
                }
            }
            
            valid_prompt_lengths = []
            
            for search in recent_searches:
                request_id = search.get('request_id')
                prompt = search.get('prompt')
                status = search.get('status', 'unknown')
                created_at = search.get('created_at')
                
                # Analyze prompt
                if prompt is None:
                    analysis["null_prompt_count"] += 1
                    analysis["null_prompt_searches"].append({
                        "request_id": request_id,
                        "status": status,
                        "created_at": created_at,
                        "issue": "null_prompt"
                    })
                elif isinstance(prompt, str) and not prompt.strip():
                    analysis["empty_prompt_count"] += 1
                    analysis["null_prompt_searches"].append({
                        "request_id": request_id,
                        "status": status,
                        "created_at": created_at,
                        "issue": "empty_prompt"
                    })
                else:
                    analysis["valid_prompt_count"] += 1
                    if isinstance(prompt, str):
                        prompt_length = len(prompt.strip())
                        valid_prompt_lengths.append(prompt_length)
                        analysis["prompt_length_stats"]["total_length"] += prompt_length
                        analysis["prompt_length_stats"]["min"] = min(
                            analysis["prompt_length_stats"]["min"], prompt_length
                        )
                        analysis["prompt_length_stats"]["max"] = max(
                            analysis["prompt_length_stats"]["max"], prompt_length
                        )
                
                # Status distribution
                analysis["status_distribution"][status] = analysis["status_distribution"].get(status, 0) + 1
                
                # Timestamp range
                if created_at:
                    if analysis["timestamp_range"]["earliest"] is None or created_at < analysis["timestamp_range"]["earliest"]:
                        analysis["timestamp_range"]["earliest"] = created_at
                    if analysis["timestamp_range"]["latest"] is None or created_at > analysis["timestamp_range"]["latest"]:
                        analysis["timestamp_range"]["latest"] = created_at
            
            # Calculate average prompt length
            if valid_prompt_lengths:
                analysis["prompt_length_stats"]["avg"] = analysis["prompt_length_stats"]["total_length"] / len(valid_prompt_lengths)
            else:
                analysis["prompt_length_stats"]["min"] = 0
            
            # Calculate percentages
            if analysis["total_searches"] > 0:
                analysis["null_prompt_percentage"] = (analysis["null_prompt_count"] / analysis["total_searches"]) * 100
                analysis["empty_prompt_percentage"] = (analysis["empty_prompt_count"] / analysis["total_searches"]) * 100
                analysis["valid_prompt_percentage"] = (analysis["valid_prompt_count"] / analysis["total_searches"]) * 100
            
            self.logger.info(f"Analyzed {analysis['total_searches']} searches: "
                           f"{analysis['null_prompt_count']} null prompts, "
                           f"{analysis['empty_prompt_count']} empty prompts, "
                           f"{analysis['valid_prompt_count']} valid prompts")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing null prompt patterns: {str(e)}")
            return {"error": str(e)}
    
    def get_data_flow_metrics(self, request_id: Optional[str] = None, 
                            hours_back: int = 24) -> Dict[str, Any]:
        """
        Get data flow metrics from the logging system.
        
        Args:
            request_id: Optional specific request ID to analyze
            hours_back: Hours of history to include in analysis
            
        Returns:
            Dict containing data flow metrics
        """
        if not LOGGER_AVAILABLE:
            self.logger.error("Search data logger not available for metrics")
            return {"error": "logger_not_available"}
        
        try:
            # Get data flow summary
            summary = get_data_flow_summary(request_id)
            
            # Add time-based filtering if needed
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Filter log entries by time if no specific request_id
            if not request_id and hasattr(search_data_logger, 'data_flow_log'):
                filtered_entries = []
                for entry in search_data_logger.data_flow_log:
                    try:
                        entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                        if entry_time >= cutoff_time:
                            filtered_entries.append(entry)
                    except (ValueError, TypeError):
                        # Include entries with invalid timestamps
                        filtered_entries.append(entry)
                
                # Recalculate summary with filtered entries
                summary = self._calculate_summary_from_entries(filtered_entries)
            
            # Add additional metrics
            summary["analysis_timestamp"] = datetime.utcnow().isoformat()
            summary["hours_analyzed"] = hours_back
            summary["request_id_filter"] = request_id
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting data flow metrics: {str(e)}")
            return {"error": str(e)}
    
    def track_prompt_integrity_over_time(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Track prompt integrity patterns over time.
        
        Args:
            hours_back: Hours of history to analyze
            
        Returns:
            Dict containing integrity tracking results
        """
        if not LOGGER_AVAILABLE:
            return {"error": "logger_not_available"}
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            integrity_data = {
                "time_range": {
                    "start": cutoff_time.isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "integrity_checks": [],
                "success_rate": 0.0,
                "failure_patterns": {},
                "operations_analyzed": 0
            }
            
            if hasattr(search_data_logger, 'data_flow_log'):
                integrity_checks = 0
                integrity_successes = 0
                
                for entry in search_data_logger.data_flow_log:
                    try:
                        entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                        if entry_time >= cutoff_time:
                            # Look for integrity check entries
                            if entry.get('operation', '').startswith('track_') or 'integrity_ok' in entry:
                                integrity_checks += 1
                                
                                if entry.get('integrity_ok') is True or entry.get('has_prompt') is True:
                                    integrity_successes += 1
                                else:
                                    # Track failure patterns
                                    operation = entry.get('operation', 'unknown')
                                    issue = entry.get('prompt_info', {}).get('issue', 'unknown')
                                    pattern_key = f"{operation}_{issue}"
                                    integrity_data["failure_patterns"][pattern_key] = \
                                        integrity_data["failure_patterns"].get(pattern_key, 0) + 1
                                
                                integrity_data["integrity_checks"].append({
                                    "timestamp": entry.get('timestamp'),
                                    "operation": entry.get('operation'),
                                    "request_id": entry.get('request_id'),
                                    "success": entry.get('integrity_ok', entry.get('has_prompt', False))
                                })
                    except (ValueError, TypeError):
                        continue
                
                integrity_data["operations_analyzed"] = integrity_checks
                if integrity_checks > 0:
                    integrity_data["success_rate"] = (integrity_successes / integrity_checks) * 100
            
            return integrity_data
            
        except Exception as e:
            self.logger.error(f"Error tracking prompt integrity: {str(e)}")
            return {"error": str(e)}
    
    def generate_monitoring_report(self, include_database_analysis: bool = True,
                                 include_flow_metrics: bool = True,
                                 hours_back: int = 24) -> Dict[str, Any]:
        """
        Generate a comprehensive monitoring report.
        
        Args:
            include_database_analysis: Whether to include database analysis
            include_flow_metrics: Whether to include data flow metrics
            hours_back: Hours of history to analyze
            
        Returns:
            Dict containing comprehensive monitoring report
        """
        report = {
            "report_timestamp": datetime.utcnow().isoformat(),
            "analysis_period_hours": hours_back,
            "sections": {}
        }
        
        try:
            if include_database_analysis:
                self.logger.info("Generating database analysis section...")
                report["sections"]["database_analysis"] = self.analyze_null_prompt_patterns()
            
            if include_flow_metrics:
                self.logger.info("Generating data flow metrics section...")
                report["sections"]["flow_metrics"] = self.get_data_flow_metrics(hours_back=hours_back)
                report["sections"]["integrity_tracking"] = self.track_prompt_integrity_over_time(hours_back)
            
            # Generate summary
            report["summary"] = self._generate_report_summary(report["sections"])
            
            self.logger.info("Monitoring report generated successfully")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating monitoring report: {str(e)}")
            report["error"] = str(e)
            return report
    
    def _calculate_summary_from_entries(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from log entries."""
        summary = {
            'total_operations': len(entries),
            'operations_by_type': {},
            'prompt_issues': [],
            'integrity_failures': [],
            'database_errors': []
        }
        
        for entry in entries:
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
    
    def _generate_report_summary(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the monitoring report."""
        summary = {
            "overall_health": "unknown",
            "key_findings": [],
            "recommendations": []
        }
        
        try:
            # Analyze database section
            if "database_analysis" in sections:
                db_analysis = sections["database_analysis"]
                if not db_analysis.get("error"):
                    null_percentage = db_analysis.get("null_prompt_percentage", 0)
                    empty_percentage = db_analysis.get("empty_prompt_percentage", 0)
                    total_issues = null_percentage + empty_percentage
                    
                    if total_issues == 0:
                        summary["key_findings"].append("No null or empty prompts found in recent searches")
                        summary["overall_health"] = "good"
                    elif total_issues < 5:
                        summary["key_findings"].append(f"Low prompt issues: {total_issues:.1f}% of searches")
                        summary["overall_health"] = "fair"
                    else:
                        summary["key_findings"].append(f"High prompt issues: {total_issues:.1f}% of searches")
                        summary["overall_health"] = "poor"
                        summary["recommendations"].append("Investigate prompt data handling in storage pipeline")
            
            # Analyze flow metrics section
            if "flow_metrics" in sections:
                flow_metrics = sections["flow_metrics"]
                if not flow_metrics.get("error"):
                    prompt_issues = len(flow_metrics.get("prompt_issues", []))
                    total_ops = flow_metrics.get("total_operations", 0)
                    
                    if prompt_issues == 0:
                        summary["key_findings"].append("No prompt issues detected in data flow")
                    else:
                        issue_rate = (prompt_issues / total_ops * 100) if total_ops > 0 else 0
                        summary["key_findings"].append(f"Data flow prompt issues: {issue_rate:.1f}% of operations")
            
            # Analyze integrity tracking
            if "integrity_tracking" in sections:
                integrity = sections["integrity_tracking"]
                if not integrity.get("error"):
                    success_rate = integrity.get("success_rate", 0)
                    if success_rate >= 95:
                        summary["key_findings"].append(f"High integrity success rate: {success_rate:.1f}%")
                    elif success_rate >= 80:
                        summary["key_findings"].append(f"Moderate integrity success rate: {success_rate:.1f}%")
                        summary["recommendations"].append("Monitor integrity patterns for improvement opportunities")
                    else:
                        summary["key_findings"].append(f"Low integrity success rate: {success_rate:.1f}%")
                        summary["recommendations"].append("Urgent: Investigate integrity failures")
            
            # Set overall health if not already set
            if summary["overall_health"] == "unknown":
                if len(summary["recommendations"]) == 0:
                    summary["overall_health"] = "good"
                elif len(summary["recommendations"]) <= 2:
                    summary["overall_health"] = "fair"
                else:
                    summary["overall_health"] = "poor"
            
        except Exception as e:
            summary["error"] = f"Error generating summary: {str(e)}"
        
        return summary


# Global monitor instance
data_flow_monitor = DataFlowMonitor()


def analyze_null_prompt_patterns(limit: int = 50) -> Dict[str, Any]:
    """Convenience function for analyzing null prompt patterns."""
    return data_flow_monitor.analyze_null_prompt_patterns(limit)


def get_data_flow_metrics(request_id: Optional[str] = None, hours_back: int = 24) -> Dict[str, Any]:
    """Convenience function for getting data flow metrics."""
    return data_flow_monitor.get_data_flow_metrics(request_id, hours_back)


def generate_monitoring_report(include_database_analysis: bool = True,
                             include_flow_metrics: bool = True,
                             hours_back: int = 24) -> Dict[str, Any]:
    """Convenience function for generating monitoring report."""
    return data_flow_monitor.generate_monitoring_report(
        include_database_analysis, include_flow_metrics, hours_back
    )


if __name__ == "__main__":
    # Test the monitoring functionality
    print("🔍 Testing Data Flow Monitor...")
    
    # Test null prompt pattern analysis
    print("\n📊 Analyzing null prompt patterns...")
    patterns = analyze_null_prompt_patterns(10)
    if "error" not in patterns:
        print(f"  - Total searches analyzed: {patterns.get('total_searches', 0)}")
        print(f"  - Null prompts: {patterns.get('null_prompt_count', 0)}")
        print(f"  - Valid prompts: {patterns.get('valid_prompt_count', 0)}")
    else:
        print(f"  - Error: {patterns['error']}")
    
    # Test data flow metrics
    print("\n📈 Getting data flow metrics...")
    metrics = get_data_flow_metrics(hours_back=1)
    if "error" not in metrics:
        print(f"  - Total operations: {metrics.get('total_operations', 0)}")
        print(f"  - Prompt issues: {len(metrics.get('prompt_issues', []))}")
    else:
        print(f"  - Error: {metrics['error']}")
    
    # Generate comprehensive report
    print("\n📋 Generating monitoring report...")
    report = generate_monitoring_report(hours_back=1)
    if "error" not in report:
        print(f"  - Report generated at: {report.get('report_timestamp')}")
        print(f"  - Overall health: {report.get('summary', {}).get('overall_health', 'unknown')}")
        findings = report.get('summary', {}).get('key_findings', [])
        if findings:
            print(f"  - Key findings: {len(findings)} items")
    else:
        print(f"  - Error: {report['error']}")
    
    print("\n✅ Data Flow Monitor test completed")