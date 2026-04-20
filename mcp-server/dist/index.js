#!/usr/bin/env node
/**
 * API Explorer MCP Server
 *
 * This MCP server wraps the API Explorer backend to make it accessible to AI agents.
 */
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema, } from '@modelcontextprotocol/sdk/types.js';
// Configuration
const API_EXPLORER_BASE_URL = 'http://localhost:3002';
const SERVER_NAME = 'api-explorer-mcp-server';
const SERVER_VERSION = '1.0.0';
// Simple fetch function for Node.js compatibility
async function fetchJson(url, options = {}) {
    try {
        // Use dynamic import for node-fetch
        const { default: fetch } = await import('node-fetch');
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    }
    catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}
/**
 * API Explorer Client - Handles communication with the backend
 */
class ApiExplorerClient {
    baseUrl;
    constructor(baseUrl = API_EXPLORER_BASE_URL) {
        this.baseUrl = baseUrl;
    }
    async searchApis(query) {
        try {
            console.log(`🔍 [MCP] Searching APIs with query: "${query}"`);
            const data = await fetchJson(`${this.baseUrl}/agent/tools/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
            });
            console.log(`✅ [MCP] Search completed: ${data.success ? 'Found match' : 'No match'}`);
            return data;
        }
        catch (error) {
            console.error('❌ [MCP] Search failed:', error);
            return {
                success: false,
                message: `Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
                suggestions: ['get users', 'create user', 'list products', 'get weather']
            };
        }
    }
    async listApis() {
        try {
            console.log('📋 [MCP] Listing all APIs');
            const data = await fetchJson(`${this.baseUrl}/agent/tools/list`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            console.log(`✅ [MCP] Listed ${data.totalAPIs || 0} APIs`);
            return data;
        }
        catch (error) {
            console.error('❌ [MCP] List failed:', error);
            return {
                success: false,
                totalAPIs: 0,
                apis: [],
                responseTime: 0
            };
        }
    }
    async executeApi(method, path, api) {
        try {
            console.log(`🚀 [MCP] Executing API: ${method} ${path} (${api})`);
            const data = await fetchJson(`${this.baseUrl}/agent/tools/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ method, path, api }),
            });
            console.log(`✅ [MCP] Execution completed: ${data.success ? 'Success' : 'Failed'}`);
            return data;
        }
        catch (error) {
            console.error('❌ [MCP] Execution failed:', error);
            return {
                success: false,
                message: `Execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`
            };
        }
    }
    async testConnection() {
        try {
            console.log('🔧 [MCP] Testing connection to API Explorer backend...');
            const data = await fetchJson(`${this.baseUrl}/`);
            console.log(`✅ [MCP] Connected to API Explorer: ${data.message || 'OK'}`);
            return true;
        }
        catch (error) {
            console.error('❌ [MCP] Connection failed:', error);
            return false;
        }
    }
}
/**
 * MCP Server Implementation
 */
class ApiExplorerMcpServer {
    server;
    client;
    constructor() {
        this.server = new Server({
            name: SERVER_NAME,
            version: SERVER_VERSION,
        }, {
            capabilities: {
                tools: {},
            },
        });
        this.client = new ApiExplorerClient();
        this.setupToolHandlers();
        this.setupErrorHandling();
    }
    setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            console.log('📋 [MCP] Listing available tools');
            return {
                tools: [
                    {
                        name: 'search_apis',
                        description: 'Search for APIs using natural language queries',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                query: {
                                    type: 'string',
                                    description: 'Natural language query (e.g., "get users", "create pet")',
                                },
                            },
                            required: ['query'],
                        },
                    },
                    {
                        name: 'list_apis',
                        description: 'List all available APIs in the registry',
                        inputSchema: {
                            type: 'object',
                            properties: {},
                        },
                    },
                    {
                        name: 'execute_api',
                        description: 'Execute an API endpoint with mock responses',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                method: { type: 'string', description: 'HTTP method' },
                                path: { type: 'string', description: 'API endpoint path' },
                                api: { type: 'string', description: 'Name of the API' },
                            },
                            required: ['method', 'path', 'api'],
                        },
                    },
                ],
            };
        });
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            console.log(`🔧 [MCP] Tool called: ${name}`);
            try {
                let result;
                switch (name) {
                    case 'search_apis': {
                        const { query } = args;
                        if (!query)
                            throw new Error('Query parameter is required');
                        result = await this.client.searchApis(query);
                        break;
                    }
                    case 'list_apis': {
                        result = await this.client.listApis();
                        break;
                    }
                    case 'execute_api': {
                        const { method, path, api } = args;
                        if (!method || !path || !api) {
                            throw new Error('Method, path, and api parameters are required');
                        }
                        result = await this.client.executeApi(method, path, api);
                        break;
                    }
                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
                return {
                    content: [
                        {
                            type: 'text',
                            text: JSON.stringify(result, null, 2),
                        },
                    ],
                };
            }
            catch (error) {
                console.error(`❌ [MCP] Tool execution failed: ${name}`, error);
                return {
                    content: [
                        {
                            type: 'text',
                            text: JSON.stringify({
                                success: false,
                                error: error instanceof Error ? error.message : 'Unknown error',
                                tool: name,
                                timestamp: new Date().toISOString()
                            }, null, 2),
                        },
                    ],
                    isError: true,
                };
            }
        });
    }
    setupErrorHandling() {
        this.server.onerror = (error) => {
            console.error('❌ [MCP] Server error:', error);
        };
        process.on('SIGINT', async () => {
            console.log('\n🛑 [MCP] Shutting down server...');
            await this.server.close();
            process.exit(0);
        });
    }
    async start() {
        console.log(`🚀 [MCP] Starting ${SERVER_NAME} v${SERVER_VERSION}`);
        // Test connection to backend
        const connected = await this.client.testConnection();
        if (!connected) {
            console.warn('⚠️  [MCP] Warning: Could not connect to API Explorer backend');
            console.warn('⚠️  [MCP] Make sure the backend is running on http://localhost:3002');
        }
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.log('✅ [MCP] Server started and ready for connections');
        console.log('📋 [MCP] Available tools: search_apis, list_apis, execute_api');
    }
}
/**
 * Main entry point
 */
async function main() {
    try {
        const server = new ApiExplorerMcpServer();
        await server.start();
    }
    catch (error) {
        console.error('💥 [MCP] Failed to start server:', error);
        process.exit(1);
    }
}
// Start the server
main().catch((error) => {
    console.error('💥 [MCP] Unhandled error:', error);
    process.exit(1);
});
//# sourceMappingURL=index.js.map