#!/usr/bin/env node

/**
 * Simple MCP Client Test
 * Tests the API Explorer MCP server functionality
 */

import { spawn } from 'child_process';

console.log('🧪 Testing API Explorer MCP Server');
console.log('=' * 40);

// Start the MCP server process
const mcpServer = spawn('node', ['src/index.js'], {
  stdio: ['pipe', 'pipe', 'inherit'],
  cwd: process.cwd()
});

// Test messages
const testMessages = [
  // Initialize
  {
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'test-client',
        version: '1.0.0'
      }
    }
  },
  // List tools
  {
    jsonrpc: '2.0',
    id: 2,
    method: 'tools/list',
    params: {}
  },
  // Search APIs
  {
    jsonrpc: '2.0',
    id: 3,
    method: 'tools/call',
    params: {
      name: 'search_apis',
      arguments: {
        query: 'get users'
      }
    }
  }
];

let messageIndex = 0;

// Handle server output
mcpServer.stdout.on('data', (data) => {
  const output = data.toString();
  console.log('📤 Server Response:', output);
  
  // Send next test message
  if (messageIndex < testMessages.length) {
    setTimeout(() => {
      const message = testMessages[messageIndex++];
      console.log('📥 Sending:', JSON.stringify(message));
      mcpServer.stdin.write(JSON.stringify(message) + '\n');
    }, 1000);
  } else {
    // All tests done
    setTimeout(() => {
      console.log('✅ MCP Server test completed!');
      mcpServer.kill();
      process.exit(0);
    }, 2000);
  }
});

// Handle server errors
mcpServer.on('error', (error) => {
  console.error('❌ Server error:', error);
});

mcpServer.on('close', (code) => {
  console.log(`🛑 Server exited with code ${code}`);
});

// Start the test
console.log('🚀 Starting MCP server test...');
setTimeout(() => {
  const initMessage = testMessages[messageIndex++];
  console.log('📥 Sending initialize:', JSON.stringify(initMessage));
  mcpServer.stdin.write(JSON.stringify(initMessage) + '\n');
}, 1000);