# 🎯 KeenEye v2.0 - AI Resume Ranking System (Cloud API Edition)

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-API-orange?style=for-the-badge)](https://groq.com)
[![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)

**An intelligent, AI-powered resume ranking system that matches candidates to job opportunities using state-of-the-art NLP and LLM technologies.**

---

## 🚀 **What's New in v2.0?**

✅ **100% Cloud-Based** - Runs on Streamlit Cloud (no local GPU required!)  
✅ **Free Forever** - Uses free-tier APIs (Groq + Gemini)  
✅ **Lightning Fast** - 3-5 second cold start vs 60+ seconds for local models  
✅ **Production Ready** - Scalable, reliable, and professionally deployed  

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT CLOUD APP                       │
│                     (2-3GB RAM Usage)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬───────────────┐
        │            │            │               │
        ▼            ▼            ▼               ▼
┌──────────────┐ ┌─────────┐ ┌──────────┐ ┌────────────┐
│ Gemini API   │ │ Groq    │ │APILayer  │ │ FAISS      │
│ (Embeddings) │ │ (LLM)   │ │ (Parser) │ │ (Search)   │
│ FREE         │ │ FREE    │ │ FREE     │ │ Local      │
│ Unlimited    │ │ 14.4K/d │ │ 100/mo   │ │            │
└──────────────┘ └─────────┘ └──────────┘ └────────────┘
```

### **4-Stage Ranking Pipeline**

1. **Stage 1: Semantic Search** (Gemini Embeddings + FAISS)
   - Embed resume using Gemini API
   - Search against pre-indexed job embeddings
   - Return top 50 semantically similar jobs

2. **Stage 2: Skill Matching** (Rule-Based)
   - Extract skills from resume and job descriptions
   - Calculate skill coverage scores
   - Identify matched and missing skills

3. **Stage 3: Multi-Modal Scoring** (Weighted Ensemble)
   - Combine semantic similarity (35%)
   - Skill coverage (30%)
   - Experience fit (15%)
   - LLM analysis (20%)

4. **Stage 4: LLM Deep Analysis** (Groq Llama 3.3 70B)
   - Generate comprehensive match insights
   - Identify strengths and weaknesses
   - Provide actionable recommendations

---

## 📦 **Installation & Setup**

### **Prerequisites**
- Python 3.10 or higher
- Git
- GitHub account
- Streamlit Cloud account (free)

### **1. Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/KeenEye-Cloud.git
cd KeenEye-Cloud
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Get API Keys** (All FREE!)

#### **Groq API Key** (Required)
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up with Google/GitHub
3. Navigate to "API Keys" → "Create API Key"
4. Copy key (starts with `gsk_...`)

#### **Google Gemini API Key** (Required)
1. Go to [https://ai.google.dev](https://ai.google.dev)
2. Click "Get API Key in Google AI Studio"
3. Click "Create API Key"
4. Copy key (starts with `AIza...`)

#### **APILayer Resume Parser** (Optional)
1. Go to [https://apilayer.com](https://apilayer.com)
2. Sign up and subscribe to "Resume Parser API"
3. Select FREE plan (100 requests/month)
4. Copy API key from dashboard

### **4. Configure API Keys**

#### **For Local Testing:**
Create `.env` file:
```bash
cp .env.example .env
nano .env  # Edit and add your API keys
```

#### **For Streamlit Cloud:**
Create `.streamlit/secrets.toml`:
```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
nano .streamlit/secrets.toml  # Edit and add your API keys
```

### **5. Add Jobs Dataset**
Place your `jobs_dataset.csv` in the root directory with columns:
- `Job_ID`
- `Job Title`
- `Company`
- `Job Description`
- `Min_Experience`
- `Max_Experience`
- `skills_list` (list of required skills)

Or use the built-in sample generator (automatic if file not found).

---

## 🚀 **Running Locally**

```bash
streamlit run streamlit_app_cloud.py
```

The app will open at `http://localhost:8501`

---

## ☁️ **Deploying to Streamlit Cloud**

### **Step 1: Push to GitHub**
```bash
git add .
git commit -m "Initial commit: KeenEye v2.0 Cloud"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/KeenEye-Cloud.git
git push -u origin main
```

### **Step 2: Deploy on Streamlit Cloud**
1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Configure:
   - **Repository:** `YOUR_USERNAME/KeenEye-Cloud`
   - **Branch:** `main`
   - **Main file:** `streamlit_app_cloud.py`
4. Click "Advanced settings" → "Secrets"
5. Paste your API keys in TOML format:
```toml
GROQ_API_KEY = "gsk_xxx..."
GEMINI_API_KEY = "AIza..."
APILAYER_API_KEY = "xxx..."
```
6. Click "Deploy"
7. Wait 3-5 minutes for deployment

### **Your app will be live at:**
```
https://YOUR_USERNAME-keeneye-cloud-streamlit-app-cloud-xxxxx.streamlit.app
```

---

## 📊 **Usage Guide**

1. **Upload Resume** - Drag & drop PDF, DOCX, or TXT file
2. **Click "Analyze Resume"** - System processes in 4 stages
3. **View Results** - Top job matches with AI insights
4. **Explore Analytics** - Score distributions and visualizations
5. **Review Details** - Strengths, weaknesses, and recommendations

---

## 🎨 **Features**

### **Core Features**
✅ Multi-stage AI-powered ranking  
✅ Semantic similarity search (Gemini embeddings)  
✅ Skill gap analysis  
✅ Experience fit scoring  
✅ LLM-powered insights (Groq Llama 3.3 70B)  
✅ Interactive visualizations (Plotly)  

### **User Experience**
✅ Real-time progress indicators  
✅ Expandable job cards  
✅ Match score breakdowns  
✅ Actionable recommendations  
✅ Export results (coming soon)  

### **Technical**
✅ FAISS vector indexing  
✅ Batch processing for efficiency  
✅ API retry logic with exponential backoff  
✅ Local parser fallback  
✅ Session state caching  

---

## 🔧 **Configuration**

Edit `config_cloud.py` to customize:

```python
# Ranking Parameters
TOP_K_SEMANTIC = 50      # Jobs to retrieve semantically
TOP_K_FINAL = 15         # Final ranked results

# Scoring Weights
SEMANTIC_WEIGHT = 0.35   # Semantic similarity weight
SKILL_WEIGHT = 0.30      # Skill match weight
EXPERIENCE_WEIGHT = 0.15 # Experience fit weight
LLM_WEIGHT = 0.20        # LLM analysis weight

# Features
USE_CROSS_ENCODER = False  # Enable cross-encoder re-ranking
USE_CACHE = True           # Enable caching
```

---

## 🐛 **Troubleshooting**

### **"Missing API key" Error**
- Verify keys are set in `.streamlit/secrets.toml` (local) or Streamlit Cloud secrets
- Check key format matches documentation

### **"Rate limit exceeded" Error**
- Groq: 14,400/day limit - wait 1 hour or use OpenRouter fallback
- APILayer: 100/month limit - system auto-falls back to local parser

### **"Memory error" in Streamlit Cloud**
- Reduce `MAX_JOBS_SAMPLE` in config
- Ensure jobs dataset < 10,000 rows

### **App crashes on startup**
- Check all dependencies in `requirements.txt` are installed
- Verify Python version >= 3.10

---

## 📈 **Performance Benchmarks**

| Metric | Local Version | Cloud API Version |
|--------|---------------|-------------------|
| **Cold Start Time** | 60-90 seconds | 3-5 seconds |
| **Memory Usage** | 12-16GB | 2-3GB |
| **Inference Speed** | Medium | Ultra-fast (Groq) |
| **Deployment** | ❌ Fails on cloud | ✅ Works perfectly |
| **Cost** | $0 | $0 |

---

## 💰 **Cost Analysis**

### **Free Tier Limits**
- **Groq:** 14,400 requests/day = 600 resumes/day
- **Gemini:** Unlimited embeddings (rate limited to 1,500 RPM)
- **APILayer:** 100 parses/month (falls back to local)

### **Estimated Usage**
- 50 users/day × 1 resume each = 750 API calls/day
- **Total Cost:** $0/month ✅

---

## 🗺️ **Roadmap**

### **v2.1 (Next)**
- [ ] User authentication
- [ ] Resume history tracking
- [ ] PDF report generation
- [ ] Email integration

### **v3.0 (Future)**
- [ ] Real-time job scraping
- [ ] Multi-language support
- [ ] Video interview insights
- [ ] Skills gap training recommendations

---

## 🤝 **Contributing**

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License.

---

## 👤 **Author**

**Akhiranand Boddani**  
📧 Email: your.email@example.com  
🔗 LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)  
🐙 GitHub: [Your GitHub](https://github.com/yourusername)

---

## 🙏 **Acknowledgments**

- **Groq** - Ultra-fast LLM inference
- **Google AI** - Gemini embeddings API
- **Streamlit** - Cloud deployment platform
- **FAISS** - Efficient similarity search
- **APILayer** - Resume parsing API

---

## 📞 **Support**

Having issues? Check:
- [Documentation](./docs/)
- [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)
- [GitHub Issues](https://github.com/YOUR_USERNAME/KeenEye-Cloud/issues)

---

**⭐ If you find this project helpful, please give it a star on GitHub!**