# 🚀 Niharika's API Explorer Pipeline - PoC

> **An enhanced Proof of Concept for an API Explorer pipeline that parses OpenAPI JSON files and serves them through a simple backend.**

**Author:** Niharika Jakkula  
**Project:** GSoC 2026 PoC  
**Repository:** [https://github.com/Niharikajakkula/gsoc-poc](https://github.com/Niharikajakkula/gsoc-poc)

## 📋 Overview

This project demonstrates an enhanced pipeline that:

1. **Parses** OpenAPI JSON files using Python with comprehensive validation
2. **Extracts** key API information (name, base URL, endpoints) with data normalization
3. **Prevents Duplicates** using smart name + baseUrl combination checking
4. **Stores** the data in a structured JSON registry with UUID tracking
5. **Serves** the APIs through a Node.js Express backend with RESTful design

## 🏗️ Project Structure

```text
niharika_api-explorer-poc/
├── pipeline/
│   └── parser.py              # Enhanced Python OpenAPI parser
├── data/
│   ├── sample_openapi.json    # Sample OpenAPI file
│   ├── minimal_openapi.json   # Minimal example (edge cases)
│   └── test_new_api.json      # Duplicate testing
├── registry/
│   └── apis.json             # Generated API registry (auto-created)
├── backend/
│   ├── server.js             # Simple Express backend
│   └── package.json          # Node.js dependencies
├── test-improvements.py      # Comprehensive test suite
├── run-demo.py              # Quick demo script
├── IMPROVEMENTS.md          # Enhancement documentation
└── README.md                # This file
```

## ✨ Enhanced Features

### 🔄 **Duplicate Prevention**

- Prevents duplicate APIs by checking `name` + `baseUrl` combination
- Updates existing APIs instead of creating duplicates
- Handles same name with different baseUrl as separate APIs

**Example Logic:**

```text
"Pet Store API" + "https://api.v1.com" → API #1
"Pet Store API" + "https://api.v2.com" → API #2 (separate entry)
"Pet Store API" + "https://api.v1.com" → Updates API #1 (no duplicate)
```

### 🧹 **Data Normalization**

- Converts all HTTP methods to uppercase (GET, POST, PUT, DELETE)
- Ensures missing summaries are stored as empty strings `""`
- Removes null/undefined fields
- Sorts endpoints alphabetically by path and method

**Before vs After:**

```python
# Before: "get" → After: "GET"
# Before: null summary → After: ""
# Before: undefined baseUrl → After: ""
```

### 🛡️ **Robust Error Handling**

- Validates OpenAPI file structure
- Handles missing `servers` field gracefully (sets baseUrl = "")
- Provides clear error messages for invalid JSON
- Safe registry file operations with backup/recovery

**Error Types Handled:**

- File not found
- Invalid JSON format
- Missing required OpenAPI sections
- Registry file corruption

### 🆔 **Enhanced Tracking**

- Unique UUID for each API entry
- `lastUpdated` timestamp in ISO format
- Detailed console progress logging
- Operation tracking (Added vs Updated)

**Registry Enhancement:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Pet Store API",
  "lastUpdated": "2024-01-01T12:00:00.000000"
}
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.6+** (no external libraries required)
- **Node.js 14+** (for backend server)

### Step 1: Parse OpenAPI Files

```bash
# Navigate to project directory
cd niharika_api-explorer-poc

# Parse sample Pet Store API
python pipeline/parser.py data/sample_openapi.json

# Parse minimal API (tests edge cases)
python pipeline/parser.py data/minimal_openapi.json

# Parse same name, different baseUrl (tests duplicate prevention)
python pipeline/parser.py data/test_new_api.json
```

**Expected Output:**

```text
[SUCCESS] Pipeline completed successfully!
[SUMMARY] API Added Successfully:
   Name: Pet Store API
   Endpoints: 7
```

### Step 2: Start the Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Start the server
npm start
```

### Step 3: Test the API Endpoints

```bash
# Get all APIs
curl http://localhost:3000/apis

# Get specific API by index
curl http://localhost:3000/apis/0

# Health check
curl http://localhost:3000/health

# API documentation
curl http://localhost:3000/
```

**Expected Response:**

```json
{
  "success": true,
  "count": 2,
  "apis": [...],
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## 🧪 Testing & Validation

### Run Comprehensive Tests

```bash
# Test all improvements and features
python test-improvements.py
```

**Expected Output:**

```text
🧪 Testing Enhanced API Explorer Parser
==================================================
1️⃣ Testing: Add new API
✅ First API added successfully
2️⃣ Testing: Update existing API (duplicate prevention)
✅ Duplicate prevention working
🎉 All tests passed!
```

### Run Quick Demo

```bash
# Run interactive demo
python run-demo.py
```

### Test Individual Components

```bash
# Test parser with different files
python pipeline/parser.py data/sample_openapi.json
python pipeline/parser.py data/minimal_openapi.json

# Test error handling
python pipeline/parser.py nonexistent.json
```

## 📊 Example Input/Output

### Input (OpenAPI JSON)

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Pet Store API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://petstore.example.com/api/v1"
    }
  ],
  "paths": {
    "/pets": {
      "get": {
        "summary": "List all pets"
      },
      "post": {
        "summary": "Create a new pet"
      }
    }
  }
}
```

### Output (Generated Registry)

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Pet Store API",
    "baseUrl": "https://petstore.example.com/api/v1",
    "endpoints": [
      {
        "path": "/pets",
        "method": "GET",
        "summary": "List all pets"
      },
      {
        "path": "/pets",
        "method": "POST",
        "summary": "Create a new pet"
      }
    ],
    "lastUpdated": "2024-01-01T12:00:00.000000"
  }
]
```

