import boto3
import json
import logging
import os
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentGenerator:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        # Use environment variable for model ID, fallback to Nova Lite if not set
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-micro-v1:0')
        
        # Document templates
        self.resume_template = """
        # {name}
        {contact_info}
        
        ## Professional Summary
        {summary}
        
        ## Skills
        {skills}
        
        ## Experience
        {experience}
        
        ## Education
        {education}
        
        ## Projects
        {projects}
        """
    
    def create_resume(self, personal_info: str, experience: str, skills: str) -> str:
        """Generate a personalized resume"""
        try:
            resume_content = self._generate_resume_content(personal_info, experience, skills)
            return self._format_resume(resume_content)
            
        except Exception as e:
            logger.error(f"Resume generation error: {e}")
            return f"Error generating resume: {str(e)}"
    
    def create_cover_letter(self, job_description: str, user_profile: Dict) -> str:
        """Generate a personalized cover letter"""
        try:
            cover_letter = self._generate_cover_letter_content(job_description, user_profile)
            return self._format_cover_letter(cover_letter)
            
        except Exception as e:
            logger.error(f"Cover letter generation error: {e}")
            return f"Error generating cover letter: {str(e)}"
    
    def create_linkedin_summary(self, user_profile: Dict) -> str:
        """Generate LinkedIn profile summary"""
        try:
            summary = self._generate_linkedin_summary(user_profile)
            return summary
            
        except Exception as e:
            logger.error(f"LinkedIn summary generation error: {e}")
            return f"Error generating LinkedIn summary: {str(e)}"
    
    def _generate_resume_content(self, personal_info: str, experience: str, skills: str) -> Dict:
        """Generate resume content using Bedrock"""
        prompt = f"""
        Create a professional resume based on this information:
        
        Personal Information: {personal_info}
        Experience: {experience}
        Skills: {skills}
        
        Generate content for each section:
        1. Professional Summary (3-4 sentences highlighting key strengths)
        2. Skills (organized by category: Technical, Soft Skills, Tools)
        3. Experience (formatted with achievements and metrics)
        4. Education (if mentioned)
        5. Notable Projects (if applicable)
        
        Make it ATS-friendly and professionally written. Use action verbs and quantify achievements where possible.
        
        Format the response as structured sections I can parse.
        """
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 1200,
                    "temperature": 0.3
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['output']['message']['content'][0]['text']
            
            # Parse the structured response
            return self._parse_resume_content(content, personal_info)
            
        except Exception as e:
            logger.error(f"Resume content generation error: {e}")
            return self._create_basic_resume_content(personal_info, experience, skills)
    
    def _parse_resume_content(self, content: str, personal_info: str) -> Dict:
        """Parse the generated resume content into sections"""
        sections = {
            'name': self._extract_name(personal_info),
            'contact_info': self._extract_contact_info(personal_info),
            'summary': '',
            'skills': '',
            'experience': '',
            'education': '',
            'projects': ''
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if 'summary' in line.lower():
                current_section = 'summary'
            elif 'skill' in line.lower():
                current_section = 'skills'
            elif 'experience' in line.lower():
                current_section = 'experience'
            elif 'education' in line.lower():
                current_section = 'education'
            elif 'project' in line.lower():
                current_section = 'projects'
            elif current_section and not line.startswith('#'):
                sections[current_section] += line + '\n'
        
        return sections
    
    def _extract_name(self, personal_info: str) -> str:
        """Extract name from personal information"""
        lines = personal_info.split('\n')
        for line in lines:
            if 'name' in line.lower() and ':' in line:
                return line.split(':')[1].strip()
        return "Your Name"
    
    def _extract_contact_info(self, personal_info: str) -> str:
        """Extract contact information"""
        contact_lines = []
        lines = personal_info.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['email', 'phone', 'linkedin', 'address']):
                contact_lines.append(line.strip())
        
        return '\n'.join(contact_lines) if contact_lines else "Contact Information"
    
    def _format_resume(self, content: Dict) -> str:
        """Format the resume with proper styling"""
        formatted = f"""# 📄 Professional Resume

## {content['name']}
{content['contact_info']}

---

## 🎯 Professional Summary
{content['summary']}

---

## 💪 Skills
{content['skills']}

---

## 💼 Professional Experience
{content['experience']}

---

## 🎓 Education
{content['education']}

---

## 🚀 Projects
{content['projects']}

---

*Resume generated by LaunchPad.AI on {datetime.now().strftime('%B %d, %Y')}*
"""
        return formatted
    
    def _generate_cover_letter_content(self, job_description: str, user_profile: Dict) -> str:
        """Generate cover letter content"""
        prompt = f"""
        Write a compelling cover letter for this job:
        
        Job Description: {job_description}
        
        Candidate Profile:
        - Skills: {user_profile.get('skills', '')}
        - Experience: {user_profile.get('experience', '')}
        - Achievements: {user_profile.get('achievements', '')}
        
        Structure:
        1. Opening paragraph: Hook and position interest
        2. Body paragraphs: Match qualifications to job requirements
        3. Closing: Call to action and next steps
        
        Make it professional, enthusiastic, and specific to the role.
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
            return response_body['output']['message']['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Cover letter generation error: {e}")
            return "Unable to generate cover letter at this time."
    
    def _format_cover_letter(self, content: str) -> str:
        """Format the cover letter"""
        formatted = f"""# 📝 Cover Letter

{content}

---

*Cover letter generated by LaunchPad.AI on {datetime.now().strftime('%B %d, %Y')}*

## 💡 Tips for Success:
- Customize the company name and specific role details
- Add specific examples from your experience
- Proofread for grammar and spelling
- Keep it to one page when printed
- Save as PDF for applications
"""
        return formatted
    
    def _generate_linkedin_summary(self, user_profile: Dict) -> str:
        """Generate LinkedIn profile summary"""
        prompt = f"""
        Create an engaging LinkedIn summary for:
        
        Skills: {user_profile.get('skills', '')}
        Experience: {user_profile.get('experience', '')}
        Goals: {user_profile.get('goals', '')}
        Industry: {user_profile.get('industry', '')}
        
        Requirements:
        - 2-3 paragraphs, conversational tone
        - Include relevant keywords for searchability
        - Highlight unique value proposition
        - End with a call to action
        - Be authentic and professional
        
        Write in first person and make it engaging.
        """
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 600,
                    "temperature": 0.5
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            summary = response_body['output']['message']['content'][0]['text']
            
            return f"""# 💼 LinkedIn Profile Summary

{summary}

---

*Summary generated by LaunchPad.AI on {datetime.now().strftime('%B %d, %Y')}*

## 📝 Optimization Tips:
- Add relevant keywords for your industry
- Include a professional headshot
- Keep it under 2,000 characters
- Update regularly as you grow
- Engage with your network's content
"""
            
        except Exception as e:
            logger.error(f"LinkedIn summary generation error: {e}")
            return "Unable to generate LinkedIn summary at this time."
    
    def _create_basic_resume_content(self, personal_info: str, experience: str, skills: str) -> Dict:
        """Create basic resume content as fallback"""
        return {
            'name': self._extract_name(personal_info),
            'contact_info': self._extract_contact_info(personal_info),
            'summary': "Motivated professional with strong skills and experience seeking new opportunities.",
            'skills': skills,
            'experience': experience,
            'education': "Education details to be added",
            'projects': "Notable projects to be highlighted"
        }
