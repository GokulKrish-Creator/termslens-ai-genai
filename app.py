import os
import re
import hashlib
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from termslens.extractors import extract_uploaded_file, fetch_website, split_into_chunks
from termslens.analysis import ask_document, run_document_review, summarize_document

load_dotenv()
st.set_page_config(page_title="TermsLens AI", page_icon="📜", layout="wide")

st.markdown("""
<style>
.main .block-container {max-width: 1180px; padding-top: 1.5rem;}
.hero {padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#172554,#134e4a); color: white; margin-bottom: 1rem;}
.hero h1 {font-size: 2.35rem; margin: 0 0 .4rem 0;}
.hero p {opacity: .92; margin: 0; font-size: 1.05rem;}
.small-muted {color: #9ca3af; font-size: .9rem;}
</style>
<div class="hero">
<h1>📜 TermsLens AI</h1>
<p>Understand terms, privacy policies, contracts, and company policies in plain language.</p>
</div>
""", unsafe_allow_html=True)

st.write("Upload a document or provide a public webpage URL. Ask questions, review key obligations, and compare potential benefits and drawbacks for both the user and the company.")

with st.sidebar:
    st.header("🔐 AI connection")
    configured_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    model_name = (os.getenv("GEMINI_MODEL") or "gemini-3.8-flash").strip()
    if configured_key:
        st.success("Gemini is configured")
    else:
        st.error("Gemini API key not found")
        st.caption("Set GEMINI_API_KEY in Windows Environment Variables, then fully close and reopen this app. Alternatively, create a local .env file beside app.py. Never share or commit that file.")
    st.caption(f"Model: {model_name}")
    st.caption("Document text is sent to Gemini only when you request an answer, summary, or review. Avoid uploading confidential documents unless you are allowed to share them with the AI service.")
    st.divider()
    st.caption("Educational information only — not legal advice.")

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""
if "doc_source" not in st.session_state:
    st.session_state.doc_source = ""
if "doc_hash" not in st.session_state:
    st.session_state.doc_hash = ""

def get_client():
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not key:
        st.error("Gemini API key was not found in this app process. Set GEMINI_API_KEY in Windows Environment Variables, then fully close and reopen the launcher; or create a local .env file as described in README.md.")
        return None
    try:
        return genai.Client(api_key=key)
    except Exception as exc:
        st.error(f"Could not initialize Gemini: {exc}")
        return None

tab_upload, tab_url = st.tabs(["📄 Upload a document", "🌐 Read a public webpage"])

with tab_upload:
    upload = st.file_uploader(
        "Choose a policy or terms document",
        type=["pdf", "docx", "txt", "md", "html", "htm"],
        help="Supported: PDF, Word, TXT, Markdown, and HTML."
    )
    if upload is not None and st.button("Load document", type="primary", key="load_upload"):
        try:
            text, source = extract_uploaded_file(upload.name, upload.getvalue())
            if not text.strip():
                st.error("No readable text was found. If this is a scanned PDF, run OCR first or upload a text-based copy.")
            else:
                st.session_state.doc_text = text
                st.session_state.doc_name = upload.name
                st.session_state.doc_source = source
                st.session_state.doc_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
                st.success(f"Loaded {upload.name} — {len(text):,} characters.")
        except Exception as exc:
            st.error(f"Could not read this file: {exc}")

with tab_url:
    url = st.text_input("Public webpage URL", placeholder="https://example.com/terms")
    st.caption("Only use public pages you are allowed to access. Login-only pages and sites that block automated requests may not work.")
    if st.button("Read webpage", type="primary", key="load_url"):
        try:
            text, title = fetch_website(url)
            if not text.strip():
                st.error("No readable page text was found.")
            else:
                st.session_state.doc_text = text
                st.session_state.doc_name = title or urlparse(url).netloc
                st.session_state.doc_source = url
                st.session_state.doc_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
                st.success(f"Loaded webpage: {st.session_state.doc_name} — {len(text):,} characters.")
        except Exception as exc:
            st.error(f"Could not read webpage: {exc}")

if st.session_state.doc_text:
    st.divider()
    left, right = st.columns([3, 1])
    with left:
        st.subheader(f"📑 Active document: {st.session_state.doc_name}")
        st.caption(f"Source: {st.session_state.doc_source} · {len(st.session_state.doc_text):,} characters")
    with right:
        if st.button("Clear document"):
            st.session_state.doc_text = ""
            st.session_state.doc_name = ""
            st.session_state.doc_source = ""
            st.session_state.doc_hash = ""
            st.rerun()

    with st.expander("Preview extracted text", expanded=False):
        st.text(st.session_state.doc_text[:12000] + ("\n\n[Preview shortened]" if len(st.session_state.doc_text) > 12000 else ""))

    st.subheader("What would you like to do?")
    qtab, reviewtab, summarytab = st.tabs(["💬 Ask a question", "⚖️ Benefits & drawbacks", "🧾 Plain-language summary"])

    with qtab:
        question = st.text_area("Ask about this document", placeholder="For example: Can the company share my personal data with advertisers?", height=100)
        if st.button("Ask TermsLens", type="primary", key="ask_doc"):
            client = get_client()
            if client and question.strip():
                with st.spinner("Finding relevant sections and preparing an answer..."):
                    try:
                        answer = ask_document(client, model_name, st.session_state.doc_text, question.strip())
                        st.markdown(answer)
                    except Exception as exc:
                        st.error(f"Gemini request failed: {exc}")
            elif not question.strip():
                st.warning("Enter a question first.")

    with reviewtab:
        st.write("Identify potential user benefits and risks, as well as company benefits and risks. TermsLens will distinguish explicit wording from reasonable interpretation.")
        focus = st.text_input("Optional focus", placeholder="e.g. cancellation, data privacy, automatic renewal")
        if st.button("Review benefits and drawbacks", type="primary", key="review_doc"):
            client = get_client()
            if client:
                with st.spinner("Reviewing the document in sections..."):
                    try:
                        report = run_document_review(client, model_name, st.session_state.doc_text, focus.strip())
                        st.markdown(report)
                    except Exception as exc:
                        st.error(f"Gemini review failed: {exc}")

    with summarytab:
        if st.button("Create plain-language summary", type="primary", key="summary_doc"):
            client = get_client()
            if client:
                with st.spinner("Summarizing the document..."):
                    try:
                        st.markdown(summarize_document(client, model_name, st.session_state.doc_text))
                    except Exception as exc:
                        st.error(f"Summary failed: {exc}")

st.divider()
st.markdown("**TermsLens AI** is a document-understanding assistant, not a lawyer. It can miss context, exceptions, jurisdiction-specific rules, and changes in online policies. Verify important conclusions against the original text and consult a qualified professional for high-stakes decisions.")
