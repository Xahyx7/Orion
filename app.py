import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import streamlit.components.v1 as components
from supabase import create_client, Client

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="NEON STUDY OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# GLOBAL CSS — OLED + FUTURISTIC MINIMAL
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
section[data-testid="stSidebar"],
.main .block-container {
    background-color: #000000 !important;
    color: #e0e0e0 !important;
    font-family: 'Syne', sans-serif !important;
}

.main .block-container {
    padding: 2rem 3rem !important;
    max-width: 1400px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #1a1a1a; border-radius: 2px; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    border-right: 1px solid #111 !important;
    padding-top: 2rem !important;
}
section[data-testid="stSidebar"] * { font-family: 'Syne', sans-serif !important; }
section[data-testid="stSidebar"] .stRadio label {
    color: #555 !important;
    font-size: 0.75rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    padding: 10px 0 !important;
    transition: color 0.3s !important;
}
section[data-testid="stSidebar"] .stRadio label:hover { color: #00f2fe !important; }

/* ── HEADINGS ── */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; letter-spacing: -1px !important; }

/* ── INPUTS ── */
input, textarea {
    background-color: #080808 !important;
    color: #e0e0e0 !important;
    border: 1px solid #1c1c1c !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    transition: border-color 0.3s !important;
}
input:focus, textarea:focus { border-color: #00f2fe !important; outline: none !important; box-shadow: 0 0 0 2px rgba(0,242,254,0.08) !important; }

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background-color: #080808 !important;
    border: 1px solid #1c1c1c !important;
    border-radius: 8px !important;
    color: #e0e0e0 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: #000 !important;
    color: #00f2fe !important;
    border: 1px solid #00f2fe !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button:hover {
    background: #00f2fe !important;
    color: #000 !important;
    box-shadow: 0 0 25px rgba(0,242,254,0.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* ── METRIC CARDS ── */
[data-testid="stMetric"] {
    background: #060606 !important;
    border: 1px solid #111 !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.5rem !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stMetric"]::before {
    content: '' !important;
    position: absolute !important;
    top: 0; left: 0; right: 0 !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, #00f2fe, transparent) !important;
}
[data-testid="stMetricValue"] { color: #00f2fe !important; font-family: 'Space Mono', monospace !important; font-size: 1.8rem !important; }
[data-testid="stMetricLabel"] { color: #333 !important; font-size: 0.65rem !important; letter-spacing: 3px !important; text-transform: uppercase !important; }

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border: 1px solid #111 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── DIVIDER ── */
hr { border-color: #111 !important; margin: 2rem 0 !important; }

/* ── TOGGLE ── */
[data-testid="stToggle"] span { font-size: 0.7rem !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: #555 !important; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDeployButton"] { display: none; }

/* ── PLOTLY CHART BACKGROUND ── */
.js-plotly-plot, .plotly, .plot-container { background: transparent !important; }

/* ── SIDEBAR USER BADGE ── */
.user-badge {
    background: #060606;
    border: 1px solid #111;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.user-dot {
    width: 8px; height: 8px;
    background: #00f2fe;
    border-radius: 50%;
    box-shadow: 0 0 8px #00f2fe;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── SUBJECT PILL ── */
.subject-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SUPABASE INIT
# ─────────────────────────────────────────
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# ─────────────────────────────────────────
# SUBJECT CONFIG (colors + icons)
# ─────────────────────────────────────────
SUBJECTS = {
    "Physical Chemistry":   {"color": "#00f2fe", "icon": "⚗️"},
    "Organic Chemistry":    {"color": "#a78bfa", "icon": "🧪"},
    "Inorganic Chemistry":  {"color": "#34d399", "icon": "🔬"},
    "Physics":              {"color": "#f59e0b", "icon": "⚡"},
    "Mathematics":          {"color": "#f472b6", "icon": "∑"},
    "Mock Test / Revision": {"color": "#94a3b8", "icon": "📋"},
}

def get_color(subject):
    return SUBJECTS.get(subject, {}).get("color", "#00f2fe")

def get_icon(subject):
    return SUBJECTS.get(subject, {}).get("icon", "📚")

# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
if 'username' not in st.session_state:
    st.markdown("""
    <div style="min-height: 80vh; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <div style="text-align: center; margin-bottom: 48px;">
            <div style="font-size: 0.65rem; letter-spacing: 8px; color: #333; text-transform: uppercase; font-family: 'Space Mono', monospace; margin-bottom: 16px;">
                SYSTEM BOOT
            </div>
            <h1 style="font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; color: #fff; margin: 0; line-height: 1;">
                NEON<span style="color: #00f2fe;">.</span>OS
            </h1>
            <div style="font-size: 0.65rem; letter-spacing: 6px; color: #222; text-transform: uppercase; font-family: 'Space Mono', monospace; margin-top: 12px;">
                JEE STUDY TERMINAL
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        user_input = st.text_input("", placeholder="ENTER CODENAME")
        if st.button("⟶  AUTHENTICATE"):
            if user_input.strip():
                st.session_state.username = user_input.strip()
                st.rerun()
    st.stop()

# ─────────────────────────────────────────
# LOAD DATA (per user, safe)
# ─────────────────────────────────────────
@st.cache_data(ttl=5)
def load_data(user):
    try:
        response = supabase.table("study_logs").select("*").eq("username", user).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['Date'] = pd.to_datetime(df['Date'])
            df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce').fillna(0)
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=["Date", "Subject", "Task", "Duration", "Time", "username"])

db = load_data(st.session_state.username)

# ─────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────
for k, v in {
    'session_active': False, 'session_paused': False,
    'start_time': 0.0, 'accumulated_time': 0.0,
    'current_subject': '', 'current_task': '',
    'zen_mode': False
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────
# ZEN MODE OVERRIDE
# ─────────────────────────────────────────
if st.session_state.session_active and st.session_state.zen_mode:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    header { display: none !important; }
    .main .block-container { padding: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)
    page = "Live Session"
else:
    # SIDEBAR
    with st.sidebar:
        st.markdown(f"""
        <div class="user-badge">
            <div class="user-dot"></div>
            <div>
                <div style="font-size: 0.6rem; letter-spacing: 3px; color: #333; text-transform: uppercase; font-family: 'Space Mono', monospace;">LOGGED IN</div>
                <div style="font-size: 0.9rem; font-weight: 700; color: #fff;">{st.session_state.username}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("LOGOUT"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.55rem; letter-spacing: 4px; color: #222; text-transform: uppercase; font-family: Space Mono, monospace; padding-left: 4px; margin-bottom: 8px;'>NAVIGATE</div>", unsafe_allow_html=True)
        page = st.radio("", ["Live Session", "Daily Timeline", "Deep Analytics"], label_visibility="collapsed")

        # Sidebar stats teaser
        if not db.empty:
            st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)
            total_hrs = round(db['Duration'].sum() / 60, 1)
            total_sessions = len(db)
            st.markdown(f"""
            <div style="padding: 16px; background: #060606; border: 1px solid #0e0e0e; border-radius: 10px;">
                <div style="font-size: 0.55rem; letter-spacing: 3px; color: #222; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 12px;">ALL TIME</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #00f2fe; font-family: Space Mono, monospace; line-height: 1;">{total_hrs}h</div>
                <div style="font-size: 0.6rem; color: #333; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px;">{total_sessions} SESSIONS</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# PAGE 1 — LIVE SESSION
# ═══════════════════════════════════════════
if page == "Live Session":

    if not st.session_state.session_active:
        st.markdown("""
        <h1 style='font-size: 2.8rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 4px;'>
            START SESSION
        </h1>
        <p style='color: #333; font-size: 0.7rem; letter-spacing: 4px; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 40px;'>
            LOCK IN · TRACK · CRUSH IT
        </p>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns([1.2, 1])
        with col_a:
            subject = st.selectbox("SUBJECT", list(SUBJECTS.keys()))
            task_notes = st.text_input("SESSION GOAL", placeholder="e.g., HC Verma Ch.8 — Optics")
        with col_b:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            # Subject preview card
            subj_color = get_color(subject)
            subj_icon = get_icon(subject)
            st.markdown(f"""
            <div style="background: #060606; border: 1px solid #111; border-left: 3px solid {subj_color}; border-radius: 10px; padding: 20px 24px; margin-top: 8px;">
                <div style="font-size: 2rem; margin-bottom: 8px;">{subj_icon}</div>
                <div style="font-size: 0.6rem; letter-spacing: 4px; text-transform: uppercase; font-family: Space Mono, monospace; color: {subj_color};">{subject}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
        zen_toggle = st.toggle("🌌  ZEN MODE — hide all distractions")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("▶  LAUNCH SESSION"):
                st.session_state.zen_mode = zen_toggle
                st.session_state.session_active = True
                st.session_state.start_time = time.time()
                st.session_state.accumulated_time = 0.0
                st.session_state.current_subject = subject
                st.session_state.current_task = task_notes
                st.rerun()

    else:
        subj_color = get_color(st.session_state.current_subject)
        subj_icon = get_icon(st.session_state.current_subject)

        if st.session_state.session_paused:
            st.markdown(f"""
            <div style="text-align:center; padding: 8px; background: rgba(245,158,11,0.05); border: 1px solid rgba(245,158,11,0.15); border-radius: 8px; margin-bottom: 16px;">
                <span style="font-size: 0.6rem; letter-spacing: 5px; color: #f59e0b; text-transform: uppercase; font-family: Space Mono, monospace;">⏸  PAUSED</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; margin-bottom: 8px;">
            <span style="font-size: 0.6rem; letter-spacing: 5px; color: #333; text-transform: uppercase; font-family: Space Mono, monospace;">{subj_icon}  {st.session_state.current_subject}</span>
        </div>
        """, unsafe_allow_html=True)

        start_time_ms = int(st.session_state.start_time * 1000)
        accumulated_ms = int(st.session_state.accumulated_time * 1000)
        is_paused_js = "true" if st.session_state.session_paused else "false"
        glow_color = subj_color

        flip_clock_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 220px;
            overflow: hidden;
        }}
        .clock-wrap {{
            display: flex;
            align-items: center;
            gap: 8px;
            opacity: {"0.35" if st.session_state.session_paused else "1"};
            transition: opacity 0.4s ease;
        }}
        .unit {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
        }}
        .digit-card {{
            background: #050505;
            border: 1px solid #0e0e0e;
            border-radius: 10px;
            width: 130px;
            height: 130px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }}
        .digit-card::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: #000;
            z-index: 2;
        }}
        .digit-card::before {{
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(ellipse at 50% 0%, rgba({','.join(str(int(glow_color.lstrip('#')[i:i+2], 16)) for i in (0,2,4))}, 0.06) 0%, transparent 70%);
        }}
        .digit {{
            font-family: 'Space Mono', monospace;
            font-size: 78px;
            font-weight: 700;
            color: {glow_color};
            text-shadow: 0 0 20px {glow_color}66, 0 0 50px {glow_color}22;
            letter-spacing: -3px;
            line-height: 1;
            position: relative;
            z-index: 1;
            transition: all 0.1s;
        }}
        .label {{
            font-family: 'Space Mono', monospace;
            font-size: 9px;
            letter-spacing: 4px;
            color: #1e1e1e;
            text-transform: uppercase;
        }}
        .sep {{
            font-family: 'Space Mono', monospace;
            font-size: 60px;
            color: #111;
            margin-bottom: 22px;
            font-weight: 700;
        }}
        </style>
        </head>
        <body>
        <div class="clock-wrap">
            <div class="unit">
                <div class="digit-card"><div class="digit" id="h">00</div></div>
                <div class="label">HOURS</div>
            </div>
            <div class="sep">:</div>
            <div class="unit">
                <div class="digit-card"><div class="digit" id="m">00</div></div>
                <div class="label">MINS</div>
            </div>
            <div class="sep">:</div>
            <div class="unit">
                <div class="digit-card"><div class="digit" id="s">00</div></div>
                <div class="label">SECS</div>
            </div>
        </div>
        <script>
        var startTime = {start_time_ms};
        var acc = {accumulated_ms};
        var isPaused = {is_paused_js};
        var prevS = -1;

        function pad(n) {{ return n.toString().padStart(2,'0'); }}

        function update(d) {{
            var h = Math.floor(d/3600000);
            var m = Math.floor((d%3600000)/60000);
            var s = Math.floor((d%60000)/1000);
            document.getElementById("h").innerText = pad(h);
            document.getElementById("m").innerText = pad(m);
            var sEl = document.getElementById("s");
            if(s !== prevS) {{
                sEl.style.transform = 'scale(1.08)';
                setTimeout(function(){{ sEl.style.transform = 'scale(1)'; }}, 120);
                prevS = s;
            }}
            sEl.innerText = pad(s);
        }}

        if(isPaused) {{
            update(acc);
        }} else {{
            setInterval(function() {{
                update(acc + (new Date().getTime() - startTime));
            }}, 250);
        }}
        </script>
        </body>
        </html>
        """
        components.html(flip_clock_html, height=220)

        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.session_state.session_paused:
                if st.button("▶  RESUME"):
                    st.session_state.start_time = time.time()
                    st.session_state.session_paused = False
                    st.rerun()
            else:
                if st.button("⏸  PAUSE"):
                    st.session_state.accumulated_time += (time.time() - st.session_state.start_time)
                    st.session_state.session_paused = True
                    st.rerun()
        with c3:
            if st.button("⏹  SAVE & END"):
                if not st.session_state.session_paused:
                    st.session_state.accumulated_time += (time.time() - st.session_state.start_time)
                duration_mins = round(st.session_state.accumulated_time / 60, 2)
                h = datetime.now().hour
                time_of_day = "Morning" if h < 12 else "Afternoon" if h < 18 else "Evening/Night"
                new_row = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Subject": st.session_state.current_subject,
                    "Task": st.session_state.current_task,
                    "Duration": duration_mins,
                    "Time": time_of_day,
                    "username": st.session_state.username
                }
                supabase.table("study_logs").insert(new_row).execute()
                st.session_state.session_active = False
                st.session_state.zen_mode = False
                st.cache_data.clear()
                st.balloons()
                time.sleep(1.5)
                st.rerun()


# ═══════════════════════════════════════════
# PAGE 2 — DAILY TIMELINE
# ═══════════════════════════════════════════
elif page == "Daily Timeline":
    st.markdown("""
    <h1 style='font-size: 2.8rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 4px;'>TODAY</h1>
    <p style='color: #333; font-size: 0.65rem; letter-spacing: 4px; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 40px;'>
        SESSION LOG
    </p>
    """, unsafe_allow_html=True)

    today = pd.Timestamp.now().normalize()
    todays_data = db[db["Date"] == today].copy() if not db.empty else pd.DataFrame()

    if todays_data.empty:
        st.markdown("""
        <div style="text-align: center; padding: 80px 0; color: #1e1e1e;">
            <div style="font-size: 3rem; margin-bottom: 16px;">◎</div>
            <div style="font-size: 0.65rem; letter-spacing: 4px; text-transform: uppercase; font-family: Space Mono, monospace;">NO SESSIONS YET TODAY</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_mins = todays_data['Duration'].sum()
        total_hrs = round(total_mins / 60, 2)
        session_count = len(todays_data)

        c1, c2, c3 = st.columns(3)
        c1.metric("HOURS TODAY", f"{total_hrs}h")
        c2.metric("SESSIONS", session_count)
        c3.metric("TOP SUBJECT", todays_data.groupby('Subject')['Duration'].sum().idxmax() if not todays_data.empty else "—")

        st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)

        # Timeline visual
        st.markdown("<div style='font-size: 0.6rem; letter-spacing: 4px; color: #222; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 20px;'>SESSION BREAKDOWN</div>", unsafe_allow_html=True)

        for _, row in todays_data.sort_values('Duration', ascending=False).iterrows():
            subj_color = get_color(row['Subject'])
            pct = min(100, (row['Duration'] / (todays_data['Duration'].max() + 0.01)) * 100)
            dur_str = f"{int(row['Duration'])}m" if row['Duration'] < 60 else f"{row['Duration']/60:.1f}h"
            task_str = row['Task'] if str(row['Task']) not in ['nan', 'None', ''] else "—"
            st.markdown(f"""
            <div style="background: #040404; border: 1px solid #0e0e0e; border-radius: 10px; padding: 16px 20px; margin-bottom: 10px; position: relative; overflow: hidden;">
                <div style="position: absolute; bottom: 0; left: 0; height: 2px; width: {pct}%; background: {subj_color}; opacity: 0.6;"></div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase; font-family: Space Mono, monospace; color: {subj_color};">{get_icon(row['Subject'])}  {row['Subject']}</div>
                        <div style="font-size: 0.8rem; color: #555; margin-top: 5px;">{task_str}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: 800; color: #fff; font-family: Space Mono, monospace;">{dur_str}</div>
                        <div style="font-size: 0.6rem; color: #222; text-transform: uppercase; letter-spacing: 2px;">{row['Time']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PAGE 3 — DEEP ANALYTICS
# ═══════════════════════════════════════════
elif page == "Deep Analytics":
    st.markdown("""
    <h1 style='font-size: 2.8rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 4px;'>ANALYTICS</h1>
    <p style='color: #333; font-size: 0.65rem; letter-spacing: 4px; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 32px;'>
        DEEP INTELLIGENCE
    </p>
    """, unsafe_allow_html=True)

    if db.empty:
        st.markdown("""
        <div style="text-align: center; padding: 80px 0; color: #1e1e1e;">
            <div style="font-size: 3rem; margin-bottom: 16px;">◎</div>
            <div style="font-size: 0.65rem; letter-spacing: 4px; text-transform: uppercase; font-family: Space Mono, monospace;">RECORD SESSIONS TO SEE ANALYTICS</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        tf = st.selectbox("TIMEFRAME", ["Today", "Yesterday", "This Week", "This Month", "This Year", "All Time"])
        now = pd.Timestamp.now().normalize()

        if tf == "Today":             fdb = db[db['Date'] == now]
        elif tf == "Yesterday":       fdb = db[db['Date'] == now - pd.Timedelta(days=1)]
        elif tf == "This Week":       fdb = db[(db['Date'].dt.isocalendar().week == now.isocalendar().week) & (db['Date'].dt.year == now.year)]
        elif tf == "This Month":      fdb = db[(db['Date'].dt.month == now.month) & (db['Date'].dt.year == now.year)]
        elif tf == "This Year":       fdb = db[db['Date'].dt.year == now.year]
        else:                         fdb = db.copy()

        if fdb.empty:
            st.info(f"No data for {tf}.")
        else:
            # ── HERO METRICS ──
            total_hrs = round(fdb['Duration'].sum() / 60, 1)
            top_subj = fdb.groupby('Subject')['Duration'].sum().idxmax()
            avg_session = round(fdb['Duration'].mean(), 1)
            streak = 0
            if tf in ["All Time", "This Year", "This Month", "This Week"]:
                dates = db['Date'].dt.normalize().unique()
                d = now
                while d in dates:
                    streak += 1
                    d -= pd.Timedelta(days=1)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("TOTAL HOURS", f"{total_hrs}h")
            c2.metric("TOP SUBJECT", top_subj.split()[0])
            c3.metric("AVG SESSION", f"{avg_session}m")
            c4.metric("DAY STREAK 🔥", f"{streak}")

            st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)

            CHART_LAYOUT = dict(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Space Mono, monospace', color='#333', size=10),
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False,
            )
            AXIS_STYLE = dict(
                showgrid=True,
                gridcolor='#0a0a0a',
                gridwidth=1,
                zeroline=False,
                showline=False,
                tickfont=dict(color='#333', size=9),
                tickcolor='#111',
            )

            # ── ROW 1: Donut + Bar ──
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<div style='font-size: 0.55rem; letter-spacing: 4px; color: #222; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 12px;'>SUBJECT MIX</div>", unsafe_allow_html=True)
                subj_sum = fdb.groupby('Subject')['Duration'].sum().reset_index()
                colors = [get_color(s) for s in subj_sum['Subject']]
                fig_donut = go.Figure(go.Pie(
                    labels=subj_sum['Subject'],
                    values=subj_sum['Duration'],
                    hole=0.72,
                    marker=dict(colors=colors, line=dict(color='#000', width=3)),
                    textinfo='none',
                    hovertemplate='<b>%{label}</b><br>%{value:.0f} min<extra></extra>',
                ))
                fig_donut.add_annotation(
                    text=f"<b>{total_hrs}h</b>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=28, color='#00f2fe', family='Space Mono, monospace')
                )
                fig_donut.update_layout(**CHART_LAYOUT, height=260)
                st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

                # Subject legend
                for _, r in subj_sum.sort_values('Duration', ascending=False).iterrows():
                    pct = round(r['Duration'] / subj_sum['Duration'].sum() * 100, 1)
                    c = get_color(r['Subject'])
                    st.markdown(f"""
                    <div style="display:flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #080808;">
                        <div style="display:flex; align-items:center; gap: 8px;">
                            <div style="width:6px; height:6px; border-radius:50%; background:{c}; box-shadow: 0 0 6px {c}66;"></div>
                            <span style="font-size:0.7rem; color: #555;">{r['Subject']}</span>
                        </div>
                        <span style="font-size:0.65rem; font-family: Space Mono, monospace; color: {c};">{pct}%</span>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.markdown("<div style='font-size: 0.55rem; letter-spacing: 4px; color: #222; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 12px;'>HOURS BY SUBJECT</div>", unsafe_allow_html=True)
                subj_hrs = subj_sum.copy()
                subj_hrs['Hours'] = subj_hrs['Duration'] / 60
                subj_hrs['ShortLabel'] = subj_hrs['Subject'].apply(lambda x: x.split()[0])
                subj_hrs = subj_hrs.sort_values('Hours', ascending=True)
                colors_bar = [get_color(s) for s in subj_hrs['Subject']]

                fig_bar = go.Figure(go.Bar(
                    x=subj_hrs['Hours'],
                    y=subj_hrs['ShortLabel'],
                    orientation='h',
                    marker=dict(
                        color=colors_bar,
                        opacity=0.85,
                        line=dict(width=0),
                    ),
                    hovertemplate='<b>%{y}</b><br>%{x:.1f}h<extra></extra>',
                ))
                fig_bar.update_layout(
                    **CHART_LAYOUT,
                    height=300,
                    xaxis=dict(**AXIS_STYLE, title=''),
                    yaxis=dict(**AXIS_STYLE, title='', showgrid=False),
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

            st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)

            # ── ROW 2: Daily trend heatmap-style area chart ──
            if tf not in ["Today", "Yesterday"]:
                st.markdown("<div style='font-size: 0.55rem; letter-spacing: 4px; color: #222; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 12px;'>DAILY STUDY HOURS</div>", unsafe_allow_html=True)

                daily = fdb.groupby('Date')['Duration'].sum().reset_index()
                daily['Hours'] = daily['Duration'] / 60

                fig_area = go.Figure()
                fig_area.add_trace(go.Scatter(
                    x=daily['Date'],
                    y=daily['Hours'],
                    mode='lines',
                    line=dict(color='#00f2fe', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0,242,254,0.04)',
                    hovertemplate='%{x|%b %d}<br><b>%{y:.1f}h</b><extra></extra>',
                ))
                fig_area.update_layout(
                    **CHART_LAYOUT,
                    height=200,
                    xaxis=dict(**AXIS_STYLE, title=''),
                    yaxis=dict(**AXIS_STYLE, title=''),
                )
                st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})

            # ── ROW 3: Time of Day + Weekly Heatmap ──
            col3, col4 = st.columns(2)

            with col3:
                st.markdown("<div style='font-size: 0.55rem; letter-spacing: 4px; color: #222; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 12px;'>TIME OF DAY</div>", unsafe_allow_html=True)
                tod = fdb.groupby('Time')['Duration'].sum().reset_index()
                tod_order = ["Morning", "Afternoon", "Evening/Night"]
                tod['Time'] = pd.Categorical(tod['Time'], categories=tod_order, ordered=True)
                tod = tod.sort_values('Time')
                tod_colors = ['#f59e0b', '#a78bfa', '#00f2fe']

                fig_tod = go.Figure(go.Bar(
                    x=tod['Time'],
                    y=tod['Duration'] / 60,
                    marker=dict(color=tod_colors[:len(tod)], opacity=0.85, line=dict(width=0)),
                    hovertemplate='%{x}<br><b>%{y:.1f}h</b><extra></extra>',
                ))
                fig_tod.update_layout(
                    **CHART_LAYOUT,
                    height=220,
                    xaxis=dict(**AXIS_STYLE, title=''),
                    yaxis=dict(**AXIS_STYLE, title=''),
                )
                st.plotly_chart(fig_tod, use_container_width=True, config={'displayModeBar': False})

            with col4:
                st.markdown("<div style='font-size: 0.55rem; letter-spacing: 4px; color: #222; text-transform: uppercase; font-family: Space Mono, monospace; margin-bottom: 12px;'>SESSION LOG</div>", unsafe_allow_html=True)
                recent = fdb.sort_values('Date', ascending=False).head(8)
                for _, row in recent.iterrows():
                    subj_color = get_color(row['Subject'])
                    dur_str = f"{int(row['Duration'])}m" if row['Duration'] < 60 else f"{row['Duration']/60:.1f}h"
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 7px 0; border-bottom: 1px solid #080808;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <div style="width:5px; height:5px; border-radius:50%; background:{subj_color};"></div>
                            <span style="font-size:0.7rem; color:#444;">{row['Subject'].split()[0]}</span>
                        </div>
                        <div style="display:flex; gap:12px; align-items:center;">
                            <span style="font-size:0.6rem; color:#222; font-family: Space Mono, monospace;">{row['Date'].strftime('%b %d')}</span>
                            <span style="font-size:0.75rem; font-weight:700; color:{subj_color}; font-family: Space Mono, monospace;">{dur_str}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
