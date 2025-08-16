# Design Document

## Overview

This design addresses the disconnect between working HubSpot OAuth API endpoints and the lack of integration runs in the Prismatic.io dashboard. The issue appears to be a deployment synchronization problem where the API endpoints exist but the Prismatic integration isn't properly connected or configured to use them.

The solution involves creating comprehensive diagnostic tools to identify the root cause and provide automated verification of the deployment pipeline.

## Architecture

The diagnostic system will have multiple layers:

1. **API Endpoint Verification** - Verify all endpoints work in both environments
2. **Prismatic Integration Analysis** - Check integration configuration and connectivity
3. **Environment Synchronization Check** - Compare local vs production deployment
4. **Automated Remediation** - Provide specific fix recommendations

## Components and Interfaces

### 1. Enhanced Deployment Diagnostic Tool

**Purpose**: Extend the existing `test_deployment_debug.py` to include Prismatic-specific checks

**New Features**:
- Prismatic webhook URL verification
- Integration configuration validation
- Environment variable comparison
- Network connectivity testing

**Implementation**:
```python
class PrismaticIntegrationDiagnostic:
    def __init__(self, base_url: str, prismatic_config: Dict):
        self.base_url = base_url
        self.prismatic_config = prismatic_config
        
    async def verify_prismatic_connectivity(self):
        """Test if Prismatic can reach our API endpoints"""
        # Test webhook endpoints that Prismatic would call
        # Verify authentication works
        # Check response formats match expectations
        
    async def validate_integration_config(self):
        """Verify Prismatic integration configuration"""
        # Check webhook URLs point to correct endpoints
        # Verify authentication credentials
        # Validate trigger conditions
        
    async def compare_environments(self):
        """Compare local vs production configuration"""
        # Environment variables
        # Available endpoints
        # Response formats
```

### 2. Prismatic Configuration Validator

**Purpose**: Validate that Prismatic integration is properly configured

**Key Checks**:
- Webhook URL format and accessibility
- Authentication token validity
- Trigger event configuration
- Response format compatibility

**Implementation**:
```python
class PrismaticConfigValidator:
    def validate_webhook_urls(self, config):
        """Ensure webhook URLs are correct and accessible"""
        
    def validate_auth_config(self, config):
        """Verify authentication configuration"""
        
    def validate_triggers(self, config):
        """Check trigger conditions and events"""
```

### 3. API Endpoint Health Monitor

**Purpose**: Comprehensive health checking for all OAuth endpoints

**Enhanced Checks**:
- Response time monitoring
- Error rate tracking
- Authentication flow testing
- JSON response validation

**Implementation**:
```python
@app.get("/api/system/health/comprehensive")
async def comprehensive_health_check():
    """Comprehensive system health including Prismatic integration"""
    return {
        "api_endpoints": await check_all_endpoints(),
        "prismatic_connectivity": await test_prismatic_connection(),
        "environment_config": await validate_environment(),
        "deployment_status": await check_deployment_sync()
    }
```

### 4. Deployment Synchronization Checker

**Purpose**: Verify that production deployment matches local development

**Key Features**:
- Route comparison between environments
- Environment variable validation
- Code version verification
- Configuration drift detection

**Implementation**:
```python
class DeploymentSyncChecker:
    async def compare_routes(self, local_url, prod_url):
        """Compare available routes between environments"""
        
    async def verify_env_vars(self):
        """Check critical environment variables are set"""
        
    async def check_code_version(self):
        """Verify deployed code version matches expected"""
```

## Data Models

### PrismaticDiagnosticResult
```python
class PrismaticDiagnosticResult(BaseModel):
    timestamp: datetime
    environment: str
    api_health: Dict[str, Any]
    prismatic_connectivity: Dict[str, Any]
    integration_config: Dict[str, Any]
    deployment_sync: Dict[str, Any]
    recommendations: List[str]
    critical_issues: List[str]
```

### IntegrationConfigValidation
```python
class IntegrationConfigValidation(BaseModel):
    webhook_urls_valid: bool
    auth_config_valid: bool
    triggers_configured: bool
    response_format_compatible: bool
    issues: List[str]
    recommendations: List[str]
```

## Error Handling

### Diagnostic Failures
- **Network Issues**: Retry with exponential backoff
- **Authentication Failures**: Provide specific credential guidance
- **Configuration Errors**: Return detailed validation messages
- **Timeout Issues**: Adjust timeouts and provide performance recommendations

### Integration Issues
- **Webhook Failures**: Test webhook endpoints and provide curl examples
- **Authentication Problems**: Validate tokens and provide refresh guidance
- **Configuration Drift**: Show exact differences and remediation steps

## Testing Strategy

### Integration Tests
- Test actual Prismatic webhook calls
- Verify end-to-end OAuth flow
- Test error scenarios and recovery
- Validate configuration changes

### Deployment Tests
- Automated post-deployment verification
- Environment comparison testing
- Performance regression testing
- Configuration validation testing

## Implementation Notes

### Prismatic Integration Points
1. **Webhook Endpoints**: Verify Prismatic can call our API
2. **Authentication Flow**: Ensure OAuth tokens work with Prismatic
3. **Response Formats**: Validate JSON responses match Prismatic expectations
4. **Error Handling**: Ensure errors are properly formatted for Prismatic

### Deployment Pipeline Integration
1. **Pre-deployment**: Validate configuration before deploy
2. **Post-deployment**: Automatic verification of all endpoints
3. **Monitoring**: Continuous health checking
4. **Alerting**: Immediate notification of issues

### Root Cause Analysis
The most likely causes of the Prismatic integration not showing runs:

1. **Webhook URL Mismatch**: Prismatic configured with wrong endpoint URLs
2. **Authentication Issues**: OAuth tokens not properly configured in Prismatic
3. **Trigger Configuration**: Integration triggers not properly set up
4. **Network Connectivity**: Prismatic cannot reach the deployed API
5. **Response Format Issues**: API responses don't match Prismatic expectations
6. **Environment Variables**: Missing or incorrect configuration in production

### Remediation Strategy
1. **Immediate**: Fix critical configuration issues
2. **Short-term**: Implement comprehensive monitoring
3. **Long-term**: Automated deployment verification pipeline