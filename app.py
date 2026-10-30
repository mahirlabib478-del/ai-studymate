import os
import streamlit as st
from openai import OpenAI
from pypdf.errors import PdfReadError
from utils import build_study_prompt, extract_pdf_text

st.set_page_config(
    page_title="StudyMate | Your AI Study Partner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f7f8ff 0%, #f4f7fb 55%, #eef5ff 100%); }
    [data-testid="stSidebar"] { background: #101a35; }
    [data-testid="stSidebar"] * { color: #f4f7ff !important; }
    .hero { padding: 1.5rem 1.7rem; border-radius: 22px; color: white;
            background: linear-gradient(115deg, #172554, #3348a5 58%, #4778d5);
            margin-bottom: 1rem; box-shadow: 0 12px 30px rgba(31,55,120,.15); }
    .hero h1 { color: white; margin: 0; font-size: 2.3rem; }
    .hero p { color: #e5edff; margin: .45rem 0 0 0; }
    .small-note { color: #64748b; font-size: .88rem; }
    div[data-testid="stChatMessage"] { border-radius: 14px; }
    .stButton > button { border-radius: 10px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

def get_api_key():
    try:
        return st.secrets.get("NEBIUS_API_KEY", "") or os.getenv("NEBIUS_API_KEY", "")
    except Exception:
        return os.getenv("NEBIUS_API_KEY", "")

def ask_model(messages):
    api_key = get_api_key()
    if not api_key:
        st.error("Nebius API key is not configured yet. Add NEBIUS_API_KEY in Streamlit Secrets.")
        st.info("For local testing, set NEBIUS_API_KEY as an environment variable. Never put the key in a source file.")
        return None
    client = OpenAI(
        base_url=os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
        api_key=api_key,
        timeout=90.0,
        max_retries=2,
    )
    model = os.getenv("NEBIUS_MODEL", "nvidia/Nemotron-3_5-Lightning")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.35,
            max_tokens=1400,
        )
        return response.choices[0].message.content
    except Exception as exc:
        st.error("The AI request could not be completed. Check your Nebius key, model access, and connection.")
        with st.expander("Technical details"):
            st.code(str(exc))
        return None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "document_name" not in st.session_state:
    st.session_state.document_name = ""

with st.sidebar:
    st.markdown("## 🎓 StudyMate")
    st.caption("Your personal AI learning partner")
    subject = st.selectbox("Study subject", ["General", "Computer Science", "Mathematics", "Science", "Medicine", "Business", "Languages", "Other"])
    level = st.selectbox("Learning level", ["Beginner", "School", "University", "Advanced"])
    st.markdown("---")
    st.markdown("### 📄 Study material")
    uploaded = st.file_uploader("Upload a text-based PDF", type=["pdf"], help="Scanned image-only PDFs may not contain extractable text.")
    if uploaded is not None:
        if st.button("Load PDF", use_container_width=True):
            try:
                extracted = extract_pdf_text(uploaded.getvalue())
                if not extracted.strip():
                    st.warning("No selectable text was found. This may be a scanned PDF.")
                else:
                    st.session_state.document_text = extracted
                    st.session_state.document_name = uploaded.name
                    st.success(f"Loaded {uploaded.name}")
            except (PdfReadError, Exception) as exc:
                st.error(f"Could not read this PDF: {exc}")
    if st.session_state.document_name:
        st.caption(f"Loaded: {st.session_state.document_name}")
        if st.button("Remove document", use_container_width=True):
            st.session_state.document_text = ""
            st.session_state.document_name = ""
            st.rerun()
    st.markdown("---")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    st.caption("AI can make mistakes. Verify important academic facts.")

st.markdown("""
<div class="hero">
  <h1>🎓 StudyMate</h1>
  <p>Learn smarter. Understand deeply. Prepare confidently.</p>
</div>
""", unsafe_allow_html=True)

metric_cols = st.columns(3)
for col, title, detail in zip(metric_cols,
    ["💬 AI Tutor", "📚 PDF Notes", "🧠 Practice Quiz"],
    ["Ask and learn step by step", "Turn material into revision notes", "Test your understanding"]):
    with col:
        st.markdown(f"**{title}**")
        st.caption(detail)

tab_chat, tab_notes, tab_quiz = st.tabs(["💬 Ask StudyMate", "📚 Summarize PDF", "🧠 Generate Quiz"])

with tab_chat:
    st.subheader("Your personal tutor")
    st.caption(f"Subject: {subject} · Level: {level}")
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    question = st.chat_input("Ask a question, or tell me what you want to understand...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        system = build_study_prompt("Tutor", subject, level, st.session_state.document_text)
        history = [{"role": "system", "content": system}]
        history.extend(st.session_state.chat_history[-12:])
        with st.chat_message("assistant"):
            with st.spinner("StudyMate is thinking..."):
                answer = ask_model(history)
            if answer:
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

with tab_notes:
    st.subheader("Turn your PDF into revision notes")
    if st.session_state.document_text:
        st.success(f"Ready to summarize: {st.session_state.document_name}")
        if st.button("✨ Generate exam-focused notes", type="primary"):
            with st.spinner("Reading your material and preparing notes..."):
                prompt = build_study_prompt("Summarize notes", subject, level, st.session_state.document_text)
                result = ask_model([{"role": "system", "content": prompt},
                                    {"role": "user", "content": "Please summarize this study material."}])
            if result:
                st.markdown(result)
                st.download_button("⬇️ Download notes", result, file_name="studymate-notes.md", mime="text/markdown")
    else:
        st.info("Upload and load a text-based PDF from the sidebar to create notes.")

with tab_quiz:
    st.subheader("Practice with an AI-generated quiz")
    quiz_topic = st.text_input("Topic (optional if you uploaded a PDF)", placeholder="e.g. Python loops, derivatives, cell biology")
    quiz_difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Challenging"], value="Medium")
    if st.button("🧠 Create 5 MCQs", type="primary"):
        if not quiz_topic.strip() and not st.session_state.document_text:
            st.warning("Enter a topic or upload a PDF first.")
        else:
            quiz_prompt = build_study_prompt("Create MCQ quiz", subject, level, st.session_state.document_text)
            user_prompt = f"Create exactly five {quiz_difficulty.lower()} multiple-choice questions about: {quiz_topic or subject}. Use the uploaded material as the source if provided."
            with st.spinner("Creating your practice quiz..."):
                result = ask_model([{"role": "system", "content": quiz_prompt},
                                    {"role": "user", "content": user_prompt}])
            if result:
                st.markdown(result)
                st.download_button("⬇️ Download quiz", result, file_name="studymate-quiz.md", mime="text/markdown")

st.markdown("---")
st.markdown('<p class="small-note">Built with NVIDIA Nemotron on Nebius Token Factory · StudyMate is an educational aid, not a substitute for your course materials or instructor.</p>', unsafe_allow_html=True)
