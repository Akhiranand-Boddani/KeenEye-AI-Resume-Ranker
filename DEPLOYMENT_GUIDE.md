# 🚀 KeenEye v2.0 - Complete Deployment Guide

## 📋 **Pre-Deployment Checklist**

Before deploying, ensure you have:

- [ ] All source code files in project directory
- [ ] API keys obtained (Groq + Gemini minimum)
- [ ] GitHub account created
- [ ] Streamlit Cloud account created
- [ ] Jobs dataset CSV prepared (or using sample data)
- [ ] Tested locally and all APIs working

---

## 🔑 **Step 1: Get API Keys (15 minutes)**

### **1.1 Groq API Key (Required)**

1. Visit [https://console.groq.com](https://console.groq.com)
2. Click "Sign Up" (use Google/GitHub for quick signup)
3. Verify email if required
4. Navigate to "API Keys" in left sidebar
5. Click "Create API Key"
6. Name it: `KeenEye-Production`
7. Copy the key (starts with `gsk_...`)
8. **Save it securely!** (You can't view it again)

**Free Tier:** 14,400 requests/day (600 resumes/day)

---

### **1.2 Google Gemini API Key (Required)**

1. Visit [https://ai.google.dev](https://ai.google.dev)
2. Click "Get API Key in Google AI Studio"
3. Sign in with Google account
4. Click "Create API Key"
5. Select "Create API key in new project"
6. Copy the key (starts with `AIza...`)
7. **Save it securely!**

**Free Tier:** Unlimited (rate limited to 1,500 RPM)

---

### **1.3 APILayer Key (Optional - Recommended)**

1. Visit [https://apilayer.com](https://apilayer.com)
2. Sign up with email
3. Verify email
4. Search for "Resume Parser API"
5. Click "Subscribe" → Select "FREE" plan
6. Go to Dashboard → Copy API key
7. **Save it!**

**Free Tier:** 100 requests/month

> **Note:** If you skip this, the system will automatically use local parsing.

---

## 💻 **Step 2: Local Testing (30 minutes)**

### **2.1 Clone/Setup Project**

```bash
# Create project directory
mkdir KeenEye-Cloud
cd KeenEye-Cloud

# Initialize git
git init

# Copy all provided files into this directory:
# - streamlit_app_cloud.py
# - api_clients.py
# - config_cloud.py
# - semantic_ranker_api.py
# - llm_analyst_api.py
# - requirements.txt
# - .gitignore
# - README.md
# - test_api_clients.py
# - .streamlit/config.toml
# - .streamlit/secrets.toml.example
# - .env.example
```

### **2.2 Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2.3 Configure API Keys (Local)**

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your favorite editor

# Add your API keys:
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxx
APILAYER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx  # optional
```

### **2.4 Test API Connections**

```bash
# Run test script
python test_api_clients.py

# You should see:
# ✅ Groq API working!
# ✅ Gemini API working!
# ⚠️ APILayer API... (optional)
# ✅ Local parser working!
# ✅ ALL CRITICAL TESTS PASSED!
```

If tests fail, verify your API keys are correct.

### **2.5 Test Streamlit App Locally**

```bash
# Run app
streamlit run streamlit_app_cloud.py

# Browser should open at http://localhost:8501
# Test by uploading a sample resume PDF
```

**✅ If app works locally, you're ready to deploy!**

---

## 🌐 **Step 3: GitHub Setup (15 minutes)**

### **3.1 Create GitHub Repository**

1. Go to [https://github.com/new](https://github.com/new)
2. Repository name: `KeenEye-Cloud`
3. Description: `AI-powered resume ranking system using free APIs`
4. Choose: **Public** (required for free Streamlit Cloud)
5. **DO NOT** initialize with README (we have one)
6. Click "Create repository"

### **3.2 Push Code to GitHub**

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/KeenEye-Cloud.git

# Stage all files
git add .

# Commit
git commit -m "Initial commit: KeenEye v2.0 Cloud API Edition"

# Push to main branch
git branch -M main
git push -u origin main
```

### **3.3 Verify Upload**

Go to your GitHub repository page and verify all files are there.

**⚠️ CRITICAL:** Check that `.env` and `.streamlit/secrets.toml` are **NOT** uploaded!  
They should be blocked by `.gitignore`.

---

## ☁️ **Step 4: Streamlit Cloud Deployment (20 minutes)**

### **4.1 Sign Up for Streamlit Cloud**

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click "Sign up" or "Sign in"
3. **Use same email as GitHub** for easy linking
4. Authorize Streamlit to access your GitHub

### **4.2 Create New App**

1. Click "New app" button
2. Fill in details:

```
Repository: YOUR_USERNAME/KeenEye-Cloud
Branch: main
Main file path: streamlit_app_cloud.py
```

3. Click "Advanced settings" (don't deploy yet!)

### **4.3 Configure Secrets**

In the "Secrets" text box, paste:

```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
GEMINI_API_KEY = "AIza_your_actual_key_here"
APILAYER_API_KEY = "your_apilayer_key_here"
```

**⚠️ Replace with your ACTUAL API keys!**

### **4.4 Configure Python Version**

In "Advanced settings":
- Python version: `3.10` or `3.11`

### **4.5 Deploy!**

1. Click "Deploy"
2. Wait 3-5 minutes while Streamlit Cloud:
   - Pulls your code from GitHub
   - Installs dependencies
   - Starts the app

### **4.6 Monitor Deployment**

Watch the deployment logs in the Streamlit Cloud interface.

**Look for:**
```
✅ Installed all dependencies
✅ Running on port 8501
✅ App is live!
```

### **4.7 Test Production App**

Your app will be live at:
```
https://YOUR_USERNAME-keeneye-cloud-streamlit-app-cloud-xxxxx.streamlit.app
```

Test it:
1. Upload a resume
2. Click "Analyze Resume"
3. Verify all 4 stages execute
4. Check results display correctly

**🎉 If everything works, deployment is complete!**

---

## 📊 **Step 5: Add Jobs Dataset (Optional)**

### **Option A: Use Sample Data**
The app automatically generates 100 sample jobs if no dataset found.

### **Option B: Upload Your Dataset**

1. Prepare CSV with columns:
   - `Job_ID`
   - `Job Title`
   - `Company`
   - `Job Description`
   - `Min_Experience`
   - `Max_Experience`
   - `skills_list`

2. Add to GitHub repo:
```bash
# Add jobs CSV
git add jobs_dataset.csv
git commit -m "Add jobs dataset"
git push

# Streamlit Cloud will auto-redeploy
```

---

## 🔧 **Step 6: Post-Deployment Configuration**

### **6.1 Custom Domain (Optional)**

Streamlit Cloud provides custom domains:
1. Go to app settings
2. Click "Custom domain"
3. Follow instructions to set up

### **6.2 Monitor API Usage**

Check your API dashboards regularly:

- **Groq:** [https://console.groq.com/usage](https://console.groq.com/usage)
- **Gemini:** [https://ai.google.dev/gemini-api/docs/quota](https://ai.google.dev/gemini-api/docs/quota)
- **APILayer:** [https://apilayer.com/dashboard](https://apilayer.com/dashboard)

Set up alerts if usage approaches limits.

### **6.3 Update App Settings**

In Streamlit Cloud app settings:
- Enable "Always rerun" for auto-updates
- Set "Instance type" to default (1 core, 8GB RAM)
- Configure analytics (optional)

---

## 🐛 **Troubleshooting Common Issues**

### **Issue 1: "Missing API key" Error**

**Symptom:** App shows error about missing API keys

**Solution:**
1. Go to Streamlit Cloud → Your App → Settings → Secrets
2. Verify all keys are set correctly in TOML format
3. Check for typos in key names (case-sensitive!)
4. Click "Save" and wait for app to restart

---

### **Issue 2: App Crashes During Startup**

**Symptom:** Deployment fails with "ModuleNotFoundError"

**Solution:**
1. Check `requirements.txt` has all dependencies
2. Verify Python version in advanced settings (use 3.10 or 3.11)
3. Look at deployment logs for specific missing package
4. Add missing package to `requirements.txt`
5. Push to GitHub and redeploy

---

### **Issue 3: "Rate Limit Exceeded" Error**

**Symptom:** Groq/Gemini API errors after heavy usage

**Solution for Groq (14,400/day limit):**
- Wait 1 hour for limit reset
- Add OpenRouter as fallback API
- Reduce number of LLM analyses per resume

**Solution for Gemini (1,500 RPM limit):**
- Add delays between batch embedding calls
- Already handled by retry logic in code
- Should not occur in normal usage

---

### **Issue 4: Resume Parsing Fails**

**Symptom:** "Resume parsing failed" error

**Solution:**
1. Verify APILayer key is set (if using API parsing)
2. Check file format (PDF, DOCX, TXT)
3. Ensure file size < 10MB
4. System should auto-fallback to local parser
5. Check logs for specific error message

---

### **Issue 5: Memory Error on Streamlit Cloud**

**Symptom:** "Memory limit exceeded" error

**Solution:**
1. Reduce `MAX_JOBS_SAMPLE` in `config_cloud.py` to 5000
2. Limit jobs dataset to < 10,000 rows
3. Disable cross-encoder if enabled
4. Clear cache and restart app

---

### **Issue 6: Slow Response Times**

**Symptom:** App takes > 30 seconds to analyze resume

**Solution:**
1. Pre-compute job embeddings (add to repo as `.npz` file)
2. Reduce `TOP_K_SEMANTIC` from 50 to 30
3. Reduce `TOP_K_FINAL` from 15 to 10
4. Check API status dashboards for outages

---

## 📈 **Monitoring & Maintenance**

### **Daily Checks**
- [ ] App is accessible and loading
- [ ] API keys are valid and working
- [ ] No error messages in Streamlit Cloud logs

### **Weekly Checks**
- [ ] Review API usage metrics
- [ ] Check for any user-reported issues
- [ ] Update dependencies if needed

### **Monthly Checks**
- [ ] Rotate API keys (security best practice)
- [ ] Review and update jobs dataset
- [ ] Check for Streamlit/library updates
- [ ] Analyze usage patterns and optimize

---

## 🔄 **Updating Your Deployed App**

To update your app after deployment:

```bash
# Make code changes locally
nano streamlit_app_cloud.py

# Test locally
streamlit run streamlit_app_cloud.py

# Commit and push
git add .
git commit -m "Update: Added new feature"
git push

# Streamlit Cloud will automatically redeploy!
# Takes 2-3 minutes
```

---

## 🔐 **Security Best Practices**

### **API Key Security**
- ✅ Never commit API keys to GitHub
- ✅ Use `.gitignore` to exclude `.env` and `secrets.toml`
- ✅ Rotate keys every 90 days
- ✅ Use separate keys for dev/prod
- ✅ Monitor usage for unusual activity

### **User Data Privacy**
- ✅ Don't store uploaded resumes permanently
- ✅ Clear session state after analysis
- ✅ Inform users their data isn't saved
- ✅ Add privacy policy if collecting analytics

---

## 📊 **Performance Optimization Tips**

### **1. Pre-Compute Job Embeddings**

Instead of computing embeddings on every deployment:

```python
# One-time script: precompute_embeddings.py
import numpy as np
from api_clients import GeminiEmbeddingClient
import pandas as pd

# Load jobs
jobs_df = pd.read_csv('jobs_dataset.csv')
client = GeminiEmbeddingClient(api_key="YOUR_KEY")

# Generate embeddings
embeddings = client.embed(jobs_df['Job Description'].tolist())

# Save to file
np.savez_compressed('job_embeddings.npz', 
                   embeddings=np.array(embeddings),
                   job_ids=jobs_df['Job_ID'].values)

# Add to GitHub repo (< 100MB)
# App will load this instead of recomputing
```

### **2. Use Caching Effectively**

```python
# In streamlit_app_cloud.py
@st.cache_resource
def load_precomputed_embeddings():
    data = np.load('job_embeddings.npz')
    return data['embeddings'], data['job_ids']

# Load once per deployment
embeddings, job_ids = load_precomputed_embeddings()
```

### **3. Batch API Calls**

```python
# Process multiple resumes efficiently
def batch_analyze_resumes(resume_files):
    # Batch embeddings in groups of 32
    for batch in chunks(resume_files, 32):
        embeddings = client.embed([r.text for r in batch])
        # Process batch...
```

---

## 🎯 **Success Criteria**

Your deployment is successful if:

✅ App loads in < 5 seconds (cold start)  
✅ Resume analysis completes in < 30 seconds  
✅ All 4 ranking stages execute without errors  
✅ Results display with visualizations  
✅ API usage stays within free tiers  
✅ No memory errors on Streamlit Cloud  
✅ App is accessible via public URL  

---

## 🚀 **Going Production-Ready**

For serious production use, consider:

### **1. Upgrade Infrastructure**
- Streamlit Cloud paid tier ($20/month) for more resources
- Dedicated API keys with higher limits
- CDN for faster global access

### **2. Add Features**
- User authentication (Auth0, Firebase)
- Resume history and tracking
- Email notifications for matches
- PDF report generation
- Analytics dashboard

### **3. Implement CI/CD**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python test_api_clients.py
```

### **4. Set Up Monitoring**
- Sentry for error tracking
- Google Analytics for usage
- Uptime monitoring (UptimeRobot)
- Custom logging and metrics

---

## 📞 **Getting Help**

### **Resources**
- **Streamlit Docs:** [https://docs.streamlit.io](https://docs.streamlit.io)
- **Groq Docs:** [https://console.groq.com/docs](https://console.groq.com/docs)
- **Gemini Docs:** [https://ai.google.dev/docs](https://ai.google.dev/docs)

### **Community Support**
- **Streamlit Forum:** [https://discuss.streamlit.io](https://discuss.streamlit.io)
- **Stack Overflow:** Tag `streamlit` + `groq-api`
- **GitHub Issues:** Create issue in your repo

### **Direct Support**
- Check project README for maintainer contact
- Join Discord/Slack communities for Streamlit
- Twitter: #streamlit #groq #gemini

---

## ✅ **Final Checklist**

Before considering deployment complete:

- [ ] App is live and accessible
- [ ] All API connections tested in production
- [ ] Resume upload and parsing works
- [ ] All 4 ranking stages execute
- [ ] Results display correctly
- [ ] Visualizations render properly
- [ ] Mobile responsiveness checked
- [ ] Error handling tested
- [ ] API usage monitored
- [ ] Documentation updated
- [ ] GitHub repo organized
- [ ] README includes live URL
- [ ] Demo video recorded (optional)
- [ ] Shared on LinkedIn/portfolio (optional)

---

## 🎉 **Congratulations!**

You've successfully deployed KeenEye v2.0 to the cloud!

**Next Steps:**
1. Share your app URL with potential users
2. Gather feedback and iterate
3. Add to your portfolio/resume
4. Consider contributing improvements back to the community

**Your app is now:**
- ✅ Live and accessible 24/7
- ✅ Running on free infrastructure
- ✅ Using state-of-the-art AI
- ✅ Scalable and production-ready

**Happy ranking! 🎯**

---

**Need help? Found a bug? Want to contribute?**  
Open an issue on GitHub or contact the maintainer.

**⭐ Don't forget to star the repo if you find it useful!**