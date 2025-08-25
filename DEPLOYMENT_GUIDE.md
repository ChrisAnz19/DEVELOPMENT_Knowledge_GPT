# URL Evidence Finder - Deployment Guide

This guide provides step-by-step instructions for deploying the URL Evidence Finder system to production.

## 📋 Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 1GB free space for caching and logs
- **Network**: Stable internet connection for OpenAI API calls

### Dependencies

```bash
pip install openai>=1.0.0 pydantic>=2.0.0 httpx>=0.24.0 asyncio
```

### API Keys

- **OpenAI API Key**: Required for web search functionality
- **Rate Limits**: Ensure adequate OpenAI API rate limits for your usage

## 🚀 Deployment Steps

### Step 1: Environment Setup

1. **Create Environment File**
   ```bash
   # Create .env file
   cat > .env << EOF
   # Core Configuration
   OPENAI_API_KEY=your-openai-api-key-here
   EVIDENCE_FINDER_ENABLED=true
   
   # Performance Settings
   EVIDENCE_FINDER_CACHE=true
   EVIDENCE_FINDER_ASYNC=true
   EVIDENCE_MAX_CANDIDATES=10
   EVIDENCE_TIMEOUT=30
   EVIDENCE_CACHE_SIZE=1000
   
   # Quality Settings
   EVIDENCE_MIN_EXPLANATION_LENGTH=10
   EVIDENCE_REQUIRE_BEHAVIORAL=false
   EOF
   ```

2. **Load Environment Variables**
   ```bash
   source .env
   # Or use python-dotenv in your application
   ```

### Step 2: File Deployment

1. **Copy Core Files**
   ```bash
   # Core system files
   cp explanation_analyzer.py /path/to/your/app/
   cp search_query_generator.py /path/to/your/app/
   cp web_search_engine.py /path/to/your/app/
   cp evidence_validator.py /path/to/your/app/
   cp evidence_models.py /path/to/your/app/
   cp evidence_cache.py /path/to/your/app/
   cp url_evidence_finder.py /path/to/your/app/
   cp evidence_integration.py /path/to/your/app/
   cp evidence_monitoring.py /path/to/your/app/
   ```

2. **Set File Permissions**
   ```bash
   chmod 644 *.py
   chmod +x url_evidence_finder.py
   ```

### Step 3: API Integration

1. **Modify `api/main.py`**

   Add the import at the top of the file:
   ```python
   # Import evidence integration
   try:
       from evidence_integration import enhance_candidates_with_evidence_urls, get_evidence_integration_stats
       EVIDENCE_INTEGRATION_AVAILABLE = True
       print("[API] Evidence integration module loaded successfully")
   except ImportError as e:
       EVIDENCE_INTEGRATION_AVAILABLE = False
       print(f"[API] Evidence integration not available: {e}")
   ```

2. **Add Evidence Enhancement**

   In the `process_search` function, after behavioral data processing:
   ```python
   # Enhance candidates with evidence URLs (new feature)
   if EVIDENCE_INTEGRATION_AVAILABLE and candidates:
       try:
           print(f"[Evidence Enhancement] Processing {len(candidates)} candidates for evidence URLs")
           evidence_start_time = time.time()
           
           # Enhance candidates with evidence URLs
           candidates = await enhance_candidates_with_evidence_urls(candidates, prompt)
           
           evidence_processing_time = time.time() - evidence_start_time
           print(f"[Evidence Enhancement] Completed in {evidence_processing_time:.2f}s")
           
           # Log evidence statistics
           evidence_count = sum(len(c.get('evidence_urls', [])) for c in candidates if isinstance(c, dict))
           candidates_with_evidence = sum(1 for c in candidates if isinstance(c, dict) and c.get('evidence_urls'))
           
           print(f"[Evidence Enhancement] Found {evidence_count} total evidence URLs for {candidates_with_evidence}/{len(candidates)} candidates")
           
       except Exception as e:
           print(f"[Evidence Enhancement Error] Failed to enhance candidates with evidence: {str(e)}")
           # Continue processing without evidence URLs - don't fail the entire search
   ```

