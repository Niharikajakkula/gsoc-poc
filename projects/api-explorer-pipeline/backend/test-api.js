#!/usr/bin/env node

/**
 * Quick API Test Script
 * Tests if the backend is working correctly
 */

const http = require('http');

const API_BASE_URL = 'http://localhost:3002';

console.log('\n🔍 API Explorer Backend Test\n');
console.log('=' .repeat(50));

// Test 1: Root endpoint
console.log('\n✅ Test 1: Root Endpoint');
testEndpoint('/', 'GET', null, (data) => {
    console.log('   Message:', data.message);
    console.log('   Version:', data.version);
});

// Test 2: /apis endpoint
setTimeout(() => {
    console.log('\n✅ Test 2: /apis Endpoint');
    testEndpoint('/apis', 'GET', null, (data) => {
        console.log('   Success:', data.success);
        console.log('   APIs loaded:', data.count);
        console.log('   Total APIs:', data.totalCount);
        console.log('   Categories:', data.categories.length);
    });
}, 500);

// Test 3: /categories endpoint
setTimeout(() => {
    console.log('\n✅ Test 3: /categories Endpoint');
    testEndpoint('/categories', 'GET', null, (data) => {
        console.log('   Categories:', data.categories.join(', '));
        console.log('   Total:', data.total);
    });
}, 1000);

// Test 4: /agent/tools/search endpoint
setTimeout(() => {
    console.log('\n✅ Test 4: /agent/tools/search Endpoint');
    const body = JSON.stringify({ query: 'get users' });
    testEndpoint('/agent/tools/search', 'POST', body, (data) => {
        console.log('   Success:', data.success);
        console.log('   Query:', data.query);
        console.log('   Matches:', data.matches ? data.matches.length : 0);
    });
}, 1500);

// Helper function
function testEndpoint(path, method, body, callback) {
    const url = new URL(API_BASE_URL + path);
    const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
            try {
                const json = JSON.parse(data);
                callback(json);
            } catch (e) {
                console.log('   ❌ Invalid JSON response');
            }
        });
    });

    req.on('error', (error) => {
        console.log('   ❌ Error:', error.message);
    });

    if (body) req.write(body);
    req.end();
}

// Summary
setTimeout(() => {
    console.log('\n' + '=' .repeat(50));
    console.log('\n✅ All tests completed!\n');
}, 2500);
