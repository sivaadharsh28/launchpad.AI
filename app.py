import gradio as gr
import boto3
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import logging

from src.ai_agent import LaunchPadAgent
from src.aws_services import AWSServices
from src.skill_analyzer import SkillAnalyzer
from src.career_planner import CareerPlanner
from src.document_generator import DocumentGenerator
from src.job_searcher import JobSearcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LaunchPadAI:
    def __init__(self):
        self.aws_services = AWSServices()
        self.agent = LaunchPadAgent()
        self.skill_analyzer = SkillAnalyzer()
        self.career_planner = CareerPlanner()
        self.document_generator = DocumentGenerator()
        self.job_searcher = JobSearcher()
        
    def analyze_skills(self, user_input: str, resume_text: str = "") -> str:
        """Analyze user skills and interests"""
        try:
            analysis = self.skill_analyzer.analyze(user_input, resume_text)
            return f"### 🎯 Skill Analysis Results\n\n{analysis}"
        except Exception as e:
            logger.error(f"Skill analysis error: {e}")
            return f"Error analyzing skills: {str(e)}"
    
    def suggest_career_paths(self, skills: str, interests: str, experience: str) -> str:
        """Generate career path suggestions"""
        try:
            suggestions = self.career_planner.suggest_paths(skills, interests, experience)
            return f"### 🚀 Career Path Suggestions\n\n{suggestions}"
        except Exception as e:
            logger.error(f"Career planning error: {e}")
            return f"Error generating career suggestions: {str(e)}"
    
    def generate_resume(self, personal_info: str, experience: str, skills: str) -> str:
        """Generate personalized resume"""
        try:
            resume = self.document_generator.create_resume(personal_info, experience, skills)
            return f"### 📄 Generated Resume\n\n{resume}"
        except Exception as e:
            logger.error(f"Resume generation error: {e}")
            return f"Error generating resume: {str(e)}"
    
    def search_jobs(self, role: str, location: str, experience_level: str) -> str:
        """Search for relevant job opportunities"""
        try:
            jobs = self.job_searcher.search(role, location, experience_level)
            return f"### 💼 Job Opportunities\n\n{jobs}"
        except Exception as e:
            logger.error(f"Job search error: {e}")
            return f"Error searching jobs: {str(e)}"
    
    def chat_with_agent(self, message: str, history: List) -> tuple:
        """Main chat interface with the AI agent"""
        try:
            response = self.agent.process_message(message, history)
            history.append((message, response))
            return "", history
        except Exception as e:
            logger.error(f"Agent chat error: {e}")
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            history.append((message, error_response))
            return "", history

# Initialize the application
app = LaunchPadAI()

# Create Gradio interface
with gr.Blocks(title="LaunchPad.AI - Your AI Career Copilot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🚀 LaunchPad.AI - Your AI Career Copilot
    
    Navigate your career journey from dream to job offer with AI-powered guidance.
    """)
    
    with gr.Tabs():
        # Main Chat Interface
        with gr.TabItem("💬 AI Career Chat"):
            chatbot = gr.Chatbot(
                height=500,
                placeholder="Hello! I'm your AI Career Copilot. How can I help you today?"
            )
            msg = gr.Textbox(
                placeholder="Ask me about career planning, skill development, or job search...",
                label="Your Message"
            )
            clear_btn = gr.Button("Clear Chat")
            
            msg.submit(app.chat_with_agent, [msg, chatbot], [msg, chatbot])
            clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])
        
        # Skill Analysis
        with gr.TabItem("🎯 Skill Analysis"):
            with gr.Row():
                with gr.Column():
                    skill_input = gr.Textbox(
                        label="Tell me about your current skills and experience",
                        placeholder="I have experience in Python, data analysis, and project management...",
                        lines=3
                    )
                    resume_upload = gr.Textbox(
                        label="Paste your resume text (optional)",
                        placeholder="Copy and paste your resume here for detailed analysis...",
                        lines=5
                    )
                    analyze_btn = gr.Button("Analyze Skills", variant="primary")
                
                with gr.Column():
                    skill_output = gr.Markdown()
            
            analyze_btn.click(
                app.analyze_skills,
                inputs=[skill_input, resume_upload],
                outputs=skill_output
            )
        
        # Career Planning
        with gr.TabItem("🗺️ Career Planning"):
            with gr.Row():
                with gr.Column():
                    skills_input = gr.Textbox(
                        label="Your Skills",
                        placeholder="Python, Machine Learning, Communication...",
                        lines=2
                    )
                    interests_input = gr.Textbox(
                        label="Your Interests",
                        placeholder="Technology, Healthcare, Finance...",
                        lines=2
                    )
                    experience_input = gr.Textbox(
                        label="Experience Level",
                        placeholder="Entry-level, Mid-level, Senior...",
                        lines=1
                    )
                    plan_btn = gr.Button("Get Career Suggestions", variant="primary")
                
                with gr.Column():
                    career_output = gr.Markdown()
            
            plan_btn.click(
                app.suggest_career_paths,
                inputs=[skills_input, interests_input, experience_input],
                outputs=career_output
            )
        
        # Document Generation
        with gr.TabItem("📄 Document Generator"):
            with gr.Row():
                with gr.Column():
                    personal_info = gr.Textbox(
                        label="Personal Information",
                        placeholder="Name, Contact, Summary...",
                        lines=3
                    )
                    experience_info = gr.Textbox(
                        label="Work Experience",
                        placeholder="Job titles, companies, achievements...",
                        lines=5
                    )
                    skills_info = gr.Textbox(
                        label="Skills & Education",
                        placeholder="Technical skills, certifications, education...",
                        lines=3
                    )
                    generate_btn = gr.Button("Generate Resume", variant="primary")
                
                with gr.Column():
                    document_output = gr.Markdown()
            
            generate_btn.click(
                app.generate_resume,
                inputs=[personal_info, experience_info, skills_info],
                outputs=document_output
            )
        
        # Job Search
        with gr.TabItem("💼 Job Search"):
            with gr.Row():
                with gr.Column():
                    job_role = gr.Textbox(
                        label="Job Role",
                        placeholder="Data Scientist, Software Engineer, Product Manager...",
                        lines=1
                    )
                    job_location = gr.Textbox(
                        label="Location",
                        placeholder="San Francisco, Remote, New York...",
                        lines=1
                    )
                    job_experience = gr.Dropdown(
                        label="Experience Level",
                        choices=["Entry Level", "Mid Level", "Senior Level", "Executive"],
                        value="Mid Level"
                    )
                    search_btn = gr.Button("Search Jobs", variant="primary")
                
                with gr.Column():
                    job_output = gr.Markdown()
            
            search_btn.click(
                app.search_jobs,
                inputs=[job_role, job_location, job_experience],
                outputs=job_output
            )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
