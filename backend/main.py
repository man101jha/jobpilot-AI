import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agents.crew import run_full_job_application_pipeline, run_refinement
from utils.pdf_parser import extract_text_from_pdf

app = FastAPI(title="JobPilot AI API")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated PDF/DOCX files for download
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
async def root():
    return {"message": "JobPilot AI API is running"}


@app.post("/analyze")
async def analyze_job(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Full pipeline: PDF → AI agents → optimized resume + cover letter + files.
    """
    print(f"[analyze] Received file: {resume_file.filename}")

    pdf_content = await resume_file.read()
    resume_text = extract_text_from_pdf(pdf_content)

    if not resume_text:
        return {"error": "Failed to extract text from PDF. Please check the file."}

    print(f"[analyze] Parsed {len(resume_text)} characters.")
    results = run_full_job_application_pipeline(resume_text, job_description)
    return results


class RefineRequest(BaseModel):
    doc_type: str
    current_content: str
    instructions: str
    candidate_name: str = "Candidate"
    contact_info: str = ""

 
@app.post("/refine")
async def refine_document(req: RefineRequest):
    """
    Refines content based on user instructions. No files generated here.
    """
    if req.doc_type not in ("resume", "cover_letter"):
        return {"error": "doc_type must be 'resume' or 'cover_letter'"}

    result = run_refinement(
        doc_type=req.doc_type,
        current_content=req.current_content,
        instructions=req.instructions,
        candidate_name=req.candidate_name,
        contact_info=req.contact_info,
    )
    return result


class GenerateRequest(BaseModel):
    content: str
    candidate_name: str = "Candidate"
    contact_info: str = ""
    format: str = "pdf" # "pdf" or "docx"


@app.post("/generate")
async def generate_file(req: GenerateRequest):
    """
    Generates a PDF or DOCX on-demand from provided content.
    """
    from utils.pdf_generator import generate_resume_pdf
    from utils.doc_generator import generate_resume_docx

    data = {
        "name": req.candidate_name,
        "contact_info": req.contact_info,
        "content": req.content
    }

    if req.format == "pdf":
        file_path = generate_resume_pdf(data)
    else:
        file_path = generate_resume_docx(data)

    return {"file_url": file_path}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
