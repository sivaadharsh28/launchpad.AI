import boto3
import json
import re
import logging
import os
from typing import Dict, List, Set
from collections import Counter

logger = logging.getLogger(__name__)

class SkillAnalyzer:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.sagemaker_client = boto3.client('sagemaker-runtime', region_name='us-east-1')
        # Use Nova inference profile instead of direct model ID
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-micro-v1:0')
        
        # Skill categories and keywords
        self.skill_categories = {
            'technical': ['python', 'java', 'javascript', 'sql', 'aws', 'machine learning', 'data science'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'creativity'],
            'industry': ['healthcare', 'finance', 'technology', 'education', 'retail', 'manufacturing'],
            'tools': ['excel', 'tableau', 'power bi', 'jira', 'git', 'docker', 'kubernetes']
        }
    
    def analyze(self, user_input: str, resume_text: str = "") -> str:
        """Analyze user skills and provide detailed assessment"""
        try:
            combined_text = f"{user_input}\n\n{resume_text}".strip()
            
            # Extract skills using NLP
            extracted_skills = self._extract_skills(combined_text)
            
            # Analyze skill gaps using Bedrock
            gap_analysis = self._analyze_skill_gaps(extracted_skills, user_input)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(extracted_skills, gap_analysis)
            
            # Format results
            return self._format_analysis_results(extracted_skills, gap_analysis, recommendations)
            
        except Exception as e:
            logger.error(f"Skill analysis error: {e}")
            return f"Error analyzing skills: {str(e)}"
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from text using keyword matching and NLP"""
        text_lower = text.lower()
        extracted = {category: [] for category in self.skill_categories}
        
        # Keyword-based extraction
        for category, keywords in self.skill_categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    extracted[category].append(keyword.title())
        
        # Use Bedrock for advanced skill extraction
        try:
            bedrock_skills = self._extract_skills_with_bedrock(text)
            for category, skills in bedrock_skills.items():
                if category in extracted:
                    extracted[category].extend(skills)
        except Exception as e:
            logger.warning(f"Bedrock skill extraction failed: {e}")
        
        # Remove duplicates
        for category in extracted:
            extracted[category] = list(set(extracted[category]))
        
        return extracted
    
    def _extract_skills_with_bedrock(self, text: str) -> Dict[str, List[str]]:
        """Use Bedrock to extract skills with better accuracy"""
        prompt = f"""
        Analyze the following text and extract skills in these categories:
        - Technical Skills (programming languages, frameworks, technologies)
        - Soft Skills (communication, leadership, etc.)
        - Industry Knowledge (domain expertise)
        - Tools & Software (applications, platforms)
        
        Text: {text}
        
        Return the skills in JSON format with categories as keys and lists of skills as values.
        """
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 500,
                    "temperature": 0.3
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['output']['message']['content'][0]['text']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                skills_data = json.loads(json_match.group())
                return {
                    'technical': skills_data.get('Technical Skills', []),
                    'soft_skills': skills_data.get('Soft Skills', []),
                    'industry': skills_data.get('Industry Knowledge', []),
                    'tools': skills_data.get('Tools & Software', [])
                }
        except Exception as e:
            logger.error(f"Bedrock skill extraction error: {e}")
        
        return {category: [] for category in self.skill_categories}
    
    def _analyze_skill_gaps(self, extracted_skills: Dict, user_goals: str) -> Dict:
        """Analyze skill gaps based on career goals"""
        prompt = f"""
        Based on these extracted skills and user goals, identify skill gaps and areas for improvement:
        
        Current Skills:
        - Technical: {', '.join(extracted_skills['technical'])}
        - Soft Skills: {', '.join(extracted_skills['soft_skills'])}
        - Industry: {', '.join(extracted_skills['industry'])}
        - Tools: {', '.join(extracted_skills['tools'])}
        
        User Goals: {user_goals}
        
        Provide:
        1. Missing critical skills for their goals
        2. Skills that need improvement
        3. Emerging skills they should consider
        4. Priority level for each gap (High/Medium/Low)
        
        Format as structured text.
        """
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 800,
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
            logger.error(f"Skill gap analysis error: {e}")
            return {"analysis": "Unable to analyze skill gaps at this time."}
    
    def _generate_recommendations(self, skills: Dict, gap_analysis: Dict) -> str:
        """Generate learning recommendations"""
        prompt = f"""
        Based on this skill analysis, provide specific learning recommendations:
        
        Current Skills: {skills}
        Gap Analysis: {gap_analysis.get('analysis', '')}
        
        Provide:
        1. Top 5 recommended courses/certifications
        2. Practical projects to build portfolio
        3. Timeline for skill development
        4. Free and paid learning resources
        
        Make recommendations specific and actionable.
        """
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 800,
                    "temperature": 0.5
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['output']['message']['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return "Unable to generate recommendations at this time."
    
    def _format_analysis_results(self, skills: Dict, gap_analysis: Dict, recommendations: str) -> str:
        """Format the complete analysis results"""
        result = "## 🎯 Skill Analysis Results\n\n"
        
        # Current Skills
        result += "### 💪 Your Current Skills\n\n"
        for category, skill_list in skills.items():
            if skill_list:
                result += f"**{category.replace('_', ' ').title()}:** {', '.join(skill_list)}\n\n"
        
        # Gap Analysis
        result += "### 📊 Skill Gap Analysis\n\n"
        result += gap_analysis.get('analysis', 'No gap analysis available.') + "\n\n"
        
        # Recommendations
        result += "### 🎓 Learning Recommendations\n\n"
        result += recommendations + "\n\n"
        
        # Action Items
        result += "### ✅ Next Steps\n\n"
        result += "1. Review the skill gaps and prioritize based on your career goals\n"
        result += "2. Start with high-priority skills that have immediate impact\n"
        result += "3. Create a learning schedule and track your progress\n"
        result += "4. Build portfolio projects to demonstrate new skills\n"
        result += "5. Update your resume and LinkedIn profile as you develop new skills\n"
        
        return result
