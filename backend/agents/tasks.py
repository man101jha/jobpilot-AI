from crewai import Task


class ResumeTasks:

    def resume_optimization_task(self, agent, resume_text, job_description):
        return Task(
            description=f"""
You are a world-class professional resume writer and ATS (Applicant Tracking System) optimization expert.

Your task is to produce a FULLY UPDATED, TAILORED resume that maximizes the candidate's chances of landing this specific role.

══════════════════════════════════════════
CANDIDATE'S ORIGINAL RESUME:
══════════════════════════════════════════
{resume_text}

══════════════════════════════════════════
TARGET JOB DESCRIPTION:
══════════════════════════════════════════
{job_description}

══════════════════════════════════════════
YOUR REWRITING INSTRUCTIONS:
══════════════════════════════════════════

CRITICAL RULE: NEVER hallucinate or add missing sections. If a section (e.g., Experience, Projects, Skills) is entirely missing from the original resume, DO NOT create it. Only enhance sections that already exist.

STEP 1 — ANALYZE:
- Extract the top 5 hard skills and top 3 soft skills the JD emphasizes.
- Identify the exact keywords, tools, and technologies the hiring manager cares about.
- Note the seniority level and tone (startup-casual vs. enterprise-formal).

STEP 2 — REWRITE EXPERIENCE BULLETS (if present):
- Each bullet must start with a STRONG action verb (Architected, Spearheaded, Engineered, Delivered, Optimized, etc.).
- Quantify every bullet where possible: numbers, %, $, scale (e.g., "reduced API latency by 38%", "served 1.2M users").
- Mirror the exact vocabulary from the job description naturally within bullets.
- Remove any experience that is completely irrelevant to this role.
- Elevate and expand bullets that directly match the JD's must-haves.

STEP 3 — REWRITE SKILLS SECTION (if present):
- Reorder skills so the ones most relevant to the JD appear first.
- Add any missing keywords from the JD that the candidate legitimately has experience with.
- Group into logical categories (Languages, Frameworks, Cloud/DevOps, Databases, Tools, etc.).

STEP 4 — REWRITE SUMMARY (if present):
- Write a 2-sentence professional summary that names the exact role and mirrors the JD's tone.
- Highlight the candidate's most impressive, relevant achievement.

STEP 5 — PROJECTS & EDUCATION (if present):
- Keep all projects but reframe descriptions to emphasize JD-relevant impact.
- Keep education as-is, add relevant coursework only if it strengthens the application.

══════════════════════════════════════════
STRICT OUTPUT FORMAT (follow exactly):
══════════════════════════════════════════
- Use Markdown section headings for existing sections only (e.g., ## SUMMARY, ## EXPERIENCE, ## SKILLS, ## PROJECTS, ## EDUCATION).
- For each role: **Job Title | Company Name | Month Year – Month Year**
- Below each role, indent bullets as: - <achievement bullet>
- For skills: - Category: Skill1, Skill2, Skill3
- DO NOT output LaTeX, HTML, JSON, XML, or code fences (no ``` blocks).
- DO NOT include any preamble, explanation, or commentary before or after the resume.
- ABSOLUTELY NO phrases like "Here is the rewritten resume" or "Sure, I can help with that".
- Start your output DIRECTLY with the first ## section heading.
- Maintain 100% factual honesty — only reframe, never fabricate.
""",
            expected_output=(
                "A complete, ATS-optimized Markdown resume starting directly with a ## section heading. "
                "Every bullet uses strong action verbs and quantified metrics. "
                "The skills section mirrors the job description's top keywords. "
                "Missing sections are completely omitted. "
                "No LaTeX, no code fences, no explanatory text — resume content only."
            ),
            agent=agent,
        )

    def cover_letter_task(self, agent, resume_text, job_description):
        return Task(
            description=f"""
You are an elite cover letter strategist who has helped thousands of candidates land interviews at top companies.

Your task is to write a HIGHLY PERSONALIZED, COMPELLING cover letter that feels human — not templated.

══════════════════════════════════════════
CANDIDATE'S RESUME:
══════════════════════════════════════════
{resume_text}

══════════════════════════════════════════
TARGET JOB DESCRIPTION:
══════════════════════════════════════════
{job_description}

══════════════════════════════════════════
YOUR WRITING INSTRUCTIONS:
══════════════════════════════════════════

STEP 1 — RESEARCH THE JD:
- Extract the company name and the exact job title.
- Identify the top 3 "must-have" requirements the hiring manager listed.
- Note the company's apparent culture/tone (e.g., innovative startup, established enterprise, mission-driven nonprofit).

STEP 2 — CRAFT THE LETTER using this 4-paragraph structure:

PARAGRAPH 1 — THE HOOK (3-4 sentences):
- Open with a compelling, specific statement — NOT "I am writing to apply for...".
- Name the exact role and company.
- Lead with your most impressive, relevant credential or achievement that directly maps to the JD.
- Convey genuine excitement for this specific company (reference something real from the JD).

PARAGRAPH 2 — THE EVIDENCE (4-5 sentences):
- Present 2-3 of the candidate's strongest achievements that directly address the JD's must-haves.
- Be specific: include numbers, scale, and outcomes (same as resume bullets).
- Show a direct line from the candidate's past work to the value they'll bring to this role.

PARAGRAPH 3 — THE CONNECTION (3-4 sentences):
- Demonstrate understanding of the company's challenges or goals mentioned in the JD.
- Explain WHY this specific company, not just any company with this job.
- Connect the candidate's values or working style to the company's culture.

PARAGRAPH 4 — THE CLOSE (2-3 sentences):
- Restate enthusiasm and confidence.
- Include a clear, polite call to action (requesting an interview/conversation).
- End with a professional, memorable sign-off.

══════════════════════════════════════════
STRICT OUTPUT FORMAT:
══════════════════════════════════════════
- Output in clean Markdown.
- Start your output DIRECTLY with the Hiring Manager greeting (e.g., "Dear Hiring Team," or "Dear [Name],").
- DO NOT include a date or your own contact info at the top — start with the greeting.
- Include 4 body paragraphs and a professional closing (e.g., "Sincerely, [Name]").
- ABSOLUTELY NO internal section headings (like "The Evidence", "The Hook", "The Connection", etc.).
- ABSOLUTELY NO preamble/intro text like "Here is the output" or "Sure, here is your letter".
- USE A WARM, HUMAN TONE. Avoid AI-sounding transitions. Write like a passionate professional, not a robot.
- NO generic phrases: avoid "I am a team player", "passionate about", "I believe I would be a great fit".
- NO LaTeX, no code fences, no commentary outside the letter itself.
- The letter must be between 280-380 words (concise but impactful).
""",
            expected_output=(
                "A polished, highly personalized 4-paragraph cover letter in Markdown format. "
                "The letter names the specific company and role, references 2-3 quantified achievements "
                "from the candidate's background, demonstrates genuine company knowledge, and ends with "
                "a clear call to action. No generic phrases, no LaTeX, no preamble text outside the letter."
            ),
            agent=agent,
        )

    def refine_task(self, agent, doc_type: str, current_content: str, instructions: str):
        """
        Refines an existing resume or cover letter based on user instructions.
        doc_type: 'resume' or 'cover_letter'
        """
        if doc_type == "resume":
            format_rules = """
STRICT OUTPUT FORMAT (resume):
- Keep all Markdown section headings (## SUMMARY, ## EXPERIENCE, etc.)
- Keep **Job Title | Company | Date** format for roles
- Use "- " for bullet points
- DO NOT add LaTeX, HTML, or code fences
- Start output directly with the first ## section, no preamble
"""
            doc_label = "RESUME"
        else:
            format_rules = """
STRICT OUTPUT FORMAT (cover letter):
- Output clean Markdown
- Start directly with the greeting (e.g., "Dear Hiring Team,").
- DO NOT include a date at the top.
- Keep the 4 paragraph structure and professional closing.
- ABSOLUTELY NO internal section headings (The Hook, Evidence, etc.).
- ABSOLUTELY NO preamble/intro text like "Here is your refined letter".
- USE A WARM, HUMAN TONE. Avoid AI-sounding phrases.
- NO generic phrases, NO LaTeX, NO code fences
- Output the letter only.
"""
            doc_label = "COVER LETTER"

        return Task(
            description=f"""
You are an expert document editor. You will refine an existing {doc_label} based on specific user instructions.

══════════════════════════════════════════
CURRENT {doc_label}:
══════════════════════════════════════════
{current_content}

══════════════════════════════════════════
USER'S REFINEMENT INSTRUCTIONS:
══════════════════════════════════════════
{instructions}

══════════════════════════════════════════
YOUR TASK:
══════════════════════════════════════════
- Apply ONLY the changes the user requested.
- Preserve everything else exactly as-is — do not rewrite sections that weren't asked about.
- If the user asks for a tone change, apply it throughout naturally.
- If the user asks to add/remove/change specific content, do exactly that.
- If the user asks to make it shorter or longer, respect that.
- Maintain 100% factual accuracy — never fabricate new information.
- CRITICAL: Never add entirely new sections (like Experience, Projects, etc.) unless explicitly asked. If a section is missing, do not add it.

{format_rules}
""",
            expected_output=(
                f"The refined {doc_label} with exactly the requested changes applied. "
                "Preserves original structure and content where not explicitly changed. "
                "No preamble, no explanation — document content only."
            ),
            agent=agent,
        )


