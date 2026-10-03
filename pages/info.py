import streamlit as st
from pathlib import Path


st.set_page_config(
    page_title="ValidationLoop Info",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PATHS
# ============================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"


# ============================================================
# HELPERS
# ============================================================
def render_html(html: str) -> None:
    """Render a raw HTML/CSS fragment with Streamlit's native HTML renderer."""
    st.html(html.strip())


# ============================================================
# HOME BUTTON
# ============================================================
if st.button("← Back to Home", type="secondary"):
    st.switch_page("app.py")


# ============================================================
# STYLING
# ============================================================
render_html(
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
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 3rem;
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
            font-size: 1rem;
            font-weight: 500;
        }

        .brand-tagline span {
            color: var(--blue-2);
        }

        .info-card {
            background: rgba(92,101,116,0.10);
            border: 1px solid rgba(148,156,171,0.17);
            border-radius: 22px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.02),
                0 12px 36px rgba(0,0,0,0.12);
        }

        .section-title {
            color: var(--blue-2);
            font-size: 1.15rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .body-text {
            color: var(--text);
            font-size: 1rem;
            line-height: 1.65;
        }

        .muted-text {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .step {
            background: rgba(17,19,23,0.58);
            border: 1px solid #2c333e;
            border-radius: 16px;
            padding: 1rem 1.05rem;
            margin-top: 0.8rem;
        }

        .step-number {
            color: var(--blue);
            font-weight: 800;
            font-size: 0.86rem;
            margin-bottom: 0.25rem;
        }

        .step-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }

        .step-text {
            color: var(--muted);
            font-size: 0.91rem;
            line-height: 1.55;
        }

        .contact-box {
            background: rgba(47,124,255,0.07);
            border: 1px solid rgba(47,124,255,0.22);
            border-radius: 18px;
            padding: 1.1rem 1.2rem;
            margin-top: 1rem;
        }

        .contact-box a {
            color: var(--blue-2);
            text-decoration: none;
            font-weight: 700;
        }

        .contact-box a:hover {
            text-decoration: underline;
        }

        @media (max-width: 780px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .brand-name {
                font-size: 2rem;
            }

            .info-card {
                padding: 1.1rem 1.05rem;
                border-radius: 17px;
            }
        }
    </style>
    """
)


# ============================================================
# HEADER
# ============================================================
render_html(
    """
    <div class="brand-wrap">
        <div class="brand">
            <div class="brand-name">ValidationLoop</div>
            <div class="brand-tagline"><span>Validate</span> before you build.</div>
        </div>
    </div>
    """
)


# ============================================================
# INTRO
# ============================================================
render_html(
    """
    <div class="info-card">
        <div class="section-title">What is ValidationLoop?</div>
        <div class="body-text">
            ValidationLoop is a step-by-step system designed to help users
            validate business ideas before building them.
        </div>
    </div>
    """
)

render_html(
    """
    <div class="info-card">
        <div class="section-title">How it works</div>
        <div class="body-text">
            A user can describe a business idea, whether it is a startup idea,
            a new product, a way to increase sales, or something similar.
            After describing the idea, the platform guides the user through
            the next steps needed to validate it.
        </div>
    </div>
    """
)


# ============================================================
# VALIDATION APPROACH
# ============================================================
render_html(
    """
    <div class="info-card">
        <div class="section-title">Validation approach</div>
        <div class="body-text">
            The guidance is based on practical frameworks and techniques from
            books such as <i>The Mom Test</i>, <i>The Right It</i>,
            <i>Demand-Side Sales 101</i>, and similar resources.
        </div>
        <div class="muted-text" style="margin-top:0.65rem;">
            Instead of giving theoretical advice or a complete plan at once,
            the platform guides the user step by step.
        </div>
    </div>
    """
)


# ============================================================
# WHAT THE PLATFORM PROVIDES
# ============================================================
render_html(
    """
    <div class="info-card">
        <div class="section-title">What the platform provides</div>

        <div class="step">
            <div class="step-number">STEP 1</div>
            <div class="step-title">Concrete actions</div>
            <div class="step-text">
                The platform provides specific actions, checkboxes, questions
                to answer, things to find out, experiments to run, and clear
                next steps.
            </div>
        </div>

        <div class="step">
            <div class="step-number">STEP 2</div>
            <div class="step-title">Customer discovery</div>
            <div class="step-text">
                For example, for an AI-powered mock interview website, the
                first stage might be customer discovery. The tool could ask
                the user to talk to 10 to 15 students who are currently
                looking for jobs.
            </div>
        </div>

        <div class="step">
            <div class="step-number">STEP 3</div>
            <div class="step-title">Find potential users</div>
            <div class="step-text">
                It could provide tasks such as finding potential users through
                LinkedIn, GitHub, Kaggle, university communities, or other
                relevant sources.
            </div>
        </div>

        <div class="step">
            <div class="step-number">STEP 4</div>
            <div class="step-title">Run the right conversations</div>
            <div class="step-text">
                It would also explain how to reach out, what questions to ask,
                what not to say, and what signals to look for.
            </div>
        </div>

        <div class="step">
            <div class="step-number">STEP 5</div>
            <div class="step-title">Share evidence</div>
            <div class="step-text">
                After completing interviews, the user can return and upload
                notes, chats, transcripts, or answers. The platform can then
                use the findings to determine the next experiment.
            </div>
        </div>

        <div class="step">
            <div class="step-number">STEP 6</div>
            <div class="step-title">Experiment and iterate</div>
            <div class="step-text">
                Examples include a fake-door test or a prototyping test.
                The process continues iteratively:
                customer interviews → share results → analyze findings →
                run experiment → share results → continue based on evidence.
            </div>
        </div>
    </div>
    """
)


# ============================================================
# BROADER VALIDATION SCOPE
# ============================================================
render_html(
    """
    <div class="info-card">
        <div class="section-title">What else can be validated?</div>
        <div class="body-text">
            The platform can also help identify competitors, alternative
            solutions, target users, positioning, and existing products.
        </div>

        <div class="muted-text" style="margin-top:0.7rem;">
            The goal is not simply to help users build their idea, but to help
            them determine whether they should build it in the first place.
        </div>
    </div>
    """
)


# ============================================================
# EXAMPLE LOOP
# ============================================================
render_html(
    """
    <div class="info-card">
        <div class="section-title">Example validation loop</div>
        <div class="body-text">
            Customer interviews → share results → analyze findings →
            run experiment → share results → continue based on evidence.
        </div>
    </div>
    """
)


# ============================================================
# CONCEPT NOTE
# ============================================================
render_html(
    """
    <div class="info-card">
        <div class="section-title">See the concept in detail</div>
        <div class="muted-text">
            The detailed product concept and step-by-step validation workflow
            are represented by the project assets stored in the <code>assets</code>
            folder. Screenshots are intentionally not rendered on this page.
        </div>
    </div>
    """
)


# ============================================================
# CONTACT
# ============================================================
render_html(
    """
    <div class="info-card">
        <div class="section-title">Contact</div>
        <div class="body-text">
            Have a question about ValidationLoop?
        </div>

        <div class="contact-box">
            <div class="muted-text">
                Please email:
            </div>

            <div style="margin-top:0.35rem;">
                <a href="mailto:y.india.main@gmail.com">
                    y.india.main@gmail.com
                </a>
            </div>
        </div>
    </div>
    """
)


st.caption("ValidationLoop • Validate before you build.")