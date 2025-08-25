#!/usr/bin/env python3
"""
Diversity Monitoring and Analytics for URL Evidence Enhancement.

This module provides monitoring, analytics, and reporting functionality
for the diversity enhancement system.
"""

import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque

from diversity_metrics import BatchDiversityMetrics, DiversityScore
from enhanced_data_models import ProcessingStats, DiversityConfig


@dataclass
class DiversityAlert:
    """Alert for diversity system issues."""
    timestamp: float
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    metrics: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PerformanceMetrics:
    """Performance metrics for diversity processing."""
    processing_time_ms: float
    memory_usage_mb: float
    api_calls_made: int
    cache_hit_rate: float
    success_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DiversityMonitor:
    """
    Monitors diversity system performance, quality, and health.
    Provides real-time analytics and alerting.
    """
    
    def __init__(self, alert_thresholds: Optional[Dict[str, float]] = None):
        # Monitoring data
        self.session_stats = ProcessingStats()
        self.performance_history = deque(maxlen=1000)  # Last 1000 operations
        self.diversity_history = deque(maxlen=100)     # Last 100 batches
        self.alerts = deque(maxlen=50)                 # Last 50 alerts
        
        # Alert thresholds
        self.alert_thresholds = alert_thresholds or {
            'uniqueness_rate_min': 0.7,
            'diversity_index_min': 2.0,
            'processing_time_max_ms': 5000,
            'success_rate_min': 0.8,
            'major_sources_max_percentage': 0.6
        }
        
        # Tracking
        self.start_time = time.time()
        self.last_batch_metrics = None
        
    def record_batch_processing(
        self,
        batch_metrics: BatchDiversityMetrics,
        performance_metrics: PerformanceMetrics,
        config: DiversityConfig
    ):
        """
        Record metrics from a batch processing operation.
        
        Args:
            batch_metrics: Diversity metrics for the batch
            performance_metrics: Performance metrics
            config: Configuration used for processing
        """
        # Update session stats
        self.session_stats.candidates_processed += batch_metrics.total_candidates
        self.session_stats.urls_found += batch_metrics.total_urls
        self.session_stats.unique_domains = batch_metrics.unique_domains
        self.session_stats.diversity_score = batch_metrics.diversity_index
        self.session_stats.processing_time_total += performance_metrics.processing_time_ms / 1000
        
        # Store history
        self.performance_history.append(performance_metrics)
        self.diversity_history.append(batch_metrics)
        self.last_batch_metrics = batch_metrics
        
        # Check for alerts
        self._check_alerts(batch_metrics, performance_metrics, config)
        
        print(f"[Diversity Monitor] Recorded batch: {batch_metrics.total_candidates} candidates, "
              f"{batch_metrics.total_urls} URLs, {batch_metrics.diversity_index:.2f} diversity index")
    
    def record_candidate_processing(
        self,
        candidate_id: str,
        urls_found: int,
        processing_time_ms: float,
        diversity_scores: List[DiversityScore],
        success: bool
    ):
        """
        Record metrics from individual candidate processing.
        
        Args:
            candidate_id: ID of processed candidate
            urls_found: Number of URLs found
            processing_time_ms: Processing time in milliseconds
            diversity_scores: Diversity scores for found URLs
            success: Whether processing was successful
        """
        # Create performance metrics
        performance_metrics = PerformanceMetrics(
            processing_time_ms=processing_time_ms,
            memory_usage_mb=0.0,  # Would need actual memory tracking
            api_calls_made=0,     # Would need API call tracking
            cache_hit_rate=0.0,   # Would need cache tracking
            success_rate=1.0 if success else 0.0
        )
        
        # Store in history
        self.performance_history.append(performance_metrics)
        
        # Update session stats
        self.session_stats.urls_found += urls_found
        if success:
            self.session_stats.candidates_processed += 1
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics."""
        current_time = time.time()
        uptime_seconds = current_time - self.start_time
        
        # Calculate recent performance
        recent_performance = list(self.performance_history)[-10:]  # Last 10 operations
        avg_processing_time = (
            sum(p.processing_time_ms for p in recent_performance) / 
            max(len(recent_performance), 1)
        )
        
        # Calculate recent diversity
        recent_diversity = list(self.diversity_history)[-5:]  # Last 5 batches
        avg_diversity_index = (
            sum(d.diversity_index for d in recent_diversity) /
            max(len(recent_diversity), 1)
        )
        
        return {
            'uptime_seconds': uptime_seconds,
            'session_stats': self.session_stats.to_dict(),
            'recent_performance': {
                'avg_processing_time_ms': avg_processing_time,
                'operations_tracked': len(recent_performance)
            },
            'recent_diversity': {
                'avg_diversity_index': avg_diversity_index,
                'batches_tracked': len(recent_diversity)
            },
            'active_alerts': len([a for a in self.alerts if a.severity in ['high', 'critical']]),
            'last_batch': self.last_batch_metrics.to_dict() if self.last_batch_metrics else None
        }
    
    def get_diversity_analytics(self) -> Dict[str, Any]:
        """Get comprehensive diversity analytics."""
        if not self.diversity_history:
            return {'message': 'No diversity data available yet'}
        
        # Aggregate metrics across all batches
        total_candidates = sum(d.total_candidates for d in self.diversity_history)
        total_urls = sum(d.total_urls for d in self.diversity_history)
        
        # Calculate trends
        diversity_scores = [d.diversity_index for d in self.diversity_history]
        uniqueness_rates = [d.uniqueness_rate for d in self.diversity_history]
        
        # Domain distribution analysis
        all_domains = {}
        for batch in self.diversity_history:
            for domain, count in batch.domain_distribution.items():
                all_domains[domain] = all_domains.get(domain, 0) + count
        
        # Source tier analysis
        all_tiers = defaultdict(int)
        for batch in self.diversity_history:
            for tier, count in batch.source_tier_distribution.items():
                all_tiers[tier] += count
        
        return {
            'summary': {
                'total_candidates_processed': total_candidates,
                'total_urls_found': total_urls,
                'batches_analyzed': len(self.diversity_history),
                'avg_diversity_index': sum(diversity_scores) / len(diversity_scores),
                'avg_uniqueness_rate': sum(uniqueness_rates) / len(uniqueness_rates)
            },
            'trends': {
                'diversity_scores': diversity_scores[-20:],  # Last 20 batches
                'uniqueness_rates': uniqueness_rates[-20:]
            },
            'domain_analysis': {
                'total_unique_domains': len(all_domains),
                'top_domains': sorted(all_domains.items(), key=lambda x: x[1], reverse=True)[:10],
                'domain_concentration': max(all_domains.values()) / sum(all_domains.values()) if all_domains else 0
            },
            'source_tier_analysis': {
                'distribution': dict(all_tiers),
                'alternative_percentage': all_tiers.get('alternative', 0) / max(sum(all_tiers.values()), 1),
                'major_percentage': all_tiers.get('major', 0) / max(sum(all_tiers.values()), 1)
            }
        }
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics and trends."""
        if not self.performance_history:
            return {'message': 'No performance data available yet'}
        
        # Calculate performance metrics
        processing_times = [p.processing_time_ms for p in self.performance_history]
        success_rates = [p.success_rate for p in self.performance_history]
        
        # Recent vs historical comparison
        recent_times = processing_times[-50:]  # Last 50 operations
        historical_times = processing_times[:-50] if len(processing_times) > 50 else []
        
        return {
            'summary': {
                'operations_tracked': len(self.performance_history),
                'avg_processing_time_ms': sum(processing_times) / len(processing_times),
                'avg_success_rate': sum(success_rates) / len(success_rates),
                'min_processing_time_ms': min(processing_times),
                'max_processing_time_ms': max(processing_times)
            },
            'trends': {
                'recent_processing_times': recent_times,
                'recent_avg_time_ms': sum(recent_times) / max(len(recent_times), 1),
                'historical_avg_time_ms': sum(historical_times) / max(len(historical_times), 1) if historical_times else 0
            },
            'performance_distribution': {
                'fast_operations_percentage': len([t for t in processing_times if t < 1000]) / len(processing_times),
                'slow_operations_percentage': len([t for t in processing_times if t > 3000]) / len(processing_times)
            }
        }
    
    def get_alerts(self, severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current alerts, optionally filtered by severity.
        
        Args:
            severity_filter: Filter by severity (low, medium, high, critical)
            
        Returns:
            List of alert dictionaries
        """
        alerts = list(self.alerts)
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]
        
        return [asdict(alert) for alert in alerts]
    
    def _check_alerts(
        self,
        batch_metrics: BatchDiversityMetrics,
        performance_metrics: PerformanceMetrics,
        config: DiversityConfig
    ):
        """Check for alert conditions and generate alerts."""
        current_time = time.time()
        
        # Check uniqueness rate
        if batch_metrics.uniqueness_rate < self.alert_thresholds['uniqueness_rate_min']:
            self._create_alert(
                alert_type='low_uniqueness',
                severity='medium',
                message=f"Low URL uniqueness rate: {batch_metrics.uniqueness_rate:.1%}",
                metrics={'uniqueness_rate': batch_metrics.uniqueness_rate},
                recommendations=[
                    "Consider increasing diversity weight in configuration",
                    "Check if too many major sources are being used",
                    "Verify alternative source database is comprehensive"
                ]
            )
        
        # Check diversity index
        if batch_metrics.diversity_index < self.alert_thresholds['diversity_index_min']:
            self._create_alert(
                alert_type='low_diversity',
                severity='medium',
                message=f"Low diversity index: {batch_metrics.diversity_index:.2f}",
                metrics={'diversity_index': batch_metrics.diversity_index},
                recommendations=[
                    "Increase diversity weight in configuration",
                    "Enable more aggressive diversity mode",
                    "Expand alternative source database"
                ]
            )
        
        # Check processing time
        if performance_metrics.processing_time_ms > self.alert_thresholds['processing_time_max_ms']:
            self._create_alert(
                alert_type='slow_processing',
                severity='high',
                message=f"Slow processing time: {performance_metrics.processing_time_ms:.0f}ms",
                metrics={'processing_time_ms': performance_metrics.processing_time_ms},
                recommendations=[
                    "Check for API rate limiting issues",
                    "Consider reducing number of search queries per candidate",
                    "Optimize caching strategies"
                ]
            )
        
        # Check major sources percentage
        total_sources = sum(batch_metrics.source_tier_distribution.values())
        if total_sources > 0:
            major_percentage = batch_metrics.source_tier_distribution.get('major', 0) / total_sources
            if major_percentage > self.alert_thresholds['major_sources_max_percentage']:
                self._create_alert(
                    alert_type='too_many_major_sources',
                    severity='low',
                    message=f"High percentage of major sources: {major_percentage:.1%}",
                    metrics={'major_sources_percentage': major_percentage},
                    recommendations=[
                        "Enable prioritize_alternatives in configuration",
                        "Increase diversity weight",
                        "Add more alternative sources to database"
                    ]
                )
    
    def _create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        metrics: Dict[str, Any],
        recommendations: List[str]
    ):
        """Create and store an alert."""
        alert = DiversityAlert(
            timestamp=time.time(),
            alert_type=alert_type,
            severity=severity,
            message=message,
            metrics=metrics,
            recommendations=recommendations
        )
        
        self.alerts.append(alert)
        
        # Log alert
        print(f"[Diversity Alert - {severity.upper()}] {message}")
    
    def export_analytics_report(self, filepath: str):
        """Export comprehensive analytics report to JSON file."""
        report = {
            'generated_at': time.time(),
            'real_time_metrics': self.get_real_time_metrics(),
            'diversity_analytics': self.get_diversity_analytics(),
            'performance_analytics': self.get_performance_analytics(),
            'alerts': self.get_alerts(),
            'configuration': {
                'alert_thresholds': self.alert_thresholds,
                'monitoring_start_time': self.start_time
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"[Diversity Monitor] Analytics report exported to {filepath}")
    
    def reset_monitoring(self):
        """Reset all monitoring data (for testing or new sessions)."""
        self.session_stats = ProcessingStats()
        self.performance_history.clear()
        self.diversity_history.clear()
        self.alerts.clear()
        self.start_time = time.time()
        self.last_batch_metrics = None
        
        print(f"[Diversity Monitor] Monitoring data reset")


def test_diversity_monitoring():
    """Test function for diversity monitoring."""
    print("Testing Diversity Monitoring:")
    print("=" * 50)
    
    # Create monitor
    monitor = DiversityMonitor()
    
    # Create test data
    from diversity_metrics import BatchDiversityMetrics
    
    # Simulate batch processing
    test_batch_metrics = BatchDiversityMetrics(
        total_candidates=5,
        total_urls=20,
        unique_domains=15,
        domain_distribution={
            'example.com': 2,
            'alternative.com': 3,
            'niche-source.com': 2,
            'specialized.org': 1
        },
        source_tier_distribution={
            'alternative': 8,
            'niche': 6,
            'mid-tier': 4,
            'major': 2
        },
        evidence_type_distribution={
            'product_page': 8,
            'pricing_page': 5,
            'comparison_site': 4,
            'review_site': 3
        },
        diversity_index=2.5,
        uniqueness_rate=0.75,
        average_urls_per_candidate=4.0
    )
    
    test_performance_metrics = PerformanceMetrics(
        processing_time_ms=2500,
        memory_usage_mb=50.0,
        api_calls_made=15,
        cache_hit_rate=0.3,
        success_rate=1.0
    )
    
    from enhanced_data_models import DiversityConfig
    test_config = DiversityConfig()
    
    # Record batch processing
    print("1. Recording batch processing:")
    monitor.record_batch_processing(test_batch_metrics, test_performance_metrics, test_config)
    
    # Get real-time metrics
    print("\n2. Real-time metrics:")
    real_time = monitor.get_real_time_metrics()
    for key, value in real_time.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for sub_key, sub_value in value.items():
                print(f"     {sub_key}: {sub_value}")
        else:
            print(f"   {key}: {value}")
    
    # Simulate more batches to trigger alerts
    print("\n3. Simulating low diversity batch (should trigger alert):")
    low_diversity_batch = BatchDiversityMetrics(
        total_candidates=3,
        total_urls=12,
        unique_domains=5,  # Low uniqueness
        domain_distribution={'major-site.com': 8, 'another-major.com': 4},
        source_tier_distribution={'major': 10, 'mid-tier': 2},
        evidence_type_distribution={'product_page': 12},
        diversity_index=1.2,  # Low diversity
        uniqueness_rate=0.4,  # Low uniqueness
        average_urls_per_candidate=4.0
    )
    
    slow_performance = PerformanceMetrics(
        processing_time_ms=6000,  # Slow processing
        memory_usage_mb=100.0,
        api_calls_made=25,
        cache_hit_rate=0.1,
        success_rate=0.7  # Low success rate
    )
    
    monitor.record_batch_processing(low_diversity_batch, slow_performance, test_config)
    
    # Check alerts
    print("\n4. Generated alerts:")
    alerts = monitor.get_alerts()
    for alert in alerts:
        print(f"   Alert: {alert['alert_type']} ({alert['severity']})")
        print(f"   Message: {alert['message']}")
        print(f"   Recommendations: {len(alert['recommendations'])} provided")
        print()
    
    # Get analytics
    print("5. Diversity analytics:")
    diversity_analytics = monitor.get_diversity_analytics()
    summary = diversity_analytics['summary']
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n6. Performance analytics:")
    performance_analytics = monitor.get_performance_analytics()
    perf_summary = performance_analytics['summary']
    for key, value in perf_summary.items():
        print(f"   {key}: {value}")


if __name__ == '__main__':
    test_diversity_monitoring()