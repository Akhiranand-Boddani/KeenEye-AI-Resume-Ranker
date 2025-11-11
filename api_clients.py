import requests
import time
import re
import os
import warnings
from typing import List, Dict, Optional
import google.generativeai as genai
from io import BytesIO


# CORRECT:
class GroqClient:
    def __init__(self, api_key: str):
        if not api_key or api_key == "":
            raise ValueError("Groq API key is required")

        self.api_key = api_key
        self.client = None
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.3-70b-versatile"
        self.max_retries = 3

        # Try to import and initialize the official Groq client.
        try:
            from groq import Groq  # Import here
            try:
                # Primary attempt: construct client normally.
                self.client = Groq(api_key=api_key)
            except TypeError as e:
                # Known failure mode: some environments or older libs may pass unexpected kwargs like 'proxies'
                if 'proxies' in str(e).lower():
                    # Fall back to using the REST endpoint directly via requests.
                    warnings.warn(
                        "Groq client init failed due to unexpected 'proxies' kwarg. "
                        "Falling back to direct HTTP calls. Consider upgrading the 'groq' package."
                    )
                    self.client = None
                else:
                    # Unknown TypeError: re-raise to avoid hiding surprising failures
                    raise
            except Exception:
                # Any other exception initializing official client -> fall back
                self.client = None

        except Exception:
            # If import itself fails or any other import-time error occurs, fall back to REST
            self.client = None

    def generate(self, prompt: str, max_tokens: int = 1024,
                 temperature: float = 0.3) -> str:
        """Generate LLM response with retry logic.

        If the official Groq client could not be instantiated (client is None),
        we fallback to calling the Groq REST-compatible OpenAI endpoint directly.
        """
        if self.client is not None:
            # Use official client if available
            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are an expert HR analyst specializing in resume-job matching."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise Exception(f"Groq API (client) failed after {self.max_retries} attempts: {str(e)}")
        else:
            # Fallback: call REST endpoint similar to OpenAI chat completions
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert HR analyst specializing in resume-job matching."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            for attempt in range(self.max_retries):
                try:
                    resp = requests.post(url, headers=headers, json=body, timeout=30)
                    resp.raise_for_status()
                    data = resp.json()
                    # Try multiple possible response shapes but prefer choices[0].message.content
                    if isinstance(data, dict):
                        choices = data.get("choices", [])
                        if choices:
                            # OpenAI shape
                            choice = choices[0]
                            # handle chat-style response
                            message = choice.get("message")
                            if message and isinstance(message, dict):
                                return message.get("content", "")
                            # handle text-like response
                            text = choice.get("text")
                            if text:
                                return text
                    # If we didn't return above, attempt to synthesize a string
                    return str(data)
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise Exception(f"Groq REST API failed after {self.max_retries} attempts: {str(e)}")


class GeminiEmbeddingClient:
    """Google Gemini API client for embeddings"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        self.api_key = api_key
        self.model_name = "models/text-embedding-004"
        self.max_retries = 3
        self._configured = True
        self._configure_error = None

        # Defensive configure: some versions of google-generativeai may raise TypeError('proxies')
        try:
            genai.configure(api_key=api_key)
        except TypeError as e:
            msg = str(e).lower()
            if 'proxies' in msg or 'unexpected keyword' in msg:
                # Known incompatibility: mark as not configured and provide clear guidance.
                self._configured = False
                self._configure_error = str(e)
                warnings.warn(
                    "google.generativeai.configure raised a TypeError about 'proxies' or unexpected kwargs. "
                    "Embeddings will be unavailable via the python client. "
                    "Please upgrade google-generativeai to a newer version (or remove incompatible wrappers). "
                    f"Original error: {e}"
                )
            else:
                # Re-raise other TypeErrors
                raise
        except Exception as e:
            # Any other configure-time exception: mark as unavailable but keep message
            self._configured = False
            self._configure_error = str(e)
            warnings.warn(f"google.generativeai.configure failed: {e}")

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self._configured:
            raise Exception(
                "Gemini embeddings are unavailable because google.generativeai.configure failed. "
                f"Original error: {self._configure_error}. "
                "Fix: upgrade google-generativeai or ensure your environment does not inject unexpected kwargs like 'proxies'."
            )

        embeddings = []
        for text in texts:
            for attempt in range(self.max_retries):
                try:
                    result = genai.embed_content(
                        model=self.model_name,
                        content=text,
                        task_type="retrieval_document"
                    )
                    # genai.embed_content may return a mapping with 'embedding'
                    # or more complex nested shapes depending on version
                    if isinstance(result, dict) and 'embedding' in result:
                        embeddings.append(result['embedding'])
                    elif hasattr(result, 'embedding'):
                        embeddings.append(result.embedding)
                    else:
                        # Last resort: try to find the embedding in returned structure
                        emb = None
                        if isinstance(result, dict):
                            for v in result.values():
                                if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                                    emb = v
                                    break
                        if emb is None:
                            raise Exception("Unexpected embedding response shape")
                        embeddings.append(emb)
                    break

                except Exception as e:
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    # Fallback to zero vector to avoid crashing downstream, but warn loudly
                    fallback_dim = 768
                    embeddings.append([0.0] * fallback_dim)
                    print(f"⚠️ Embedding failed for text, using fallback zero-vector. Error: {str(e)[:200]}")

        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for search query"""
        if not self._configured:
            raise Exception(
                "Gemini query embedding is unavailable because google.generativeai.configure failed. "
                f"Original error: {self._configure_error}. Fix: upgrade google-generativeai or remove injected kwargs like 'proxies'."
            )

        for attempt in range(self.max_retries):
            try:
                result = genai.embed_content(
                    model=self.model_name,
                    content=query,
                    task_type="retrieval_query"
                )
                if isinstance(result, dict) and 'embedding' in result:
                    return result['embedding']
                elif hasattr(result, 'embedding'):
                    return result.embedding
                else:
                    # try to locate embedding in dict
                    if isinstance(result, dict):
                        for v in result.values():
                            if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                                return v
                    raise Exception("Unexpected embedding response shape")
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise Exception(f"Query embedding failed: {str(e)}")


