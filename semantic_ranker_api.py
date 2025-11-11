
import numpy as np
from typing import List, Tuple, Dict
import faiss
import pandas as pd


class SemanticRankerAPI:
    """Semantic ranking using Gemini API embeddings"""
    
    def __init__(self, embedding_client, config):
        self.embedding_client = embedding_client
        self.config = config
        self.index = None
        self.job_embeddings = None
        self.jobs_df = None
    
    def build_index(self, jobs_df: pd.DataFrame, text_column: str = 'Job Description'):
        """Build FAISS index from job descriptions"""
        
        self.jobs_df = jobs_df
        job_texts = jobs_df[text_column].fillna('').tolist()
        
        print(f"🔄 Generating embeddings for {len(job_texts)} jobs using Gemini API...")
        
        # Generate embeddings via API (batch processing)
        batch_size = self.config.BATCH_SIZE
        all_embeddings = []
        
        for i in range(0, len(job_texts), batch_size):
            batch = job_texts[i:i+batch_size]
            batch_embeddings = self.embedding_client.embed(batch)
            all_embeddings.extend(batch_embeddings)
            
            # Progress indicator
            progress = min(100, int((i + batch_size) / len(job_texts) * 100))
            if progress % 20 == 0:
                print(f"   Progress: {progress}%")
        
        self.job_embeddings = np.array(all_embeddings, dtype='float32')
        
        # Build FAISS index
        dimension = self.job_embeddings.shape[1]
        
        if len(job_texts) > 1000:
            # Use IVF for large datasets
            nlist = min(100, len(job_texts) // 10)
            quantizer = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
            self.index.train(self.job_embeddings)
        else:
            # Use flat index for small datasets
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(self.job_embeddings)
        print(f"✅ FAISS index built: {len(job_texts)} jobs indexed")
    
    def search(self, query_text: str, top_k: int = None) -> List[Tuple[int, float]]:
        """Search for top-K most similar jobs"""
        
        if top_k is None:
            top_k = self.config.TOP_K_SEMANTIC
        
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Generate query embedding
        print(f"🔍 Generating query embedding...")
        query_embedding = self.embedding_client.embed_query(query_text)
        query_array = np.array([query_embedding], dtype='float32')
        
        # Search using FAISS
        distances, indices = self.index.search(query_array, top_k)
        
        # Convert L2 distances to similarity scores (0-1 range)
        # Formula: similarity = 1 / (1 + distance)
        similarities = 1 / (1 + distances[0])
        
        # Return list of (job_index, similarity_score) tuples
        results = list(zip(indices[0].tolist(), similarities.tolist()))
        
        print(f"✅ Found top {len(results)} semantic matches")
        return results
    
    def get_ranked_jobs(self, query_text: str, top_k: int = None) -> pd.DataFrame:
        """Get ranked jobs as DataFrame with scores"""
        
        results = self.search(query_text, top_k)
        
        # Extract job indices and scores
        job_indices = [idx for idx, _ in results]
        scores = [score for _, score in results]
        
        # Get corresponding job data
        ranked_jobs = self.jobs_df.iloc[job_indices].copy()
        ranked_jobs['semantic_score'] = scores
        ranked_jobs['rank'] = range(1, len(ranked_jobs) + 1)
        
        return ranked_jobs.reset_index(drop=True)


class SkillMatcher:
    """Skill-based matching (unchanged from local version)"""
    
    def __init__(self):
        self.skill_synonyms = {
            'python': ['python', 'py', 'python3'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs'],
            'machine learning': ['ml', 'machine learning', 'machinelearning'],
            'deep learning': ['dl', 'deep learning', 'deeplearning', 'neural networks'],
            'react': ['react', 'reactjs', 'react.js'],
            'aws': ['aws', 'amazon web services']
        }
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        text_lower = text.lower()
        found_skills = set()
        
        for canonical, variations in self.skill_synonyms.items():
            for variant in variations:
                if variant in text_lower:
                    found_skills.add(canonical)
                    break
        
        return list(found_skills)
    
    def calculate_skill_match(self, resume_skills: List[str], 
                             job_skills: List[str]) -> Dict:
        """Calculate skill matching metrics"""
        
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        
        matched = resume_set & job_set
        missing = job_set - resume_set
        extra = resume_set - job_set
        
        coverage = len(matched) / len(job_set) if job_set else 0.0
        
        return {
            'matched_skills': list(matched),
            'missing_skills': list(missing),
            'extra_skills': list(extra),
            'match_count': len(matched),
            'total_required': len(job_set),
            'coverage_score': coverage
        }


class ExperienceMatcher:
    """Experience-based matching (unchanged from local version)"""
    
    def calculate_experience_fit(self, candidate_years: float, 
                                 min_years: float, 
                                 max_years: float) -> Dict:
        """Calculate experience fit score"""
        
        if min_years <= candidate_years <= max_years:
            fit_score = 1.0
            fit_category = "Perfect Fit"
        elif candidate_years < min_years:
            gap = min_years - candidate_years
            fit_score = max(0.0, 1.0 - (gap / 5))  # Penalize 20% per year under
            fit_category = "Under-Qualified"
        else:  # candidate_years > max_years
            excess = candidate_years - max_years
            fit_score = max(0.5, 1.0 - (excess / 10))  # Gentle penalty for overqualification
            fit_category = "Over-Qualified"
        
        return {
            'fit_score': fit_score,
            'fit_category': fit_category,
            'candidate_years': candidate_years,
            'required_min': min_years,
            'required_max': max_years
        }
