
import os
import json
import logging
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv
import traceback
import sys

load_dotenv()

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class IntelligenceEngine:
    def __init__(self):
        logger.info("=" * 60)
        logger.info("Initializing Intelligence Engine with Grok API (Fast Mode)")
        logger.info("=" * 60)
        
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        self.model_name = "llama-3.1-8b-instant"  # Working Groq model
        self.is_xai = False
        self.using_groq_fallback = False
        
        if not self.api_key:
            logger.error("❌ GROQ_API_KEY not found in environment!")
            return
        
        logger.info(f"✓ API Key found: {self.api_key[:10]}...{self.api_key[-10:]}")
        
        # Initialize Grok/xAI client
        try:
            if self.api_key.startswith("xai-"):
                logger.info("✓ Detected xAI Grok API Key")
                self.is_xai = True
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.x.ai/v1",
                )
                # Try different model name variations for xAI
                self.model_name = "grok-2-latest"
                logger.info(f"✓ Using xAI Grok model: {self.model_name}")
            else:
                logger.info("✓ Using Groq API")
                self.client = Groq(api_key=self.api_key)
                self.model_name = "llama-3.1-8b-instant"  # Verified working model
                logger.info(f"✓ Using Groq model: {self.model_name}")
                
            logger.info("✓ Client initialized successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to initialize client: {e}")
            logger.error(traceback.format_exc())
            self.client = None

        self.chunks = []

    def create_vector_store(self, chunks):
        """Skip embeddings - store chunks directly for fast access"""
        self.chunks = chunks
        logger.info(f"✓ Loaded {len(chunks)} chunks ({len(''.join(chunks))} chars total)")

    def analyze_document(self):
        """Direct Grok analysis - no embeddings, ultra-fast"""
        logger.info("=" * 60)
        logger.info("Starting Document Analysis")
        logger.info("=" * 60)
        
        if not self.chunks:
            logger.error("❌ No chunks available!")
            return self._get_emergency_mock()
        
        if not self.client:
            logger.error("❌ Client is not initialized!")
            return self._get_emergency_mock()
        
        # Combine chunks (use all for better context)
        context = "\n\n".join(self.chunks)
        logger.info(f"📄 Context length: {len(context)} characters")
        
        prompt = f"""You are a strategic business intelligence analyst. Analyze the following document carefully and extract insights.

DOCUMENT CONTENT:
{context}

TASK: Extract business intelligence from above document in JSON format.

RETURN ONLY JSON (no markdown, no code blocks, no extra text). Must be valid JSON.

Return exactly this structure with real analysis based on the document:
{{
  "executive_summary": [
    "First key finding from document",
    "Second key finding from document", 
    "Third key finding from document"
  ],
  "key_risks": [
    "First risk identified in document",
    "Second risk identified in document",
    "Third risk identified in document"
  ],
  "opportunities": [
    "First opportunity from document",
    "Second opportunity from document",
    "Third opportunity from document"
  ],
  "strategic_recommendations": [
    "First recommendation based on analysis",
    "Second recommendation based on analysis",
    "Third recommendation based on analysis"
  ]
}}

IMPORTANT: Analyze the ACTUAL document content above. Do NOT return generic text."""

        try:
            logger.info(f"🚀 Calling {self.model_name} API...")
            
            # Build request parameters
            api_params = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 2000,
            }
            
            logger.debug(f"API Params: {list(api_params.keys())}")
            response = None
            
            # Try initial model
            try:
                response = self.client.chat.completions.create(**api_params)
                logger.info("✓ API response received")
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Primary model failed: {error_msg[:100]}")
                
                # If xAI model fails, try alternatives
                if self.is_xai and ("not found" in error_msg.lower() or "model" in error_msg.lower()):
                    logger.info("⚠️  Trying alternative xAI models...")
                    for alt_model in ["grok-vision-beta", "grok-2-vision-beta", "grok-beta", "grok"]:
                        try:
                            logger.debug(f"Attempting: {alt_model}")
                            api_params["model"] = alt_model
                            response = self.client.chat.completions.create(**api_params)
                            self.model_name = alt_model
                            self.using_groq_fallback = False
                            logger.info(f"✅ Using {alt_model}")
                            break
                        except Exception as e2:
                            logger.debug(f"  {alt_model} failed: {str(e2)[:50]}")
                            continue
                
                # If still no response and using xAI, try Groq as fallback
                if response is None and self.is_xai:
                    logger.warning("⚠️  xAI models exhausted, falling back to Groq...")
                    try:
                        self.client = Groq(api_key=self.api_key.replace("xai-", ""))
                        self.model_name = "llama-3.1-8b-instant"
                        self.is_xai = False
                        self.using_groq_fallback = True
                        api_params["model"] = self.model_name
                        response = self.client.chat.completions.create(**api_params)
                        logger.info(f"✅ Using Groq fallback: {self.model_name}")
                    except Exception as e3:
                        logger.error(f"Groq fallback also failed: {e3}")
                
                if response is None:
                    raise e
            
            content = response.choices[0].message.content.strip()
            logger.info(f"Raw response length: {len(content)} characters")
            logger.debug(f"Raw response: {content[:300]}...")
            
            # Clean up response
            if content.startswith("```"):
                logger.info("📝 Cleaning JSON (removing code blocks)")
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            logger.info("🔍 Parsing JSON...")
            result = json.loads(content)
            logger.info("✅ Analysis completed successfully!")
            logger.info(f"📊 Results: {len(result.get('executive_summary', []))} summaries, {len(result.get('key_risks', []))} risks")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {e}")
            logger.error(f"Content that failed to parse: {content[:500]}")
            return self._parse_text_response(content)
        except Exception as e:
            logger.error(f"❌ API call failed: {e}")
            logger.error(traceback.format_exc())
            return self._get_emergency_mock()

    def _parse_text_response(self, text):
        """Fallback: parse text response into structured format"""
        logger.info("Using text fallback parser...")
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return {
            "executive_summary": lines[:3] if len(lines) > 0 else ["Unable to parse response"],
            "key_risks": lines[3:6] if len(lines) > 3 else [],
            "opportunities": lines[6:9] if len(lines) > 6 else [],
            "strategic_recommendations": lines[9:12] if len(lines) > 9 else []
        }

    def _get_emergency_mock(self):
        logger.warning("Returning emergency mock structure")
        return {
            "executive_summary": ["Analysis service currently unavailable.", "Please check your API configuration."],
            "key_risks": ["Service connection issue", "Rate limit or quota exceeded"],
            "opportunities": ["Configure local fallbacks", "Check cloud API status"],
            "strategic_recommendations": ["Re-run analysis in a few moments", "Verify document text extraction"]
        }

