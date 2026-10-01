import json
import re
import socket
import time
import uuid
from datetime import datetime, timezone
from urllib import error as urllib_error
from urllib import request as urllib_request
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="ValidationLoop",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# If your main Streamlit file has a different name, change this path.
MAIN_PAGE = "app.py"
SURVEY_PAGE = "pages/survey.py"
APPS_SCRIPT_SHEET_NAME = "Signups"

# Apps Script can be slow (cold starts, sheet locks, redirects), so allow
# plenty of time for the response.
APPS_SCRIPT_TIMEOUT_SECONDS = 60

# Result states returned by send_to_google_sheet()
SAVE_CONFIRMED = "confirmed"   # Apps Script confirmed the row was written.
SAVE_UNCONFIRMED = "unconfirmed"  # Request was sent, response timed out. Row is likely written.
SAVE_FAILED = "failed"         # Definite failure (config error, HTTP error, script error, etc.)

# -----------------------------
# Theme / UX
# -----------------------------
st.markdown(
    """
    <style>
        :root {
            --bg: #111317;
            --panel: #1a1e24;
            --panel-2: #20252d;
            --border: #2d3440;
            --text: #f3f6fa;
            --muted: #949cab;
            --blue: #2f7cff;
            --blue-2: #58a0ff;
            --pink: #ff3b9d;
            --success: #62d39b;
        }

        .stApp {
            background:
                radial-gradient(circle at 50% 0%, rgba(47,124,255,0.08), transparent 34%),
                radial-gradient(circle at 88% 70%, rgba(255,59,157,0.045), transparent 28%),
                var(--bg);
            color: var(--text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.0rem;
            padding-bottom: 2rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            visibility: hidden;
            height: 0;
        }

        /* Header */
        .brand-wrap {
            display: flex;
            justify-content: center;
            text-align: center;
            margin: 1rem auto 2.2rem auto;
        }

        .brand {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            gap: 0.35rem;
        }

        .brand-name {
            color: var(--blue);
            font-size: 2.45rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1;
        }

        .brand-tagline {
            color: var(--muted);
            font-size: 1.0rem;
            font-weight: 500;
            letter-spacing: 0.01em;
        }

        .brand-tagline span {
            color: var(--blue-2);
        }

        /* Intro area */
        .intro-box {
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 1.35rem 1.55rem;
            margin-bottom: 1.45rem;
            border-radius: 22px;
            border: 1px solid rgba(148,156,171,0.17);
            background: rgba(92,101,116,0.10);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.02),
                0 12px 36px rgba(0,0,0,0.12);
        }

        .intro-title {
            color: var(--text);
            font-size: 1.22rem;
            font-weight: 750;
            letter-spacing: -0.02em;
            margin: 0 0 0.3rem 0;
        }

        .intro-subtitle {
            color: var(--muted);
            font-size: 0.91rem;
            line-height: 1.5;
            margin: 0;
        }

        /* Streamlit inputs */
        div[data-testid="stTextInput"] > div > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextArea"] textarea:focus {
            border-radius: 12px !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: #15191f !important;
            color: var(--text) !important;
            border: 1px solid #303743 !important;
            min-height: 46px !important;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border: 1px solid var(--blue) !important;
            box-shadow: 0 0 0 1px rgba(47,124,255,0.18) !important;
        }

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #6f7785 !important;
        }

        /* Buttons */
        div.stButton > button {
            width: 100%;
            min-height: 46px;
            border-radius: 12px;
            border: 1px solid #34404d;
            background: #1d232b;
            color: #eaf0f7;
            font-weight: 700;
            transition: all 0.16s ease;
        }

        div.stButton > button:hover {
            border-color: var(--blue);
            color: #ffffff;
            transform: translateY(-1px);
        }

        div.stButton > button[kind="primary"] {
            background: var(--blue);
            border-color: var(--blue);
            color: #ffffff;
            box-shadow: 0 8px 24px rgba(47,124,255,0.22);
        }

        div.stButton > button[kind="primary"]:hover {
            background: #236ee7;
            border-color: #236ee7;
            box-shadow: 0 10px 28px rgba(47,124,255,0.30);
        }

        div.stButton > button:disabled {
            opacity: 0.42;
            cursor: not-allowed;
            transform: none !important;
        }

        /* Requirement card */
        .requirement-card {
            background: rgba(17,19,23,0.58);
            border: 1px solid #2c333e;
            border-radius: 18px;
            padding: 1rem 1.05rem;
            margin-top: 1.2rem;
        }

        .requirement-title {
            color: var(--blue-2);
            font-size: 0.9rem;
            font-weight: 750;
            margin-bottom: 0.35rem;
        }

        .requirement-text {
            color: #9199a7;
            font-size: 0.79rem;
            line-height: 1.55;
            margin: 0;
        }

        /* Status */
        .status-success {
            margin-top: 1rem;
            padding: 0.85rem 1rem;
            border: 1px solid rgba(98,211,155,0.28);
            background: rgba(98,211,155,0.08);
            border-radius: 12px;
            color: #bbf1d6;
            font-size: 0.88rem;
        }

        .status-error {
            margin-top: 1rem;
            padding: 0.85rem 1rem;
            border: 1px solid rgba(255,59,157,0.24);
            background: rgba(255,59,157,0.07);
            border-radius: 12px;
            color: #ffd0e8;
            font-size: 0.88rem;
        }

        .helper {
            color: #6f7785;
            text-align: center;
            font-size: 0.75rem;
            margin-top: 1rem;
        }

        .post-box {
            background: rgba(17,19,23,0.58);
            border: 1px solid #2c333e;
            border-radius: 18px;
            padding: 1rem 1.05rem;
            margin-top: 1rem;
        }

        /* Decorative line */
        .accent-line {
            height: 2px;
            width: 78px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--blue), var(--pink));
            margin: 0.65rem 0 1.25rem 0;
        }

        @media (max-width: 780px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .intro-box {
                min-height: 100px;
                padding: 1.1rem 1.15rem;
                border-radius: 17px;
            }

            .brand-name {
                font-size: 2rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# State
# -----------------------------
DEFAULTS = {
    "signin_message": "",
    "signin_error": "",
    "survey_completed": False,
    "survey_answers": {},
    "survey_started_at": None,
    "survey_completed_at": None,
    "survey_duration_seconds": None,
    "form_name": "",
    "form_email": "",
    "form_post_url": "",
    # Idempotency / duplicate protection
    "submission_id": "",
    "submission_sent": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# Helpers
# -----------------------------
SHARE_POST_TEXT = """**Validation Loop** is a step-by-step system for validating business ideas before building them.

It is based on practical frameworks from books like *The Mom Test*, *The Right It*, and *Demand-Side Sales 101*.

For example, instead of giving generic advice, it can say:

**“Find 20 data engineers or data analysts on LinkedIn or GitHub and test your assumptions with them.”**

After the interviews, upload the notes and get the **next step based on the evidence collected**.

It can also guide competitor research, fake-door tests, landing-page experiments, willingness-to-pay tests, and more.

**Not just a chatbot. A validation loop.**

🔗 https://validationloop.streamlit.app/"""

SIGNIN_MESSAGE = """We’ll reach out to you first once Validation Loop is ready. We’re working continuously to bring it to completion. Thank you for your interest and support. You are signed up for the early-access
list. 
We’ll email you when Validation Loop is ready to use. If you have any questions, please email [y.india.main@gmail.com](mailto:y.india.main@gmail.com)"""


def valid_post_url(value: str | None) -> bool:
    return bool(value and value.strip())


def copy_post_button(text_to_copy: str) -> None:
    payload = json.dumps(text_to_copy)
    components.html(
        f"""
        <div style="font-family: sans-serif;">
            <button
                id="copy-post"
                onclick='copyPost()'
                style="
                    width:100%;
                    min-height:46px;
                    padding:0 16px;
                    border-radius:12px;
                    border:1px solid #34404d;
                    background:#1d232b;
                    color:#eaf0f7;
                    font-weight:700;
                    cursor:pointer;
                    font-size:14px;
                "
            >Copy post</button>
        </div>
        <script>
            const text = {payload};

            async function copyPost() {{
                const button = document.getElementById("copy-post");
                try {{
                    await navigator.clipboard.writeText(text);
                    button.textContent = "Copied ✓";
                    setTimeout(() => button.textContent = "Copy post", 1600);
                }} catch (error) {{
                    const area = document.createElement("textarea");
                    area.value = text;
                    document.body.appendChild(area);
                    area.select();
                    document.execCommand("copy");
                    area.remove();
                    button.textContent = "Copied ✓";
                    setTimeout(() => button.textContent = "Copy post", 1600);
                }}
            }}
        </script>
        """,
        height=58,
    )


class _NoRedirectHandler(urllib_request.HTTPRedirectHandler):
    """Stop urllib from auto-following redirects so we can handle them ourselves."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _is_timeout(exc: BaseException) -> bool:
    """True if the exception (or the reason wrapped inside a URLError) is a timeout."""
    timeout_types = (TimeoutError, socket.timeout)
    if isinstance(exc, timeout_types):
        return True
    if isinstance(exc, urllib_error.URLError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, timeout_types):
            return True
        if reason is not None and "timed out" in str(reason).lower():
            return True
    return "timed out" in str(exc).lower()


def send_to_google_sheet(
    *,
    submission_id: str,
    name: str,
    email: str,
    post_url: str,
    survey_answers: dict,
    survey_started_at: float | None,
    survey_completed_at: float | None,
    survey_duration_seconds: float | None,
) -> tuple[str, str]:
    """Send one completed submission to a Google Apps Script web app.

    The Apps Script web app receives the JSON and appends it to the private
    Google Sheet. No Google Cloud service account is required.

    Returns (status, message) where status is one of:
      - SAVE_CONFIRMED:   Apps Script replied with success.
      - SAVE_UNCONFIRMED: The request was sent but the response timed out.
                          Apps Script normally still writes the row in this
                          case, so this must NOT be shown as a failure and
                          must NOT be retried automatically (a retry could
                          create a duplicate row).
      - SAVE_FAILED:      A definite failure.

    A unique `submission_id` is included in the payload so the Apps Script
    can optionally de-duplicate rows if the same submission ever arrives twice.
    """

    try:
        apps_script = st.secrets["apps_script"]
        endpoint = str(apps_script["url"]).strip()
        token = str(apps_script.get("token", "")).strip()

        if not endpoint:
            return SAVE_FAILED, "Google Sheets is not configured: Apps Script URL is empty."

        def utc_iso(timestamp: float | None) -> str:
            if timestamp is None:
                return ""
            return datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc,
            ).isoformat()

        payload = {
            "token": token,
            "sheet_name": APPS_SCRIPT_SHEET_NAME,
            "submission_id": submission_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "name": name,
            "email": email,
            "survey_started_utc": utc_iso(survey_started_at),
            "survey_completed_utc": utc_iso(survey_completed_at),
            "survey_duration_seconds": (
                round(float(survey_duration_seconds), 1)
                if survey_duration_seconds is not None
                else ""
            ),
            "survey_completed": "YES",
            "q1_idea": survey_answers.get("q1_idea", ""),
            "q2_target_customer": survey_answers.get("q2_target_customer", ""),
            "q3_problem": survey_answers.get("q3_problem", ""),
            "q4_current_evidence": survey_answers.get("q4_current_evidence", ""),
            "q5_reach_users": survey_answers.get("q5_reach_users", ""),
            "q6_alternatives": survey_answers.get("q6_alternatives", ""),
            "q7_willingness_to_pay": survey_answers.get("q7_willingness_to_pay", ""),
            "q8_biggest_assumption": survey_answers.get("q8_biggest_assumption", ""),
            "post_url": post_url,
        }

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib_request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "ValidationLoop/1.0",
            },
            method="POST",
        )

        unconfirmed = (
            SAVE_UNCONFIRMED,
            "The confirmation from Google Sheets could not be read, but your submission was sent.",
        )

        # Apps Script runs doPost() first and then answers with a 302 redirect to
        # a one-time result URL. We handle that redirect ourselves: once the 302
        # arrives, the row has already been written. Errors while fetching the
        # result URL (e.g. HTTP 404) therefore do NOT mean the save failed.
        opener = urllib_request.build_opener(_NoRedirectHandler)
        redirect_url = ""
        response_text = ""
        status_code = 200

        try:
            with opener.open(req, timeout=APPS_SCRIPT_TIMEOUT_SECONDS) as response:
                response_text = response.read().decode("utf-8", errors="replace")
                status_code = getattr(response, "status", 200)
        except urllib_error.HTTPError as exc:
            if exc.code in (301, 302, 303, 307, 308) and exc.headers.get("Location"):
                redirect_url = exc.headers.get("Location", "")
            else:
                raise

        if redirect_url:
            try:
                follow_req = urllib_request.Request(
                    redirect_url,
                    headers={"User-Agent": "ValidationLoop/1.0"},
                    method="GET",
                )
                with urllib_request.urlopen(
                    follow_req, timeout=APPS_SCRIPT_TIMEOUT_SECONDS
                ) as response:
                    response_text = response.read().decode("utf-8", errors="replace")
                    status_code = getattr(response, "status", 200)
            except Exception:
                # The POST was already received by Apps Script.
                return unconfirmed

            if status_code < 200 or status_code >= 300:
                return unconfirmed
        elif status_code < 200 or status_code >= 300:
            return SAVE_FAILED, f"Google Sheets save failed: HTTP {status_code}."

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            if redirect_url:
                return unconfirmed
            return SAVE_FAILED, "Google Sheets save failed: Apps Script returned an invalid response."

        if not result.get("success"):
            message = result.get("error", "Unknown Apps Script error.")
            return SAVE_FAILED, f"Google Sheets save failed: {message}"

        return SAVE_CONFIRMED, "Saved successfully."

    except KeyError as exc:
        return SAVE_FAILED, f"Google Sheets configuration is missing in .streamlit/secrets.toml: {exc}"
    except urllib_error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:
            detail = str(exc)
        return SAVE_FAILED, f"Google Sheets request failed (HTTP {exc.code}): {detail[:300]}"
    except Exception as exc:
        # The request was already sent when a timeout happens, and Apps Script
        # typically writes the row even if its response is slow. Treat this as
        # "submitted, unconfirmed" instead of a failure, and never auto-retry.
        if _is_timeout(exc):
            return (
                SAVE_UNCONFIRMED,
                "The confirmation from Google Sheets took too long, but your submission was sent.",
            )
        if isinstance(exc, urllib_error.URLError):
            return SAVE_FAILED, f"Could not reach the Google Sheets Apps Script: {exc.reason}"
        return SAVE_FAILED, f"Google Sheets save failed: {exc}"


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="brand-wrap">
        <div class="brand">
            <div class="brand-name">ValidationLoop</div>
            <div class="brand-tagline"><span>Validate</span> before you build.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Authentication / signup details
# -----------------------------
st.markdown(
    """
    <div class="intro-box">
        <div class="intro-title">Welcome to ValidationLoop</div>
        <p class="intro-subtitle">
            Enter your details to get started.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

name = st.text_input(
    "Name",
    value=st.session_state.form_name,
    placeholder="Enter your name",
    label_visibility="visible",
    key="name_input",
)
email = st.text_input(
    "Email address",
    value=st.session_state.form_email,
    placeholder="you@example.com",
    label_visibility="visible",
    key="email_input",
)
st.session_state.form_name = name
st.session_state.form_email = email

clean_name = (name or "").strip()
clean_email = (email or "").strip()

email_valid = bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", clean_email))
basic_details_complete = bool(clean_name and email_valid)
st.markdown("<div style='height: 0.55rem'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="post-box" style="margin-top: 0;">
        <div style="font-weight: 750; color: #58a0ff; margin-bottom: 0.35rem;">
            Watch the demo
        </div>
        <div style="color: #949cab; font-size: 0.86rem; line-height: 1.5;">
            See how ValidationLoop works before you complete the survey.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.link_button(
    "Watch demo",
    "https://drive.google.com/file/d/1hD3mnig6_rvTic-apqvgYlMdl9l9-11k/view?usp=drive_link",
    use_container_width=True,
)

st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

# -----------------------------
# Survey gate
# -----------------------------
if not st.session_state.survey_completed:
    st.markdown(
        """
        <div class="requirement-card">
            <div class="requirement-title">2-minute survey</div>
            <p class="requirement-text">
                Complete the short validation survey first. The social-post step
                appears only after the survey is completed.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    survey_ready = st.button(
        "Start 2-minute survey",
        type="primary",
        use_container_width=True,
        disabled=not basic_details_complete,
    )

    if survey_ready:
        st.session_state.form_name = clean_name
        st.session_state.form_email = clean_email
        st.session_state.survey_started_at = None
        st.session_state.survey_completed = False
        # A new survey run means a new submission.
        st.session_state.submission_id = ""
        st.session_state.submission_sent = False
        st.session_state.signin_message = ""
        st.switch_page(SURVEY_PAGE)

    if not basic_details_complete:
        st.caption("Enter your name and a valid email address to unlock the survey.")

    st.stop()

# -----------------------------
# Post requirement after survey
# -----------------------------
st.success("Survey completed. You can now complete the final social-post step.")

st.markdown("**Post this on LinkedIn or another social platform:**")

st.markdown('<div class="post-box">', unsafe_allow_html=True)
st.code(SHARE_POST_TEXT, language="markdown")
st.markdown('</div>', unsafe_allow_html=True)

copy_post_button(SHARE_POST_TEXT)

st.caption(
    "Copy the text above and paste it into your social media post. Make sure to include the link to your post in the field below."
)

post_url = st.text_input(
    "Post URL",
    value=st.session_state.form_post_url,
    placeholder="Paste your post link here",
    label_visibility="visible",
    key="post_url_input",
)

st.session_state.form_post_url = post_url

clean_post_url = (post_url or "").strip()
post_url_valid = valid_post_url(clean_post_url)

form_complete = bool(
    clean_name
    and email_valid
    and st.session_state.survey_completed
    and post_url_valid
)

# Once a submission has been sent (confirmed or not), the button is disabled so
# it can't be clicked again and create a duplicate row.
already_sent = bool(st.session_state.submission_sent)

signin_clicked = st.button(
    "Complete",
    type="primary",
    use_container_width=True,
    disabled=(not form_complete) or already_sent,
)

if signin_clicked and not already_sent:
    st.session_state.signin_message = ""
    st.session_state.signin_error = ""

    if not form_complete:
        st.session_state.signin_error = "Complete the survey and enter a post link."
    else:
        # One stable ID per submission. It is created once and reused, so the
        # Apps Script can de-duplicate if the same submission is ever received twice.
        if not st.session_state.submission_id:
            st.session_state.submission_id = uuid.uuid4().hex

        with st.spinner("Saving your submission..."):
            status, save_message = send_to_google_sheet(
                submission_id=st.session_state.submission_id,
                name=clean_name,
                email=clean_email,
                post_url=clean_post_url,
                survey_answers=st.session_state.survey_answers,
                survey_started_at=st.session_state.survey_started_at,
                survey_completed_at=st.session_state.survey_completed_at,
                survey_duration_seconds=st.session_state.survey_duration_seconds,
            )

        if status in (SAVE_CONFIRMED, SAVE_UNCONFIRMED):
            # Confirmed, or request sent but the response timed out. In both
            # cases show the normal success message. No automatic retry, to
            # avoid duplicate rows.
            st.session_state.submission_sent = True
            st.session_state.signin_message = SIGNIN_MESSAGE
            st.balloons()
        else:
            st.session_state.signin_error = SIGNIN_ERROR_MESSAGE

# Success message (persists across reruns so the user still sees it).
if st.session_state.signin_message:
    st.success(st.session_state.signin_message)

if st.session_state.signin_error:
    st.markdown(
        f'<div class="status-error">{st.session_state.signin_error}</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="requirement-card">
        <div class="requirement-title">Final requirement</div>
        <p class="requirement-text">
            Complete your details, finish the 2-minute survey, and paste any
            non-empty post link to complete the process.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)