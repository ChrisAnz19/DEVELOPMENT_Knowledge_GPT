# Design Document

## Overview

This design implements the missing HubSpot OAuth API endpoints that the frontend expects. The system already has a `HubSpotOAuthClient` class with the core OAuth logic, but lacks the actual FastAPI endpoints to expose this functionality.

The solution is straightforward: create two new API endpoints that wrap the existing `HubSpotOAuthClient` functionality.

## Architecture

The design leverages the existing `HubSpotOAuthClient` class and follows the established FastAPI patterns in the codebase.

**Existing Components**:
- `HubSpotOAuthClient` class (already implemented)
- Environment variable configuration for HubSpot credentials
- Error handling patterns in FastAPI

**New Components**:
- POST `/api/hubspot/oauth/token` endpoint
- GET `/api/hubspot/oauth/health` endpoint

## Components and Interfaces

### 1. Token Exchange Endpoint

**Route**: `POST /api/hubspot/oauth/token`

**Request Model**:
```python
class HubSpotTokenRequest(BaseModel):
    code: str = Field(..., description="Authorization code from HubSpot")
    redirect_uri: str = Field(..., description="Redirect URI used in authorization")
```

**Response**: JSON object with token data or error information

**Implementation**:
```python
@app.post("/api/hubspot/oauth/token")
async def exchange_hubspot_token(request: HubSpotTokenRequest):
    try:
        client = HubSpotOAuthClient()
        result = await client.exchange_code_for_tokens(
            code=request.code,
            redirect_uri=request.redirect_uri
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HubSpot OAuth error: {str(e)}")
```

### 2. Health Check Endpoint

**Route**: `GET /api/hubspot/oauth/health`

**Response**: JSON object with health status

**Implementation**:
```python
@app.get("/api/hubspot/oauth/health")
async def hubspot_oauth_health():
    try:
        client_id = os.getenv('HUBSPOT_CLIENT_ID')
        client_secret = os.getenv('HUBSPOT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return {
                "status": "unhealthy",
                "message": "HubSpot OAuth credentials not configured",
                "details": {
                    "client_id_configured": bool(client_id),
                    "client_secret_configured": bool(client_secret)
                }
            }
        
        return {
            "status": "healthy",
            "message": "HubSpot OAuth service is ready",
            "details": {
                "client_id_configured": True,
                "client_secret_configured": True
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }
```

## Data Models

### HubSpotTokenRequest
- `code`: Authorization code received from HubSpot OAuth flow
- `redirect_uri`: The redirect URI that was used in the authorization request

### Response Models
The endpoints will return the existing response formats from `HubSpotOAuthClient` without modification to maintain consistency.

## Error Handling

### Token Exchange Errors
- **400 Bad Request**: Missing or invalid request parameters
- **500 Internal Server Error**: HubSpot credentials not configured
- **502 Bad Gateway**: HubSpot API errors or network issues

### Health Check Errors
- Always returns 200 OK with status information in the response body
- Uses "healthy", "unhealthy", or "error" status indicators

## Testing Strategy

### Unit Tests
- Test token exchange with valid parameters
- Test error handling for missing credentials
- Test error handling for invalid HubSpot responses
- Test health check with and without credentials

### Integration Tests
- Test actual token exchange with HubSpot (using test credentials)
- Test error scenarios with malformed requests
- Verify response formats match frontend expectations

## Implementation Notes

### Dependencies
- Uses existing `HubSpotOAuthClient` class
- Follows existing FastAPI patterns in `api/main.py`
- No new external dependencies required

### Placement
- Add endpoints to existing `api/main.py` file
- Place near other OAuth-related code
- Add request model class with other Pydantic models