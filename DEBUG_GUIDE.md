# Diagnostic Guide - Grok API Issues

## Quick Checklist

### 1. Verify API Key
```bash
# In your .env file, you should have:
GROQ_API_KEY=xai-your_key_here
# OR
GROQ_API_KEY=gsk_your_groq_key_here
```

### 2. Test API Connection  
```bash
cd backend
python test_api.py
```
This will show:
- ✅ If API key is recognized
- ✅ If client initializes properly  
- ✅ If API call succeeds
- ✅ If JSON response is valid

### 3. Run Backend with Debug Logging
```bash
cd backend
python main.py
```

Then upload a PDF and watch the terminal logs. You should see:
```
============================================================
Initializing Intelligence Engine with Grok API (Fast Mode)
============================================================
✓ API Key found: xai-...
✓ Detected xAI Grok API Key
✓ Using xAI Grok model: grok-2
✓ Client initialized successfully!

============================================================
Starting Document Analysis
============================================================
📄 Context length: 15234 characters
🚀 Calling grok-2 API...
✓ API response received
Raw response length: 1245 characters
✅ Analysis completed successfully!
```

### 4. Common Issues & Fixes

**Issue: "Analysis service currently unavailable"**
- ❌ API key validation failed
- ❌ API call threw exception
- ❌ JSON parsing failed

**Fix:**
1. Verify API key format (starts with `xai-` or `gsk_`)
2. Check API key is valid at https://console.x.ai or https://console.groq.com
3. Ensure .env file is in backend folder
4. Restart backend after changing .env

**Issue: JSON parsing error**
- Model returned malformed JSON
- Response wrapped in code blocks improperly

**Fix:**
- Check terminal logs for "Raw response" 
- Verify JSON is valid at https://jsonlint.com
- The code now auto-cleans markdown code blocks

### 5. Improve Response Quality

The updated code now:
✅ Uses all document chunks (not just 10) for better context
✅ Has detailed error logging
✅ Supports both xAI Grok and standard Groq
✅ Better prompt formatting
✅ JSON response validation

## Next Steps

1. **Run the test:**
   ```bash
   python backend/test_api.py
   ```

2. **Check output:**
   - If GREEN ✅: API works, issue is in document processing
   - If RED ❌: API key/client issue - share the error

3. **Upload document & watch logs:**
   - Terminal should show detailed processing logs
   - Each step marked with ✓ or ❌

4. **Share feedback:**
   - Test results
   - Terminal logs
   - Any error messages
