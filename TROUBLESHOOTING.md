# 🔧 API Explorer - Troubleshooting Guide

## Problem: APIs Not Loading

### ✅ Backend Status: WORKING
- ✅ 11 APIs loaded
- ✅ 5 categories available
- ✅ All endpoints responding

### 🔍 Diagnosis Steps

#### Step 1: Check Backend is Running

```bash
# Terminal 1: Start backend
cd projects/api-explorer-pipeline/backend
node simple-server.js
```

**Expected Output:**
```
🚀 API Explorer Backend running on port 3002
📚 APIs loaded from registry
🤖 Agent endpoints available
```

#### Step 2: Test Backend Directly

```bash
# In another terminal, test the API
curl http://localhost:3002/apis
```

**Expected Response:**
```json
{
  "success": true,
  "count": 11,
  "totalCount": 11,
  "apis": [...]
}
```

#### Step 3: Check Frontend Configuration

Open browser console (F12) and check:

```javascript
// Should show the correct API_BASE_URL
console.log('API_BASE_URL:', API_BASE_URL);

// Should show: http://localhost:3002 (local) or https://gsoc-api-explorer.onrender.com (production)
```

#### Step 4: Test Frontend Connection

1. Open `test-connection.html` in browser:
   ```
   http://localhost:3001/test-connection.html
   ```

2. Click "Run Tests" button

3. Check results:
   - ✅ Configuration loaded
   - ✅ Backend connected
   - ✅ /apis endpoint working
   - ✅ /categories endpoint working

---

## Common Issues & Solutions

### Issue 1: "Failed to fetch" Error

**Cause:** Backend not running or wrong URL

**Solution:**
```bash
# 1. Check if backend is running
netstat -ano | findstr :3002

# 2. If not running, start it
cd projects/api-explorer-pipeline/backend
node simple-server.js

# 3. If port is in use, kill the process
taskkill /PID <PID> /F

# 4. Try again
node simple-server.js
```

### Issue 2: CORS Error

**Cause:** Backend CORS not enabled

**Solution:**
Check `simple-server.js` line 10:
```javascript
app.use(cors());  // Must be present
```

If missing, add it:
```javascript
const cors = require('cors');
app.use(cors());
```

### Issue 3: Registry File Not Found

**Cause:** `global_index.json` missing or in wrong location

**Solution:**
```bash
# Check if file exists
ls -la projects/api-explorer-pipeline/registry/global_index.json

# If missing, regenerate
cd projects/api-explorer-pipeline
python pipeline/batch_processor.py apis --clear
```

### Issue 4: Empty API List

**Cause:** Registry file exists but is empty

**Solution:**
```bash
# Check registry file size
ls -lh projects/api-explorer-pipeline/registry/global_index.json

# If empty, regenerate
cd projects/api-explorer-pipeline
python pipeline/batch_processor.py apis --clear
```

### Issue 5: Port Already in Use

**Cause:** Another process using port 3002

**Solution:**
```bash
# Windows
taskkill /F /IM node.exe

# Mac/Linux
pkill -f "node simple-server.js"

# Then restart
node simple-server.js
```

---

## Quick Diagnostic Checklist

- [ ] Backend running on port 3002?
  ```bash
  curl http://localhost:3002/
  ```

- [ ] Registry file exists?
  ```bash
  ls projects/api-explorer-pipeline/registry/global_index.json
  ```

- [ ] Registry has data?
  ```bash
  curl http://localhost:3002/apis | grep -c "Pet Store"
  ```

- [ ] Frontend can reach backend?
  ```bash
  # Open test-connection.html in browser
  http://localhost:3001/test-connection.html
  ```

- [ ] API_BASE_URL correct?
  ```javascript
  // In browser console
  console.log(API_BASE_URL);
  ```

- [ ] No JavaScript errors?
  ```
  F12 → Console → Check for red errors
  ```

---

## Testing Commands

### Test Backend Endpoints

```bash
# Get all APIs
curl http://localhost:3002/apis

# Get categories
curl http://localhost:3002/categories

# Search for APIs
curl -X POST http://localhost:3002/agent/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query":"get users"}'

# Get API details
curl http://localhost:3002/apis/048fb1a3bf14/details
```

### Test Frontend

```bash
# Start frontend server
cd projects/api-explorer-pipeline/frontend
node serve.js

# Open in browser
http://localhost:3001

# Open test page
http://localhost:3001/test-connection.html
```

---

## Debug Mode

### Enable Verbose Logging

Edit `script.js` and add:

```javascript
// At the top of loadAPIs function
console.log('🔍 DEBUG: Loading APIs');
console.log('🔍 DEBUG: API_BASE_URL =', API_BASE_URL);
console.log('🔍 DEBUG: Fetch URL =', url);

// After fetch
console.log('🔍 DEBUG: Response status =', response.status);
console.log('🔍 DEBUG: Response data =', data);
```

### Check Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Reload page
4. Look for `/apis` request
5. Check:
   - Status code (should be 200)
   - Response (should have JSON data)
   - Headers (should have CORS headers)

---

## Still Not Working?

### Step 1: Verify Backend is Healthy

```bash
node projects/api-explorer-pipeline/backend/test-api.js
```

### Step 2: Check File Permissions

```bash
# Make sure files are readable
chmod +r projects/api-explorer-pipeline/registry/global_index.json
```

### Step 3: Reinstall Dependencies

```bash
cd projects/api-explorer-pipeline/backend
rm -rf node_modules
npm install
node simple-server.js
```

### Step 4: Check Node.js Version

```bash
node --version  # Should be 16+
npm --version   # Should be 7+
```

### Step 5: Clear Browser Cache

```
Ctrl+Shift+Delete (Windows)
Cmd+Shift+Delete (Mac)
```

---

## Getting Help

1. **Check browser console** (F12 → Console)
2. **Check backend logs** (terminal where you ran `node simple-server.js`)
3. **Run test-connection.html** to verify connectivity
4. **Run test-api.js** to verify backend
5. **Check GitHub Issues** for similar problems

---

## Success Indicators

✅ **Backend Working:**
- Server starts without errors
- `/apis` returns 11 APIs
- `/categories` returns 5 categories
- No "registry not found" messages

✅ **Frontend Working:**
- Page loads without errors
- API list appears in sidebar
- Search/filter works
- Can click on APIs to view details

✅ **Integration Working:**
- Frontend connects to backend
- APIs load automatically
- No CORS errors
- No "Failed to fetch" errors

---

## Performance Tips

1. **Clear browser cache** if APIs don't update
2. **Restart backend** if it becomes unresponsive
3. **Check system resources** if slow
4. **Use test-connection.html** to verify connectivity

---

**Last Updated:** April 29, 2026
