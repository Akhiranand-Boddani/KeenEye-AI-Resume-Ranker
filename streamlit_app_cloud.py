import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Import custom modules
from config_cloud import CloudConfig
from api_clients import (
    GroqClient, 
    GeminiEmbeddingClient, 
    APILayerParserClient,
    LocalResumeParser
)
from semantic_ranker_api import SemanticRankerAPI, SkillMatcher, ExperienceMatcher
from llm_analyst_api import LLMAnalystAPI

# Debug: Check if secrets are loaded
st.sidebar.write("🔍 Debug Info")
if hasattr(st, 'secrets'):
    st.sidebar.write(f"✅ Secrets loaded: {len(st.secrets)} keys")
    st.sidebar.write(f"Groq key present: {bool(st.secrets.get('GROQ_API_KEY', ''))}")
    st.sidebar.write(f"Groq key length: {len(st.secrets.get('GROQ_API_KEY', ''))}")
else:
    st.sidebar.error("❌ No secrets found!")

# Page Configuration
st.set_page_config(
    page_title="KeenEye v2.0 - AI Resume Ranker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'config' not in st.session_state:
        st.session_state.config = CloudConfig()
    
    if 'clients_initialized' not in st.session_state:
        st.session_state.clients_initialized = False
    
    if 'jobs_loaded' not in st.session_state:
        st.session_state.jobs_loaded = False
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'api_logs' not in st.session_state:
        st.session_state.api_logs = []


def initialize_clients(config):
    """Initialize API clients"""
    try:
        config.validate()
        
        groq_client = GroqClient(config.GROQ_API_KEY)
        gemini_client = GeminiEmbeddingClient(config.GEMINI_API_KEY)
        
        # Optional: APILayer parser
        if config.APILAYER_API_KEY:
            parser_client = APILayerParserClient(config.APILAYER_API_KEY)
        else:
            parser_client = LocalResumeParser()
        
        return groq_client, gemini_client, parser_client
    
    except Exception as e:
        st.error(f"❌ Failed to initialize API clients: {e}")
        st.stop()


@st.cache_data
def load_jobs_dataset():
    """Load jobs dataset (cached)"""
    try:
        # Try to load from default location
        df = pd.read_csv('jobs_dataset.csv')
        return df
    except FileNotFoundError:
        # Generate sample dataset if file not found
        st.warning("⚠️ Jobs dataset not found. Using sample data.")
        return generate_sample_jobs()


def generate_sample_jobs(n=100):
    """Generate sample jobs dataset for demo"""
    np.random.seed(42)
    
    titles = ['Data Scientist', 'ML Engineer', 'Software Engineer', 'Data Analyst', 'AI Researcher']
    companies = ['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix', 'Tesla']
    skills = ['Python', 'Machine Learning', 'Deep Learning', 'SQL', 'AWS', 'Docker', 'TensorFlow']
    
    data = {
        'Job_ID': range(1, n+1),
        'Job Title': np.random.choice(titles, n),
        'Company': np.random.choice(companies, n),
        'Job Description': [
            f"Looking for experienced {title} with {np.random.randint(2,8)} years experience. "
            f"Skills required: {', '.join(np.random.choice(skills, 4, replace=False))}. "
            f"Responsibilities include building scalable systems and working with cross-functional teams."
            for title in np.random.choice(titles, n)
        ],
        'Min_Experience': np.random.randint(0, 5, n),
        'Max_Experience': np.random.randint(5, 15, n),
        'skills_list': [list(np.random.choice(skills, 5, replace=False)) for _ in range(n)]
    }
    
    return pd.DataFrame(data)


@st.cache_resource
def build_job_index(_gemini_client, jobs_df, config):
    """Build FAISS index for jobs (cached across users)"""
    ranker = SemanticRankerAPI(_gemini_client, config)
    ranker.build_index(jobs_df, text_column='Job Description')
    return ranker


def parse_resume(file, parser_client, use_local_fallback=True):
    """Parse uploaded resume"""
    try:
        file_content = file.read()
        filename = file.name
        
        # Try API parser first
        try:
            result = parser_client.parse_resume(file_content, filename)
            st.success("✅ Resume parsed using API")
            return result
        except Exception as e:
            if use_local_fallback:
                st.warning(f"⚠️ API parsing failed, using local fallback: {str(e)[:100]}")
                local_parser = LocalResumeParser()
                return local_parser.parse_resume(file_content, filename)
            else:
                raise e
    
    except Exception as e:
        st.error(f"❌ Resume parsing failed: {e}")
        return None


def display_results(results_df, llm_analyses):
    """Display ranking results with visualizations"""
    
    st.markdown("---")
    st.markdown("## 📊 Ranking Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Jobs Analyzed", len(results_df))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        avg_score = results_df['final_score'].mean()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Match Score", f"{avg_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        top_matches = len(results_df[results_df['final_score'] >= 75])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Strong Matches", top_matches)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        avg_skills = results_df['skill_coverage'].mean()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Skill Match", f"{avg_skills:.0%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizations
    tab1, tab2, tab3 = st.tabs(["📋 Rankings", "📈 Analytics", "🔍 Detailed Analysis"])
    
    with tab1:
        st.markdown("### Top Job Matches")
        
        for idx, row in results_df.head(10).iterrows():
            with st.expander(
                f"#{row['rank']} - {row['Job Title']} at {row['Company']} "
                f"(Score: {row['final_score']:.1f}%)",
                expanded=(idx == 0)
            ):
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.markdown(f"**Job Description:**")
                    st.write(row['Job Description'][:500] + "...")
                    
                    st.markdown(f"**Required Experience:** {row['Min_Experience']}-{row['Max_Experience']} years")
                
                with col_b:
                    st.markdown("**Match Breakdown:**")
                    st.progress(row['semantic_score'], text=f"Semantic: {row['semantic_score']:.2f}")
                    st.progress(row['skill_coverage'], text=f"Skills: {row['skill_coverage']:.0%}")
                    st.progress(row['final_score']/100, text=f"Overall: {row['final_score']:.1f}%")
                
                # LLM Analysis
                if llm_analyses and idx < len(llm_analyses):
                    analysis = llm_analyses[idx]
                    
                    st.markdown("---")
                    st.markdown("**🤖 AI Analysis:**")
                    
                    col_x, col_y = st.columns(2)
                    
                    with col_x:
                        st.markdown("**Strengths:**")
                        for strength in analysis.get('strengths', [])[:2]:
                            st.markdown(f"✅ {strength.get('point', 'N/A')}")
                    
                    with col_y:
                        st.markdown("**Areas for Improvement:**")
                        for weakness in analysis.get('weaknesses', [])[:2]:
                            st.markdown(f"⚠️ {weakness.get('point', 'N/A')}")
                    
                    rec = analysis.get('recommendation', {})
                    decision = rec.get('decision', 'maybe')
                    emoji = '🟢' if decision == 'yes' else '🟡' if decision == 'maybe' else '🔴'
                    st.markdown(f"{emoji} **Recommendation:** {rec.get('reasoning', 'Review needed')}")
    
    with tab2:
        st.markdown("### Score Distribution")
        
        fig = px.histogram(
            results_df,
            x='final_score',
            nbins=20,
            title='Distribution of Match Scores',
            labels={'final_score': 'Match Score (%)', 'count': 'Number of Jobs'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Component Scores Comparison")
        
        fig2 = go.Figure()
        fig2.add_trace(go.Box(y=results_df['semantic_score']*100, name='Semantic'))
        fig2.add_trace(go.Box(y=results_df['skill_coverage']*100, name='Skills'))
        fig2.add_trace(go.Box(y=results_df['final_score'], name='Final'))
        fig2.update_layout(title='Score Components Distribution', yaxis_title='Score (%)')
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.markdown("### Complete Rankings Table")
        st.dataframe(
            results_df[[
            'rank', 'Job Title', 'Company', 'semantic_score',
            'skill_coverage', 'final_score'
            ]],
            use_container_width=True
        )


def main():
    """Main application"""
    
    # Initialize
    initialize_session_state()
    config = st.session_state.config
    
    # Header
    st.markdown('<h1 class="main-header">🎯 KeenEye v2.0</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Resume Ranking System | Cloud API Edition</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
        st.markdown("## Configuration")
        
        # API Status
        with st.expander("🔑 API Status"):
            status = config.get_api_status()
            for api, stat in status.items():
                st.markdown(f"**{api}:** {stat}")
        
        # Settings
        with st.expander("⚙️ Settings"):
            top_k = st.slider("Top Results", 5, 20, config.TOP_K_FINAL)
            config.TOP_K_FINAL = top_k
            
            show_debug = st.checkbox("Show Debug Info", value=False)
            config.SHOW_DEBUG_INFO = show_debug
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.info("KeenEye v2.0 uses state-of-the-art AI APIs for intelligent resume ranking.")
    
    # Initialize clients
    if not st.session_state.clients_initialized:
        with st.spinner("🚀 Initializing AI systems..."):
            groq_client, gemini_client, parser_client = initialize_clients(config)
            st.session_state.groq_client = groq_client
            st.session_state.gemini_client = gemini_client
            st.session_state.parser_client = parser_client
            st.session_state.clients_initialized = True
        st.success("✅ AI systems ready!")
    
    # Load jobs dataset
    if not st.session_state.jobs_loaded:
        with st.spinner("📚 Loading jobs dataset..."):
            jobs_df = load_jobs_dataset()
            st.session_state.jobs_df = jobs_df
            st.session_state.jobs_loaded = True
        st.success(f"✅ Loaded {len(jobs_df)} jobs")
    
    # Main interface
    st.markdown("---")
    st.markdown("## 📄 Upload Resume")
    
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF, DOCX, or TXT)",
        type=['pdf', 'docx', 'doc', 'txt'],
        help="Upload a resume to find matching job opportunities"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"📎 File uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        
        with col2:
            analyze_button = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)
        
        if analyze_button:
            # Step 1: Parse Resume
            with st.status("🔄 Processing resume...", expanded=True) as status:
                st.write("📄 Parsing resume...")
                resume_data = parse_resume(
                    uploaded_file, 
                    st.session_state.parser_client,
                    use_local_fallback=config.USE_LOCAL_PARSER_FALLBACK
                )
                
                if not resume_data:
                    st.error("Failed to parse resume")
                    st.stop()
                
                st.write(f"✅ Extracted {len(resume_data.get('skills', []))} skills")
                
                # Step 2: Build/Load Index
                st.write("🔍 Building semantic search index...")
                semantic_ranker = build_job_index(
                    st.session_state.gemini_client,
                    st.session_state.jobs_df,
                    config
                )
                
                # Step 3: Semantic Search
                st.write("🎯 Finding semantically similar jobs...")
                resume_text = resume_data.get('raw_text', '')
                search_results = semantic_ranker.search(resume_text, top_k=config.TOP_K_SEMANTIC)
                st.write(f"✅ Found {len(search_results)} candidate matches")
                
                # Step 4: Skill Matching
                st.write("🔧 Analyzing skill matches...")
                skill_matcher = SkillMatcher()
                
                results_data = []
                skill_analyses = []
                
                for job_idx, semantic_score in search_results[:config.TOP_K_FINAL]:
                    job = st.session_state.jobs_df.iloc[job_idx]
                    
                    # Skill analysis
                    job_skills = job.get('skills_list', [])
                    if isinstance(job_skills, str):
                        job_skills = eval(job_skills)
                    
                    skill_analysis = skill_matcher.calculate_skill_match(
                        resume_data.get('skills', []),
                        job_skills
                    )
                    skill_analyses.append(skill_analysis)
                    
                    # Calculate final score
                    final_score = (
                        semantic_score * config.SEMANTIC_WEIGHT * 100 +
                        skill_analysis['coverage_score'] * config.SKILL_WEIGHT * 100 +
                        50 * config.EXPERIENCE_WEIGHT  # Placeholder
                    )
                    
                    results_data.append({
                        'Job_ID': job['Job_ID'],
                        'Job Title': job['Job Title'],
                        'Company': job['Company'],
                        'Job Description': job['Job Description'],
                        'Min_Experience': job.get('Min_Experience', 0),
                        'Max_Experience': job.get('Max_Experience', 10),
                        'semantic_score': semantic_score,
                        'skill_coverage': skill_analysis['coverage_score'],
                        'final_score': final_score,
                        'rank': 0
                    })
                
                # Create results DataFrame
                results_df = pd.DataFrame(results_data)
                results_df = results_df.sort_values('final_score', ascending=False).reset_index(drop=True)
                results_df['rank'] = range(1, len(results_df) + 1)
                
                # Step 5: LLM Analysis
                st.write("🤖 Generating AI insights...")
                llm_analyst = LLMAnalystAPI(st.session_state.groq_client, config)
                
                top_jobs = results_df.head(5).to_dict('records')
                llm_analyses = llm_analyst.batch_analyze(
                    resume=resume_data,
                    ranked_jobs=top_jobs,
                    skill_analyses=skill_analyses[:5],
                    semantic_scores=results_df.head(5)['semantic_score'].tolist()
                )
                
                status.update(label="✅ Analysis complete!", state="complete", expanded=False)
            
            # Store results
            st.session_state.analysis_results = {
                'results_df': results_df,
                'llm_analyses': llm_analyses,
                'resume_data': resume_data
            }
            
            # Display results
            display_results(results_df, llm_analyses)
    
    else:
        st.info("👆 Upload a resume to get started")
        
        # Show sample
        with st.expander("💡 See Example Results"):
            st.markdown("Upload your resume to see personalized job matches with AI-powered insights!")
            st.image("https://img.icons8.com/fluency/96/resume.png", width=100)


if __name__ == "__main__":
    main()
