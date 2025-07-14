# Knowledge_GPT Supabase Deployment Guide

## 🚀 Environment Variables Setup

### Required Environment Variables for Render Deployment

You need to set these environment variables in your Render dashboard:

#### 1. **Supabase Database Variables**
```
SUPABASE_HOST=hmvcvtrucfoqxcrfinep.supabase.co
SUPABASE_USER=ChrisAnz19
SUPABASE_PASSWORD=2ndSight@2023
SUPABASE_DBNAME=postgres
SUPABASE_PORT=5432
```

#### 2. **API Keys**
```
OPENAI_API_KEY=your_openai_api_key_here
INTERNAL_DATABASE_API_KEY=your_apollo_api_key_here
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
```

#### 3. **Render Configuration**
```
PORT=8000
```

## 📋 Step-by-Step Deployment Instructions

### Step 1: Set Environment Variables in Render

1. **Go to your Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Select your Knowledge_GPT service

2. **Access Environment Variables**
   - Click on "Environment" in the left sidebar
   - Click "Add Environment Variable" for each variable

3. **Add Each Variable**
   ```
   Key: SUPABASE_HOST
   Value: hmvcvtrucfoqxcrfinep.supabase.co
   
   Key: SUPABASE_USER
   Value: ChrisAnz19
   
   Key: SUPABASE_PASSWORD
   Value: 2ndSight@2023
   
   Key: SUPABASE_DBNAME
   Value: postgres
   
   Key: SUPABASE_PORT
   Value: 5432
   
   Key: OPENAI_API_KEY
   Value: [Your OpenAI API Key]
   
   Key: INTERNAL_DATABASE_API_KEY
   Value: [Your Apollo API Key]
   
   Key: BRIGHT_DATA_API_KEY
   Value: [Your Bright Data API Key]
   
   Key: PORT
   Value: 8000
   ```

### Step 2: Deploy the Latest Code

1. **Push Latest Code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy Supabase integration with environment variables"
   git push origin main
   ```

2. **Trigger Render Deployment**
   - Render will automatically detect the push and start deploying
   - Monitor the deployment logs in your Render dashboard

### Step 3: Verify Database Connection

1. **Check Database Stats Endpoint**
   ```bash
   curl -X GET "https://knowledge-gpt-siuq.onrender.com/api/database/stats"
   ```

2. **Expected Response**
   ```json
   {
     "database_status": "connected",
     "total_searches": 0,
     "total_candidates": 0,
     "total_exclusions": 0
   }
   ```

### Step 4: Test Full System

1. **Run System Test**
   ```bash
   python3 test_full_system.py
   ```

2. **Verify Database Storage**
   - Check that searches are stored in Supabase
   - Verify candidate data is saved
   - Confirm exclusion system is working

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify Supabase credentials are correct
   - Check if Supabase database is accessible
   - Ensure tables are created using schema.sql

2. **Environment Variables Not Set**
   - Double-check all variables in Render dashboard
   - Restart the service after adding variables

3. **API Keys Missing**
   - Ensure all API keys are valid and active
   - Check API key permissions and quotas

### Verification Commands

```bash
# Test API health
curl -X GET "https://knowledge-gpt-siuq.onrender.com/"

# Test database connection
curl -X GET "https://knowledge-gpt-siuq.onrender.com/api/database/stats"

# Test search creation
curl -X POST "https://knowledge-gpt-siuq.onrender.com/api/search" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find marketing directors in San Francisco", "max_candidates": 1}'

# Test exclusions
curl -X GET "https://knowledge-gpt-siuq.onrender.com/api/exclusions"
```

## 📊 Expected Results After Deployment

1. **Database Integration Active**
   - `/api/database/stats` returns connection status
   - Searches are stored in Supabase tables
   - Candidates are saved with LinkedIn data

2. **Exclusion System Working**
   - `/api/exclusions` shows excluded candidates
   - 30-day automatic exclusion is active
   - Cleanup endpoint works

3. **Full Pipeline Operational**
   - Search creation → Database storage → Results retrieval
   - LinkedIn scraping → Profile photo storage
   - Behavioral data generation

## 🎯 Success Criteria

✅ Database connection established  
✅ Tables created successfully  
✅ Search data stored in Supabase  
✅ Candidate data with LinkedIn info saved  
✅ Exclusion system operational  
✅ All API endpoints responding  
✅ Previous 2 search entries migrated to database  

## 📞 Support

If you encounter any issues:
1. Check Render deployment logs
2. Verify environment variables are set correctly
3. Test database connection manually
4. Review API key permissions

---

**Ready to deploy! 🚀** 