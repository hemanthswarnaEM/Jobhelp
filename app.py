import streamlit as st
import os
import json
import re
import pandas as pd
import datetime
import tempfile
import subprocess
import shutil
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import smtplib
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate, make_msgid
from openai import OpenAI
import google.generativeai as genai
from groq import Groq

# Dynamically append MiKTeX bin to PATH if it exists (so Windows restarts aren't required)
miktex_bin = r"C:\Users\heman\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
if os.path.exists(miktex_bin) and miktex_bin not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + miktex_bin

# Set page configuration
st.set_page_config(
    page_title="JobCraft Studio - Precision Resume & Outreach Suite",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Editorial Serif & Warm Sage Theme
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,600&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Typography & App Base */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1A2218;
    }
    
    .stApp {
        background-color: #F6F4ED !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.015em !important;
        color: #141813 !important;
    }
    
    /* Crisp White Containers with warm border */
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 12px !important;
        border: 1px solid #E5E1D6 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03) !important;
        background: #FFFFFF !important;
        transition: all 0.25s ease;
    }
    
    /* Custom Minimal Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: #D4CEBF;
        border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #BAB3A2;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background: #FFFFFF !important;
        border-right: 1px solid #E6E2D6 !important;
    }
    
    /* Primary Sage Green Buttons */
    div.stButton > button {
        background: #9BB094 !important;
        color: #141D12 !important;
        border: none !important;
        padding: 0.65rem 1.6rem !important;
        border-radius: 6px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(155, 176, 148, 0.25) !important;
    }
    div.stButton > button:hover {
        background: #8FA885 !important;
        color: #0B1209 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(155, 176, 148, 0.45) !important;
    }
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Secondary & Destructive buttons */
    div.stButton > button[data-baseweb="button"]:has(span:contains("✕")),
    div.stButton > button[data-baseweb="button"]:has(span:contains("Del")),
    div.stButton > button[data-baseweb="button"]:has(span:contains("Delete")),
    div.stButton > button[data-baseweb="button"]:has(span:contains("Clear")),
    div.stButton > button[data-baseweb="button"]:has(span:contains("Close")) {
        background: #FDF3F2 !important;
        color: #9E3535 !important;
        border: 1px solid #F5D3D0 !important;
        box-shadow: none !important;
        border-radius: 6px !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }
    div.stButton > button[data-baseweb="button"]:has(span:contains("✕")):hover,
    div.stButton > button[data-baseweb="button"]:has(span:contains("Del")):hover,
    div.stButton > button[data-baseweb="button"]:has(span:contains("Delete")):hover,
    div.stButton > button[data-baseweb="button"]:has(span:contains("Clear")):hover,
    div.stButton > button[data-baseweb="button"]:has(span:contains("Close")):hover {
        background: #FBE5E3 !important;
        color: #801E1E !important;
        transform: translateY(-1px) !important;
    }
    
    /* Input fields and textareas */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1px solid #DCD6C8 !important;
        background-color: #FFFFFF !important;
        color: #1A2218 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #8FA885 !important;
        box-shadow: 0 0 0 3px rgba(155, 176, 148, 0.25) !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #EAE6DC;
        padding: 4px;
        border-radius: 8px;
        border: 1px solid #DCD6C8;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 6px 16px;
        font-family: 'Playfair Display', Georgia, serif;
        font-weight: 600;
        font-size: 0.88rem;
        color: #555E52;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #1C2618 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Modern Popping Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.7rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-pending { background: #FAF2E3; color: #8C5F1C; border: 1px solid #EADBBE; }
    .badge-processing { background: #EBF3E8; color: #2B5722; border: 1px solid #C4DAC0; }
    .badge-done { background: #9BB094; color: #141D12; border: 1px solid #8FA885; }
    .badge-error { background: #FDF1EF; color: #9C2E24; border: 1px solid #F4C7C3; }
    
    /* Active vs Inactive Workspace Card highlight rules */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.active-workspace-card),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.active-workspace-card) > div {
        border: 2px solid #8FA885 !important;
        background: #F8FAF7 !important;
        box-shadow: 0 8px 20px rgba(155, 176, 148, 0.2) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.inactive-workspace-card):hover,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.inactive-workspace-card):hover > div {
        border: 1px solid #BACBB1 !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Metric cards styling - 50% Compact */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        border: 1px solid #E5E1D6 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
        min-height: auto !important;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        color: #636D5F !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        margin-bottom: 2px !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        color: #141813 !important;
        line-height: 1.1 !important;
    }
    
    /* Inline layout for workspace card buttons */
    .card-buttons-wrapper ~ div[data-testid="stElementContainer"] {
        display: inline-block !important;
        width: auto !important;
        margin-right: 6px !important;
        vertical-align: middle !important;
    }
    .card-buttons-wrapper ~ div[data-testid="stElementContainer"] button {
        padding: 6px 14px !important;
        font-size: 0.82rem !important;
        height: auto !important;
        min-height: unset !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- CONSTANTS & PATHS -----------------
WORKSPACE_DIR = os.getcwd()
BASE_RESUME_PATH = os.path.join(WORKSPACE_DIR, "base_resume.tex")
CSV_LOG_PATH = os.path.join(WORKSPACE_DIR, "applications_log.csv")

# ----------------- FILE INITIALIZATION -----------------
# Ensure base resume is pre-populated
if not os.path.exists(BASE_RESUME_PATH):
    default_latex = r"""\documentclass{article}
\begin{document}
Hemanth Swarna's CV
\end{document}"""
    with open(BASE_RESUME_PATH, "w", encoding="utf-8") as f:
        f.write(default_latex)

# Read base resume default content
with open(BASE_RESUME_PATH, "r", encoding="utf-8") as f:
    default_base_resume = f.read()

# ----------------- SESSION STATE INIT -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "base_resume_latex" not in st.session_state:
    st.session_state.base_resume_latex = default_base_resume

if "queue" not in st.session_state:
    st.session_state.queue = []

if "applications" not in st.session_state:
    st.session_state.applications = {}

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = None

if "current_jd_input" not in st.session_state:
    st.session_state.current_jd_input = ""

if "jd_input_counter" not in st.session_state:
    st.session_state.jd_input_counter = 0

# ----------------- AUTHENTICATION GATEKEEPER -----------------
if not st.session_state.authenticated:
    _, col_center, _ = st.columns([1, 1.4, 1])
    with col_center:
        st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                """
                <div style='text-align: center; padding: 20px 0 25px 0;'>
                    <h1 style='margin: 0 0 6px 0; font-size: 2.2rem; font-weight: 700; color: #141813;'>JobCraft Studio</h1>
                    <p style='color: #636D5F; font-size: 0.95rem; margin-top: 4px; font-weight: 500;'>Sign in to access your application workspace</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            login_user = st.text_input("Username", key="login_username_input", placeholder="Enter username")
            login_pwd = st.text_input("Password", type="password", key="login_pwd_input", placeholder="Enter password")
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Sign In ➔", use_container_width=True, type="primary"):
                u = login_user.strip()
                p = login_pwd.strip()
                if u == "admin" and p == "Remember@1":
                    st.session_state.authenticated = True
                    st.session_state.user_role = "admin"
                    st.toast("Signed in as Admin")
                    st.rerun()
                elif u == "user" and p == "I1tech":
                    st.session_state.authenticated = True
                    st.session_state.user_role = "user"
                    st.toast("Signed in successfully")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. Please try again.")
    st.stop()

# ----------------- LOCAL & ONLINE LATEX COMPILER -----------------
def compile_latex(latex_code):
    """
    Compiles LaTeX code into a PDF binary object.
    First tries online TexLive CGI compilation (from the other project),
    and falls back to local pdflatex.
    Returns (pdf_bytes, error_message).
    """
    import requests
    import time
    
    # --- METHOD 1: ONLINE CGI COMPILATION (TEXLIVE.NET) ---
    online_err_msg = None
    try:
        files = [
            ("filename[]", (None, "document.tex")),
            ("filecontents[]", ("document.tex", latex_code.encode("utf-8"), "text/plain"))
        ]
        data = {"engine": "pdflatex", "return": "pdf"}
        
        # Try compiling with a 30s timeout and 2 attempts
        for attempt in range(2):
            try:
                res = requests.post("https://texlive.net/cgi-bin/latexcgi", files=files, data=data, timeout=30)
                
                # Handle redirects
                if res.status_code in (301, 302):
                    loc = res.headers.get("location")
                    if loc:
                        res = requests.get(f"https://texlive.net{loc}", timeout=30)
                
                if res.ok:
                    content = res.content
                    if content.startswith(b"%PDF-"):
                        return content, None
                    else:
                        # Got log instead of PDF, raise error to fall back or report
                        log_msg = content.decode("utf-8", errors="ignore")
                        raise RuntimeError(f"CGI returned non-PDF. Log:\n{log_msg[-1000:]}")
            except Exception as e:
                if attempt == 1:
                    raise RuntimeError(f"Online compilation failed: {str(e)}")
                time.sleep(1)
    except Exception as online_err:
        online_err_msg = str(online_err)
        # Proceed to fallback local compilation
        pass

    # --- METHOD 2: FALLBACK TO LOCAL PDFLATEX COMPILER ---
    pdflatex_path = shutil.which("pdflatex")
    if not pdflatex_path:
        return None, (
            "LaTeX compilation failed:\n\n"
            f"- Online CGI compilation failed: {online_err_msg or 'Unknown error'}\n"
            "- Local pdflatex was not found in your system PATH."
        )

    # Configure MiKTeX dynamically to auto-install missing packages silently
    initexmf_path = shutil.which("initexmf")
    if initexmf_path:
        try:
            subprocess.run([initexmf_path, "--set-config-value", "[MPM]AutoInstall=1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        except Exception:
            pass

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file_path = os.path.join(tmpdir, "resume.tex")
        with open(tex_file_path, "w", encoding="utf-8") as f:
            f.write(latex_code)
        
        try:
            # Run pdflatex twice
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-enable-installer", "resume.tex"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30
                )
            
            pdf_file_path = os.path.join(tmpdir, "resume.pdf")
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as f:
                    return f.read(), None
            else:
                return None, f"Local LaTeX Compilation Error:\n\n{result.stdout}\n\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return None, "Local LaTeX compilation timed out (30s limit)."
        except Exception as e:
            return None, f"Local LaTeX compiler failed: {str(e)}"

# ----------------- LOCAL FILE AUTO-SAVE UTILITY -----------------
def save_files_locally(latex_content, pdf_bytes, company, download_dir):
    """
    Saves the LaTeX source and PDF binary to the user's local directory.
    Format: Hemanth_swarna_ resume.pdf and Hemanth_swarna_ resume.tex
    """
    if not download_dir:
        return None
    try:
        # Ensure download folder exists
        os.makedirs(download_dir, exist_ok=True)
        
        pdf_filename = "Hemanth_swarna_ resume.pdf"
        tex_filename = "Hemanth_swarna_ resume.tex"
        
        pdf_filepath = os.path.join(download_dir, pdf_filename)
        tex_filepath = os.path.join(download_dir, tex_filename)
        
        # Write LaTeX file
        with open(tex_filepath, "w", encoding="utf-8") as f_tex:
            f_tex.write(latex_content)
            
        # Write PDF file if we have bytes
        if pdf_bytes:
            with open(pdf_filepath, "wb") as f_pdf:
                f_pdf.write(pdf_bytes)
                
        return pdf_filepath, tex_filepath
    except Exception as e:
        print(f"Error auto-saving locally: {e}")
        return None

# ----------------- LLM CLIENT ADAPTERS -----------------
def call_llm(provider, api_key, model, prompt, response_format=None):
    """
    Calls the specified LLM provider with the API key and returns the response string.
    """
    if not api_key:
        raise ValueError(f"API Key for {provider} is required. Please set it in the sidebar.")
    
    if provider == "Google Gemini":
        genai.configure(api_key=api_key)
        # Use generative model
        generation_config = {}
        if response_format == "json":
            generation_config["response_mime_type"] = "application/json"
        
        model_instance = genai.GenerativeModel(model_name=model)
        response = model_instance.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text.strip()
        
    elif provider == "OpenAI":
        client = OpenAI(api_key=api_key)
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}
            
        chat_completion = client.chat.completions.create(**kwargs)
        return chat_completion.choices[0].message.content.strip()
        
    elif provider == "Groq":
        client = Groq(api_key=api_key)
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}
            
        chat_completion = client.chat.completions.create(**kwargs)
        return chat_completion.choices[0].message.content.strip()
        
    else:
        raise ValueError("Unsupported provider selected.")

# ----------------- PARSING & EXTRACTION -----------------
def extract_latex_from_response(response_text):
    """
    Robustly extracts the LaTeX content from LLM response text,
    stripping markdown block tags or wrapping structures.
    """
    text = response_text.strip()
    
    # 1. Check for standard markdown latex block
    if "```latex" in text:
        parts = text.split("```latex")
        text = parts[1].split("```")[0]
    elif "```tex" in text:
        parts = text.split("```tex")
        text = parts[1].split("```")[0]
    # 2. Check for general code block if no specific latex tag
    elif "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
            
    text = text.strip()
    
    # 3. Double-check and slice directly to \documentclass and \end{document}
    if "\\documentclass" in text and "\\end{document}" in text:
        start_idx = text.find("\\documentclass")
        end_idx = text.find("\\end{document}") + len("\\end{document}")
        text = text[start_idx:end_idx]
        
    return text

def parse_json_from_response(response_text):
    """
    Robustly parses JSON from the response text, stripping markdown tags if present.
    """
    text = response_text.strip()
    # Remove markdown formatting if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
            
    text = text.strip()
    return json.loads(text)

# ----------------- 7-DAY DATA RETENTION & CSV DATABASE -----------------
RETENTION_DAYS = 7

def get_cutoff_date():
    return datetime.date.today() - datetime.timedelta(days=RETENTION_DAYS)

def prune_and_load_history():
    """
    Loads applications_log.csv, prunes entries older than 7 days,
    writes back the cleaned CSV, and returns the active DataFrame.
    """
    cutoff = get_cutoff_date()
    columns = ["Date", "Company", "Job Title", "Recruiter Email", "Phone Number", "Location", "Status"]
    
    if os.path.exists(CSV_LOG_PATH):
        try:
            df = pd.read_csv(CSV_LOG_PATH)
            if not df.empty and "Date" in df.columns:
                df["ParsedDate"] = pd.to_datetime(df["Date"], errors='coerce').dt.date
                df = df[df["ParsedDate"] >= cutoff].drop(columns=["ParsedDate"], errors='ignore')
                df.to_csv(CSV_LOG_PATH, index=False)
                return df
        except Exception as e:
            print(f"Error pruning history CSV: {e}")
            
    return pd.DataFrame(columns=columns)

def log_application(company, job_title, email, phone, location, status="Generated"):
    """
    Appends the application to the daily CSV database while pruning records older than 7 days.
    """
    cutoff = get_cutoff_date()
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    new_row = {
        "Date": date_str,
        "Company": company or "N/A",
        "Job Title": job_title or "N/A",
        "Recruiter Email": email or "N/A",
        "Phone Number": phone or "N/A",
        "Location": location or "N/A",
        "Status": status
    }
    
    columns = ["Date", "Company", "Job Title", "Recruiter Email", "Phone Number", "Location", "Status"]
    if os.path.exists(CSV_LOG_PATH):
        try:
            df = pd.read_csv(CSV_LOG_PATH)
            if not df.empty and "Date" in df.columns:
                df["ParsedDate"] = pd.to_datetime(df["Date"], errors='coerce').dt.date
                df = df[df["ParsedDate"] >= cutoff].drop(columns=["ParsedDate"], errors='ignore')
            else:
                df = pd.DataFrame(columns=columns)
        except Exception:
            df = pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_LOG_PATH, index=False)
    st.session_state.history = df

def update_application_status(company, job_title, new_status):
    """
    Updates the status for the most recent matching application row in CSV.
    """
    if os.path.exists(CSV_LOG_PATH):
        try:
            df = pd.read_csv(CSV_LOG_PATH)
            matches = df[(df["Company"] == company) & (df["Job Title"] == job_title)]
            if not matches.empty:
                idx = matches.index[-1]
                df.loc[idx, "Status"] = new_status
                df.to_csv(CSV_LOG_PATH, index=False)
                st.session_state.history = df
        except Exception as e:
            print(f"Error updating CSV status: {e}")

# Load and prune 7-day history on startup
st.session_state.history = prune_and_load_history()

# ----------------- GMAIL & EMAIL DISPATCH ENGINE -----------------
def create_mime_message(sender_email, recipient_email, subject, body, pdf_bytes=None, pdf_filename="Hemanth_swarna_ resume.pdf"):
    """
    Constructs a standard RFC 2822 MIME multipart email with attached PDF.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    if recipient_email and recipient_email != "N/A" and "@" in recipient_email:
        msg['To'] = recipient_email
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid()
    
    # Text body
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # PDF Attachment
    if pdf_bytes:
        part = MIMEApplication(pdf_bytes, Name=pdf_filename)
        part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        msg.attach(part)
        
    return msg

def save_to_gmail_drafts(sender_email, app_password, recipient_email, subject, body, pdf_bytes=None, pdf_filename="Hemanth_swarna_ resume.pdf"):
    """
    Saves an email draft with attachment to Gmail's '[Gmail]/Drafts' folder via IMAP.
    Works even if recipient email is not yet available in the JD.
    Returns (success: bool, message: str)
    """
    if not sender_email or not app_password:
        return False, "Gmail App Password is not set. Please add GMAIL_APP_PASSWORD in Streamlit Secrets."
        
    clean_password = app_password.replace(" ", "").strip()
    
    try:
        recip = recipient_email if (recipient_email and recipient_email != "N/A" and "@" in recipient_email) else ""
        msg = create_mime_message(sender_email, recip, subject, body, pdf_bytes, pdf_filename)
        raw_msg = msg.as_bytes()
        
        # Connect to Gmail IMAP
        imap = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=20)
        try:
            imap.login(sender_email, clean_password)
        except imaplib.IMAP4.error as auth_err:
            return False, f"Gmail Login Failed (Invalid App Password). Please generate a new App Password in your Google Account: {str(auth_err)}"
        
        folder_candidates = ['"[Gmail]/Drafts"', 'Drafts', '"[Google Mail]/Drafts"']
        saved = False
        last_err = ""
        for folder in folder_candidates:
            try:
                res, data = imap.append(folder, r'(\Draft)', imaplib.Time2Internaldate(time.time()), raw_msg)
                if res == "OK":
                    saved = True
                    break
            except Exception as fe:
                last_err = str(fe)
                
        # If standard candidate names failed, query server for Drafts folder
        if not saved:
            try:
                res, mailboxes = imap.list()
                if res == "OK":
                    for box in mailboxes:
                        box_str = box.decode("utf-8", errors="ignore")
                        if "draft" in box_str.lower():
                            parts = box_str.split(' "/" ')
                            if len(parts) >= 2:
                                folder_name = parts[1].strip()
                                res, data = imap.append(folder_name, r'(\Draft)', imaplib.Time2Internaldate(time.time()), raw_msg)
                                if res == "OK":
                                    saved = True
                                    break
            except Exception as fe2:
                last_err = str(fe2)
                
        imap.logout()
        
        if saved:
            return True, "Draft created in your Gmail Drafts folder with resume attached!"
        else:
            return False, f"Could not save draft to Gmail Drafts folder: {last_err}"
    except Exception as e:
        return False, f"Gmail IMAP error: {str(e)}"

