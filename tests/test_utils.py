from utils import build_study_prompt


def test_tutor_prompt_mentions_step_by_step():
    prompt = build_study_prompt("Tutor", "Computer Science", "Beginner")
    assert "step by step" in prompt
    assert "Computer Science" in prompt
    assert "Beginner" in prompt


def test_quiz_prompt_requires_five_questions_and_answer_key():
    prompt = build_study_prompt("Create MCQ quiz")
    assert "exactly 5" in prompt
    assert "answer key" in prompt


def test_document_is_included_as_primary_source():
    prompt = build_study_prompt("Summarize notes", document_text="Photosynthesis converts light energy.")
    assert "primary source" in prompt
    assert "Photosynthesis converts light energy." in prompt


def test_unknown_mode_falls_back_to_tutor():
    prompt = build_study_prompt("anything else")
    assert "Answer the learner's study question step by step" in prompt