class APILayerParserClient:
    """APILayer Resume Parser client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.apilayer.com/resume_parser/upload"
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    def parse_resume(self, file_content: bytes, filename: str) -> Dict:
        """Parse resume file and extract structured data"""

        if len(file_content) > self.max_file_size:
            raise ValueError(f"File too large: {len(file_content)} bytes (max 10MB)")

        try:
            # APILayer expects multipart/form-data with proper headers
            headers = {
                'apikey': self.api_key
            }

            files = {
                'file': (filename, file_content, self._get_mime_type(filename))
            }

            response = requests.post(
                self.endpoint,
                headers=headers,
                files=files,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Standardize output format
            return {
                'raw_text': data.get('raw_text', '') or data.get('text', ''),
                'skills': data.get('skills', []),
                'experience_years': self._extract_years(data.get('experience', [])),
                'education': data.get('education', []),
                'name': data.get('name', 'Unknown'),
                'email': data.get('email', ''),
                'phone': data.get('phone', '')
            }

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                raise Exception("APILayer rate limit exceeded (100/month). Falling back to local parser.")
            elif e.response is not None and e.response.status_code == 400:
                # Try to get error details
                try:
                    error_detail = e.response.json()
                    raise Exception(f"APILayer Bad Request: {error_detail}")
                except:
                    raise Exception(f"APILayer Bad Request - check file format and API key")
            raise Exception(f"Resume parsing failed: {str(e)}")

        except Exception as e:
            raise Exception(f"Resume parsing error: {str(e)}")

    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        ext = filename.lower().split('.')[-1]
        mime_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'txt': 'text/plain'
        }
        return mime_types.get(ext, 'application/octet-stream')

    def _extract_years(self, experience_list):
        """Extract total years from experience list"""
        if not experience_list:
            return 0.0

        total = 0
        for exp in experience_list:
            if isinstance(exp, dict):
                years = exp.get('years', 0)
                total += float(years) if years else 0

        return total


class LocalResumeParser:
    """Fallback parser using PDFMiner + regex"""

    def parse_resume(self, file_content: bytes, filename: str) -> Dict:
        """Basic local parsing as fallback"""

        # Extract text from file
        if filename.lower().endswith('.pdf'):
            text = self._extract_pdf(file_content)
        elif filename.lower().endswith(('.docx', '.doc')):
            text = self._extract_docx(file_content)
        else:
            text = file_content.decode('utf-8', errors='ignore')

        # Extract basic info
        return {
            'raw_text': text,
            'skills': self._extract_skills(text),
            'experience_years': self._extract_experience(text),
            'education': self._extract_education(text),
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text)
        }

    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            from pdfminer.high_level import extract_text
            return extract_text(BytesIO(content))
        except Exception as e:
            print(f"PDF extraction failed: {e}")
            return ""

    def _extract_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            import docx2txt
            # docx2txt supports file paths and file-like objects in some versions;
            # try both approaches for robustness.
            try:
                return docx2txt.process(BytesIO(content))
            except Exception:
                # As a fallback, write to a temp file and process
                import tempfile
                with tempfile.NamedTemporaryFile(delete=True, suffix=".docx") as tmp:
                    tmp.write(content)
                    tmp.flush()
                    return docx2txt.process(tmp.name)
        except Exception as e:
            print(f"DOCX extraction failed: {e}")
            return ""

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using keyword matching"""
        skill_keywords = [
            'python', 'java', 'javascript', 'sql', 'react', 'angular', 'vue',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'tensorflow',
            'pytorch', 'scikit-learn', 'pandas', 'numpy', 'spark', 'hadoop',
            'git', 'linux', 'rest api', 'microservices', 'agile', 'scrum'
        ]
        text_lower = text.lower()
        found_skills = []

        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())

        return found_skills

    def _extract_experience(self, text: str) -> float:
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s*:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs\s+(?:of\s+)?experience'
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1))

        return 0.0

    def _extract_education(self, text: str) -> List[str]:
        """Extract education degrees"""
        degrees = []
        degree_keywords = {
            'bachelor': "Bachelor's Degree",
            'master': "Master's Degree",
            'phd': 'PhD',
            'mba': 'MBA',
            'b.s.': "Bachelor's Degree",
            'm.s.': "Master's Degree",
            'b.tech': "Bachelor's Degree",
            'm.tech': "Master's Degree"
        }

        text_lower = text.lower()
        for keyword, degree in degree_keywords.items():
            if keyword in text_lower and degree not in degrees:
                degrees.append(degree)

        return degrees

    def _extract_name(self, text: str) -> str:
        """Extract candidate name (first line heuristic)"""
        lines = text.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            if len(first_line) < 50 and not any(c.isdigit() for c in first_line):
                return first_line
        return "Unknown"

    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10}'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return ""