3. **Add Monitoring Endpoint**

   Add this endpoint before the demo endpoints:
   ```python
   @app.get("/api/evidence/stats")
   async def get_evidence_stats():
       """Get evidence integration statistics and performance metrics."""
       try:
           if not EVIDENCE_INTEGRATION_AVAILABLE:
               return {
                   "enabled": False,
                   "error": "Evidence integration module not available"
               }
           
           stats = get_evidence_integration_stats()
           return stats
           
       except Exception as e:
           raise HTTPException(status_code=500, detail=f"Failed to get evidence stats: {str(e)}")
   ```

### Step 4: Testing Deployment

1. **Run System Tests**
   ```bash
   python test_evidence_finder.py
   ```

2. **Test API Integration**
   ```bash
   # Start your API server
   python api/main.py
   
   # Test evidence stats endpoint
   curl http://localhost:8000/api/evidence/stats
   ```

3. **Test Evidence Generation**
   ```bash
   # Make a search request and check for evidence_urls in response
   curl -X POST http://localhost:8000/api/search \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Find executives researching CRM solutions"}'
   ```

### Step 5: Production Configuration

1. **Logging Configuration**
   ```python
   # In your application startup
   import logging
   
   # Configure evidence finder logging
   evidence_logger = logging.getLogger('evidence_finder')
   evidence_logger.setLevel(logging.INFO)
   
   # Add file handler for production
   file_handler = logging.FileHandler('/var/log/evidence_finder.log')
   file_handler.setFormatter(logging.Formatter(
       '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   ))
   evidence_logger.addHandler(file_handler)
   ```

2. **Performance Tuning**
   ```bash
   # For high-volume production
   export EVIDENCE_CACHE_SIZE=5000
   export EVIDENCE_MAX_CANDIDATES=20
   export EVIDENCE_TIMEOUT=45
   ```

3. **Monitoring Setup**
   ```python
   # Add to your application monitoring
   from evidence_monitoring import get_performance_dashboard, get_alerts
   
   # Schedule regular monitoring checks
   async def monitor_evidence_system():
       dashboard = get_performance_dashboard()
       alerts = get_alerts(severity="high")
       
       # Send to your monitoring system
       if alerts:
           send_alert_notification(alerts)
   ```

## 🔧 Configuration Options

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `EVIDENCE_FINDER_ENABLED` | `true` | Enable/disable the entire system |
| `EVIDENCE_FINDER_CACHE` | `true` | Enable result caching |
| `EVIDENCE_FINDER_ASYNC` | `true` | Enable async processing |
| `EVIDENCE_MAX_CANDIDATES` | `10` | Max candidates to process per request |
| `EVIDENCE_TIMEOUT` | `30` | Processing timeout in seconds |
| `EVIDENCE_CACHE_SIZE` | `1000` | Maximum cache entries |
| `EVIDENCE_MIN_EXPLANATION_LENGTH` | `10` | Minimum explanation length to process |
| `EVIDENCE_REQUIRE_BEHAVIORAL` | `false` | Require behavioral data for processing |

### Performance Tuning

#### Low-Volume Deployment (< 100 requests/day)
```bash
EVIDENCE_CACHE_SIZE=500
EVIDENCE_MAX_CANDIDATES=5
EVIDENCE_TIMEOUT=20
```

#### Medium-Volume Deployment (100-1000 requests/day)
```bash
EVIDENCE_CACHE_SIZE=2000
EVIDENCE_MAX_CANDIDATES=10
EVIDENCE_TIMEOUT=30
```

#### High-Volume Deployment (> 1000 requests/day)
```bash
EVIDENCE_CACHE_SIZE=10000
EVIDENCE_MAX_CANDIDATES=20
EVIDENCE_TIMEOUT=45
```

## 📊 Monitoring & Maintenance

### Health Checks

1. **System Health Endpoint**
   ```python
   @app.get("/api/evidence/health")
   async def evidence_health_check():
       from evidence_monitoring import monitoring_health_check
       return await monitoring_health_check()
   ```

2. **Performance Monitoring**
   ```bash
   # Check performance dashboard
   curl http://localhost:8000/api/evidence/stats
   
   # Check for alerts
   curl http://localhost:8000/api/evidence/stats | jq '.statistics.errors'
   ```

### Log Monitoring

Monitor these log patterns:

```bash
# Success patterns
grep "Evidence Enhancement.*Completed" /var/log/evidence_finder.log

# Error patterns  
grep "Evidence Enhancement Error" /var/log/evidence_finder.log

# Performance issues
grep "Processing time exceeded" /var/log/evidence_finder.log
```

