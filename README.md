# StudyMate — Your Personal AI Study Partner

StudyMate is a beginner-friendly educational web app powered by **NVIDIA Nemotron through Nebius Token Factory**. It helps learners ask questions, turn text-based PDFs into revision notes, and generate practice multiple-choice quizzes.

## Features

- **AI Tutor:** ask questions and receive step-by-step explanations adapted to a selected subject and learning level.
- **PDF Notes:** upload a text-based PDF and generate exam-focused revision notes.
- **Practice Quiz:** generate five MCQs at easy, medium, or challenging difficulty, with an answer key and explanations.
- **Privacy-conscious credentials:** API keys are read from environment variables or Streamlit Secrets and are never stored in the repository.

## Technology

- Python + Streamlit
- Nebius Token Factory OpenAI-compatible API
- NVIDIA Nemotron 3.5 Lightning (configurable)
- OpenAI Python SDK
- pypdf for PDF text extraction

## Run locally

1. Install Python 3.10 or newer.
2. Clone this repository and open its folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a Nebius Token Factory API key in the Nebius console.
5. Set the key as an environment variable. On Windows PowerShell:

   ```powershell
   $env:NEBIUS_API_KEY="your-key-here"
   ```

6. Start the app:

   ```bash
   streamlit run app.py
   ```

The app uses these defaults:

- API base URL: `https://api.tokenfactory.nebius.com/v1/`
- Model: `nvidia/Nemotron-3_5-Lightning`

You can override them with `NEBIUS_BASE_URL` and `NEBIUS_MODEL`. Check the model catalog in your Nebius account to confirm that your API key has access to the selected model.

## Deploy on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Create an app from this repository and select `app.py` as the entry point.
3. In the app's **Settings → Secrets**, add:

   ```toml
   NEBIUS_API_KEY = "your-key-here"
   ```

4. Deploy. Do not commit API keys, `.env` files, or Streamlit secrets to GitHub.

## Tests

Run:

```bash
pytest -q
```

## Important limitations

- PDF support extracts selectable text. Image-only/scanned PDFs require OCR and are not supported in this first version.
- Uploaded document text is sent to the configured model provider to generate responses. Do not upload confidential, personal, or sensitive documents.
- Model outputs can be inaccurate. Verify important facts against trusted course materials.
- A valid Nebius Token Factory account, API key, model access, and any applicable credits/billing are required for live AI responses.

## Hackathon track

**Best Apps & Agents Track.** The project uses an NVIDIA Nemotron open model served through Nebius Token Factory. The final submission should include a working deployed demo, this public repository, and a short public demo video.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
