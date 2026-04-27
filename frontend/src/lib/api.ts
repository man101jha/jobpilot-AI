const BACKEND = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeJob(resumeFile: File, jobDescription: string) {
  const formData = new FormData();
  formData.append("resume_file", resumeFile);
  formData.append("job_description", jobDescription);

  const response = await fetch(`${BACKEND}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || err.error || "Analysis failed");
  }

  return response.json();
} 

export interface RefinePayload {
  doc_type: "resume" | "cover_letter";
  current_content: string;
  instructions: string;
  candidate_name?: string;
  contact_info?: string;
}

export async function refineDocument(payload: RefinePayload) {
  const response = await fetch(`${BACKEND}/refine`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || err.error || "Refinement failed");
  }

  return response.json();
}

export interface GeneratePayload {
  content: string;
  candidate_name: string;
  contact_info: string;
  format: "pdf" | "docx";
}

export async function generateFile(payload: GeneratePayload) {
  const response = await fetch(`${BACKEND}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || err.error || "Generation failed");
  }

  return response.json();
}
