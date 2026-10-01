import time

import streamlit as st
import streamlit.components.v1 as components


MAIN_PAGE = "app.py"

# ============================================================
# EDIT YOUR SURVEY HERE
# ============================================================
# Change only "question" to change what the user sees.
# Keep "key" unchanged if you want to keep the same Google
# Sheets columns used by app.py / your Apps Script.
#
# The answer choices are currently fixed to Yes / No.
# ============================================================
SURVEY_QUESTIONS = [
    {
        "key": "q1_idea",
        "question": "Do you have a specific business idea you want to validate?",
    },
    {
        "key": "q2_target_customer",
        "question": "Do you know who your specific target customer is?",
    },
    {
        "key": "q3_problem",
        "question": "Have you clearly identified a problem that this customer has?",
    },
    {
        "key": "q4_current_evidence",
        "question": "Do you already have evidence that this problem exists?",
    },
    {
        "key": "q5_reach_users",
        "question": "Do you know how you would reach at least 20 people in your target group?",
    },
    {
        "key": "q6_alternatives",
        "question": "Do you know what alternatives or competitors your target customers use today?",
    },
    {
        "key": "q7_willingness_to_pay",
        "question": "Do you have evidence that your target customers would be willing to pay for a solution?",
    },
    {
        "key": "q8_biggest_assumption",
        "question": "Have you identified the biggest assumption that could invalidate your idea?",
    },
]

SURVEY_SECONDS = 2 * 60


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

        .timer {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--blue-2);
            margin: 0.5rem 0 1rem 0;
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

if "survey_started_at" not in st.session_state:
    st.session_state.survey_started_at = None


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
        <h3 style="margin:0 0 0.35rem 0;">2-minute validation survey</h3>
        <p style="color:#949cab; margin:0;">
            Answer each question with Yes or No.
            Keep your answers based on what you know today.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Start the timer only when the user explicitly starts the survey.
if st.session_state.survey_started_at is None:
    if st.button("Start survey", type="primary", use_container_width=True):
        st.session_state.survey_started_at = time.time()
        st.rerun()

    st.caption("The timer starts when you click Start survey.")
    st.stop()


started_at = float(st.session_state.survey_started_at)
deadline = started_at + SURVEY_SECONDS
remaining = max(0, int(deadline - time.time()))


# Visual countdown. The server-side deadline check below remains authoritative.
components.html(
    f"""
    <div class="timer" id="timer">02:00 remaining</div>
    <script>
        const deadlineMs = {int(deadline * 1000)};
        const timer = document.getElementById("timer");

        function updateTimer() {{
            const remaining = Math.max(0, deadlineMs - Date.now());
            const totalSeconds = Math.floor(remaining / 1000);
            const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
            const seconds = (totalSeconds % 60).toString().padStart(2, "0");
            timer.textContent = minutes + ":" + seconds + " remaining";

            if (totalSeconds <= 0) {{
                timer.textContent = "Time is up";
            }}
        }}

        updateTimer();
        setInterval(updateTimer, 1000);
    </script>
    """,
    height=45,
)


# The questions are generated from SURVEY_QUESTIONS above.
# To edit the survey, change the question text there.
with st.form("two_minute_survey"):
    answers = {}

    for index, item in enumerate(SURVEY_QUESTIONS, start=1):
        answers[item["key"]] = st.radio(
            f"{index}. {item['question']}",
            options=["Yes", "No"],
            index=None,
            key=f"survey_{item['key']}",
            horizontal=True,
        )

    submitted = st.form_submit_button(
        "Complete survey",
        type="primary",
        use_container_width=True,
        disabled=remaining <= 0,
    )


if submitted:
    now = time.time()

    if now > deadline:
        st.error("The 2-minute survey window has ended. Please restart the survey.")
        st.session_state.survey_started_at = None
        st.rerun()

    # Require an answer to every question.
    if any(answer not in {"Yes", "No"} for answer in answers.values()):
        st.error("Please answer every survey question before continuing.")
    else:
        st.session_state.survey_answers = answers
        st.session_state.survey_completed_at = now
        st.session_state.survey_duration_seconds = now - started_at
        st.session_state.survey_completed = True

        st.success("Survey completed.")
        st.switch_page(MAIN_PAGE)


st.caption("Thanks for your time.")