def send_email_smtp(sender_email, app_password, recipient_email, subject, body, pdf_bytes=None, pdf_filename="Hemanth_swarna_ resume.pdf"):
    """
    Sends an email with attachment directly via Gmail SMTP.
    Returns (success: bool, message: str)
    """
    if not sender_email or not app_password:
        return False, "Sender email and Gmail App Password are required."
    if not recipient_email or recipient_email == "N/A" or "@" not in recipient_email:
        return False, f"Invalid recipient email address: '{recipient_email}'"
        
    clean_password = app_password.replace(" ", "").strip()
    
    try:
        msg = create_mime_message(sender_email, recipient_email, subject, body, pdf_bytes, pdf_filename)
        
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=25)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, clean_password)
        server.sendmail(sender_email, [recipient_email], msg.as_string())
        server.quit()
        return True, f"Email sent successfully to {recipient_email}!"
    except Exception as e:
        return False, f"Gmail SMTP error: {str(e)}"

def test_gmail_credentials(sender_email, app_password):
    """
    Tests IMAP and SMTP login to verify Gmail App Password.
    """
    if not sender_email or not app_password:
        return False, "Please enter both Sender Email and Gmail App Password."
        
    clean_password = app_password.replace(" ", "").strip()
    errors = []
    
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=10)
        imap.login(sender_email, clean_password)
        imap.logout()
    except Exception as e:
        errors.append(f"IMAP Login failed: {str(e)}")
        
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, clean_password)
        server.quit()
    except Exception as e:
        errors.append(f"SMTP Login failed: {str(e)}")
        
    if errors:
        return False, "\n".join(errors)
    return True, "Gmail connection successful! Both Draft creation (IMAP) and 1-Click Sending (SMTP) are verified."

