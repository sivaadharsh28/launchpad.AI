import boto3
import json
import logging
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CareerPlanner:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        # Use environment variable for model ID, fallback to Nova Micro if not set
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-micro-v1:0')
        
        # Career pathway templates
        self.career_paths = {
            'technology': {
                'software_engineer': ['Junior Developer', 'Software Engineer', 'Senior Engineer', 'Tech Lead', 'Engineering Manager'],
                'data_scientist': ['Data Analyst', 'Data Scientist', 'Senior Data Scientist', 'Principal Data Scientist', 'Chief Data Officer'],
                'product_manager': ['Associate PM', 'Product Manager', 'Senior PM', 'Director of Product', 'VP of Product']
            },
            'business': {
                'consultant': ['Analyst', 'Consultant', 'Senior Consultant', 'Manager', 'Partner'],
                'marketing': ['Marketing Coordinator', 'Marketing Manager', 'Senior Manager', 'Director', 'VP Marketing'],
                'finance': ['Financial Analyst', 'Senior Analyst', 'Finance Manager', 'Finance Director', 'CFO']
            }
        }
    
    def suggest_paths(self, skills: str, interests: str, experience: str) -> str:
        """Generate personalized career path suggestions"""
        try:
            # Analyze user profile
            profile_analysis = self._analyze_user_profile(skills, interests, experience)
            
            # Generate career suggestions
            career_suggestions = self._generate_career_suggestions(profile_analysis)
            
            # Create detailed roadmaps
            roadmaps = self._create_career_roadmaps(career_suggestions, skills, experience)
            
            # Format results
            return self._format_career_suggestions(career_suggestions, roadmaps)
            
        except Exception as e:
            logger.error(f"Career planning error: {e}")
            return f"Error generating career suggestions: {str(e)}"
    
    def _analyze_user_profile(self, skills: str, interests: str, experience: str) -> Dict:
        """Analyze user profile to understand career preferences"""
        prompt = f"""
        Analyze this user profile for career planning:
        
        Skills: {skills}
        Interests: {interests}
        Experience Level: {experience}
        
        Provide analysis in these areas:
        1. Strengths and unique value proposition
        2. Industry alignment based on interests
        3. Career stage and progression potential
        4. Growth areas and development needs
        5. Personality and work style indicators
        
        Be specific and actionable in your analysis.
        """
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.4
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return {"analysis": response_body['output']['message']['content'][0]['text']}
            
        except Exception as e:
            logger.error(f"Profile analysis error: {e}")
            return {"analysis": "Unable to analyze profile at this time."}
    
    def _generate_career_suggestions(self, profile_analysis: Dict) -> List[Dict]:
        """Generate specific career path suggestions"""
        prompt = f"""
        Based on this profile analysis, suggest 3-5 specific career paths:
        
        Profile Analysis: {profile_analysis.get('analysis', '')}
        
        For each career path, provide:
        1. Job title/role name
        2. Industry and company types
        3. Why it's a good fit (2-3 reasons)
        4. Salary range expectations
        5. Growth potential and trajectory
        6. Key requirements and qualifications
        7. Timeline to reach this role
        
        Make suggestions realistic and achievable while being aspirational.
        Format as structured text with clear sections for each career path.
        """
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 1200,
                    "temperature": 0.5
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            suggestions_text = response_body['output']['message']['content'][0]['text']
            
            # Parse suggestions (simplified - in production, use more sophisticated parsing)
            suggestions = self._parse_career_suggestions(suggestions_text)
            return suggestions
            
        except Exception as e:
            logger.error(f"Career suggestions error: {e}")
            return [{"title": "Error", "description": "Unable to generate suggestions."}]
    
    def _parse_career_suggestions(self, text: str) -> List[Dict]:
        """Parse career suggestions from text response"""
        suggestions = []
        lines = text.split('\n')
        current_suggestion = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_suggestion:
                    suggestions.append(current_suggestion)
                    current_suggestion = {}
                continue
            
            if any(keyword in line.lower() for keyword in ['path', 'career', 'role']) and ':' in line:
                current_suggestion['title'] = line.split(':')[-1].strip()
            elif 'industry' in line.lower():
                current_suggestion['industry'] = line
            elif 'fit' in line.lower() or 'why' in line.lower():
                current_suggestion['fit_reason'] = line
            elif 'salary' in line.lower():
                current_suggestion['salary'] = line
            elif 'timeline' in line.lower():
                current_suggestion['timeline'] = line
        
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions if suggestions else [{"title": "Custom Career Path", "description": text}]
    
    def _create_career_roadmaps(self, suggestions: List[Dict], skills: str, experience: str) -> Dict:
        """Create detailed roadmaps for career suggestions"""
        roadmaps = {}
        
        for i, suggestion in enumerate(suggestions[:3]):  # Top 3 suggestions
            title = suggestion.get('title', f'Career Path {i+1}')
            
            prompt = f"""
            Create a detailed 12-month career roadmap for: {title}
            
            Current Skills: {skills}
            Experience Level: {experience}
            Career Goal: {suggestion.get('description', title)}
            
            Provide a month-by-month plan including:
            - Skills to develop each quarter
            - Certifications or courses to complete
            - Networking and professional development activities
            - Portfolio projects or experience to gain
            - Job search and application timeline
            - Milestones and success metrics
            
            Make it specific and actionable.
            """
            
            try:
                body = {
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 1000,
                        "temperature": 0.4
                    }
                }
                
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body)
                )
                
                response_body = json.loads(response['body'].read())
                roadmaps[title] = response_body['output']['message']['content'][0]['text']
                
            except Exception as e:
                logger.error(f"Roadmap creation error: {e}")
                roadmaps[title] = "Roadmap temporarily unavailable."
        
        return roadmaps
    
    def _format_career_suggestions(self, suggestions: List[Dict], roadmaps: Dict) -> str:
        """Format career suggestions and roadmaps"""
        result = "## 🚀 Personalized Career Path Suggestions\n\n"
        
        for i, suggestion in enumerate(suggestions[:3], 1):
            title = suggestion.get('title', f'Career Path {i}')
            result += f"### {i}. {title}\n\n"
            
            # Suggestion details
            for key, value in suggestion.items():
                if key != 'title' and value:
                    result += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
            
            # Roadmap
            if title in roadmaps:
                result += f"#### 📋 12-Month Roadmap for {title}\n\n"
                result += roadmaps[title] + "\n\n"
            
            result += "---\n\n"
        
        # Additional guidance
        result += "## 💡 Next Steps\n\n"
        result += "1. **Choose Your Path**: Review the suggestions and select the one that resonates most with your goals\n"
        result += "2. **Start Learning**: Begin with the first quarter's skill development recommendations\n"
        result += "3. **Build Your Network**: Connect with professionals in your chosen field\n"
        result += "4. **Create a Portfolio**: Start working on projects that demonstrate your growing skills\n"
        result += "5. **Track Progress**: Set monthly check-ins to review your progress and adjust the plan\n\n"
        
        result += "Remember: Career paths are flexible. You can pivot and adjust as you learn and grow! 🌟"
        
        return result
