# MCP Integration Example

This document shows how to integrate the API Explorer MCP server with AI agents.

## Example AI Agent Conversation

### **User Query**: "Find an API to get user information"

**AI Agent Process:**
1. Calls `search_apis("get users")`
2. Receives structured response with templates
3. Presents options to user

**MCP Tool Call:**
```json
{
  "tool": "search_apis",
  "arguments": {
    "query": "get users"
  }
}
```

**MCP Response:**
```json
{
  "success": true,
  "query": "get users",
  "intent": "GET",
  "entity": "users",
  "confidence": 100,
  "api": "Auth Examples API",
  "endpoint": {
    "method": "GET",
    "path": "/users",
    "summary": "Get all users"
  },
  "authType": "apiKey",
  "baseUrl": "https://api.example.com/v1",
  "templates": {
    "curl": "curl -X GET \"https://api.example.com/v1/users\" -H \"X-API-Key: YOUR_API_KEY\"",
    "powershell": "Invoke-RestMethod -Uri \"https://api.example.com/v1/users\" -Method GET -Headers @{\"X-API-Key\"=\"YOUR_API_KEY\"}"
  },
  "alternatives": [
    {
      "api": "Auth Examples API",
      "endpoint": "GET /users/{id}",
      "confidence": 100
    }
  ],
  "totalFound": 5,
  "responseTime": 12
}
```

**AI Agent Response to User:**
> I found a perfect match! The **Auth Examples API** has a `GET /users` endpoint that retrieves all users. Here's how to use it:
> 
> **cURL:**
> ```bash
> curl -X GET "https://api.example.com/v1/users" \
>   -H "X-API-Key: YOUR_API_KEY"
> ```
> 
> **PowerShell:**
> ```powershell
> Invoke-RestMethod -Uri "https://api.example.com/v1/users" \
>   -Method GET -Headers @{"X-API-Key"="YOUR_API_KEY"}
> ```
> 
> **Authentication:** Requires an API key in the header
> **Alternative:** There's also a `GET /users/{id}` endpoint for individual users

---

### **User Query**: "Show me all available APIs"

**MCP Tool Call:**
```json
{
  "tool": "list_apis",
  "arguments": {}
}
```

**MCP Response:**
```json
{
  "success": true,
  "totalAPIs": 13,
  "apis": [
    {
      "id": "eabdaadb1a37",
      "name": "Auth Examples API",
      "baseUrl": "https://api.example.com/v1",
      "authType": "apiKey",
      "endpointCount": 2,
      "category": "Social",
      "description": "API for user authentication and management",
      "tags": ["GET", "Protected", "Users"]
    },
    {
      "id": "6f7c887ecd63",
      "name": "AI Language Model API",
      "baseUrl": "https://api.openai.com/v1",
      "authType": "bearer",
      "endpointCount": 2,
      "category": "AI",
      "description": "Advanced AI language model API for chat completions",
      "tags": ["Chat", "Completions", "GET", "Models", "POST"]
    }
  ],
  "responseTime": 5
}
```

**AI Agent Response to User:**
> Here are all 13 available APIs in the registry:
> 
> **🤖 AI Category:**
> - **AI Language Model API** (2 endpoints) - Advanced AI language model API for chat completions
> 
> **👥 Social Category:**
> - **Auth Examples API** (2 endpoints) - API for user authentication and management
> 
> **🌤️ Weather Category:**
> - **Weather Forecast API** (2 endpoints) - Get current weather conditions and forecasts
> 
> **💰 Finance Category:**
> - **E-commerce Store API** (5 endpoints) - Complete shopping platform API
> 
> Each API includes ready-to-use templates and authentication details. Would you like to explore any specific category?

---

### **User Query**: "Test the user API"

**MCP Tool Call:**
```json
{
  "tool": "execute_api",
  "arguments": {
    "method": "GET",
    "path": "/users",
    "api": "Auth Examples API"
  }
}
```

**MCP Response:**
```json
{
  "success": true,
  "api": "Auth Examples API",
  "endpoint": "GET /users",
  "method": "GET",
  "path": "/users",
  "timestamp": "2026-04-19T15:30:00.000Z",
  "responseTime": 150,
  "status": 200,
  "response": {
    "users": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "admin"
      },
      {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "role": "user"
      }
    ],
    "total": 2,
    "page": 1
  }
}
```

**AI Agent Response to User:**
> ✅ **API Test Successful!**
> 
> **Endpoint:** GET /users (Auth Examples API)  
> **Status:** 200 OK  
> **Response Time:** 150ms  
> 
> **Sample Response:**
> ```json
> {
>   "users": [
>     {
>       "id": 1,
>       "name": "John Doe",
>       "email": "john@example.com",
>       "role": "admin"
>     },
>     {
>       "id": 2,
>       "name": "Jane Smith", 
>       "email": "jane@example.com",
>       "role": "user"
>     }
>   ],
>   "total": 2,
>   "page": 1
> }
> ```
> 
> The API is working correctly and returns a list of users with their details.

## Integration Benefits

1. **Natural Language Interface**: Users can ask for APIs in plain English
2. **Ready-to-Use Templates**: Immediate curl/PowerShell commands
3. **Rich Metadata**: Categories, confidence scores, alternatives
4. **Mock Testing**: Safe API execution without real calls
5. **Structured Responses**: Perfect for AI agent processing

## Supported MCP Clients

- Claude Desktop
- Any MCP-compatible AI agent
- Custom MCP implementations

The API Explorer MCP server follows standard MCP protocol, making it compatible with any MCP client implementation.