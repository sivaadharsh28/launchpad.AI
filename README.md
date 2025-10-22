---
title: launchpad.AI
app_file: app.py
sdk: gradio
sdk_version: 5.49.1
---
# 🚀 LaunchPad.AI — Your AI Career Copilot

### 🎯 Inspiration
Students and young professionals often struggle to plan their career paths effectively — not because of a lack of ambition, but due to a lack of structured, personalized guidance. We were inspired to build LaunchPad.AI to give every learner an intelligent, always-available AI career coach that helps them navigate from *dream to job offer*.

---

### 🧠 What It Does
LaunchPad.AI is an autonomous AI career copilot built entirely on AWS.  
It helps users plan, prepare, and apply for jobs through reasoning, learning, and automation.

**Key features:**
- **Skill & Goal Analysis**: Uses Amazon SageMaker to assess user strengths, interests, and gaps.  
- **Career Path Discovery**: Employs Bedrock LLMs (Claude / Nova) to suggest tailored roles and industries.  
- **Learning Recommendations**: Maps skill gaps to online courses and learning pathways.  
- **Autonomous Document Creation**: Generates personalized resumes, cover letters, and LinkedIn summaries.  

---

### 🤖 Why It's an AI Agent
LaunchPad.AI qualifies as an AWS-defined AI Agent because it:

1. **Uses reasoning LLMs** (Bedrock Claude/Nova) to interpret user goals, reason about next steps, and make decisions.  
2. **Autonomously performs multi-step tasks** — fetching data, generating content, and scheduling actions — without human input.  
4. **Maintains context and user memory** through DynamoDB and S3 for persistent learning.  
5. **Employs Bedrock AgentCore primitives** for planning, execution, and tool-calling — the hallmark of an AWS agentic system.  

---

### ⚙️ Built With
- **Amazon Bedrock (Claude / Nova)** — Reasoning LLM for planning and decision-making  
- **Amazon SageMaker** — Custom ML models for skill-gap detection  
- **AWS Lambda + API Gateway** — Task orchestration and automation  
- **Amazon Bedrock AgentCore** — Agentic task execution  
- **Amazon DynamoDB / S3** — Memory and persistent data storage  
- **Gradio** — Interactive web-based frontend  
- **Python (Boto3, LangChain)** — Backend integrations  

---

### 🧩 System Architecture
```text
User → Gradio Frontend → API Gateway → Lambda
     → Bedrock AgentCore ↔️ SageMaker (Skill Analysis)
     ↔️ DynamoDB/S3 (Memory)
     ↔️ External APIs (Job Boards, Learning Platforms)
```

---

### 🚀 Quick Start

#### Prerequisites
- Python 3.8 or higher
- AWS Account with appropriate permissions
- AWS CLI configured (optional but recommended)

#### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd launchpad.AI
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment and install dependencies
python3 create_venv.py

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# OR run the convenience script:
./activate_venv.sh

# On Windows:
venv\Scripts\activate.bat
# OR double-click:
activate_venv.bat
```

3. **Configure AWS credentials**
   - Option 1: AWS CLI
     ```bash
     aws configure
     ```
   - Option 2: Environment variables in `.env` file
     ```bash
     cp .env.example .env
     # Edit .env with your credentials
     ```

4. **Deploy AWS infrastructure**
```bash
python deploy.py
```

5. **Start the application**
```bash
python run.py
```

6. **Open your browser**
   - Navigate to `http://localhost:7860`
   - Start using your AI Career Copilot!