import json
import socket
import time
import uuid
from datetime import datetime, timezone
from urllib import error as urllib_error
from urllib import request as urllib_request

import streamlit as st


MAIN_PAGE = "app.py"

# ============================================================
# EDIT YOUR SURVEY HERE
# ============================================================
# Keep the "key" values unchanged so the existing Google Sheets
# columns used by app.py / your Apps Script continue to work.
# ============================================================


APPS_SCRIPT_TIMEOUT_SECONDS = 60


class _NoRedirectHandler(urllib_request.HTTPRedirectHandler):
    """Stop urllib from auto-following Apps Script redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _is_timeout(exc: BaseException) -> bool:
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


def send_survey_start(*, submission_id: str, name: str, email: str, started_at: float) -> tuple[bool, str]:
    """Create the STARTED row in Google Sheets."""
    try:
        apps_script = st.secrets["apps_script"]
        endpoint = str(apps_script["url"]).strip()
        token = str(apps_script.get("token", "")).strip()

        if not endpoint:
            return False, "Google Sheets is not configured: Apps Script URL is empty."

        started_iso = datetime.fromtimestamp(
            started_at,
            tz=timezone.utc,
        ).isoformat()

        payload = {
            "token": token,
            "action": "start",
            "sheet_name": "Signups",
            "submission_id": submission_id,
            "timestamp_utc": started_iso,
            "name": name.strip(),
            "email": email.strip(),
            "survey_started_utc": started_iso,
            "survey_completed": "NO",
            "status": "STARTED",
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
                    follow_req,
                    timeout=APPS_SCRIPT_TIMEOUT_SECONDS,
                ) as response:
                    response_text = response.read().decode("utf-8", errors="replace")
                    status_code = getattr(response, "status", 200)
            except Exception:
                # The POST reached Apps Script. The start is therefore treated as
                # accepted. The same submission_id makes a retry idempotent.
                return True, "Survey start was sent."

        if status_code < 200 or status_code >= 300:
            return False, f"Google Sheets start failed: HTTP {status_code}."

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            return True, "Survey start was sent."

        if not result.get("success"):
            return False, f"Google Sheets start failed: {result.get('error', 'Unknown error.')}"

        return True, "Survey started."

    except KeyError as exc:
        return False, f"Google Sheets configuration is missing in .streamlit/secrets.toml: {exc}"
    except urllib_error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:
            detail = str(exc)
        return False, f"Google Sheets request failed (HTTP {exc.code}): {detail[:300]}"
    except Exception as exc:
        if _is_timeout(exc):
            return True, "Survey start was sent."
        if isinstance(exc, urllib_error.URLError):
            return False, f"Could not reach the Google Sheets Apps Script: {exc.reason}"
        return False, f"Google Sheets start failed: {exc}"


SURVEY_QUESTIONS = [
    {
        "key": "q1_idea",
        "question": "Did you watch the demo video?",
        "type": "yes_no",
    },
    {
        "key": "q2_target_customer",
        "question": "Are you currently working on an idea?",
        "type": "yes_no",
    },
    {
        "key": "q3_problem",
        "question": "Have you ever tried validating any idea?",
        "type": "yes_no",
    },
    {
        "key": "q4_current_evidence",
        "question": "What did you like most about this web app approach?",
        "type": "text",
    },
    {
        "key": "q5_reach_users",
        "question": "Have you ever read books on idea validation like The Mom Test or Jobs to Be Done? (If not, you do not need to read them now!)",
        "type": "yes_no",
    },
    {
        "key": "q6_alternatives",
        "question": "What is your profession?",
        "type": "profession",
        "options": [
            "Student (School)",
            "Student (College)",
            "Working",
            "Graduate",
        ],
    },
    {
        "key": "q7_willingness_to_pay",
        "question": "In which area is your idea about?",
        "type": "text",
    },
    {
        "key": "q8_biggest_assumption",
        "question": "Do you have any question?",
        "type": "question",
    },
]


st.set_page_config(
    page_title="ValidationLoop Survey",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        :root {
            --bg: #111317;
            --panel: #1a1e24;
            --border: #2d3440;
            --text: #f3f6fa;
            --muted: #949cab;
            --blue: #2f7cff;
            --blue-2: #58a0ff;
            --pink: #ff3b9d;
        }

        .stApp {
            background:
                radial-gradient(circle at 50% 0%, rgba(47,124,255,0.08), transparent 34%),
                radial-gradient(circle at 88% 70%, rgba(255,59,157,0.045), transparent 28%),
                var(--bg);
            color: var(--text);
        }

        .block-container {
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            visibility: hidden;
            height: 0;
        }

        .brand-wrap {
            display: flex;
            justify-content: center;
            text-align: center;
            margin: 1rem auto 2rem auto;
        }

        .brand {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            gap: 0.35rem;
        }

        .brand-name {
            color: var(--blue);
            font-size: 2.35rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1;
        }

        .brand-tagline {
            color: var(--muted);
            font-size: 1rem;
        }

        .brand-tagline span {
            color: var(--blue-2);
        }

        .survey-card {
            background: rgba(92,101,116,0.10);
            border: 1px solid rgba(148,156,171,0.17);
            border-radius: 22px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.25rem;
        }

        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            background: #15191f !important;
            color: var(--text) !important;
            border: 1px solid #303743 !important;
            border-radius: 12px !important;
        }

        div.stButton > button {
            width: 100%;
            min-height: 46px;
            border-radius: 12px;
            border: 1px solid #34404d;
            background: #1d232b;
            color: #eaf0f7;
            font-weight: 700;
        }

        div.stButton > button[kind="primary"] {
            background: var(--blue);
            border-color: var(--blue);
            color: #ffffff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if "form_name" not in st.session_state:
    st.switch_page(MAIN_PAGE)

if not st.session_state.form_name or not st.session_state.form_email:
    st.switch_page(MAIN_PAGE)


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


st.markdown(
    """
    <div class="survey-card">
        <h3 style="margin:0 0 0.35rem 0;">Validation survey</h3>
        <p style="color:#949cab; margin:0;">
            Answer each question based on what you know today.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# The questions are generated from SURVEY_QUESTIONS above.
