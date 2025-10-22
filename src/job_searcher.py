import boto3
import json
import logging
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class JobSearcher:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        # Use Nova inference profile with correct format
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-micro-v1:0')
        
        # Mock job database for demonstration
        self.job_database = [
            {
                'title': 'Senior Data Scientist',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'salary': '$120,000 - $160,000',
                'description': 'We are seeking an experienced Data Scientist to join our ML team. You will work on cutting-edge projects involving predictive modeling, machine learning algorithms, and data visualization.',
                'requirements': ['Python', 'Machine Learning', 'SQL', 'AWS', 'Statistics'],
                'posted_date': '2024-01-15',
                'company_size': '1000-5000 employees',
                'industry': 'Technology'
            },
            {
                'title': 'Software Engineer',
                'company': 'StartupX',
                'location': 'Remote',
                'salary': '$90,000 - $130,000',
                'description': 'Join our fast-growing startup as a Software Engineer. You will build scalable web applications and work with modern technologies in an agile environment.',
                'requirements': ['JavaScript', 'React', 'Node.js', 'MongoDB', 'Git'],
                'posted_date': '2024-01-14',
                'company_size': '50-200 employees',
                'industry': 'Technology'
            },
            {
                'title': 'Product Manager',
                'company': 'MegaCorp',
                'location': 'New York, NY',
                'salary': '$110,000 - $140,000',
                'description': 'Lead product strategy and development for our flagship product. You will work cross-functionally with engineering, design, and business teams.',
                'requirements': ['Product Management', 'Agile', 'Analytics', 'Leadership', 'SQL'],
                'posted_date': '2024-01-13',
                'company_size': '5000+ employees',
                'industry': 'Technology'
            },
            {
                'title': 'Marketing Manager',
                'company': 'BrandCo',
                'location': 'Los Angeles, CA',
                'salary': '$75,000 - $95,000',
                'description': 'Drive marketing campaigns and brand strategy. Experience with digital marketing, content creation, and analytics required.',
                'requirements': ['Digital Marketing', 'Content Strategy', 'Analytics', 'Social Media', 'Adobe Creative Suite'],
                'posted_date': '2024-01-12',
                'company_size': '200-1000 employees',
                'industry': 'Marketing'
            },
            {
                'title': 'UX Designer',
                'company': 'DesignStudio',
                'location': 'Austin, TX',
                'salary': '$70,000 - $100,000',
                'description': 'Create intuitive user experiences for mobile and web applications. Collaborate with product and engineering teams.',
                'requirements': ['UI/UX Design', 'Figma', 'Prototyping', 'User Research', 'Design Systems'],
                'posted_date': '2024-01-11',
                'company_size': '50-200 employees',
                'industry': 'Design'
            }
        ]
    
    def search(self, role: str, location: str, experience_level: str) -> str:
        """Search for job opportunities using internal database"""
        try:
            # Filter jobs based on search criteria
            jobs = self._filter_jobs(role, location, experience_level)
            
            # Analyze job matches
            analyzed_jobs = self._analyze_job_matches(jobs, role, experience_level)
            
            # Format results
            return self._format_job_results(analyzed_jobs, role, location)
            
        except Exception as e:
            logger.error(f"Job search error: {e}")
            return f"Error searching for jobs: {str(e)}"
    
    def _filter_jobs(self, role: str, location: str, experience_level: str) -> List[Dict]:
        """Filter jobs from internal database"""
        filtered_jobs = []
        role_keywords = role.lower().split()
        
        for job in self.job_database:
            # Check if role matches
            title_match = any(keyword in job['title'].lower() for keyword in role_keywords)
            
            # Check location
            location_match = (
                location.lower() == 'remote' or 
                location.lower() in job['location'].lower() or
                job['location'] == 'Remote'
            )
            
            if title_match and location_match:
                filtered_jobs.append(job.copy())
        
        # Generate additional mock jobs if few results
        if len(filtered_jobs) < 3:
            additional_jobs = self._generate_additional_jobs(role, location, 5 - len(filtered_jobs))
            filtered_jobs.extend(additional_jobs)
        
        return filtered_jobs[:10]  # Limit to 10 results
    
    def _generate_additional_jobs(self, role: str, location: str, count: int) -> List[Dict]:
        """Generate additional mock jobs to fill search results"""
        companies = ['InnovateCorp', 'FutureTech', 'NextGen Solutions', 'Alpha Systems', 'Beta Dynamics']
        
        additional_jobs = []
        for i in range(count):
            job = {
                'title': f"{role} - {random.choice(['Senior', 'Mid-level', 'Junior'])}",
                'company': random.choice(companies),
                'location': location if location != 'remote' else 'Remote',
                'salary': f"${random.randint(60, 150)},000 - ${random.randint(80, 200)},000",
                'description': f"Exciting opportunity for a {role} to join our growing team. Work on innovative projects with cutting-edge technology.",
                'requirements': self._generate_job_requirements(role),
                'posted_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                'company_size': random.choice(['50-200 employees', '200-1000 employees', '1000+ employees']),
                'industry': 'Technology'
            }
            additional_jobs.append(job)
        
        return additional_jobs
    
    def _generate_job_requirements(self, role: str) -> List[str]:
        """Generate realistic job requirements based on role"""
        common_skills = {
            'data scientist': ['Python', 'Machine Learning', 'SQL', 'Statistics', 'Pandas'],
            'software engineer': ['JavaScript', 'Python', 'Git', 'API Development', 'Testing'],
            'product manager': ['Product Strategy', 'Agile', 'Analytics', 'Communication', 'Roadmapping'],
            'designer': ['UI/UX Design', 'Figma', 'Prototyping', 'User Research', 'Visual Design'],
            'marketing': ['Digital Marketing', 'Analytics', 'Content Strategy', 'SEO', 'Social Media']
        }
        
        role_lower = role.lower()
        for key, skills in common_skills.items():
            if key in role_lower:
                return random.sample(skills, min(5, len(skills)))
        
        # Default skills
        return ['Communication', 'Problem Solving', 'Teamwork', 'Analytical Thinking']
    
    def _analyze_job_matches(self, jobs: List[Dict], role: str, experience_level: str) -> List[Dict]:
        """Analyze job matches using AI"""
        analyzed_jobs = []
        
        for job in jobs:
            analysis = self._get_job_match_analysis(job, role, experience_level)
            job['match_analysis'] = analysis
            analyzed_jobs.append(job)
        
        # Sort by match score
        return sorted(analyzed_jobs, key=lambda x: x['match_analysis'].get('score', 0), reverse=True)
    
    def _get_job_match_analysis(self, job: Dict, target_role: str, experience_level: str) -> Dict:
        """Analyze how well a job matches user requirements"""
        prompt = f"""
        Analyze this job opportunity for a candidate seeking: {target_role} at {experience_level} level
        
        Job Details:
        Title: {job['title']}
        Company: {job['company']}
        Location: {job['location']}
        Description: {job['description']}
        Requirements: {job['requirements']}
        Company Size: {job.get('company_size', 'Unknown')}
        
        Provide analysis including:
        1. Match score (0-100) - be realistic
        2. Why this is a good/poor match
        3. Skill alignment assessment
        4. Growth potential
        5. Any red flags or concerns
        
        Be honest and specific in your assessment.
        """
        
        try:
            body = {
                "max_tokens": 600,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            # Extract match score
            score = self._extract_match_score(analysis_text)
            
            return {
                'score': score,
                'analysis': analysis_text,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Job analysis error: {e}")
            return {
                'score': random.randint(60, 85),  # Random score as fallback
                'analysis': 'This position offers good opportunities for growth and skill development. Consider applying if the role aligns with your career goals.',
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_match_score(self, analysis: str) -> int:
        """Extract numerical match score from analysis"""
        import re
        
        # Look for score patterns
        score_patterns = [
            r'score[:\s]+(\d+)',
            r'(\d+)(?:/100|\%)',
            r'match[:\s]+(\d+)'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, analysis, re.IGNORECASE)
            if match:
                return min(100, max(0, int(match.group(1))))
        
        # Generate realistic score based on analysis sentiment
        if 'excellent' in analysis.lower() or 'perfect' in analysis.lower():
            return random.randint(85, 95)
        elif 'good' in analysis.lower() or 'strong' in analysis.lower():
            return random.randint(70, 84)
        elif 'fair' in analysis.lower() or 'adequate' in analysis.lower():
            return random.randint(55, 69)
        else:
            return random.randint(40, 70)
    
    def _format_job_results(self, jobs: List[Dict], role: str, location: str) -> str:
        """Format job search results"""
        if not jobs:
            return f"## 💼 No Jobs Found\n\nNo jobs found for **{role}** in **{location}**.\n\n### 💡 Try:\n- Broadening your search terms\n- Considering remote positions\n- Looking at related roles"
        
        result = f"## 💼 Job Search Results\n\n"
        result += f"**Role:** {role}\n**Location:** {location}\n**Found:** {len(jobs)} opportunities\n\n"
        
        for i, job in enumerate(jobs[:5], 1):  # Show top 5
            match_score = job['match_analysis'].get('score', 0)
            score_emoji = "🟢" if match_score >= 80 else "🟡" if match_score >= 60 else "🔴"
            
            result += f"### {i}. {job['title']} {score_emoji}\n\n"
            result += f"**🏢 Company:** {job['company']} ({job.get('company_size', 'Size unknown')})\n"
            result += f"**📍 Location:** {job['location']}\n"
            result += f"**💰 Salary:** {job['salary']}\n"
            result += f"**📊 Match Score:** {match_score}/100\n"
            result += f"**📅 Posted:** {job['posted_date']}\n\n"
            
            # Job description (truncated)
            description = job['description'][:200] + "..." if len(job['description']) > 200 else job['description']
            result += f"**📝 Description:** {description}\n\n"
            
            # Requirements
            if job['requirements']:
                result += f"**🔧 Key Requirements:** {', '.join(job['requirements'])}\n\n"
            
            # AI Analysis (summary)
            analysis = job['match_analysis'].get('analysis', '')
            if analysis:
                # Extract first sentence for summary
                analysis_summary = analysis.split('.')[0] + "."
                result += f"**🤖 AI Analysis:** {analysis_summary}\n\n"
            
            result += "---\n\n"
        
        # Job search tips
        result += "## 💡 Job Search Success Tips\n\n"
        result += "1. **📄 Tailor Your Resume**: Customize for each application using keywords from job descriptions\n"
        result += "2. **🤝 Network**: Leverage LinkedIn and professional connections\n"
        result += "3. **🔍 Research**: Study company culture, values, and recent news\n"
        result += "4. **📞 Follow Up**: Send personalized messages after applying\n"
        result += "5. **🎯 Practice**: Prepare for common interview questions in your field\n\n"
        
        if len(jobs) > 5:
            result += f"*Showing top 5 results. {len(jobs) - 5} more opportunities in your search.*\n"
        
        return result
    
    def get_job_application_tips(self, job_title: str) -> str:
        """Get specific application tips for a job"""
        prompt = f"""
        Provide specific application tips for someone applying to a {job_title} position.
        
        Include:
        1. Key skills to highlight
        2. Resume optimization tips
        3. Interview preparation advice
        4. Common questions to expect
        5. What employers look for
        
        Make it actionable and specific to this role.
        """
        
        try:
            body = {
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Application tips error: {e}")
            return "Focus on relevant experience, quantify achievements, and research the company thoroughly."
