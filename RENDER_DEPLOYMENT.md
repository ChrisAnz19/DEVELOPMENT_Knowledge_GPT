# Deploying Knowledge_GPT API to Render

This guide will walk you through deploying the Knowledge_GPT API to Render.

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository

Make sure your repository contains all the necessary files:
- `api/main.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `runtime.txt` - Python version specification
- `Procfile` - Process specification

### 2. Connect to Render

1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select the repository containing your Knowledge_GPT code

### 3. Configure the Web Service

**Service Name:** `knowledge-gpt-api` (or your preferred name)

**Environment:** `Python 3`

**Build Command:** `pip install -r requirements.txt`

**Start Command:** `python api/main.py`

**Plan:** Choose the plan that fits your needs (Starter is fine for testing)

### 4. Set Environment Variables

In the Render dashboard, go to your service's "Environment" tab and add these environment variables:

```
OPENAI_API_KEY=your_openai_api_key_here
APOLLO_API_KEY=your_apollo_api_key_here
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
```

**Important:** 
- Mark these as "Secret" for security
- Don't include quotes around the values
- Make sure there are no extra spaces

### 5. Deploy

Click "Create Web Service" and Render will:
1. Clone your repository
2. Install dependencies
3. Start your application
4. Provide you with a public URL

## 🔧 Configuration Details

### Environment Variables

The API will automatically detect and use these environment variables:

- `OPENAI_API_KEY` - Required for AI processing
- `APOLLO_API_KEY` - Required for B2B data search
- `BRIGHT_DATA_API_KEY` - Optional for LinkedIn scraping
- `PORT` - Automatically set by Render

### CORS Configuration

The API is configured to allow requests from:
- Localhost (for development)
- Render domains (`*.onrender.com`)
- Your custom domains (update in `api/main.py`)

## 📊 API Endpoints

Once deployed, your API will be available at:
`https://your-service-name.onrender.com`

**Available endpoints:**
- `GET /` - Health check
- `POST /api/search` - Create search
- `GET /api/search/{request_id}` - Get search results
- `GET /api/search` - List all searches
- `DELETE /api/search/{request_id}` - Delete search

**API Documentation:**
- Interactive docs: `https://your-service-name.onrender.com/docs`
- OpenAPI spec: `https://your-service-name.onrender.com/openapi.json`

## 🔍 Monitoring and Logs

### View Logs
1. Go to your service in Render dashboard
2. Click on "Logs" tab
3. View real-time logs and errors

### Health Checks
- Render automatically checks `GET /` endpoint
- Service will restart if health check fails
- Monitor the "Events" tab for deployment status

## 🚨 Troubleshooting

### Common Issues

**1. Build Failures**
- Check that `requirements.txt` is in the root directory
- Verify Python version in `runtime.txt`
- Check build logs for dependency conflicts

**2. Runtime Errors**
- Verify all environment variables are set correctly
- Check that API keys are valid and have sufficient credits
- Review application logs for specific error messages

**3. CORS Issues**
- Update `allow_origins` in `api/main.py` with your frontend domain
- Ensure your frontend is making requests to the correct API URL

**4. Memory Issues**
- Upgrade to a higher plan if you hit memory limits
- Consider optimizing the application for lower memory usage

### Debug Commands

You can SSH into your Render instance (if available) to debug:
```bash
# Check environment variables
echo $OPENAI_API_KEY

# Check Python version
python --version

# Test API locally
curl http://localhost:$PORT/
```

## 🔄 Updating Your Deployment

### Automatic Deployments
- Render automatically redeploys when you push to your main branch
- You can configure branch-specific deployments in settings

### Manual Deployments
1. Go to your service dashboard
2. Click "Manual Deploy"
3. Select the branch/commit to deploy

### Environment Variable Updates
1. Go to "Environment" tab
2. Update the variable values
3. Click "Save Changes"
4. Service will automatically restart

## 📈 Scaling

### Free Tier Limitations
- 750 hours/month
- Sleeps after 15 minutes of inactivity
- Limited memory and CPU

### Upgrading
- Choose a paid plan for better performance
- Higher memory limits for complex searches
- Always-on service (no sleep)

## 🔗 Connecting to Your Bolt Frontend

Once deployed, update your Bolt frontend to use the Render API URL:

```typescript
// In your Bolt app
const API_URL = 'https://your-service-name.onrender.com';

// Use the API
const response = await fetch(`${API_URL}/api/search`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'Find CEOs at large software companies',
    max_candidates: 2
  })
});
```

## 🎯 Next Steps

1. **Test the API**: Use the provided test script or Postman
2. **Monitor Performance**: Check logs and metrics in Render dashboard
3. **Connect Frontend**: Update your Bolt app to use the new API URL
4. **Optimize**: Monitor usage and optimize as needed

## 📞 Support

If you encounter issues:
1. Check the Render documentation
2. Review application logs
3. Verify environment variables
4. Test locally first

Your Knowledge_GPT API should now be live and ready to serve your Bolt frontend! 🎉 