# ----------------- BACKGROUND JOB WORKER ENGINE -----------------
class BackgroundJobManager:
    """
    Manages asynchronous, non-blocking execution of resume tailoring,
    PDF compilation, auto-saving, and Gmail draft generation in worker threads.
    """
    def __init__(self, max_workers=5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs = {}  # job_id -> {id, status, progress, error, result}
        self.lock = threading.Lock()

    def submit_job(self, job_id, jd_text, provider, api_key, cheaper_model, premium_model,
                   base_resume_latex, sender_email, gmail_app_password, auto_create_draft, download_dir):
        with self.lock:
            self.jobs[job_id] = {
                "id": job_id,
                "status": "Processing",
                "progress": "🚀 Initializing background task...",
                "error": None,
                "result": None
            }
        
        self.executor.submit(
            self._run_job_pipeline,
            job_id, jd_text, provider, api_key, cheaper_model, premium_model,
            base_resume_latex, sender_email, gmail_app_password, auto_create_draft, download_dir
        )

    def _update_progress(self, job_id, progress_msg):
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["progress"] = progress_msg

    def _run_job_pipeline(self, job_id, jd_text, provider, api_key, cheaper_model, premium_model,
                          base_resume_latex, sender_email, gmail_app_password, auto_create_draft, download_dir):
        try:
            # --- STEP 1: EXTRACT METADATA, LOCATION & WRITE COVER EMAIL ---
            self._update_progress(job_id, "Processing...")
            
            metadata_extraction_prompt = f"""
            Analyze the following Job Description (JD) and extract the contact/vendor information, location, and write a cover email.
            Return a JSON object containing:
            1. 'email': The email address to send the application to (e.g., recruiter's or vendor's email). Look for patterns like mailto, resumes to, send to, contact, or general email addresses. If none found, write 'N/A'.
            2. 'phone': The phone number to contact the recruiter/vendor. If none, write 'N/A'.
            3. 'location': The job location / work arrangement (e.g., 'New York, NY (Hybrid)', 'Remote', 'Dallas, TX', 'Austin, TX (Onsite)'). If none found, write 'N/A'.
            4. 'company': The client or vendor company name. If none, write 'N/A'.
            5. 'job_title': The official job title. If none, write 'N/A'.
            6. 'subject': A professional email subject line for the job application that INCLUDES the extracted location if available. Do NOT include the applicant's name in the subject line. Format MUST be:
               - If location is available: 'Application for [Job Title] - [Location]' (e.g., 'Application for Senior Data Scientist - New York, NY (Hybrid)' or 'Application for Lead ML Engineer - Remote').
               - If location is N/A: 'Application for [Job Title]'.
            7. 'email_body': A short, clear, and compelling cover email body following this EXACT format:

Dear [Recruiter Name if mentioned in JD, otherwise 'Recruiting Team'],

[1-2 clear, punchy paragraphs explaining why Hemanth Swarna is an exceptional fit for the [Job Title] position. Highlight relevant skills matching the JD from his background: 12+ years experience, GenAI (RAG, AWS Bedrock, LangGraph, LlamaIndex), Machine Learning, and Big Data.]

Hemanth Swarna
hemanthswarna3838@gmail.com
2139866016
www.linkedin.com/in/swarna-hemanth
            
            Ensure the JSON output is well-formed.
            
            JD to analyze:
            -----------------
            {jd_text}
            -----------------
            
            JSON format:
            """
            
            metadata_raw = call_llm(
                provider=provider,
                api_key=api_key,
                model=cheaper_model,
                prompt=metadata_extraction_prompt,
                response_format="json"
            )
            metadata = parse_json_from_response(metadata_raw)
            
            company_name = metadata.get("company", "N/A")
            job_title_val = metadata.get("job_title", "N/A")
            recipient_email_val = metadata.get("email", "N/A")
            location_val = metadata.get("location", "N/A")
            
            # Post-process subject line: Remove any candidate name and ensure clean location format
            subject_val = metadata.get("subject", "").strip()
            subject_val = re.sub(r'[\s\-–—|,:]*(?:Hemanth\s*Swarna|Hemanth).*$', '', subject_val, flags=re.IGNORECASE).strip()
            if not subject_val or subject_val == "N/A":
                if location_val and location_val != "N/A":
                    subject_val = f"Application for {job_title_val} - {location_val}"
                else:
                    subject_val = f"Application for {job_title_val}"
            elif location_val and location_val != "N/A" and location_val.lower() not in subject_val.lower():
                subject_val = f"{subject_val} - {location_val}"
                
            # Post-process email body: Enforce standard signature structure with LinkedIn URL
            email_body_val = metadata.get("email_body", "").strip()
            standard_signature = (
                "Hemanth Swarna\n"
                "hemanthswarna3838@gmail.com\n"
                "2139866016\n"
                "www.linkedin.com/in/swarna-hemanth"
            )
            
            body_cleaned = re.sub(
                r'(?:(?:Best|Warm|Kind)?\s*regards|Sincerely|Thanks|Thank you|Best|Cheers)?[\s,]*\n*(?:Hemanth\s*Swarna)?[\s\S]*$',
                '',
                email_body_val,
                flags=re.IGNORECASE
            ).strip()
            if len(body_cleaned) < 50:
                body_cleaned = email_body_val
                for token in ["Hemanth Swarna", "hemanthswarna3838@gmail.com", "2139866016", "www.linkedin.com/in/swarna-hemanth", "linkedin.com/in/swarna-hemanth"]:
                    body_cleaned = body_cleaned.replace(token, "").strip()
                body_cleaned = re.sub(r'(?:(?:Best|Warm|Kind)?\s*regards|Sincerely|Thanks|Thank you|Best)[\s,]*$', '', body_cleaned, flags=re.IGNORECASE).strip()
                
            email_body_val = f"{body_cleaned}\n\n{standard_signature}"
                
            # --- STEP 2: TAILOR RESUME IN LATEX ---
            self._update_progress(job_id, "Processing...")
            
            resume_editor_prompt = f"""
            You are a professional resume editor. Take the base resume in LaTeX form and the target JD below.
            Extract all the keywords in the JD and see if there are any missing in the base resume.
            Implement the necessary changes as per the JD in the resume by keeping the structure of the resume intact:
            - Do NOT change the company names (FedEx, Citi Bank, CVS Health, State of Maryland) or timelines.
            - Keep the number of bullet points under each section exactly the same as the base resume.
            - Keep the size/length of each corresponding bullet point approximately same.
            - Inject high-density keywords and skills from the JD into the bullet points where relevant, maintaining professional tone.
            - Ensure all LaTeX control characters (like &, %, _) are properly escaped (e.g. use \\&, \\%, \\_).
            - Output ONLY valid LaTeX code. Do not include markdown code wrapping blocks, explanations, or chats. Make sure there are no syntax errors so it compiles cleanly.
            
            BASE RESUME:
            -----------------
            {base_resume_latex}
            -----------------
            
            TARGET JOB DESCRIPTION:
            -----------------
            {jd_text}
            -----------------
            """
            
            resume_raw = call_llm(
                provider=provider,
                api_key=api_key,
                model=premium_model,
                prompt=resume_editor_prompt
            )
            latex_content = extract_latex_from_response(resume_raw)
            
            # --- STEP 3: COMPILE PDF (WITH BASE RESUME FALLBACK) ---
            self._update_progress(job_id, "Processing...")
            pdf_bytes, compile_err = compile_latex(latex_content)
            is_base_fallback = False
            
            # If tailored LaTeX compilation had an issue, automatically fall back to base resume PDF for draft
            if not pdf_bytes:
                self._update_progress(job_id, "Processing...")
                base_pdf_bytes, _ = compile_latex(base_resume_latex)
                if base_pdf_bytes:
                    pdf_bytes = base_pdf_bytes
                    is_base_fallback = True
            
            # --- STEP 4: AUTO-SAVE LOCALLY ---
            self._update_progress(job_id, "Processing...")
            if download_dir and pdf_bytes:
                save_files_locally(
                    latex_content=latex_content,
                    pdf_bytes=pdf_bytes,
                    company=company_name,
                    download_dir=download_dir
                )
                
            # --- STEP 5: GMAIL DRAFT CREATION ---
            draft_status_msg = "Draft ready locally"
            draft_created_in_gmail = False
            
            if auto_create_draft and gmail_app_password:
                self._update_progress(job_id, "Processing...")
                draft_ok, draft_res = save_to_gmail_drafts(
                    sender_email=sender_email,
                    app_password=gmail_app_password,
                    recipient_email=recipient_email_val,
                    subject=subject_val,
                    body=email_body_val,
                    pdf_bytes=pdf_bytes,
                    pdf_filename="Hemanth_swarna_ resume.pdf"
                )
                if draft_ok:
                    draft_status_msg = "Saved in Gmail Drafts"
                    draft_created_in_gmail = True
                else:
                    draft_status_msg = f"Draft warning: {draft_res}"
            elif not gmail_app_password:
                draft_status_msg = "Draft ready locally (Configure GMAIL_APP_PASSWORD in Secrets / Sidebar to sync to Gmail)"
                
            # Log in contact log CSV
            log_application(
                company=company_name,
                job_title=job_title_val,
                email=recipient_email_val,
                phone=metadata.get("phone", "N/A"),
                location=location_val,
                status="Drafted" if draft_created_in_gmail else "Generated"
            )
            
            # Application Payload
            app_payload = {
                "id": job_id,
                "jd_text": jd_text,
                "job_title": job_title_val,
                "company": company_name,
                "email": recipient_email_val,
                "phone": metadata.get("phone", "N/A"),
                "location": location_val,
                "subject": subject_val,
                "email_body": email_body_val,
                "latex_content": latex_content,
                "pdf_bytes": pdf_bytes,
                "compile_error": compile_err,
                "is_base_fallback": is_base_fallback,
                "draft_status": draft_status_msg,
                "draft_created_in_gmail": draft_created_in_gmail,
                "email_sent": False,
                "sent_time": None
            }
            
            with self.lock:
                self.jobs[job_id]["status"] = "Done"
                self.jobs[job_id]["progress"] = "Completed successfully!"
                self.jobs[job_id]["result"] = app_payload
                
        except Exception as e:
            with self.lock:
                self.jobs[job_id]["status"] = "Error"
                self.jobs[job_id]["error"] = str(e)
                self.jobs[job_id]["progress"] = f"Error: {str(e)}"

    def get_job(self, job_id):
        with self.lock:
            return self.jobs.get(job_id)

@st.cache_resource
def get_job_manager():
    return BackgroundJobManager(max_workers=5)

# ----------------- DYNAMIC MODEL FETCHER -----------------
def get_available_models(provider, api_key):
    """
    Attempts to fetch available models for the given provider and api key.
    Falls back to a standard default list if the API call fails or key is empty.
    """
    if not api_key:
        return get_fallback_models(provider)
        
    try:
        if provider == "Google Gemini":
            genai.configure(api_key=api_key)
            models = genai.list_models()
            names = []
            for m in models:
                name = m.name.replace("models/", "")
                # Only keep relevant models containing 'gemini' and support generateContent
                if "gemini" in name.lower() and "generateContent" in m.supported_generation_methods:
                    # Filter out embedding, vision-legacy, tuning, aqa, and translation models
                    if not any(x in name.lower() for x in ["embed", "vision-legacy", "tuning", "aqa", "experimental", "translation"]):
                        names.append(name)
            if names:
                return sorted(list(set(names)))
        elif provider == "OpenAI":
            client = OpenAI(api_key=api_key)
            models_data = client.models.list().data
            names = []
            for m in models_data:
                id_lower = m.id.lower()
                # Only keep standard gpt models or o1/o3
                if ("gpt-" in id_lower or "o1-" in id_lower or "o3-" in id_lower or id_lower in ["gpt-4", "gpt-4o", "gpt-4o-mini", "o1", "o3-mini"]):
                    if not any(x in id_lower for x in ["vision", "instruct", "realtime", "audio", "moderation", "embedding"]):
                        names.append(m.id)
            if names:
                return sorted(list(set(names)))
        elif provider == "Groq":
            client = Groq(api_key=api_key)
            models_data = client.models.list().data
            names = []
            for m in models_data:
                id_lower = m.id.lower()
                # Exclude whisper, preview, guard models
                if not any(x in id_lower for x in ["whisper", "guard", "preview"]):
                    names.append(m.id)
            if names:
                return sorted(list(set(names)))
    except Exception:
        pass
        
    return get_fallback_models(provider)

def get_fallback_models(provider):
    if provider == "Google Gemini":
        return ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-flash-lite-latest", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    elif provider == "OpenAI":
        return ["gpt-4o-mini", "gpt-4o", "o1-mini"]
    elif provider == "Groq":
        return ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
    return []

def get_cached_models(provider, api_key):
    cache_key = f"{provider}_{api_key}"
    if "models_cache" not in st.session_state:
        st.session_state.models_cache = {}
        
    if cache_key not in st.session_state.models_cache:
        # Fetch dynamically
        st.session_state.models_cache[cache_key] = get_available_models(provider, api_key)
        
    return st.session_state.models_cache[cache_key]

def get_default_index(options, targets):
    for target in targets:
        if target in options:
            return options.index(target)
    return 0

# ----------------- UI: SIDEBAR -----------------
is_admin = (st.session_state.get("user_role") == "admin")

# Helper to read from Streamlit secrets (Streamlit Cloud) or Environment variables
def get_secret(key_name, fallback=""):
    try:
        # Check direct key in st.secrets
        if key_name in st.secrets:
            return str(st.secrets[key_name]).strip()
        # Check uppercase / lowercase in st.secrets
        if key_name.upper() in st.secrets:
            return str(st.secrets[key_name.upper()]).strip()
        if key_name.lower() in st.secrets:
            return str(st.secrets[key_name.lower()]).strip()
    except Exception:
        pass
    # Check os.environ
    val = os.environ.get(key_name, None) or os.environ.get(key_name.upper(), None) or os.environ.get(key_name.lower(), None)
    if val:
        return str(val).strip()
    return fallback

# Safe default values used in background execution for all users
provider = "Google Gemini"
api_key = get_secret("GEMINI_API_KEY", "") or get_secret("GOOGLE_API_KEY", "") or get_secret("API_KEY", "")
premium_model = "gemini-3.1-flash-lite"
cheaper_model = "gemini-3.1-flash-lite"
sender_email = get_secret("SENDER_EMAIL", "") or get_secret("EMAIL", "") or "hemanthswarna3838@gmail.com"
gmail_app_password = get_secret("GMAIL_APP_PASSWORD", "") or get_secret("GMAIL_PASSWORD", "") or get_secret("APP_PASSWORD", "")
auto_create_draft = True

default_downloads_folder = os.environ.get("DOWNLOAD_DIR", "")
if not default_downloads_folder:
    if os.name == 'nt' and os.path.exists(r"C:\Desktop\i1"):
        default_downloads_folder = r"C:\Desktop\i1"
    else:
        default_downloads_folder = os.path.join(WORKSPACE_DIR, "downloads")
try:
    os.makedirs(default_downloads_folder, exist_ok=True)
except Exception:
    default_downloads_folder = tempfile.gettempdir()
download_dir = default_downloads_folder

with st.sidebar:
    st.markdown(
        """
        <div style='padding: 10px 0 16px 0; border-bottom: 1px solid #E6E2D6; margin-bottom: 16px;'>
            <h2 style='margin: 0; font-size: 1.5rem; font-weight: 700; color: #141813;'>JobCraft Studio</h2>
            <p style='margin: 4px 0 0 0; font-size: 0.82rem; color: #636D5F; font-weight: 500;'>Application Suite</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if is_admin:
        st.markdown("<span style='background: #E8F0E6; color: #1E2818; border: 1px solid #BACBB1; padding: 4px 12px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.05em;'>ADMINISTRATOR</span>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
        
        # API Configuration Expanders
        with st.expander("API Credentials & Engine", expanded=True):
            provider = st.selectbox(
                "Select API Provider",
                ["Google Gemini", "OpenAI", "Groq"]
            )
            
            # Load API keys from Streamlit secrets or env variables if present
            default_key = ""
            if provider == "Google Gemini":
                default_key = get_secret("GEMINI_API_KEY", "")
            elif provider == "OpenAI":
                default_key = get_secret("OPENAI_API_KEY", "")
            elif provider == "Groq":
                default_key = get_secret("GROQ_API_KEY", "")
                
            api_key = st.text_input(
                f"Enter {provider} API Key",
                value=default_key,
                type="password"
            )
            
            # Test Connection button
            if st.button("Test Connection ➔", use_container_width=True):
                if not api_key:
                    st.error("Please enter an API Key first.")
                else:
                    try:
                        if provider == "Google Gemini":
                            genai.configure(api_key=api_key)
                            models = genai.list_models()
                            model_names = [m.name for m in models]
                            display_names = [n.replace("models/", "") for n in model_names]
                            st.success("Connection Successful!")
                            st.write("Available Gemini Models:")
                            st.code("\n".join(display_names), language="text")
                        elif provider == "OpenAI":
                            client = OpenAI(api_key=api_key)
                            models_data = client.models.list().data
                            model_names = [m.id for m in models_data]
                            st.success("Connection Successful!")
                            st.write("Available OpenAI Models:")
                            st.code("\n".join(sorted(model_names)), language="text")
                        elif provider == "Groq":
                            client = Groq(api_key=api_key)
                            models_data = client.models.list().data
                            model_names = [m.id for m in models_data]
                            st.success("Connection Successful!")
                            st.write("Available Groq Models:")
                            st.code("\n".join(sorted(model_names)), language="text")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")

            st.markdown("---")
            
            # Fetch models list dynamically based on key
            models_options = get_cached_models(provider, api_key)
            dropdown_options = models_options + ["Custom..."]
            
            # Premium model default targets
            p_targets = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-flash-lite-latest", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro", "gpt-4o", "llama-3.1-70b-versatile"]
            p_default_idx = get_default_index(dropdown_options, p_targets)
            
            p_sel = st.selectbox(
                "Premium Model (Resume)", 
                dropdown_options, 
                index=p_default_idx
            )
            if p_sel == "Custom...":
                premium_model = st.text_input("Enter Premium Model Name", value=p_targets[0] if p_targets[0] in dropdown_options else dropdown_options[0])
            else:
                premium_model = p_sel
                
            # Cheaper model default targets
            c_targets = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-flash-lite-latest", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gpt-4o-mini", "llama-3.1-8b-instant"]
            c_default_idx = get_default_index(dropdown_options, c_targets)
            
            c_sel = st.selectbox(
                "Cheaper Model (Email)", 
                dropdown_options, 
                index=c_default_idx
            )
            if c_sel == "Custom...":
                cheaper_model = st.text_input("Enter Cheaper Model Name", value=c_targets[0] if c_targets[0] in dropdown_options else dropdown_options[0])
            else:
                cheaper_model = c_sel

        # Gmail & Draft Automation Settings Expander
        with st.expander("Gmail & Automation", expanded=True):
            st.caption("Auto-create Gmail Drafts & send applications with 1-click.")
            
            sender_email = st.text_input(
                "Sender Email",
                value="hemanthswarna3838@gmail.com",
                help="Your Gmail address from which drafts and emails will be created/sent."
            )
            
            gmail_app_password = st.text_input(
                "Gmail App Password (16 chars)",
                value=get_secret("GMAIL_APP_PASSWORD", ""),
                type="password",
                help="16-character Google App Password."
            )
            
            auto_create_draft = st.checkbox(
                "Auto-save Draft to Gmail on JD run",
                value=True,
                help="Automatically uploads a draft with the tailored resume PDF attached to your Gmail 'Drafts' folder."
            )
            
            col_test_gmail, col_guide_gmail = st.columns([1.2, 1])
            with col_test_gmail:
                if st.button("Test Auth ➔", use_container_width=True):
                    with st.spinner("Testing Gmail connection..."):
                        is_ok, test_resp = test_gmail_credentials(sender_email, gmail_app_password)
                        if is_ok:
                            st.success(test_resp)
                        else:
                            st.error(test_resp)
                            
            with col_guide_gmail:
                with st.popover("Setup Guide", use_container_width=True):
                    st.markdown("""
                    ### How to get a Google App Password:
                    1. Open [Google Account Security](https://myaccount.google.com/security).
                    2. Make sure **2-Step Verification** is ON.
                    3. Visit **[https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)**.
                    4. Create app name `JobCraft Studio` and copy the 16-character code.
                    """)

        # Base Resume Editor Expander
        with st.expander("Base Resume Template", expanded=False):
            st.caption("This is your reference resume structure.")
            base_resume_input = st.text_area(
                "LaTeX Code",
                value=st.session_state.base_resume_latex,
                height=400
            )
            if base_resume_input != st.session_state.base_resume_latex:
                st.session_state.base_resume_latex = base_resume_input
                with open(BASE_RESUME_PATH, "w", encoding="utf-8") as f:
                    f.write(base_resume_input)
                st.toast("Base resume saved")
                
        # Local Download Folder Configuration
        st.subheader("Auto-Save Directory")
        download_dir = st.text_input(
            "Local Directory Path",
            value=default_downloads_folder,
            help="Tailored PDF & LaTeX resumes will be automatically written here."
        )
                
        # Contact Logging Section
        st.subheader("Logged Contacts")
        log_df = st.session_state.history
        
        # Filter for today's logs
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        today_df = log_df[log_df["Date"] == today_str] if not log_df.empty else log_df
        
        if not today_df.empty:
            st.dataframe(
                today_df[["Company", "Job Title", "Recruiter Email", "Phone Number", "Location"]],
                use_container_width=True,
                hide_index=True
            )
            csv_data = today_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Log CSV",
                data=csv_data,
                file_name=f"job_applications_log_{today_str}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No applications logged today yet.")
    else:
        # Standard User Clean View (No API / Gmail / Auto-save configs)
        st.markdown("<span style='background: #E8F0E6; color: #1E2818; border: 1px solid #BACBB1; padding: 4px 12px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.05em;'>STANDARD USER</span>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='background: #F6F4ED; border: 1px solid #E5E1D6; border-radius: 8px; padding: 14px;'>
                <h4 style='margin: 0 0 8px 0; font-size: 0.92rem; color: #141813;'>How to use:</h4>
                <ol style='margin: 0; padding-left: 18px; font-size: 0.85rem; color: #555E52; line-height: 1.5;'>
                    <li>Paste any Job Description in the input box.</li>
                    <li>Click <b>Queue & Run</b>.</li>
                    <li>Download your customized resume and outreach email.</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    if st.button("Log Out ➔", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()

# ----------------- MAIN LAYOUT -----------------
# Header banner with statistics
total_apps = len(st.session_state.applications)
pending_queue = sum(1 for j in st.session_state.queue if j["status"] in ["Pending", "Error"])
today_str = datetime.date.today().strftime("%Y-%m-%d")
apps_today = len(st.session_state.history[st.session_state.history["Date"] == today_str]) if not st.session_state.history.empty else 0

st.markdown("""
<div style="background: #FFFFFF; padding: 0.9rem 1.4rem; border-radius: 10px; margin-bottom: 0.8rem; border: 1px solid #E5E1D6; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
    <div>
        <h2 style="margin: 0; font-size: 1.55rem; font-weight: 700; color: #141813; letter-spacing: -0.015em; line-height: 1.2;">
            JobCraft Studio
        </h2>
    </div>
    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">
        <span style="background: #9BB094; color: #141D12; padding: 4px 10px; border-radius: 4px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;">
            Hemanth Swarna
        </span>
        <span style="background: #F6F4ED; color: #344030; border: 1px solid #D8D2C4; padding: 4px 10px; border-radius: 4px; font-size: 0.78rem; font-weight: 500;">
            hemanthswarna3838@gmail.com
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Metrics row
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric(label="● Active Workspaces", value=total_apps)
with m_col2:
    st.metric(label="● In Queue", value=pending_queue)
with m_col3:
    st.metric(label="● Logged Today", value=apps_today)

st.markdown("<div style='margin-bottom: 0.6rem;'></div>", unsafe_allow_html=True)

main_tabs = st.tabs(["Tailoring Workspace", "Application History"])

with main_tabs[0]:
    left_col, right_col = st.columns([1, 1.2])
    
    # ----------------- LEFT COLUMN: JD INPUT & QUEUE -----------------
    with left_col:
        st.header("Job Descriptions Queue")
        
        # File uploader option
        uploaded_file = st.file_uploader(
            "Upload Job Description (TXT or PDF)", 
            type=["txt", "pdf"],
            key=f"jd_uploader_{st.session_state.jd_input_counter}"
        )
        if uploaded_file is not None:
            try:
                # Read text
                if uploaded_file.name.lower().endswith(".pdf"):
                    import pypdf
                    reader = pypdf.PdfReader(uploaded_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    new_text = text.strip()
                else:
                    new_text = uploaded_file.read().decode("utf-8").strip()
                
                # Update text area value
                if new_text and new_text != st.session_state.current_jd_input:
                    st.session_state.current_jd_input = new_text
                    st.session_state.jd_input_counter += 1
                    st.toast("File text loaded successfully")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

        # Text Box to Paste New Job Description
        new_jd = st.text_area(
            "Paste Job Description (JD) here:",
            value=st.session_state.current_jd_input,
            placeholder="Include job title, company name, recruiter email, phone, location, and requirements...",
            height=200,
            key=f"jd_text_area_{st.session_state.jd_input_counter}"
        )
        
        # Get Job Manager singleton
        job_mgr = get_job_manager()

        # Sync background worker results to session state
        has_running_jobs = False
        for q_item in st.session_state.queue:
            q_id = q_item["id"]
            bg_job = job_mgr.get_job(q_id)
            if bg_job:
                q_item["status"] = bg_job["status"]
                q_item["progress"] = bg_job.get("progress", "")
                q_item["error"] = bg_job.get("error")
                if bg_job["status"] == "Done" and bg_job["result"]:
                    if q_id not in st.session_state.applications:
                        st.session_state.applications[q_id] = bg_job["result"]
                        if not st.session_state.selected_tab:
                            st.session_state.selected_tab = q_id
            if q_item["status"] == "Processing":
                has_running_jobs = True

        # Action Buttons for JD Queue
        q_col1, q_col2, q_col3 = st.columns([1.5, 1, 1])
        
        with q_col1:
            if st.button("▶ Queue & Run", use_container_width=True, type="primary"):
                if new_jd.strip():
                    if not api_key:
                        st.error("Please enter an API Key in the sidebar or Secrets first.")
                    else:
                        jd_id = f"job_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(st.session_state.queue) + 1}"
                        lines = [l.strip() for l in new_jd.strip().split("\n") if l.strip()]
                        preview_title = lines[0][:40] + "..." if lines else "Untitled JD"
                        
                        st.session_state.queue.append({
                            "id": jd_id,
                            "jd_text": new_jd,
                            "preview": preview_title,
                            "status": "Processing",
                            "progress": "",
                            "error": None
                        })
                        
                        job_mgr.submit_job(
                            job_id=jd_id,
                            jd_text=new_jd,
                            provider=provider,
                            api_key=api_key,
                            cheaper_model=cheaper_model,
                            premium_model=premium_model,
                            base_resume_latex=st.session_state.base_resume_latex,
                            sender_email=sender_email,
                            gmail_app_password=gmail_app_password,
                            auto_create_draft=auto_create_draft,
                            download_dir=download_dir
                        )
                        
                        # Immediately clear input & increment counter so text area is 100% empty and ready for next JD
                        st.session_state.current_jd_input = ""
                        st.session_state.jd_input_counter += 1
                        st.toast("Application queued")
                        st.rerun()
                else:
                    st.error("Please paste a job description first.")
                    
        with q_col2:
            if st.button("+ Add to Queue", use_container_width=True):
                if new_jd.strip():
                    jd_id = f"job_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(st.session_state.queue) + 1}"
                    lines = [l.strip() for l in new_jd.strip().split("\n") if l.strip()]
                    preview_title = lines[0][:40] + "..." if lines else "Untitled JD"
                    st.session_state.queue.append({
                        "id": jd_id,
                        "jd_text": new_jd,
                        "preview": preview_title,
                        "status": "Pending",
                        "progress": "",
                        "error": None
                    })
                    st.session_state.current_jd_input = ""
                    st.session_state.jd_input_counter += 1
                    st.toast("Added job to queue")
                    st.rerun()
                else:
                    st.error("Please paste a job description first.")
                    
        with q_col3:
            if st.button("▶ Run Pending", use_container_width=True):
                pending_jobs = [j for j in st.session_state.queue if j["status"] in ["Pending", "Error"]]
                if not pending_jobs:
                    st.info("No pending jobs to process.")
                elif not api_key:
                    st.error("Please enter an API Key in the sidebar first.")
                else:
                    for pj in pending_jobs:
                        pj["status"] = "Processing"
                        pj["progress"] = ""
                        pj["error"] = None
                        job_mgr.submit_job(
                            job_id=pj["id"],
                            jd_text=pj["jd_text"],
                            provider=provider,
                            api_key=api_key,
                            cheaper_model=cheaper_model,
                            premium_model=premium_model,
                            base_resume_latex=st.session_state.base_resume_latex,
                            sender_email=sender_email,
                            gmail_app_password=gmail_app_password,
                            auto_create_draft=auto_create_draft,
                            download_dir=download_dir
                        )
                    st.toast(f"Processing {len(pending_jobs)} job(s)")
                    st.rerun()

        st.markdown("---")
        
        # Self-refreshing Queue Status Fragment for smooth live updates without page freeze
        @st.fragment(run_every="2s" if has_running_jobs else None)
        def render_queue_status():
            st.subheader("Queue Status")
            with st.container(height=350):
                if not st.session_state.queue:
                    st.caption("Your queue is empty. Paste a JD above and click 'Queue & Run' to begin.")
                else:
                    for idx, job in enumerate(st.session_state.queue):
                        card_id = job["id"]
                        
                        # Sync latest status from manager if running
                        bg = job_mgr.get_job(card_id)
                        if bg:
                            job["status"] = bg["status"]
                            job["progress"] = bg.get("progress", "")
                            job["error"] = bg.get("error")
                            if bg["status"] == "Done" and bg["result"]:
                                if card_id not in st.session_state.applications:
                                    st.session_state.applications[card_id] = bg["result"]
                        
                        status = job["status"]
                        
                        # Badge styles
                        if status == "Pending":
                            badge_html = '<span class="badge badge-pending">Pending</span>'
                        elif status == "Processing":
                            badge_html = '<span class="badge badge-processing">Processing...</span>'
                        elif status == "Done":
                            badge_html = '<span class="badge badge-done">Completed</span>'
                        elif status == "Error":
                            badge_html = '<span class="badge badge-error">Failed</span>'
                        else:
                            badge_html = f'<span class="badge badge-pending">{status}</span>'
                        
                        with st.container(border=True):
                            c_title, c_badge = st.columns([2, 1])
                            with c_title:
                                st.markdown(f"**Job #{idx+1}**")
                            with c_badge:
                                st.markdown(badge_html, unsafe_allow_html=True)
                                
                            st.markdown(f"<div style='font-size:0.85rem; color:#636D5F; margin-bottom: 0.5rem;'>{job['preview']}</div>", unsafe_allow_html=True)
                            
                            # Action buttons for this card
                            c1, c2, c3 = st.columns([1, 1, 1])
                            with c1:
                                if st.button("▶ Run", key=f"gen_{card_id}", disabled=(status == "Processing"), use_container_width=True):
                                    if not api_key:
                                        st.error("Enter API Key in sidebar first.")
                                    else:
                                        job["status"] = "Processing"
                                        job["error"] = None
                                        job_mgr.submit_job(
                                            job_id=card_id,
                                            jd_text=job["jd_text"],
                                            provider=provider,
                                            api_key=api_key,
                                            cheaper_model=cheaper_model,
                                            premium_model=premium_model,
                                            base_resume_latex=st.session_state.base_resume_latex,
                                            sender_email=sender_email,
                                            gmail_app_password=gmail_app_password,
                                            auto_create_draft=auto_create_draft,
                                            download_dir=download_dir
                                        )
                                        st.rerun()
                            with c2:
                                with st.popover("◎ Details", use_container_width=True):
                                    st.text_area("Full Job Description", value=job["jd_text"], height=300, disabled=True, key=f"jd_text_view_{card_id}")
                            with c3:
                                if st.button("✕ Del", key=f"del_{card_id}", use_container_width=True):
                                    st.session_state.queue.pop(idx)
                                    st.toast("Removed job from queue")
                                    st.rerun()
                                    
                            if job.get("error"):
                                st.error(f"Error: {job['error']}")

        render_queue_status()
    
    # ----------------- RIGHT COLUMN: TAILORED OUTPUTS -----------------
    with right_col:
        st.header("Tailored Output & Files")
        
        with st.container(height=800):
            if not st.session_state.applications:
                st.markdown(
                    """
                    <div style="text-align: center; padding: 80px 20px; color: #636D5F;">
                        <h3 style="margin: 0 0 8px 0; color: #141813; font-weight: 700; font-size: 1.5rem;">No Active Workspaces</h3>
                        <p style="margin: 0 auto; max-width: 420px; font-size: 0.95rem; color: #636D5F; line-height: 1.6;">
                            Paste a Job Description on the left and click <b>Queue & Run</b>. Your customized resumes and cover emails will appear here.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            else:
                apps_dict = st.session_state.applications
                app_keys = list(apps_dict.keys())
                
                hdr_col1, hdr_col2 = st.columns([3, 1])
                with hdr_col1:
                    st.markdown(f"##### ● Active Workspaces ({len(app_keys)})")
                with hdr_col2:
                    if st.button("✕ Clear All", key="clear_all_workspaces", use_container_width=True, help="Clear all generated workspaces"):
                        st.session_state.applications = {}
                        st.session_state.selected_tab = None
                        st.toast("Cleared all workspaces")
                        st.rerun()
                        
                st.markdown('<div class="workspace-scroll-marker"></div>', unsafe_allow_html=True)
                
                cols = st.columns(len(app_keys))
                for index, key in enumerate(app_keys):
                    app = apps_dict[key]
                    is_active = (st.session_state.selected_tab == key)
                    
                    with cols[index]:
                        with st.container(border=True):
                            if is_active:
                                st.markdown('<div class="active-workspace-card"></div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="inactive-workspace-card"></div>', unsafe_allow_html=True)
                            
                            st.markdown(f"**{app['company']}**")
                            st.markdown(f"<div style='font-size:0.8rem; color:#636D5F; margin-bottom:0.6rem; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;'>{app['job_title']}</div>", unsafe_allow_html=True)
                            
                            compile_error = app.get("compile_error")
                            pdf_bytes = app.get("pdf_bytes")
                            is_base_fallback = app.get("is_base_fallback", False)
                            if is_admin and is_base_fallback:
                                st.markdown('<span class="badge badge-pending" title="Base resume PDF attached (tailored LaTeX had compile issues)">Base PDF Attached</span>', unsafe_allow_html=True)
                            elif pdf_bytes:
                                st.markdown('<span class="badge badge-done">Completed</span>', unsafe_allow_html=True)
                            elif is_admin and compile_error:
                                st.markdown('<span class="badge badge-error">PDF Error</span>', unsafe_allow_html=True)
                            else:
                                st.markdown('<span class="badge badge-pending">Processing</span>' if not pdf_bytes else '<span class="badge badge-done">Completed</span>', unsafe_allow_html=True)
                            
                            st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
                            st.markdown('<div class="card-buttons-wrapper"></div>', unsafe_allow_html=True)
                            
                            if st.button("View ➔", key=f"tab_sel_{key}", use_container_width=False, type="primary" if is_active else "secondary"):
                                st.session_state.selected_tab = key
                                st.rerun()
                                
                            if st.button("✕", key=f"tab_cls_{key}", use_container_width=False, help="Close Workspace"):
                                del st.session_state.applications[key]
                                remaining_keys = list(st.session_state.applications.keys())
                                if remaining_keys:
                                    st.session_state.selected_tab = remaining_keys[0]
                                else:
                                    st.session_state.selected_tab = None
                                st.toast("Workspace closed")
                                st.rerun()
                
                # Display the active tab content
                active_key = st.session_state.selected_tab
                
                # If active_key is not in application keys (e.g. deleted), select another
                if active_key not in apps_dict and app_keys:
                    active_key = app_keys[0]
                    st.session_state.selected_tab = active_key
                    
                if active_key in apps_dict:
                    app = apps_dict[active_key]
                    
                    st.markdown("---")
                    
                    # --- UNIFIED TOP HEADER ---
                    c_hdr1, c_hdr2 = st.columns([2, 1])
                    with c_hdr1:
                        st.subheader(f"{app.get('job_title', 'Role')} at {app.get('company', 'Company')}")
                        st.caption(f"Location: **{app.get('location', 'N/A')}** | Phone: **{app.get('phone', 'N/A')}**")
                    with c_hdr2:
                        if st.button("✕ Close Workspace", key=f"close_act_{active_key}", use_container_width=True):
                            del st.session_state.applications[active_key]
                            rem = list(st.session_state.applications.keys())
                            st.session_state.selected_tab = rem[0] if rem else None
                            st.rerun()
                    
                    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                    
                    # --- UNIFIED EMAIL & RESUME SIDE-BY-SIDE PANELS ---
                    col_bottom_left, col_bottom_right = st.columns([1, 1.1])
                    
                    with col_bottom_left:
                        st.markdown("### Cover Email & Outreach")
                        
                        # Status indicator banner
                        is_sent = app.get("email_sent", False)
                        is_drafted = app.get("draft_created_in_gmail", False)
                        draft_status_text = app.get("draft_status", "Draft ready locally")
                        
                        if is_sent:
                            st.success(f"● Email Sent to {app['email']} at {app.get('sent_time', '')}")
                        elif is_drafted:
                            st.info("● Draft ready in Gmail Drafts with resume attached.")
                            st.link_button("Open Gmail Drafts ➔", "https://mail.google.com/mail/u/0/#drafts", use_container_width=True)
                        else:
                            if any(w in draft_status_text.lower() for w in ["warning", "error", "failed", "configure", "invalid"]):
                                st.warning(f"● {draft_status_text}")
                            else:
                                st.caption(f"Status: {draft_status_text}")
                        
                        # Unified Recipient, Location, Subject, and Body fields
                        edited_to = st.text_input("Recipient Email (To:)", value=app.get("email", ""), key=f"recip_email_{app['id']}")
                        edited_loc = st.text_input("Job Location", value=app.get("location", ""), key=f"loc_val_{app['id']}")
                        edited_subject = st.text_input("Subject Line", value=app.get("subject", ""), key=f"sub_input_{app['id']}")
                        edited_body = st.text_area("Email Body (Edit here if needed)", value=app.get("email_body", ""), height=220, key=f"body_input_{app['id']}")
                        
                        # Sync edits to state
                        if (edited_to != app.get("email") or edited_loc != app.get("location") or 
                            edited_subject != app.get("subject") or edited_body != app.get("email_body")):
                            st.session_state.applications[active_key]["email"] = edited_to
                            st.session_state.applications[active_key]["location"] = edited_loc
                            st.session_state.applications[active_key]["subject"] = edited_subject
                            st.session_state.applications[active_key]["email_body"] = edited_body
                        
                        # Attachment status
                        current_pdf = app.get("pdf_bytes")
                        is_base_fallback = app.get("is_base_fallback", False)
                        if current_pdf:
                            pdf_size_kb = len(current_pdf) / 1024
                            if is_admin and is_base_fallback:
                                st.markdown(f"Attached: `Hemanth_swarna_ resume.pdf` *(Base Fallback, {pdf_size_kb:.1f} KB)*")
                                st.caption("ℹ️ Tailored LaTeX had compilation errors, so the clean base resume PDF was attached to the draft. You can edit the LaTeX on the right and click ⟳ Recompile PDF.")
                            else:
                                st.markdown(f"Attached: `Hemanth_swarna_ resume.pdf` *({pdf_size_kb:.1f} KB)*")
                        else:
                            st.markdown("Attachment: `PDF pending compilation`")
                            
                        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
                        
                        # Action Buttons: Send & Update Draft
                        btn_send_col, btn_draft_col = st.columns([1.3, 1])
                        
                        with btn_send_col:
                            if st.button("✉ Send Email", key=f"send_smtp_{app['id']}", use_container_width=True, type="primary"):
                                if not gmail_app_password:
                                    st.error("Please configure your Gmail App Password in Secrets / Sidebar to send emails.")
                                elif not edited_to or edited_to == "N/A" or "@" not in edited_to:
                                    st.error("Please provide a valid recipient email address in the 'Recipient Email' field.")
                                else:
                                    with st.spinner(f"Sending email directly to {edited_to}..."):
                                        send_ok, send_msg = send_email_smtp(
                                            sender_email=sender_email,
                                            app_password=gmail_app_password,
                                            recipient_email=edited_to,
                                            subject=edited_subject,
                                            body=edited_body,
                                            pdf_bytes=current_pdf,
                                            pdf_filename="Hemanth_swarna_ resume.pdf"
                                        )
                                        if send_ok:
                                            st.session_state.applications[active_key]["email_sent"] = True
                                            st.session_state.applications[active_key]["sent_time"] = datetime.datetime.now().strftime("%I:%M %p")
                                            update_application_status(app.get("company", ""), app.get("job_title", ""), "Sent")
                                            st.toast(f"Email sent successfully to {edited_to}")
                                            st.rerun()
                                        else:
                                            st.error(send_msg)
                                            
                        with btn_draft_col:
                            if st.button("✉ Sync to Gmail Drafts", key=f"save_gmail_draft_{app['id']}", use_container_width=True):
                                if not gmail_app_password:
                                    st.error("Please configure GMAIL_APP_PASSWORD in Streamlit Secrets.")
                                else:
                                    with st.spinner("Uploading draft to Gmail..."):
                                        draft_ok, draft_msg = save_to_gmail_drafts(
                                            sender_email=sender_email,
                                            app_password=gmail_app_password,
                                            recipient_email=edited_to,
                                            subject=edited_subject,
                                            body=edited_body,
                                            pdf_bytes=current_pdf,
                                            pdf_filename="Hemanth_swarna_ resume.pdf"
                                        )
                                        if draft_ok:
                                            st.session_state.applications[active_key]["draft_created_in_gmail"] = True
                                            st.session_state.applications[active_key]["draft_status"] = "Saved in Gmail Drafts"
                                            update_application_status(app.get("company", ""), app.get("job_title", ""), "Drafted")
                                            st.toast("Draft saved in Gmail Drafts")
                                            st.rerun()
                                        else:
                                            st.error(draft_msg)
                        
                        with st.expander("View Raw Text ➔", expanded=False):
                            st.markdown("**Subject:**")
                            st.code(edited_subject, language="text")
                            st.markdown("**Body:**")
                            st.code(edited_body, language="text")
                        
                    with col_bottom_right:
                        if is_admin:
                            st.markdown("### Tailored LaTeX Resume")
                            
                            # Let user view/edit LaTeX source
                            edited_latex = st.text_area(
                                "LaTeX Source Code",
                                value=app.get("latex_content", ""),
                                height=480,
                                key=f"tex_edit_{app['id']}"
                            )
                            
                            # Update LaTeX source in state if changed
                            if edited_latex != app.get("latex_content"):
                                st.session_state.applications[active_key]["latex_content"] = edited_latex
                            
                            # Action Buttons
                            st.markdown("##### Resume Actions")
                            
                            btn_c1, btn_c2, btn_c3 = st.columns([1.2, 1, 1])
                            
                            with btn_c1:
                                if st.button("⟳ Recompile PDF", key=f"recomp_{app['id']}", use_container_width=True):
                                    with st.spinner("Re-compiling PDF..."):
                                        pdf_b, comp_err = compile_latex(edited_latex)
                                        if pdf_b:
                                            st.session_state.applications[active_key]["pdf_bytes"] = pdf_b
                                            st.session_state.applications[active_key]["compile_error"] = None
                                            st.session_state.applications[active_key]["is_base_fallback"] = False
                                            st.toast("PDF successfully recompiled")
                                        else:
                                            st.session_state.applications[active_key]["compile_error"] = comp_err
                                            st.toast("Compilation encountered an issue")
                                        if download_dir and pdf_b:
                                            save_files_locally(
                                                latex_content=edited_latex,
                                                pdf_bytes=pdf_b,
                                                company=app.get("company", "Company"),
                                                download_dir=download_dir
                                            )
                                        st.rerun()
                                        
                            with btn_c2:
                                st.download_button(
                                    label="↓ Download .tex",
                                    data=app.get("latex_content", ""),
                                    file_name="Hemanth_swarna_ resume.tex",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                                
                            with btn_c3:
                                pdf_bytes = app.get("pdf_bytes")
                                if pdf_bytes:
                                    st.download_button(
                                        label="↓ Download PDF",
                                        data=pdf_bytes,
                                        file_name="Hemanth_swarna_ resume.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                else:
                                    st.button("PDF Pending", disabled=True, use_container_width=True)
                            
                            compile_error = app.get("compile_error")
                            if compile_error:
                                expander_label = "⚠️ View Tailored Compiler Log (Base PDF was used as fallback) ➔" if app.get("is_base_fallback") else "View Compiler Log ➔"
                                with st.expander(expander_label, expanded=False):
                                    st.code(compile_error, language="text")
                        else:
                            st.markdown("### Tailored Resume")
                            pdf_bytes = app.get("pdf_bytes")
                            if pdf_bytes:
                                pdf_kb = len(pdf_bytes) / 1024
                                st.markdown(f"""
                                <div style="background: #F8FAF7; border: 1px solid #C4DAC0; border-radius: 8px; padding: 20px 16px; margin-bottom: 16px;">
                                    <div style="display: flex; align-items: center; justify-content: space-between;">
                                        <div>
                                            <h4 style="margin: 0 0 4px 0; color: #141D12; font-size: 1.05rem;">📄 Hemanth_swarna_ resume.pdf</h4>
                                            <p style="margin: 0; color: #4A5B45; font-size: 0.85rem;">Customized PDF resume generated and attached ({pdf_kb:.1f} KB).</p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.download_button(
                                    label="↓ Download Tailored Resume (PDF)",
                                    data=pdf_bytes,
                                    file_name="Hemanth_swarna_ resume.pdf",
                                    mime="application/pdf",
                                    type="primary",
                                    use_container_width=True
                                )
                            else:
                                st.info("Resume PDF is processing...")

with main_tabs[1]:
    st.header("Application History")
    st.caption("Retaining activity from the past 7 days (older entries are automatically archived).")
    
    # Load history database
    log_df = st.session_state.history
    
    if log_df.empty:
        st.info("No applications logged in the database yet.")
    else:
        # Statistics
        total_logged = len(log_df)
        today_logged = len(log_df[log_df["Date"] == datetime.date.today().strftime("%Y-%m-%d")])
        unique_companies = log_df["Company"].nunique()
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Applications Logged", total_logged)
        with stat_col2:
            st.metric("Applications Logged Today", today_logged)
        with stat_col3:
            st.metric("Unique Companies", unique_companies)
            
        st.markdown("---")
        
        # Search & Filter controls
        st.subheader("Search & Filter History")
        filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
        with filter_col1:
            search_query = st.text_input("Search by Company, Job Title, or Recruiter Email", placeholder="Type to filter...")
        with filter_col2:
            status_filter = st.multiselect("Filter by Status", options=list(log_df["Status"].unique()), default=list(log_df["Status"].unique()))
        with filter_col3:
            # Parse Date column to extract min/max dates
            log_dates = pd.to_datetime(log_df["Date"], errors='coerce').dt.date.dropna()
            min_date = log_dates.min() if not log_dates.empty else datetime.date.today()
            max_date = log_dates.max() if not log_dates.empty else datetime.date.today()
            
            if min_date > max_date:
                min_date = max_date
                
            date_range = st.date_input(
                "Filter by Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
        # Apply filters
        filtered_df = log_df.copy()
        if search_query:
            query = search_query.lower()
            filtered_df = filtered_df[
                filtered_df["Company"].astype(str).str.lower().str.contains(query) |
                filtered_df["Job Title"].astype(str).str.lower().str.contains(query) |
                filtered_df["Recruiter Email"].astype(str).str.lower().str.contains(query) |
                filtered_df["Location"].astype(str).str.lower().str.contains(query)
            ]
        if status_filter:
            filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]
            
        # Apply date range filter
        if isinstance(date_range, tuple):
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = filtered_df[
                    pd.to_datetime(filtered_df["Date"], errors='coerce').dt.date.between(start_date, end_date)
                ]
            elif len(date_range) == 1:
                start_date = date_range[0]
                filtered_df = filtered_df[
                    pd.to_datetime(filtered_df["Date"], errors='coerce').dt.date >= start_date
                ]
            
        st.markdown("##### Search Results Table")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="↓ Download Filtered Log CSV",
            data=csv_data,
            file_name="filtered_logged_contacts.csv",
            mime="text/csv",
            key="dl_filtered_csv",
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("Detailed Contacts Breakdown")
        
        # Display each application detail in a clean card layout
        for idx, row in filtered_df.iterrows():
            with st.container(border=True):
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    st.markdown(f"### {row['Company']}")
                    st.markdown(f"**Job Title:** {row['Job Title']} | **Location:** {row['Location']}")
                    st.markdown(f"**Date Applied:** {row['Date']} | **Status:** `{row['Status']}`")
                with col_d2:
                    active_app = None
                    for key, val in st.session_state.applications.items():
                        if val.get("company") == row["Company"] and val.get("job_title") == row["Job Title"]:
                            active_app = val
                            break
                    if active_app:
                        st.markdown("<span class='badge badge-done'>Active Workspace</span>", unsafe_allow_html=True)
                    
                st.markdown("##### Recruiter Details")
                c_details1, c_details2, c_details3 = st.columns(3)
                with c_details1:
                    st.text_input("Recruiter Email", value=row["Recruiter Email"], key=f"hist_email_{idx}", disabled=True)
                with c_details2:
                    st.text_input("Phone Number", value=row["Phone Number"], key=f"hist_phone_{idx}", disabled=True)
                with c_details3:
                    st.text_input("Location", value=row["Location"], key=f"hist_loc_{idx}", disabled=True)