### Cache Management

```python
# Clear cache if needed
from evidence_integration import get_evidence_integration_service
service = get_evidence_integration_service()
if hasattr(service.evidence_finder, 'cleanup_cache'):
    service.evidence_finder.cleanup_cache()
```

## 🚨 Troubleshooting

### Common Deployment Issues

1. **Import Errors**
   ```bash
   # Check Python path
   python -c "import evidence_integration; print('OK')"
   
   # Install missing dependencies
   pip install -r requirements.txt
   ```

2. **OpenAI API Issues**
   ```bash
   # Test API key
   python -c "from openai import OpenAI; client = OpenAI(); print('API key valid')"
   
   # Check rate limits
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

3. **Performance Issues**
   ```bash
   # Check cache hit rate
   curl http://localhost:8000/api/evidence/stats | jq '.cache_performance.hit_rate'
   
   # Monitor processing times
   tail -f /var/log/evidence_finder.log | grep "processing time"
   ```

4. **Memory Issues**
   ```bash
   # Reduce cache size
   export EVIDENCE_CACHE_SIZE=500
   
   # Limit concurrent processing
   export EVIDENCE_MAX_CANDIDATES=5
   ```

### Error Recovery

1. **Graceful Degradation**
   - System automatically disables on repeated failures
   - Returns candidates without evidence URLs
   - Logs all errors for investigation

2. **Manual Recovery**
   ```python
   # Restart evidence service
   from evidence_integration import get_evidence_integration_service
   service = get_evidence_integration_service()
   service.config.enabled = True
   ```

## 🔒 Security Considerations

### API Key Security

1. **Environment Variables**
   ```bash
   # Never commit API keys to code
   # Use environment variables or secure key management
   export OPENAI_API_KEY="sk-..."
   ```

2. **Key Rotation**
   ```bash
   # Update API key without restart
   # The system will pick up new environment variables
   export OPENAI_API_KEY="new-key"
   # Restart application
   ```

### Data Privacy

1. **No PII Storage**
   - System only processes behavioral explanations
   - No personal information is cached or logged
   - Search results are temporary and expire

2. **Secure Logging**
   ```python
   # Sanitize logs in production
   import logging
   
   class SanitizingFormatter(logging.Formatter):
       def format(self, record):
           # Remove sensitive data from logs
           message = super().format(record)
           return re.sub(r'api_key=\w+', 'api_key=***', message)
   ```

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Stateless Design**
   - System is stateless and can be scaled horizontally
   - Cache is local to each instance
   - No shared state between instances

2. **Load Balancing**
   ```nginx
   # Nginx configuration
   upstream evidence_api {
       server app1:8000;
       server app2:8000;
       server app3:8000;
   }
   ```

### Vertical Scaling

1. **Memory Scaling**
   ```bash
   # Increase cache size for more memory
   export EVIDENCE_CACHE_SIZE=20000
   ```

2. **CPU Scaling**
   ```bash
   # Increase concurrent processing
   export EVIDENCE_MAX_CANDIDATES=50
   ```

## 🔄 Updates & Maintenance

### Rolling Updates

1. **Zero-Downtime Deployment**
   ```bash
   # Deploy to one instance at a time
   # System gracefully handles failures
   ```

2. **Feature Flags**
   ```bash
   # Disable during maintenance
   export EVIDENCE_FINDER_ENABLED=false
   
   # Re-enable after update
   export EVIDENCE_FINDER_ENABLED=true
   ```

### Backup & Recovery

1. **Configuration Backup**
   ```bash
   # Backup environment configuration
   env | grep EVIDENCE_ > evidence_config_backup.env
   ```

2. **Cache Recovery**
   - Cache is automatically rebuilt
   - No manual recovery needed
   - Performance may be slower initially

## 📞 Support

### Monitoring Alerts

Set up alerts for:
- High error rates (> 20%)
- Slow processing times (> 30s)
- Low success rates (< 80%)
- Cache performance issues

### Contact Information

For deployment issues:
1. Check logs and monitoring dashboard
2. Review troubleshooting section
3. Contact development team with:
   - Error logs
   - Performance metrics
   - Configuration details

---

**Deployment completed successfully! 🎉**

The URL Evidence Finder is now ready to enhance your candidate search results with concrete, verifiable evidence URLs.