# ── Legacy JobTasks kept for backward compatibility ──────────────────────────
class JobTasks:
    def plan_task(self, agent, resume_text, job_description):
        return Task(
            description=f"""
            Analyze the following Job Description and the provided Resume.
            1. Identify the top 3 most important requirements from the job description.
            2. Cross-reference them with the candidate's resume.
            3. Create a strategy on how to position the candidate as the perfect fit.

            Job Description: {job_description}
            Resume: {resume_text}
            """,
            expected_output="A detailed strategy document including key focus areas for the cover letter and interview.",
            agent=agent,
        )

    def analyze_task(self, agent, resume_text):
        return Task(
            description=f"""
            Extract the following information from the resume:
            - Top 5 Technical Skills
            - Top 3 Soft Skills
            - A summary of the candidate's most impressive achievement.

            Resume: {resume_text}
            """,
            expected_output="A structured summary of the candidate's profile.",
            agent=agent,
        )

    def cover_letter_task(self, agent, resume_text, job_description):
        return Task(
            description=f"""
            1. Review the candidate's resume: {resume_text}
            2. Review the job description: {job_description}
            3. Write a 3-4 paragraph cover letter that:
               - Mentions the specific role and company.
               - Highlights 2-3 key achievements that match the JD's must-haves.
               - Demonstrates an understanding of the company's culture/tone.
               - Ends with a strong call to action.
            """,
            expected_output="A polished, ready-to-send cover letter in Markdown format.",
            agent=agent,
        )