# To edit the survey, change the question text and type there.
# Start the survey and create the Google Sheets row at the same time.
if "survey_started_at" not in st.session_state:
    st.session_state.survey_started_at = None

if "submission_id" not in st.session_state:
    st.session_state.submission_id = ""

if st.session_state.survey_started_at is None:
    if st.button("Start survey", type="primary", use_container_width=True):
        submission_id = st.session_state.submission_id or uuid.uuid4().hex
        started_at = time.time()

        ok, message = send_survey_start(
            submission_id=submission_id,
            name=st.session_state.form_name,
            email=st.session_state.form_email,
            started_at=started_at,
        )

        if ok:
            st.session_state.submission_id = submission_id
            st.session_state.survey_started_at = started_at
            st.rerun()
        else:
            st.error(message)

    st.caption("Click Start survey when you are ready.")
    st.stop()


answers = {}

for index, item in enumerate(SURVEY_QUESTIONS, start=1):
    question_type = item["type"]
    key = item["key"]
    question = item["question"]

    if question_type == "yes_no":
        answers[key] = st.radio(
            f"{index}. {question}",
            options=["Yes", "No"],
            index=None,
            key=f"survey_{key}",
            horizontal=True,
        )

    elif question_type == "text":
        answers[key] = st.text_area(
            f"{index}. {question}",
            placeholder="Write your answer here...",
            key=f"survey_{key}",
        )

    elif question_type == "profession":
        answers[key] = st.radio(
            f"{index}. {question}",
            options=item["options"],
            index=None,
            key=f"survey_{key}",
            horizontal=True,
        )

    elif question_type == "question":
        question_choice = st.radio(
            f"{index}. {question}",
            options=["Any question", "No question"],
            index=None,
            key=f"survey_{key}_choice",
            horizontal=True,
        )

        if question_choice == "Any question":
            question_text = st.text_area(
                "Your question",
                placeholder="Write your question here...",
                key=f"survey_{key}_text",
            )
            answers[key] = question_text.strip()
        elif question_choice == "No question":
            answers[key] = "No question"
        else:
            answers[key] = None


submitted = st.button(
    "Complete survey",
    type="primary",
    use_container_width=True,
)


if submitted:
    missing_answers = []

    for index, item in enumerate(SURVEY_QUESTIONS, start=1):
        answer = answers.get(item["key"])
        if answer is None or (isinstance(answer, str) and not answer.strip()):
            missing_answers.append(index)

    if missing_answers:
        st.error("Please answer every survey question before continuing.")
    else:
        st.session_state.survey_answers = answers
        st.session_state.survey_completed_at = time.time()
        st.session_state.survey_duration_seconds = None
        st.session_state.survey_completed = True

        st.success("Survey completed.")
        st.switch_page(MAIN_PAGE)


st.caption("Thanks for your time.")
