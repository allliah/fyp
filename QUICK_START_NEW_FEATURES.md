# Stegbox Quick Start Guide

## 🎯 What's New?

Your Stegbox app now has 4 major new features implemented and ready to use!

---

## 1️⃣ Secure Encoding Progress Modal

**When you see it:** Click "Post" with a secret message or image

**What it shows:**
```
🔒 Secure Encoding in Progress
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ CNN Region Selection      [ ] Pending
⏳ LSB Steganography         [ ] Pending
⏳ AES-256 Encryption        [ ] Pending
⏳ RSA-OAEP Key Wrapping     [ ] Pending
                        [Progress Bar]

📊 Steganography Metrics:
   PSNR: 51.44 dB
   SSIM: 0.9980
   Suitable Pixels: 126,000
   Payload: 320 bits
```

**How to trigger:**
1. Go to Feed page
2. Write a post
3. Toggle "Hide secret message"
4. Enter your secret & pick a recipient
5. Click "Post" → Watch progress modal! ✨

---

## 2️⃣ Steganography Analysis Page

**How to access:** Click `📊 Analysis` in top navigation

**What you can do:**
- 📤 Upload any image
- 👀 See before/after comparison
- 📊 View quality metrics (PSNR, SSIM, etc.)
- 🔍 Check image properties (dimensions, channels, etc.)
- 🔐 View the steganography pipeline steps
- 📈 See detection resistance metrics

**Example workflow:**
1. Click upload area
2. Select an image
3. View metrics automatically generate
4. Scroll down to see all details
5. Learn about the encoding pipeline

---

## 3️⃣ Steganalysis Attack Demo

**How to access:** Click `⚔️ Attack Demo` in top navigation

**Available attacks:**
- **Chi-Square Analysis** - Detects histogram patterns
- **RS Analysis** - Analyzes pixel groupings
- **Sample Pairs Analysis** - Examines sample patterns
- **CNN Steganalysis** - AI-based detection

**Attack workflow:**
```
1. Upload Image → 2. Pick Attack Method → 3. Launch → 4. Watch Progress
                                              ↓
                                        Stage 1: Image Preprocessing
                                        Stage 2: Feature Extraction
                                        Stage 3: Analysis Computation
                                        Stage 4: Results Generation
                                              ↓
                                        View Results & Report
```

**Results show:**
- Confidence score (0-100%)
- Detection status (Detected/Clean)
- Detailed analysis report
- Recommendations

---

## 4️⃣ Top Navigation Bar

**Always visible at the top:**
```
🔒 Stegbox | 📱 Feed | 📊 Analysis | ⚔️ Attack Demo | 👤 Profile | 🚪 Logout
```

Click any link to navigate instantly!

---

## 🚀 Deploy to Render (Free Hosting)

### Quick Deploy (5 minutes)

**Step 1: Push to GitHub**
```bash
cd c:\Users\User\Documents\fyp7
git add .
git commit -m "Add all features"
git push origin main
```

**Step 2: Sign up for Render**
- Go to https://render.com
- Click "Sign up with GitHub"
- Authorize access

**Step 3: Create Web Service**
1. Dashboard → "New +" → "Web Service"
2. Connect your repo
3. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
4. Add environment variables:
   - SUPABASE_URL
   - SUPABASE_KEY
   - SUPABASE_SERVICE_ROLE_KEY
   - SECRET_KEY (generate random)
5. Click "Create Web Service"

**Step 4: Done!** ✅
Your app will be live in 3-5 minutes at `your-app-name.onrender.com`

---

## 📋 Checklist Before Deployment

- [ ] All new templates exist (analysis.html, attack.html)
- [ ] app.py has /analysis and /attack routes
- [ ] Procfile exists
- [ ] runtime.txt exists
- [ ] .env.example exists
- [ ] render.yaml exists
- [ ] Changes committed to Git
- [ ] Ready to push to GitHub

**Check files are created:**
```bash
# In your fyp7 directory:
- Procfile          ✅
- runtime.txt       ✅
- render.yaml       ✅
- .env.example      ✅
```

