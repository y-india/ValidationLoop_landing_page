import time
from datetime import datetime, timezone

import streamlit as st
import streamlit.components.v1 as components


MAIN_PAGE = "app.py"
SURVEY_SECONDS = 5 * 60

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
        <h3 style="margin:0 0 0.35rem 0;">5-minute validation survey</h3>
        <p style="color:#949cab; margin:0;">
            A few focused questions about the idea you want to validate.
            Keep answers specific and concise.
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
    <div class="timer" id="timer">05:00 remaining</div>
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

with st.form("five_minute_survey"):
    q1 = st.text_area(
        "1. What idea or business are you validating?",
        placeholder="Describe it in 1-3 sentences.",
        height=85,
    )

    q2 = st.text_area(
        "2. Who is the specific target customer?",
        placeholder="Name the role, company type, or user group.",
        height=85,
    )

    q3 = st.text_area(
        "3. What problem are you solving for them?",
        placeholder="State the problem, not the solution.",
        height=85,
    )

    q4 = st.text_area(
        "4. What evidence do you already have?",
        placeholder="Interviews, usage, signups, purchases, observations, or none yet.",
        height=85,
    )

    q5 = st.text_area(
        "5. How would you reach 20 people in this target group?",
        placeholder="Be concrete. For example: LinkedIn, GitHub, communities, existing network.",
        height=85,
    )

    q6 = st.text_area(
        "6. What alternatives or competitors do they use today?",
        placeholder="Include manual workarounds, not only direct competitors.",
        height=85,
    )

    q7 = st.text_area(
        "7. What would make them willing to pay?",
        placeholder="Describe the outcome or value you think could justify payment.",
        height=85,
    )

    q8 = st.text_area(
        "8. What is the biggest assumption you need to test?",
        placeholder="Write the assumption that could most strongly invalidate the idea.",
        height=85,
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
        st.error("The 5-minute survey window has ended. Please restart the survey.")
        st.session_state.survey_started_at = None
        st.rerun()

    answers = {
        "q1_idea": q1.strip(),
        "q2_target_customer": q2.strip(),
        "q3_problem": q3.strip(),
        "q4_current_evidence": q4.strip(),
        "q5_reach_users": q5.strip(),
        "q6_alternatives": q6.strip(),
        "q7_willingness_to_pay": q7.strip(),
        "q8_biggest_assumption": q8.strip(),
    }

    if any(not value for value in answers.values()):
        st.error("Please answer every survey question before continuing.")
    else:
        st.session_state.survey_answers = answers
        st.session_state.survey_completed_at = now
        st.session_state.survey_duration_seconds = now - started_at
        st.session_state.survey_completed = True

        st.success("Survey completed.")
        st.switch_page(MAIN_PAGE)

st.caption("Your survey answers will be saved with your signup when you click Sign In.")
