import os
import json
import boto3
import logging
from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LaunchPadAgent:
    def __init__(self):
        # Initialize AWS client with explicit credentials
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'eu-west-3'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Use inference profile ARN for Nova models
        self.model_configs = {
            'nova-micro': {
                'model_id': 'us.amazon.nova-micro-v1:0',  # Inference profile format
                'body_format': 'nova'
            }
        }
        
        # Primary and fallback models
        self.primary_model = os.getenv('BEDROCK_MODEL_ID', 'nova-micro')
        self.fallback_models = ['claude-haiku', 'claude-sonnet']
        
        self.max_tokens = int(os.getenv('MAX_TOKENS', 1000))
        self.temperature = float(os.getenv('TEMPERATURE', 0.7))
    
        self.system_prompt = """
        You are LaunchPad.AI, an expert AI career copilot. Your role is to help users navigate their career journey from dream to job offer.

        Core capabilities:
        - Analyze skills and identify gaps
        - Suggest personalized career paths
        - Recommend learning resources
        - Generate resumes and cover letters
        - Find job opportunities
        - Provide interview preparation

        Always be:
        - Encouraging and supportive
        - Data-driven and practical
        - Personalized to user's situation
        - Action-oriented with clear next steps

        Use reasoning to understand user goals, assess their current situation, and provide tailored guidance.
        """
    
    def process_message(self, message: str, history: List = None) -> str:
        """Process user message with reasoning and context"""
        try:
            # Build conversation context
            conversation_context = self._build_context(message, history or [])
            
            # Use Bedrock Claude for reasoning
            response = self._invoke_claude(conversation_context)
            
            # Extract and format response
            formatted_response = self._format_response(response)
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Agent processing error: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    
    def _build_context(self, message: str, history: List) -> str:
        """Build conversation context with history"""
        context = f"{self.system_prompt}\n\n"
        
        # Add conversation history
        if history:
            context += "Previous conversation:\n"
            for user_msg, agent_msg in history[-3:]:  # Last 3 exchanges
                context += f"User: {user_msg}\n"
                context += f"Assistant: {agent_msg}\n\n"
        
        # Add current message
        context += f"Current user message: {message}\n\n"
        context += "Provide a helpful, personalized response as LaunchPad.AI:"
        
        return context
    
    def _invoke_claude(self, prompt: str) -> str:
        """Invoke AI model via Bedrock with fallback support"""
        models_to_try = [self.primary_model] + self.fallback_models
        
        for model_name in models_to_try:
            try:
                if model_name not in self.model_configs:
                    continue
                    
                config = self.model_configs[model_name]
                model_id = config['model_id']
                body_format = config['body_format']
                
                logger.info(f"Attempting to invoke model: {model_id}")
                
                if body_format == 'nova':
                    body = {
                        "messages": [
                            {
                                "role": "user",
                                "content": [{"text": prompt}]
                            }
                        ],
                        "inferenceConfig": {
                            "maxTokens": self.max_tokens,
                            "temperature": self.temperature
                        }
                    }
                    
                    response = self.bedrock_client.invoke_model(
                        modelId=model_id,
                        body=json.dumps(body),
                        contentType="application/json",
                        accept="application/json"
                    )
                    
                    response_body = json.loads(response['body'].read())
                    return response_body['output']['message']['content'][0]['text']
                    
            except Exception as e:
                logger.error(f"Model invocation error for {model_name}: {e}")
                if model_name == models_to_try[-1]:  # Last model failed
                    raise e
                continue
        
        raise Exception("All models failed to respond")
    
    def _format_response(self, response: str) -> str:
        """Format the AI response for better readability"""
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        # Clean up the response
        formatted = response.strip()
        
        # Add helpful formatting
        if "steps" in formatted.lower() or "recommendations" in formatted.lower():
            formatted = formatted.replace("1.", "\n1.")
            formatted = formatted.replace("2.", "\n2.")
            formatted = formatted.replace("3.", "\n3.")
        
        return formatted
    
    def reason_about_career_path(self, user_profile: Dict) -> Dict:
        """Use reasoning to suggest career paths"""
        reasoning_prompt = f"""
        Analyze this user profile and reason about optimal career paths:
        
        Skills: {user_profile.get('skills', '')}
        Interests: {user_profile.get('interests', '')}
        Experience: {user_profile.get('experience', '')}
        Goals: {user_profile.get('goals', '')}
        
        Provide reasoning for 3 career path suggestions with:
        1. Why this path fits their profile
        2. Required skill development
        3. Timeline and milestones
        4. Potential challenges and solutions
        """
        
        try:
            response = self._invoke_claude(reasoning_prompt)
            return {"reasoning": response, "paths": self._extract_paths(response)}
        except Exception as e:
            logger.error(f"Career reasoning error: {e}")
            return {"error": str(e)}
    
    def _extract_paths(self, response: str) -> List[Dict]:
        """Extract structured career paths from reasoning response"""
        # Simple extraction - in production, use more sophisticated parsing
        paths = []
        lines = response.split('\n')
        
        current_path = {}
        for line in lines:
            if "path" in line.lower() and ":" in line:
                if current_path:
                    paths.append(current_path)
                current_path = {"title": line.split(":")[-1].strip()}
            elif current_path and line.strip():
                if "skills" in line.lower():
                    current_path["required_skills"] = line
                elif "timeline" in line.lower():
                    current_path["timeline"] = line
        
        if current_path:
            paths.append(current_path)
        
        return paths
