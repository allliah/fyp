# Render Deployment Guide for Stegbox

This guide walks you through deploying your Stegbox application to Render.

## Prerequisites

1. **GitHub Account** - Push your code to GitHub
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Supabase Project** - Already set up with your credentials

## Step 1: Prepare Your Repository

### 1.1 Add Deployment Files (Already Done ✓)
- ✅ `Procfile` - Defines how to run the app
- ✅ `runtime.txt` - Specifies Python version (3.11.7)
- ✅ `requirements.txt` - All dependencies
- ✅ `.env.example` - Template for environment variables

### 1.2 Push to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

## Step 2: Create Render Web Service

### 2.1 Sign in to Render Dashboard
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** button
3. Select **"Web Service"**

### 2.2 Connect GitHub Repository
1. Click **"Connect a repository"**
2. Select your GitHub repository containing this code
3. Authorize Render to access your GitHub

### 2.3 Configure Web Service

**Name:** `stegbox-app` (or your preferred name)

**Environment:** `Python 3`

**Build Command:** `pip install -r requirements.txt`

**Start Command:** `gunicorn app:app`

**Instance Type:** Choose based on your needs:
- **Free** - Good for demo/testing
- **Starter** - Recommended for production

### 2.4 Set Environment Variables

Click **"Advanced"** and add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | Generate a random string | Used for Flask sessions |
| `SUPABASE_URL` | Your Supabase project URL | From Supabase dashboard |
| `SUPABASE_KEY` | Your Supabase anon key | From Supabase API settings |
| `SUPABASE_SERVICE_ROLE_KEY` | Your service role key | From Supabase API settings |
| `FLASK_ENV` | `production` | Performance optimizations |
| `FLASK_DEBUG` | `False` | Disable debug mode in production |

**Getting Your Supabase Credentials:**

1. Go to [app.supabase.com](https://app.supabase.com)
2. Select your project
3. Go to **Settings → API**
4. Copy:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` → `SUPABASE_KEY`
   - `service_role` → `SUPABASE_SERVICE_ROLE_KEY`

### 2.5 Deploy

Click **"Create Web Service"**

Render will:
1. Build your application
2. Install all dependencies
3. Deploy your app
4. Assign you a `.onrender.com` URL

**Deployment typically takes 3-5 minutes**

## Step 3: Verify Deployment

Once deployment completes:

1. Check the **"Events"** tab for logs
2. Click the provided URL to access your app
3. Test all features:
   - Sign up / Login
   - Create post with image
   - Check progress modal
   - Test analysis page
   - Try attack demo

## Step 4: Set Up Custom Domain (Optional)

### 4.1 In Render Dashboard
1. Go to your service
2. Click **"Settings"**
3. Scroll to **"Custom Domains"**
4. Click **"Add Custom Domain"**
5. Enter your domain

### 4.2 In Your Domain Provider
Update DNS records to point to Render's servers (Render provides specific instructions)

## Troubleshooting

### Build Fails
- **Check logs** in the Events tab
- **Common issues:**
  - Missing `requirements.txt`
  - Incompatible dependencies
  - Python version mismatch

**Solution:** Update `requirements.txt` and push new code

### App Crashes on Startup
- **Check environment variables** - ensure all required vars are set
- **Check Supabase connection** - verify credentials are correct
- **Review logs** for specific error messages

### Static Files Not Loading
- Ensure `static/` folder is committed to GitHub
- Check file paths in templates (use `/static/...`)

### Database Connection Issues
1. Verify Supabase credentials are correct
2. Check if Supabase project is active
3. Ensure service role key has proper permissions

## Performance Tips

### 1. Enable Caching
```python
# Add to app.py
@app.after_request
def set_cache_headers(response):
    response.cache_control.max_age = 3600
    return response
```

### 2. Optimize Database Queries
- Add indexes to frequently queried columns
- Use pagination for large datasets
- Avoid N+1 queries

### 3. Image Optimization
- Compress images before upload
- Use WebP format where possible
- Implement lazy loading

### 4. Monitor Performance
- Use Render's built-in logs
- Monitor CPU and memory usage
- Set up alerts for errors

## Updating Your App

### Deploy Updates:
```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render automatically redeploys when you push to main branch!

### Manual Redeploy:
1. Go to your service in Render
2. Click **"Manual Deploy"**
3. Select branch (usually `main`)

## Scaling Up

### When You Need More Power:
1. Go to service settings
2. Increase **Instance Type** from Free → Starter → Standard
3. Monitor performance
4. Scale as needed

### Database Optimization:
- Upgrade Supabase plan if hitting limits
- Implement caching layer (Redis)
- Archive old data

## Production Checklist

Before going live:

- ✅ Enable HTTPS (automatic with Render)
- ✅ Set `FLASK_DEBUG = False`
- ✅ Update `SECRET_KEY` with strong random value
- ✅ Test all authentication flows
- ✅ Verify encryption/decryption works
- ✅ Test image upload and steganography
- ✅ Check all API endpoints
- ✅ Review error handling
- ✅ Test on mobile devices
- ✅ Set up monitoring/logging

## Useful Links

- [Render Documentation](https://render.com/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deployment/)
- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/)
- [Supabase Documentation](https://supabase.com/docs)

## Support

If you encounter issues:

1. Check Render logs for error messages
2. Review the [Render Community](https://render.com/community)
3. Check [Supabase Support](https://supabase.com/support)
4. Review this guide's troubleshooting section

---

**Happy deploying!** 🚀
