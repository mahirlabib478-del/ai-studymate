"""Small, testable helpers for AI StudyMate."""
from pypdf import PdfReader
from io import BytesIO

MAX_DOCUMENT_CHARS = 24000


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract readable text from a PDF upload, with a safe size limit."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(text)
    return "\n\n".join(pages)[:MAX_DOCUMENT_CHARS]


def build_study_prompt(mode: str, subject: str = "General", level: str = "Beginner",
                       document_text: str = "") -> str:
    """Build a mode-specific instruction that keeps answers grounded."""
    base = (
        "You are StudyMate, a patient and encouraging study tutor. "
        "Teach accurately, use clear headings and concise examples, and adapt to the learner. "
        "If the provided material does not contain an answer, say so rather than inventing one. "
        "For factual claims that may vary, mention uncertainty."
    )
    if mode == "Explain simply":
        task = "Explain the learner's topic in plain language, then give one analogy and three key takeaways."
    elif mode == "Create MCQ quiz":
        task = (
            "Create exactly 5 multiple-choice questions from the supplied study material when available. "
            "Give four options (A-D), then put the answer key and short explanations in a separate section at the end. "
            "Do not reveal answers immediately after each question."
        )
    elif mode == "Summarize notes":
        task = (
            "Create exam-focused notes with: a short overview, key concepts, important definitions, "
            "and a final quick-revision list. Do not add facts that are not supported by the supplied document."
        )
    else:
        task = "Answer the learner's study question step by step. Explain the reasoning, not just the final answer."
    context = f"\nSubject: {subject}\nLearner level: {level}\n"
    if document_text:
        context += "\nUse this uploaded document as the primary source:\n" + document_text
    return base + context + "\nTask: " + task
