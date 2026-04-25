# API Explorer MCP Server

This MCP (Model Context Protocol) server wraps the API Explorer backend to make it accessible to AI agents. It provides three main tools for API discovery, listing, and execution.

## Features

- **🔍 search_apis**: Search for APIs using natural language queries
- **📋 list_apis**: List all available APIs with metadata
- **🚀 execute_api**: Execute API endpoints with mock responses
- **🔧 Clean Integration**: Wraps existing backend without modifications
- **📊 Rich Responses**: Includes templates, alternatives, and metadata

## Prerequisites

- Node.js 18+ 
- API Explorer backend running on `http://localhost:3002`
- TypeScript (installed automatically)

## Quick Start

### 1. Install Dependencies

```bash
cd mcp-server
npm install
```

### 2. Build the Server

```bash
npm run build
```

### 3. Start the MCP Server

```bash
npm start
```

Or for development with auto-rebuild:

```bash
npm run dev
```

## Available Tools

### search_apis(query: string)

Search for APIs using natural language queries.

**Input:**
```json
{
  "query": "get users"
}
```

**Output:**
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
  "alternatives": [...],
  "totalFound": 5,
  "responseTime": 12
}
```

### list_apis()

List all available APIs in the registry.

**Input:**
```json
{}
```

**Output:**
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
    }
  ],
  "responseTime": 5
}
```

### execute_api(method: string, path: string, api: string)

Execute an API endpoint with mock responses.

**Input:**
```json
{
  "method": "GET",
  "path": "/users",
  "api": "Auth Examples API"
}
```

**Output:**
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
      {"id": 1, "name": "John Doe", "email": "john@example.com"},
      {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ]
  }
}
```

## Integration with AI Agents

### Using with Claude Desktop

1. Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "api-explorer": {
      "command": "node",
      "args": ["path/to/mcp-server/dist/index.js"],
      "cwd": "path/to/mcp-server"
    }
  }
}
```

### Using with Other MCP Clients

The server uses stdio transport and follows MCP protocol standards, making it compatible with any MCP client.

## Example Usage in AI Conversations

**User:** "Find an API to get user information"

**AI Agent:** Uses `search_apis("get users")` and receives:
- Best matching API endpoint
- Authentication requirements  
- Ready-to-use curl and PowerShell templates
- Alternative endpoints

**User:** "Show me all available APIs"

**AI Agent:** Uses `list_apis()` and receives:
- Complete API catalog
- Categories and descriptions
- Endpoint counts and authentication types

**User:** "Test the user API"

**AI Agent:** Uses `execute_api("GET", "/users", "Auth Examples API")` and receives:
- Mock response data
- Execution metadata
- Performance timing

## Development

### Project Structure

```
mcp-server/
├── src/
│   └── index.ts          # Main MCP server implementation
├── dist/                 # Compiled JavaScript (generated)
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

### Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm start` - Run the compiled server
- `npm run dev` - Build and run in one command
- `npm run watch` - Watch for changes and rebuild

### Debugging

The server includes comprehensive logging:

- `🚀` Server startup and connection status
- `🔍` Search operations and results
- `📋` List operations
- `🚀` Execute operations
- `❌` Error conditions
- `✅` Successful operations

## Troubleshooting

### "Connection failed" errors

1. Ensure API Explorer backend is running:
   ```bash
   cd backend
   node simple-server.js
   ```

2. Verify backend is accessible:
   ```bash
   curl http://localhost:3002/
   ```

### "Tool not found" errors

1. Rebuild the server:
   ```bash
   npm run build
   ```

2. Check tool names match exactly: `search_apis`, `list_apis`, `execute_api`

### TypeScript compilation errors

1. Install dependencies:
   ```bash
   npm install
   ```

2. Check Node.js version (requires 18+):
   ```bash
   node --version
   ```

## License

MIT - Part of the API Explorer GSoC project.