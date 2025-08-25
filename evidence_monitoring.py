#!/usr/bin/env python3
"""
Monitoring, Logging, and Quality Assurance for URL Evidence Finder.

This module provides comprehensive monitoring, logging, and quality assurance
features for the URL Evidence Finder system, including performance tracking,
error monitoring, and automated quality checks.
"""

import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from threading import Lock
import statistics

from evidence_models import EvidenceURL
from explanation_analyzer import SearchableClaim


@dataclass
class QualityMetrics:
    """Quality metrics for evidence URLs."""
    relevance_score_avg: float
    confidence_distribution: Dict[str, int]
    evidence_type_distribution: Dict[str, int]
    domain_authority_avg: float
    urls_per_candidate_avg: float
    processing_time_avg: float
    success_rate: float
    error_rate: float


@dataclass
class PerformanceAlert:
    """Performance alert for monitoring."""
    timestamp: float
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    metrics: Dict[str, Any]
    threshold_exceeded: str


class EvidenceQualityAssurance:
    """Quality assurance system for evidence URLs."""
    
    def __init__(self):
        self.quality_thresholds = {
            'min_relevance_score': 0.3,
            'min_domain_authority': 0.4,
            'max_processing_time': 30.0,
            'min_success_rate': 0.8,
            'max_error_rate': 0.2,
            'min_urls_per_candidate': 1,
            'max_urls_per_candidate': 10
        }
        
        self.quality_history = deque(maxlen=1000)  # Keep last 1000 quality checks
        self.lock = Lock()
    
    def validate_evidence_quality(self, evidence_urls: List[EvidenceURL], processing_time: float) -> Dict[str, Any]:
        """
        Validate the quality of evidence URLs.
        
        Args:
            evidence_urls: List of evidence URLs to validate
            processing_time: Time taken to generate evidence
            
        Returns:
            Quality validation report
        """
        with self.lock:
            validation_report = {
                'timestamp': time.time(),
                'total_urls': len(evidence_urls),
                'quality_checks': {},
                'warnings': [],
                'errors': [],
                'overall_quality': 'unknown'
            }
            
            if not evidence_urls:
                validation_report['warnings'].append('No evidence URLs found')
                validation_report['overall_quality'] = 'poor'
                return validation_report
            
            # Check relevance scores
            relevance_scores = [url.relevance_score for url in evidence_urls]
            avg_relevance = statistics.mean(relevance_scores)
            min_relevance = min(relevance_scores)
            
            validation_report['quality_checks']['relevance'] = {
                'average_score': avg_relevance,
                'minimum_score': min_relevance,
                'threshold': self.quality_thresholds['min_relevance_score'],
                'passed': min_relevance >= self.quality_thresholds['min_relevance_score']
            }
            
            if min_relevance < self.quality_thresholds['min_relevance_score']:
                validation_report['warnings'].append(f'Low relevance score detected: {min_relevance:.3f}')
            
            # Check domain authority
            domain_authorities = [url.domain_authority for url in evidence_urls]
            avg_domain_authority = statistics.mean(domain_authorities)
            min_domain_authority = min(domain_authorities)
            
            validation_report['quality_checks']['domain_authority'] = {
                'average_score': avg_domain_authority,
                'minimum_score': min_domain_authority,
                'threshold': self.quality_thresholds['min_domain_authority'],
                'passed': min_domain_authority >= self.quality_thresholds['min_domain_authority']
            }
            
            if min_domain_authority < self.quality_thresholds['min_domain_authority']:
                validation_report['warnings'].append(f'Low domain authority detected: {min_domain_authority:.3f}')
            
            # Check confidence levels
            confidence_counts = defaultdict(int)
            for url in evidence_urls:
                confidence_counts[url.confidence_level] += 1
            
            validation_report['quality_checks']['confidence_distribution'] = dict(confidence_counts)
            
            high_confidence_ratio = confidence_counts['high'] / len(evidence_urls)
            if high_confidence_ratio < 0.3:  # Less than 30% high confidence
                validation_report['warnings'].append(f'Low high-confidence ratio: {high_confidence_ratio:.1%}')
            
            # Check processing time
            validation_report['quality_checks']['processing_time'] = {
                'time_seconds': processing_time,
                'threshold': self.quality_thresholds['max_processing_time'],
                'passed': processing_time <= self.quality_thresholds['max_processing_time']
            }
            
            if processing_time > self.quality_thresholds['max_processing_time']:
                validation_report['errors'].append(f'Processing time exceeded threshold: {processing_time:.1f}s')
            
            # Check URL count
            url_count_check = {
                'count': len(evidence_urls),
                'min_threshold': self.quality_thresholds['min_urls_per_candidate'],
                'max_threshold': self.quality_thresholds['max_urls_per_candidate'],
                'passed': (
                    self.quality_thresholds['min_urls_per_candidate'] <= len(evidence_urls) <= 
                    self.quality_thresholds['max_urls_per_candidate']
                )
            }
            validation_report['quality_checks']['url_count'] = url_count_check
            
            if len(evidence_urls) < self.quality_thresholds['min_urls_per_candidate']:
                validation_report['warnings'].append(f'Too few URLs: {len(evidence_urls)}')
            elif len(evidence_urls) > self.quality_thresholds['max_urls_per_candidate']:
                validation_report['warnings'].append(f'Too many URLs: {len(evidence_urls)}')
            
            # Determine overall quality
            error_count = len(validation_report['errors'])
            warning_count = len(validation_report['warnings'])
            
            if error_count > 0:
                validation_report['overall_quality'] = 'poor'
            elif warning_count > 2:
                validation_report['overall_quality'] = 'fair'
            elif warning_count > 0:
                validation_report['overall_quality'] = 'good'
            else:
                validation_report['overall_quality'] = 'excellent'
            
            # Store in history
            self.quality_history.append(validation_report)
            
            return validation_report
    
    def get_quality_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get quality trends over the specified time period."""
        with self.lock:
            cutoff_time = time.time() - (hours * 3600)
            recent_reports = [
                report for report in self.quality_history
                if report['timestamp'] > cutoff_time
            ]
            
            if not recent_reports:
                return {'error': 'No quality data available for the specified period'}
            
            # Calculate trends
            quality_counts = defaultdict(int)
            avg_relevance_scores = []
            avg_domain_authorities = []
            processing_times = []
            
            for report in recent_reports:
                quality_counts[report['overall_quality']] += 1
                
                if 'relevance' in report['quality_checks']:
                    avg_relevance_scores.append(report['quality_checks']['relevance']['average_score'])
                
                if 'domain_authority' in report['quality_checks']:
                    avg_domain_authorities.append(report['quality_checks']['domain_authority']['average_score'])
                
                if 'processing_time' in report['quality_checks']:
                    processing_times.append(report['quality_checks']['processing_time']['time_seconds'])
            
            trends = {
                'period_hours': hours,
                'total_validations': len(recent_reports),
                'quality_distribution': dict(quality_counts),
                'metrics': {}
            }
            
            if avg_relevance_scores:
                trends['metrics']['relevance_score'] = {
                    'average': statistics.mean(avg_relevance_scores),
                    'trend': self._calculate_trend(avg_relevance_scores)
                }
            
            if avg_domain_authorities:
                trends['metrics']['domain_authority'] = {
                    'average': statistics.mean(avg_domain_authorities),
                    'trend': self._calculate_trend(avg_domain_authorities)
                }
            
            if processing_times:
                trends['metrics']['processing_time'] = {
                    'average': statistics.mean(processing_times),
                    'trend': self._calculate_trend(processing_times, reverse=True)  # Lower is better
                }
            
            return trends
    
    def _calculate_trend(self, values: List[float], reverse: bool = False) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return 'stable'
        
        # Compare first half with second half
        mid_point = len(values) // 2
        first_half_avg = statistics.mean(values[:mid_point])
        second_half_avg = statistics.mean(values[mid_point:])
        
        diff_ratio = (second_half_avg - first_half_avg) / first_half_avg
        
        if reverse:
            diff_ratio = -diff_ratio
        
        if diff_ratio > 0.05:  # 5% improvement
            return 'improving'
        elif diff_ratio < -0.05:  # 5% degradation
            return 'degrading'
        else:
            return 'stable'


class EvidenceMonitoringSystem:
    """Comprehensive monitoring system for evidence finder."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.quality_assurance = EvidenceQualityAssurance()
        
        # Performance metrics
        self.metrics = {
            'requests_processed': 0,
            'evidence_urls_generated': 0,
            'processing_time_total': 0.0,
            'errors_total': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls_made': 0
        }
        
        # Real-time monitoring
        self.recent_performance = deque(maxlen=100)  # Last 100 operations
        self.alerts = deque(maxlen=50)  # Last 50 alerts
        self.lock = Lock()
        
        # Alert thresholds
        self.alert_thresholds = {
            'max_processing_time': 30.0,
            'max_error_rate': 0.2,
            'min_success_rate': 0.8,
            'max_response_time_p95': 10.0
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('evidence_finder')
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        try:
            file_handler = logging.FileHandler('evidence_finder.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass  # File logging is optional
        
        return logger
    
    def log_evidence_generation(
        self,
        candidate_id: str,
        evidence_urls: List[EvidenceURL],
        processing_time: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log evidence generation event."""
        with self.lock:
            # Update metrics
            self.metrics['requests_processed'] += 1
            self.metrics['evidence_urls_generated'] += len(evidence_urls)
            self.metrics['processing_time_total'] += processing_time
            
            if not success:
                self.metrics['errors_total'] += 1
            
            # Log event
            log_data = {
                'candidate_id': candidate_id,
                'evidence_count': len(evidence_urls),
                'processing_time': processing_time,
                'success': success,
                'timestamp': time.time()
            }
            
            if error_message:
                log_data['error'] = error_message
                self.logger.error(f"Evidence generation failed for candidate {candidate_id}: {error_message}")
            else:
                self.logger.info(f"Generated {len(evidence_urls)} evidence URLs for candidate {candidate_id} in {processing_time:.2f}s")
            
            # Store for real-time monitoring
            self.recent_performance.append(log_data)
            
            # Quality validation
            if success and evidence_urls:
                quality_report = self.quality_assurance.validate_evidence_quality(evidence_urls, processing_time)
                log_data['quality_report'] = quality_report
                
                # Check for quality alerts
                self._check_quality_alerts(quality_report, candidate_id)
            
            # Check performance alerts
            self._check_performance_alerts(processing_time, success)
    
    def log_cache_event(self, event_type: str, cache_key: str, hit: bool = False):
        """Log cache events."""
        with self.lock:
            if hit:
                self.metrics['cache_hits'] += 1
            else:
                self.metrics['cache_misses'] += 1
            
            self.logger.debug(f"Cache {event_type}: {cache_key} ({'hit' if hit else 'miss'})")
    
    def log_api_call(self, api_name: str, duration: float, success: bool, tokens_used: int = 0):
        """Log external API calls."""
        with self.lock:
            self.metrics['api_calls_made'] += 1
            
            log_message = f"API call to {api_name}: {duration:.2f}s, {tokens_used} tokens"
            if success:
                self.logger.debug(log_message)
            else:
                self.logger.warning(f"Failed {log_message}")
    
    def _check_quality_alerts(self, quality_report: Dict[str, Any], candidate_id: str):
        """Check for quality-related alerts."""
        if quality_report['overall_quality'] == 'poor':
            alert = PerformanceAlert(
                timestamp=time.time(),
                alert_type='quality',
                severity='high',
                message=f"Poor quality evidence generated for candidate {candidate_id}",
                metrics=quality_report,
                threshold_exceeded='overall_quality'
            )
            self.alerts.append(alert)
            self.logger.warning(f"Quality alert: {alert.message}")
        
        # Check specific quality metrics
        if 'processing_time' in quality_report['quality_checks']:
            processing_check = quality_report['quality_checks']['processing_time']
            if not processing_check['passed']:
                alert = PerformanceAlert(
                    timestamp=time.time(),
                    alert_type='performance',
                    severity='medium',
                    message=f"Processing time exceeded threshold: {processing_check['time_seconds']:.1f}s",
                    metrics={'processing_time': processing_check['time_seconds']},
                    threshold_exceeded='max_processing_time'
                )
                self.alerts.append(alert)
    
    def _check_performance_alerts(self, processing_time: float, success: bool):
        """Check for performance-related alerts."""
        # Processing time alert
        if processing_time > self.alert_thresholds['max_processing_time']:
            alert = PerformanceAlert(
                timestamp=time.time(),
                alert_type='performance',
                severity='high',
                message=f"Processing time exceeded threshold: {processing_time:.1f}s",
                metrics={'processing_time': processing_time},
                threshold_exceeded='max_processing_time'
            )
            self.alerts.append(alert)
        
        # Error rate alert (check recent performance)
        if len(self.recent_performance) >= 10:
            recent_errors = sum(1 for perf in list(self.recent_performance)[-10:] if not perf['success'])
            error_rate = recent_errors / 10
            
            if error_rate > self.alert_thresholds['max_error_rate']:
                alert = PerformanceAlert(
                    timestamp=time.time(),
                    alert_type='reliability',
                    severity='critical',
                    message=f"High error rate detected: {error_rate:.1%}",
                    metrics={'error_rate': error_rate, 'recent_errors': recent_errors},
                    threshold_exceeded='max_error_rate'
                )
                self.alerts.append(alert)
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data."""
        with self.lock:
            # Calculate derived metrics
            total_requests = self.metrics['requests_processed']
            
            dashboard = {
                'timestamp': time.time(),
                'overview': {
                    'total_requests': total_requests,
                    'total_evidence_urls': self.metrics['evidence_urls_generated'],
                    'total_errors': self.metrics['errors_total'],
                    'success_rate': (
                        (total_requests - self.metrics['errors_total']) / total_requests
                        if total_requests > 0 else 0.0
                    ),
                    'avg_processing_time': (
                        self.metrics['processing_time_total'] / total_requests
                        if total_requests > 0 else 0.0
                    ),
                    'avg_urls_per_request': (
                        self.metrics['evidence_urls_generated'] / total_requests
                        if total_requests > 0 else 0.0
                    )
                },
                'cache_performance': {
                    'total_hits': self.metrics['cache_hits'],
                    'total_misses': self.metrics['cache_misses'],
                    'hit_rate': (
                        self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
                        if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0.0
                    )
                },
                'api_usage': {
                    'total_calls': self.metrics['api_calls_made']
                },
                'recent_performance': self._get_recent_performance_stats(),
                'active_alerts': len(self.alerts),
                'quality_trends': self.quality_assurance.get_quality_trends(hours=24)
            }
            
            return dashboard
    
    def _get_recent_performance_stats(self) -> Dict[str, Any]:
        """Get statistics for recent performance."""
        if not self.recent_performance:
            return {'no_data': True}
        
        recent_data = list(self.recent_performance)
        processing_times = [perf['processing_time'] for perf in recent_data]
        success_count = sum(1 for perf in recent_data if perf['success'])
        
        stats = {
            'sample_size': len(recent_data),
            'success_rate': success_count / len(recent_data),
            'avg_processing_time': statistics.mean(processing_times),
            'p95_processing_time': statistics.quantiles(processing_times, n=20)[18] if len(processing_times) >= 20 else max(processing_times),
            'min_processing_time': min(processing_times),
            'max_processing_time': max(processing_times)
        }
        
        return stats
    
    def get_alerts(self, severity: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts, optionally filtered by severity."""
        with self.lock:
            alerts = list(self.alerts)
            
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
            
            # Sort by timestamp (most recent first) and limit
            alerts.sort(key=lambda a: a.timestamp, reverse=True)
            alerts = alerts[:limit]
            
            return [asdict(alert) for alert in alerts]
    
    def clear_alerts(self, older_than_hours: int = 24):
        """Clear old alerts."""
        with self.lock:
            cutoff_time = time.time() - (older_than_hours * 3600)
            self.alerts = deque(
                [alert for alert in self.alerts if alert.timestamp > cutoff_time],
                maxlen=50
            )
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format."""
        dashboard = self.get_performance_dashboard()
        
        if format.lower() == 'json':
            return json.dumps(dashboard, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global monitoring instance
_monitoring_system: Optional[EvidenceMonitoringSystem] = None


def get_monitoring_system() -> EvidenceMonitoringSystem:
    """Get the global monitoring system instance."""
    global _monitoring_system
    
    if _monitoring_system is None:
        _monitoring_system = EvidenceMonitoringSystem()
    
    return _monitoring_system


def log_evidence_generation(
    candidate_id: str,
    evidence_urls: List[EvidenceURL],
    processing_time: float,
    success: bool,
    error_message: Optional[str] = None
):
    """Convenience function to log evidence generation."""
    monitoring = get_monitoring_system()
    monitoring.log_evidence_generation(candidate_id, evidence_urls, processing_time, success, error_message)


def log_cache_event(event_type: str, cache_key: str, hit: bool = False):
    """Convenience function to log cache events."""
    monitoring = get_monitoring_system()
    monitoring.log_cache_event(event_type, cache_key, hit)


def log_api_call(api_name: str, duration: float, success: bool, tokens_used: int = 0):
    """Convenience function to log API calls."""
    monitoring = get_monitoring_system()
    monitoring.log_api_call(api_name, duration, success, tokens_used)


def get_performance_dashboard() -> Dict[str, Any]:
    """Get performance dashboard data."""
    monitoring = get_monitoring_system()
    return monitoring.get_performance_dashboard()


def get_alerts(severity: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent alerts."""
    monitoring = get_monitoring_system()
    return monitoring.get_alerts(severity, limit)


async def monitoring_health_check() -> Dict[str, Any]:
    """Perform a health check of the monitoring system."""
    monitoring = get_monitoring_system()
    
    health_status = {
        'timestamp': time.time(),
        'status': 'healthy',
        'checks': {}
    }
    
    try:
        # Check if logging is working
        monitoring.logger.info("Health check: Logging system operational")
        health_status['checks']['logging'] = {'status': 'ok'}
    except Exception as e:
        health_status['checks']['logging'] = {'status': 'error', 'message': str(e)}
        health_status['status'] = 'degraded'
    
    try:
        # Check metrics collection
        dashboard = monitoring.get_performance_dashboard()
        health_status['checks']['metrics'] = {'status': 'ok', 'total_requests': dashboard['overview']['total_requests']}
    except Exception as e:
        health_status['checks']['metrics'] = {'status': 'error', 'message': str(e)}
        health_status['status'] = 'degraded'
    
    try:
        # Check quality assurance
        quality_trends = monitoring.quality_assurance.get_quality_trends(hours=1)
        health_status['checks']['quality_assurance'] = {'status': 'ok'}
    except Exception as e:
        health_status['checks']['quality_assurance'] = {'status': 'error', 'message': str(e)}
        health_status['status'] = 'degraded'
    
    return health_status


def test_monitoring_system():
    """Test the monitoring system functionality."""
    print("Testing Evidence Monitoring System:")
    print("=" * 50)
    
    monitoring = get_monitoring_system()
    
    # Test evidence generation logging
    from evidence_validator import EvidenceURL, EvidenceType
    
    test_evidence = [
        EvidenceURL(
            url="https://example.com/test",
            title="Test Evidence",
            description="Test evidence for monitoring",
            evidence_type=EvidenceType.PRICING_PAGE,
            relevance_score=0.85,
            confidence_level="high",
            supporting_explanation="Test explanation",
            domain_authority=0.8,
            page_quality_score=0.9,
            last_validated=time.time()
        )
    ]
    
    # Log some test events
    monitoring.log_evidence_generation("test_candidate_1", test_evidence, 2.5, True)
    monitoring.log_evidence_generation("test_candidate_2", [], 1.0, False, "No evidence found")
    monitoring.log_cache_event("get", "test_key", hit=True)
    monitoring.log_api_call("openai_search", 1.2, True, 150)
    
    # Get dashboard
    dashboard = monitoring.get_performance_dashboard()
    print(f"Total requests: {dashboard['overview']['total_requests']}")
    print(f"Success rate: {dashboard['overview']['success_rate']:.1%}")
    print(f"Cache hit rate: {dashboard['cache_performance']['hit_rate']:.1%}")
    
    # Get alerts
    alerts = monitoring.get_alerts()
    print(f"Active alerts: {len(alerts)}")
    
    # Test quality trends
    quality_trends = monitoring.quality_assurance.get_quality_trends(hours=1)
    print(f"Quality validations: {quality_trends.get('total_validations', 0)}")
    
    print("\nMonitoring system test completed successfully!")


if __name__ == '__main__':
    test_monitoring_system()