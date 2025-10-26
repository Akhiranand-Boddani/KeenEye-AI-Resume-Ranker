"""
KeenEye v2.0 - API-Based LLM Analyst
Uses Groq API for deep resume-job analysis
Author: Project Agent
Date: October 26, 2025
"""

import json
import re
from typing import Dict, List


class LLMAnalystAPI:
    """LLM-powered candidate analysis using Groq API"""
    
    def __init__(self, llm_client, config):
        self.llm_client = llm_client
        self.config = config
    
    def analyze_match(self, resume: Dict, job: Dict, 
                     skill_analysis: Dict, semantic_score: float,
                     experience_analysis: Dict = None) -> Dict:
        """Generate comprehensive match analysis"""
        
        # Build full-context prompt
        prompt = self._build_prompt(resume, job, skill_analysis, 
                                   semantic_score, experience_analysis)
        
        # Call LLM API
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=self.config.LLM_MAX_TOKENS,
                temperature=self.config.LLM_TEMPERATURE
            )
            
            # Parse JSON response
            analysis = self._parse_response(response, skill_analysis, semantic_score)
            
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}")
            # Fallback to rule-based analysis
            analysis = self._generate_fallback_analysis(
                skill_analysis, semantic_score, experience_analysis
            )
        
        return analysis
    
    def _build_prompt(self, resume: Dict, job: Dict, 
                     skill_analysis: Dict, semantic_score: float,
                     experience_analysis: Dict = None) -> str:
        """Build comprehensive prompt with full context"""
        
        # Extract job details
        job_title = job.get('Job Title', 'N/A')
        company = job.get('Company', 'N/A')
        job_desc = job.get('Job Description', 'N/A')[:1500]
        required_skills = ', '.join(job.get('skills_list', [])[:15])
        min_exp = job.get('Min_Experience', 0)
        max_exp = job.get('Max_Experience', 10)
        
        # Extract resume details
        resume_text = resume.get('raw_text', '')[:1500]
        candidate_name = resume.get('name', 'Candidate')
        candidate_skills = ', '.join(resume.get('skills', [])[:10])
        candidate_exp = resume.get('experience_years', 0)
        
        # Extract analysis details
        matched_skills = ', '.join(skill_analysis.get('matched_skills', [])[:10])
        missing_skills = ', '.join(skill_analysis.get('missing_skills', [])[:5])
        skill_coverage = skill_analysis.get('coverage_score', 0)
        
        exp_fit = "N/A"
        if experience_analysis:
            exp_fit = experience_analysis.get('fit_category', 'N/A')
        
        prompt = f"""You are an expert HR analyst. Analyze this candidate-job match comprehensively.

# JOB DETAILS
**Title:** {job_title}
**Company:** {company}
**Required Experience:** {min_exp}-{max_exp} years
**Required Skills:** {required_skills}

**Description:**
{job_desc}

# CANDIDATE PROFILE
**Name:** {candidate_name}
**Experience:** {candidate_exp} years
**Skills:** {candidate_skills}

**Resume Summary:**
{resume_text}

# PRELIMINARY ANALYSIS
- **Semantic Similarity:** {semantic_score:.3f} (0-1 scale)
- **Skills Matched:** {skill_analysis.get('match_count', 0)}/{skill_analysis.get('total_required', 0)}
- **Skill Coverage:** {skill_coverage:.1%}
- **Matched Skills:** {matched_skills or 'None'}
- **Missing Skills:** {missing_skills or 'None'}
- **Experience Fit:** {exp_fit}

# TASK
Provide a comprehensive analysis in JSON format with the following structure:

{{
  "match_score": <integer 0-100>,
  "strengths": [
    {{"point": "<strength description>", "evidence": "<specific evidence from resume>"}},
    {{"point": "<strength description>", "evidence": "<specific evidence from resume>"}}
  ],
  "weaknesses": [
    {{"point": "<weakness description>", "mitigation": "<how to address this>"}},
    {{"point": "<weakness description>", "mitigation": "<how to address this>"}}
  ],
  "recommendation": {{
    "decision": "<yes|maybe|no>",
    "reasoning": "<detailed reasoning for decision>",
    "confidence": "<high|medium|low>"
  }},
  "key_insights": [
    "<insight 1>",
    "<insight 2>"
  ]
}}

**IMPORTANT:** Return ONLY the JSON object, no additional text."""

        return prompt
    
    def _parse_response(self, response: str, skill_analysis: Dict, 
                       semantic_score: float) -> Dict:
        """Parse LLM JSON response with fallback"""
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                
                # Validate required fields
                if 'match_score' in parsed and 'strengths' in parsed:
                    return parsed
        
        except Exception as e:
            print(f"⚠️ JSON parsing failed: {e}")
        
        # Fallback to rule-based
        return self._generate_fallback_analysis(skill_analysis, semantic_score)
    
    def _generate_fallback_analysis(self, skill_analysis: Dict, 
                                   semantic_score: float,
                                   experience_analysis: Dict = None) -> Dict:
        """Generate rule-based analysis when LLM fails"""
        
        # Calculate match score
        skill_score = skill_analysis.get('coverage_score', 0) * 100
        semantic_component = semantic_score * 100
        match_score = int((skill_score * 0.6) + (semantic_component * 0.4))
        
        # Determine strengths
        strengths = []
        matched_skills = skill_analysis.get('matched_skills', [])
        if matched_skills:
            strengths.append({
                'point': 'Strong technical skill alignment',
                'evidence': f"Matched {len(matched_skills)} key skills: {', '.join(matched_skills[:3])}"
            })
        
        if semantic_score > 0.7:
            strengths.append({
                'point': 'Excellent semantic match',
                'evidence': f'High similarity score of {semantic_score:.2f} indicates strong relevance'
            })
        
        # Determine weaknesses
        weaknesses = []
        missing_skills = skill_analysis.get('missing_skills', [])
        if missing_skills:
            weaknesses.append({
                'point': 'Some skill gaps identified',
                'mitigation': f"Consider training in: {', '.join(missing_skills[:3])}"
            })
        
        if semantic_score < 0.5:
            weaknesses.append({
                'point': 'Lower semantic alignment',
                'mitigation': 'Review job description carefully to ensure fit'
            })
        
        # Determine recommendation
        if match_score >= 75:
            decision = 'yes'
            reasoning = 'Strong match with excellent skill coverage and alignment'
            confidence = 'high'
        elif match_score >= 50:
            decision = 'maybe'
            reasoning = 'Moderate match with some gaps that could be addressed'
            confidence = 'medium'
        else:
            decision = 'no'
            reasoning = 'Limited match with significant skill gaps'
            confidence = 'medium'
        
        return {
            'match_score': match_score,
            'strengths': strengths if strengths else [{'point': 'Basic qualifications met', 'evidence': 'Resume contains relevant keywords'}],
            'weaknesses': weaknesses if weaknesses else [{'point': 'Further review needed', 'mitigation': 'Detailed interview recommended'}],
            'recommendation': {
                'decision': decision,
                'reasoning': reasoning,
                'confidence': confidence
            },
            'key_insights': [
                f"Skill coverage: {skill_analysis.get('coverage_score', 0):.0%}",
                f"Semantic similarity: {semantic_score:.2f}"
            ]
        }
    
    def batch_analyze(self, resume: Dict, ranked_jobs: List[Dict], 
                     skill_analyses: List[Dict], 
                     semantic_scores: List[float]) -> List[Dict]:
        """Analyze multiple job matches in batch"""
        
        results = []
        
        for i, (job, skill_analysis, semantic_score) in enumerate(
            zip(ranked_jobs, skill_analyses, semantic_scores)
        ):
            print(f"🤖 Analyzing job {i+1}/{len(ranked_jobs)}: {job.get('Job Title', 'Unknown')}")
            
            analysis = self.analyze_match(
                resume=resume,
                job=job,
                skill_analysis=skill_analysis,
                semantic_score=semantic_score
            )
            
            # Add job info to analysis
            analysis['job_title'] = job.get('Job Title', 'Unknown')
            analysis['company'] = job.get('Company', 'Unknown')
            analysis['job_id'] = job.get('Job_ID', i)
            
            results.append(analysis)
        
        return results