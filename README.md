# JobPilot AI 🚀

JobPilot AI is an advanced, AI-powered career assistant designed to optimize your job application process. By leveraging a multi-agent system, JobPilot AI automatically analyzes your existing resume alongside a target job description to generate a deeply tailored, ATS-optimized resume and a highly personalized cover letter.

The system ensures that your unique skills and achievements are perfectly aligned with the exact requirements of your dream job, significantly boosting your chances of landing an interview. 

## ✨ Key Features
- **Intelligent Resume Parsing:** Extracts details from your raw PDF resume with high fidelity.
- **Multi-Agent Optimization:** Uses specialized AI agents (CrewAI) to rewrite and optimize your experience bullets, skills, and summary to match the job description's must-have keywords—without hallucinating missing information.
- **Personalized Cover Letters:** Generates compelling, non-robotic cover letters that connect your specific achievements to the company's mission and challenges.
- **On-the-Fly Document Generation:** Exports your polished documents directly into beautiful, modern PDF and DOCX formats.
- **Interactive Refinement:** Allows you to chat with the AI to refine your documents with custom instructions (e.g., "Make it sound more formal" or "Focus more on my leadership experience").

## 🛠️ Tech Stack

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework for building APIs.
- **AI Orchestration:** [CrewAI](https://crewai.com/) - Multi-agent framework orchestrating specialized AI roles (Resume Optimizer, Cover Letter Strategist, etc.).
- **LLM Integration:** Groq (Llama-3.3-70b-versatile) via `litellm` and `langchain_community`.
- **Document Processing:** 
  - `PyPDF2` for PDF text extraction.
  - `reportlab` for generating modern, styled PDF resumes.
  - `python-docx` for generating structured Word documents.

### Frontend
- **Framework:** [Next.js](https://nextjs.org/) (React) - Providing a dynamic, responsive user interface.
- **Styling:** Tailwind CSS (implied by typical Next.js modern setups) for sleek, customizable designs.
- **State Management & Data Fetching:** React Hooks (`useState`, etc.) handling multipart form submissions and live document preview.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- A Groq API Key (or alternative LLM provider API key).

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the `backend` directory and add your API keys:
   ```env
   GROQ_API_KEY=your_api_key_here
   MODEL=groq/llama-3.3-70b-versatile
   ```
4. Start the FastAPI development server:
   ```bash
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📄 License
This project is licensed under the MIT License.
