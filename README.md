# TermsLens AI — GenAI-only project

TermsLens AI helps people understand Terms & Conditions, privacy policies, subscription terms, and company policies using Gemini.

## Features
- Upload PDF, DOCX, TXT, Markdown, or HTML documents.
- Load public webpages by URL.
- Ask questions grounded in the source document.
- Create a plain-language summary.
- Produce a balanced stakeholder review: potential benefits and risks for the user and the company.
- Long documents are processed in sections and synthesized.
- Answers are instructed to distinguish source text from interpretation and to mention source headings/page markers where available.

## Run on Windows
1. Install Python 3.10+ (the Windows `py` launcher must work).
2. Extract the ZIP into a normal folder.
3. Double-click `Run_TermsLens_AI.bat`.
4. On the first launch, wait while dependencies install. Later launches should be quicker.
5. The app opens at `http://localhost:8501`.

## Gemini API key
The app reads `GEMINI_API_KEY` from the Windows environment or a local `.env` file. There is no API-key entry field in the interface, so everyday users do not need to know about API keys when the app is deployed with a server-side key configured.

If a key has been exposed in a message, revoke it in Google AI Studio and create a replacement. Do not hardcode keys into source code or commit them to a repository.

Optional environment variable:
- `GEMINI_MODEL` — model name available to your account. The default is `gemini-3.8-flash`, based on the model suggested by the API error seen in this user's setup. If unavailable, set it to a model listed as available in your Google AI Studio account.

## Supported documents and limitations
- Text-based PDFs are supported. Scanned/image-only PDFs need OCR before upload.
- Public webpage extraction is best-effort; login-only pages, bot-blocked sites, and non-HTML URLs may fail.
- A limited number of relevant sections are selected for question answering. Long-document summaries/reviews use section-by-section synthesis.
- No source document is stored on a server by this app; document text remains in the active Streamlit session memory while the app is running. When you ask Gemini for an answer/review/summary, relevant document text is sent to Google's API.
- Do not upload confidential material unless you have permission to send it to the configured AI service.
- This tool is educational and informational, not legal advice. Policies can be ambiguous, incomplete, outdated, or jurisdiction-specific. Verify important claims against the original document and seek qualified legal advice for high-stakes decisions.

## Troubleshooting
- If the app does not start, keep the black terminal window open and send the error text.
- If Gemini returns a model-not-found error, set `GEMINI_MODEL` to a currently available model for your API account or edit the model field in the sidebar.
- If Gemini returns authentication or quota errors, verify the key, billing/quota, and model access in Google AI Studio.


### If Windows environment variables are not detected
Windows programs inherit environment variables when they start. If you added `GEMINI_API_KEY` while the app or terminal was already open, fully close the app's black Command Prompt window and start it again. Confirm the variable is named exactly `GEMINI_API_KEY`.

Alternative local setup: create a text file named `.env` beside `app.py` and put one line in it:
`GEMINI_API_KEY=put_your_new_key_here`

Do not share `.env` or commit it to Git. The provided `.gitignore` excludes `.env`.
