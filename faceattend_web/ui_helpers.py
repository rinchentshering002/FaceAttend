
from datetime import datetime
from zoneinfo import ZoneInfo

# Bhutan timezone
BHUTAN_TZ = ZoneInfo("Asia/Thimphu")

# FaceAttend colour palette
BG = "#F4F7FB"
CARD = "#FFFFFF"
NAVY = "#2C4A6E"
NAVY_DARK = "#1E3652"
NAVY_MID = "#4A6D96"
GOLD = "#C99A2E"
GOLD_LIGHT = "#E7C76A"
TEXT = "#1A202C"
MUTED = "#6B7280"
GREEN = "#23824B"
RED = "#B93636"
BLUE = "#315A78"
BORDER = "#D6E0EC"


def bhutan_now():
    """Return current Bhutan date and time."""
    return datetime.now(BHUTAN_TZ)


def format_check_in_time(value):
    """Format an attendance time for display."""
    if not value:
        return "—"

    try:
        parsed = datetime.fromisoformat(str(value))

        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(BHUTAN_TZ)

        return parsed.strftime("%I:%M %p")

    except (ValueError, TypeError):
        return str(value)


def format_time_short(value):
    """Format time in a short 12-hour format."""
    if not value:
        return "—"

    try:
        if isinstance(value, datetime):
            parsed = value
        else:
            parsed = datetime.fromisoformat(
                f"2000-01-01T{value}"
            )

        return parsed.strftime("%I:%M %p")

    except (ValueError, TypeError):
        return str(value)


def inject_custom_css():
    """Apply consistent FaceAttend styling in Streamlit."""

    import streamlit as st

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {BG};
        }}

        [data-testid="stSidebar"] {{
            background-color: {NAVY_DARK};
        }}

        [data-testid="stSidebar"] * {{
            color: #FFFFFF;
        }}

        .faceattend-hero {{
            background: linear-gradient(
                120deg,
                {NAVY_DARK},
                {NAVY_MID}
            );
            padding: 28px;
            border-radius: 14px;
            margin-bottom: 24px;
            color: white;
        }}

        .faceattend-hero h1 {{
            color: white;
            margin-bottom: 6px;
        }}

        .faceattend-hero p {{
            color: {GOLD_LIGHT};
            margin-bottom: 0;
        }}

        .faceattend-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 20px;
        }}

        .faceattend-card-title {{
            color: {MUTED};
            font-size: 14px;
        }}

        .faceattend-card-value {{
            color: {NAVY};
            font-size: 28px;
            font-weight: 700;
        }}

        .stButton > button {{
            background-color: {NAVY};
            color: white;
            border-radius: 8px;
            border: none;
        }}

        .stButton > button:hover {{
            background-color: {NAVY_MID};
            color: white;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


def render_hero(title, subtitle):
    """Display the main FaceAttend heading."""

    import streamlit as st

    st.markdown(
        f"""
        <div class="faceattend-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(title, value):
    """Display a reusable dashboard metric card."""

    import streamlit as st

    st.markdown(
        f"""
        <div class="faceattend-card">
            <div class="faceattend-card-title">
                {title}
            </div>
            <div class="faceattend-card-value">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
