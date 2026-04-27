from crewai import Crew, Process
from .agents import JobAgents
from .tasks import ResumeTasks
from utils.pdf_generator import generate_resume_pdf
from utils.doc_generator import generate_resume_docx
import re


def _extract_name_and_contact(resume_text):
    """
    Best-effort extraction of the candidate's name and contact info
    from the raw resume text (first few lines).
    Returns (name, contact_info) strings.
    """
    lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
    if not lines:
        return "Candidate", "Contact not found"

    # First line is the name — unless it already looks like a contact line
    def _is_contact_line(line):
        return bool(re.search(r'@|linkedin|github|\+\d|\d{10}', line, re.I))

    name = lines[0] if not _is_contact_line(lines[0]) else "Candidate"

    # Collect contact fields — prefer a dedicated contact line (line 2)
    # If line 2 already contains email + phone + location together, use it directly
    contact_line = ""
    for line in lines[1:6]:
        if _is_contact_line(line):
            contact_line = line
            break

    if contact_line:
        # Clean up excessive pipes/spaces and return as-is (it's already formatted)
        contact_info = re.sub(r'\s*\|\s*', ' | ', contact_line).strip(' |')
    else:
        # Fall back to extracting individual fields
        email, phone, location = "", "", ""
        for line in lines[:10]:
            m = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', line)
            if m and not email:
                email = m.group(0)
            m2 = re.search(r'[\+\(]?[\d\s\-\(\)]{8,15}', line)
            if m2 and not phone:
                phone = m2.group(0).strip()
            if not location and any(kw in line.lower() for kw in [
                    "india", "mumbai", "delhi", "bangalore", "hyderabad",
                    "usa", "new york", "london", "remote", "pune", "chennai"]):
                location = line
        parts = [p for p in [email, phone, location] if p]
        contact_info = " | ".join(parts) if parts else "Contact not found"

    return name, contact_info


def _clean_cover_letter(text):
    """
    Strips AI preamble, dates, and internal section headings from the cover letter.
    Ensures it starts directly with "Dear [Name/Hiring Team]".
    """
    # Remove common AI preamble phrases
    preamble_patterns = [
        r"^Here is (your|the) (output|cover letter|refined letter).*",
        r"^Sure, (I can|here is).*",
        r"^I have refined.*",
        r"^Below is.*",
        # Pattern for dates like "20th February 2023" or "February 20, 2023"
        r"^(?:\d{1,2}(?:st|nd|rd|th)?\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}",
        r"^(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}",
        r"^\d{4}-\d{2}-\d{2}", # ISO dates
    ]
    lines = text.splitlines()
    cleaned_lines = []
    
    content_started = False
    for line in lines:
        s_line = line.strip()
        if not s_line:
            if content_started:
                cleaned_lines.append(line)
            continue
            
        # Check for section headings to skip
        # Common patterns: "The Hook", "## Paragraph 1", "**The Evidence**", etc.
        skip_keywords = ["The Hook", "The Evidence", "The Connection", "The Close", "Evidence", "Connection", "Close", "Paragraph"]
        if any(h in s_line for h in skip_keywords) and len(s_line) < 30:
            # Check if it's likely a header (all caps, or surrounded by asterisks/hashes)
            if re.match(r'^[#*\s]*[A-Z][a-z]+(\s+[A-Z][a-z]+)*[#*\s]*$', s_line) or "##" in s_line or "**" in s_line:
                continue

        if not content_started:
            # Check if this line looks like preamble or a date
            if any(re.match(p, s_line, re.I) for p in preamble_patterns):
                continue
            # If it doesn't start with "Dear" or "To", and we haven't started yet, it might still be preamble
            if not s_line.lower().startswith(("dear", "to ")):
                # If it's short and doesn't look like a greeting, skip it until we find "Dear"
                if len(s_line) < 50:
                    continue
            content_started = True
        
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines).strip()


def _clean_resume(text):
    """
    Strips AI preamble from the resume text by skipping lines 
    until the first Markdown heading is found.
    """
    lines = text.splitlines()
    cleaned_lines = []
    found_heading = False
    
    for line in lines:
        s_line = line.strip()
        if not s_line:
            if found_heading:
                cleaned_lines.append(line)
            continue
            
        if not found_heading:
            # Check for Markdown heading or all-caps header
            if s_line.startswith("#") or re.match(r'^[A-Z][A-Z\s&/]{2,30}$', s_line):
                found_heading = True
            else:
                continue
        
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines).strip()


def run_full_job_application_pipeline(resume_text, job_description):
    """
    Full multi-agent pipeline:
      1. Resume Optimization Agent  → tailored resume in Markdown
      2. Cover Letter Agent         → personalized cover letter in Markdown
    Then generates PDF + DOCX from the optimized resume.
    """
    # 1. Initialize Agents and Tasks
    agents = JobAgents()
    tasks  = ResumeTasks()

    # 2. Create the Agents
    optimizer = agents.resume_optimizer_agent()
    writer    = agents.cover_letter_agent()

    # 3. Define Tasks (sequential — optimizer runs first)
    optimization_task = tasks.resume_optimization_task(optimizer, resume_text, job_description)
    letter_task       = tasks.cover_letter_task(writer, resume_text, job_description)

    # 4. Assemble the Crew
    crew = Crew(
        agents=[optimizer, writer],
        tasks=[optimization_task, letter_task],
        process=Process.sequential,
        verbose=True,
    )

    # 5. Run
    result = crew.kickoff()
    print("✅ Crew finished!")

    # 6. Extract outputs
    resume_content = _clean_resume(optimization_task.output.raw)   # Markdown resume
    cover_letter   = _clean_cover_letter(str(result))            # Markdown cover letter

    # 7. Auto-detect name + contact from original resume
    name, contact_info = _extract_name_and_contact(resume_text)

    # 7. Auto-detect name + contact from original resume
    name, contact_info = _extract_name_and_contact(resume_text)

    return {
        "cover_letter":     cover_letter,
        "optimized_resume": resume_content,
        "candidate_name":   name,
        "contact_info":     contact_info,
    }


def run_refinement(doc_type: str, current_content: str, instructions: str,
                   candidate_name: str = "Candidate", contact_info: str = ""):
    """
    Refines an existing resume or cover letter based on user freeform instructions.

    doc_type        : 'resume' or 'cover_letter'
    current_content : the existing Markdown content to refine
    instructions    : the user's natural-language refinement request
    candidate_name  : used for regenerating the PDF/DOCX (resume only)
    contact_info    : used for regenerating the PDF/DOCX (resume only)

    Returns a dict with the refined content + (for resume) new file paths.
    """
    agents = JobAgents()
    tasks  = ResumeTasks()

    # Use the optimizer agent for resume, cover letter agent for letter
    if doc_type == "resume":
        agent = agents.resume_optimizer_agent()
    else:
        agent = agents.cover_letter_agent()

    refine_task = tasks.refine_task(agent, doc_type, current_content, instructions)

    crew = Crew(
        agents=[agent],
        tasks=[refine_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    refined_content = str(result)
    
    if doc_type == "cover_letter":
        refined_content = _clean_cover_letter(refined_content)
    else:
        refined_content = _clean_resume(refined_content)

    response = {
        "doc_type":         doc_type,
        "refined_content":  refined_content,
    }

    return response