## 🌐 Backend API Endpoints

### GET /apis

Returns all APIs from the registry.

**Response:**

```json
{
  "success": true,
  "count": 2,
  "apis": [...],
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### GET /apis/:id

Returns a specific API by index.

**Example:** `GET /apis/0`

**Response:**

```json
{
  "success": true,
  "api": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Pet Store API",
    "baseUrl": "https://petstore.example.com/api/v1",
    "endpoints": [...]
  },
  "index": 0,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### GET /health

Health check endpoint with system information.

**Response:**

```json
{
  "success": true,
  "status": "healthy",
  "registryExists": true,
  "apiCount": 2,
  "uptime": 123.45,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## 📝 Sample Console Output

### Parser Output

```text
API Explorer Pipeline - Enhanced OpenAPI Parser
============================================================
Features: Duplicate prevention, data normalization, error handling
============================================================

[INPUT] Input file: data/sample_openapi.json
[OUTPUT] Output file: registry/apis.json

[LOAD] Loading OpenAPI file: data/sample_openapi.json
[LOAD] Successfully loaded OpenAPI file
[PARSE] Processing 4 path(s)...
[PARSE] Parsed API: Pet Store API
[PARSE] Base URL: https://petstore.example.com/api/v1
[PARSE] Found 7 endpoint(s)
[NORM] Normalizing data...
[NORM] Normalized 7 endpoint(s)
[REG] Creating new registry: registry/apis.json
[ADD] Adding new API: Pet Store API
[SAVE] Added API in registry: registry/apis.json
[SAVE] Total APIs in registry: 1

[SUCCESS] Pipeline completed successfully!

[SUMMARY] API Added Successfully:
   ID: 550e8400-e29b-41d4-a716-446655440000
   Name: Pet Store API
   Base URL: https://petstore.example.com/api/v1
   Endpoints: 7
   Last Updated: 2024-01-01T12:00:00.000000

[ENDPOINTS] Showing first 5:
   1. GET /categories - List categories
   2. GET /pets - List all pets
   3. POST /pets - Create a new pet
   4. GET /pets/search - Search pets
   5. DELETE /pets/{petId} - Delete pet
   ... and 2 more endpoint(s)
```

### Backend Output

```text
🚀 ================================
🚀 Niharika's API Explorer Backend
🚀 ================================
🚀 Server running on port 3000
🚀 Server URL: http://localhost:3000
🚀 Registry: /path/to/registry/apis.json
🚀 APIs loaded: 1
🚀 ================================
🚀 Endpoints:
🚀   GET /apis       - List all APIs
🚀   GET /apis/:id   - Get API by index
🚀   GET /health     - Health check
🚀 ================================
```

## 🛠️ Technical Features

### Python Parser

- **Built-in Libraries Only**: Uses only `json`, `os`, `sys`, `uuid`, `datetime`
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Modular Design**: Clean separation of concerns with focused functions
- **Comprehensive Validation**: Handles edge cases and malformed data

### Node.js Backend

- **Minimal Dependencies**: Only Express and CORS
- **RESTful Design**: Standard HTTP methods and status codes
- **Error Handling**: Graceful error responses with helpful messages
- **File-Based Storage**: No database required for simplicity

## 🎯 Key Improvements Over Basic Version

| Feature | Basic Version | Enhanced Version |
| ------- | ------------- | ---------------- |
| Duplicates | Always adds new | Smart duplicate prevention |
| Data Quality | Raw data | Normalized and validated |
| Error Handling | Basic try/catch | Comprehensive validation |
| Tracking | No IDs | UUID + timestamps |
| Console Output | Minimal | Detailed progress logging |
| Code Structure | Single function | Modular functions |
| Testing | Manual only | Automated test suite |

## 🚀 Future Enhancements

This PoC provides a solid foundation for:

- **YAML Support**: Parse OpenAPI YAML files
- **Batch Processing**: Handle multiple files at once
- **API Validation**: Test API endpoints automatically
- **Web Interface**: Frontend for browsing and managing APIs
- **Database Integration**: PostgreSQL/MongoDB for larger datasets
- **CI/CD Integration**: Automated pipeline processing

## 🤝 Contributing

This is a GSoC 2026 PoC project. Suggestions and feedback are welcome!

### Development Setup

1. Fork the repository
2. Clone your fork
3. Make changes
4. Test thoroughly using `python test-improvements.py`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **GSoC 2026** for the opportunity to demonstrate API pipeline concepts
- **OpenAPI Initiative** for the specification standard
- **Open Source Community** for the amazing tools and libraries

---

**Built with ❤️ by Niharika Jakkula for GSoC 2026**  
**Demonstrating clean code, robust error handling, and production-ready architecture**