**Check templates created:**
```bash
# In templates/ directory:
- analysis.html     ✅
- attack.html       ✅
```

---

## 🧪 Test Locally First

Before deploying:

```bash
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Flask app
python app.py

# 4. Test in browser
# - Go to http://localhost:5000
# - Test feed with progress modal
# - Click "Analysis" page
# - Click "Attack Demo" page
```

**What to check:**
- ✅ Progress modal appears when posting with secret
- ✅ Analysis page loads and accepts images
- ✅ Attack demo shows all 4 stages
- ✅ Navigation bar links work
- ✅ Top nav shows active page

---

## 🐛 If Something Breaks

### Modal not showing?
```javascript
// Check browser console (F12)
// Look for JavaScript errors
```

### Analysis page not loading?
```bash
# Check app.py has route:
# @app.route("/analysis")
# def analysis():
#     return render_template("analysis.html")
```

### Attack demo broken?
- Verify attack.html exists in templates/
- Check browser console for errors
- Try with a smaller image file

### Render deployment failed?
1. Check Render dashboard logs
2. Verify environment variables are set
3. Ensure Procfile is correctly formatted
4. Review RENDER_DEPLOYMENT_GUIDE.md

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `Procfile` | Tells Render how to run the app |
| `runtime.txt` | Specifies Python 3.11.7 |
| `render.yaml` | Alternative config file |
| `.env.example` | Shows required environment variables |
| `app.py` | Main Flask app (UPDATED with new routes) |
| `templates/feed.html` | Feed with progress modal (UPDATED) |
| `templates/analysis.html` | Analysis page (NEW) |
| `templates/attack.html` | Attack demo page (NEW) |
| `RENDER_DEPLOYMENT_GUIDE.md` | Full deployment instructions |
| `IMPLEMENTATION_COMPLETE.md` | Detailed feature documentation |

---

## 💡 Pro Tips

1. **Progress Modal Metrics**
   - Metrics are randomly generated for demo
   - In production, use real CNN metrics
   - Update `simulateEncodingSteps()` function

2. **Analysis Page**
   - Currently uses simulated image processing
   - Connect to actual CNN region selector for production
   - Add real steganography to canvas processing

3. **Attack Demo**
   - Attack methods are simulated for demo
   - Implement real Chi-Square/RS/SPA analysis
   - Add real CNN steganalysis model

4. **Performance**
   - Use Redis caching for frequently analyzed images
   - Optimize image processing with PIL
   - Add lazy loading for images

5. **Security**
   - Change `SECRET_KEY` in production
   - Never commit `.env` file
   - Use strong Supabase credentials
   - Enable HTTPS (automatic on Render)

---

## 🎓 Learning Resources

- **Flask:** https://flask.palletsprojects.com/
- **Render:** https://render.com/docs
- **Supabase:** https://supabase.com/docs
- **HTML Canvas:** https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- **Steganography:** https://en.wikipedia.org/wiki/Steganography

---

## 🚀 Next Steps

1. **Test locally** - Make sure everything works
2. **Push to GitHub** - Commit all changes
3. **Deploy to Render** - Follow deployment steps
4. **Share your app** - Get that `onrender.com` URL
5. **Gather feedback** - Test with friends

---

## 📞 Need Help?

Check these files in order:
1. **RENDER_DEPLOYMENT_GUIDE.md** - For deployment issues
2. **IMPLEMENTATION_COMPLETE.md** - For feature details
3. **Browser console (F12)** - For JavaScript errors
4. **Flask logs** - For backend errors

---

## ✨ You're All Set!

Everything is implemented and ready to use. 

**What you have now:**
✅ Animated progress modal with metrics
✅ Detailed analysis page with visualizations
✅ Interactive attack demo with multiple methods
✅ Global top navigation bar
✅ Complete Render deployment setup

**What to do now:**
1. Test locally
2. Push to GitHub
3. Deploy to Render
4. Share with the world! 🌍

---

**Happy coding!** 🎉
