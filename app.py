import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import streamlit.components.v1 as components
from supabase import create_client

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Study OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# DESIGN SYSTEM: Glassmorphism + GPU Hardware Acceleration
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=DM+Mono:wght@300;400;500&display=swap');

/* Base Reset & GPU Accelerated Animations */
*, *::before, *::after { box-sizing: border-box; }

@keyframes fadeSlideUp {
    0% { opacity: 0; transform: translateY(20px); filter: blur(4px); }
    100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 10px rgba(255,255,255,0.1); }
    50% { box-shadow: 0 0 20px rgba(255,255,255,0.3); }
    100% { box-shadow: 0 0 10px rgba(255,255,255,0.1); }
}

/* Background - Fixed to prevent re-paint lag */
html, body, [data-testid="stAppViewContainer"] {
    background: #000 !important;
    background-image: radial-gradient(circle at 50% -20%, #1a1a1f 0%, #000000 70%) !important;
    background-attachment: fixed !important;
    color: #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stHeader"] { background: transparent !important; }
.main .block-container { 
    padding: 3rem 4rem !important; 
    max-width: 1200px !important; 
    animation: fadeSlideUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    will-change: transform, opacity; /* Hardware acceleration */
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255,255,255,0.03) !important;
    background: rgba(5, 5, 5, 0.4) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    transform: translateZ(0); /* Hardware acceleration */
}
section[data-testid="stSidebar"] > div { padding: 3rem 1.5rem !important; }

/* Radio Nav */
[data-testid="stSidebar"] .stRadio label {
    color: #555 !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 12px 16px !important;
    border-radius: 12px;
    transition: all 0.3s ease !important;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover { 
    color: #fff !important; 
    background: rgba(255,255,255,0.05);
    transform: translateX(4px);
}
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"] { background: transparent !important; }

/* Inputs & Textareas */
input, textarea {
    background: rgba(25, 25, 25, 0.5) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}
input:focus, textarea:focus { 
    border-color: rgba(255,255,255,0.3) !important; 
    background: rgba(35, 35, 35, 0.8) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(25, 25, 25, 0.5) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    color: #e8e8e8 !important;
}

/* Labels */
label[data-testid="stWidgetLabel"] p {
    color: #666 !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-family: 'DM Mono', monospace !important;
    margin-bottom: 8px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(180deg, #222, #111) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 50px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    background: linear-gradient(180deg, #333, #1a1a1a) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(15, 15, 15, 0.4) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
    border-radius: 24px !important;
    padding: 1.5rem !important;
    transform: translateZ(0); /* Hardware acceleration */
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-family: 'DM Mono', monospace !important;
    font-weight: 400 !important;
    font-size: 2.2rem !important;
    letter-spacing: -1.5px !important;
}
[data-testid="stMetricLabel"] p {
    color: #888 !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Custom UI Classes */
.glass-card {
    background: rgba(12, 12, 12, 0.5);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    transform: translateZ(0); /* Hardware acceleration */
}
.list-item {
    background: rgba(10, 10, 10, 0.4);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.03);
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
    transform: translateZ(0);
}

[data-testid="stToggle"] p { font-size: 0.85rem !important; color: #aaa !important; font-weight: 500;}
hr { border-color: rgba(255,255,255,0.05) !important; margin: 2rem 0 !important; }
#MainMenu, footer, [data-testid="stDeployButton"], [data-testid="stDecoration"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SUBJECTS
# ─────────────────────────────────────────────────────────────
SUBJECTS = {
    "Physical Chemistry":   {"dot": "#3b82f6", "label": "Phys Chem"},
    "Organic Chemistry":    {"dot": "#a855f7", "label": "Org Chem"},
    "Inorganic Chemistry":  {"dot": "#10b981", "label": "Inorg Chem"},
    "Physics":              {"dot": "#f97316", "label": "Physics"},
    "Mathematics":          {"dot": "#ec4899", "label": "Maths"},
    "Mock Test / Revision": {"dot": "#94a3b8", "label": "Mock / Rev"},
}
def sdot(s):   return SUBJECTS.get(s, {}).get("dot", "#555")
def slabel(s): return SUBJECTS.get(s, {}).get("label", s)

# ─────────────────────────────────────────────────────────────
# SUPABASE (Cached for 5 minutes to prevent lag)
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

@st.cache_data(ttl=300) 
def load_data(user):
    try:
        r = supabase.table("study_logs").select("*").eq("username", user).execute()
        if r.data:
            df = pd.DataFrame(r.data)
            df['Date'] = pd.to_datetime(df['Date'])
            df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce').fillna(0)
            return df
    except Exception: pass
    return pd.DataFrame(columns=["Date","Subject","Task","Duration","Time","username"])

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────
for k, v in dict(
    session_active=False, session_paused=False,
    start_time=0.0, accumulated_time=0.0,
    current_subject="", current_task="", zen_mode=False
).items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# LOGIN SCREEN
# ─────────────────────────────────────────────────────────────
if 'username' not in st.session_state:
    st.markdown("<div style='height:20vh'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style='text-align: left;'>
            <p style='font-size:0.65rem; letter-spacing:4px; color:#555; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:16px;'>System Initialized</p>
            <h1 style='font-size:4rem; font-weight:300; letter-spacing:-2.5px; color:#fff; line-height:1; margin-bottom:40px;'>Study OS.</h1>
        </div>
        """, unsafe_allow_html=True)
        name = st.text_input("", placeholder="Enter your operator ID (Name)")
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("Initialize Terminal →"):
            if name.strip():
                st.session_state.username = name.strip()
                st.rerun()
    st.stop()

db = load_data(st.session_state.username)

# ─────────────────────────────────────────────────────────────
# SYSTEM HEARTBEAT (Prevents session timeout during long focus)
# ─────────────────────────────────────────────────────────────
@st.fragment(run_every="5m")
def keep_alive_ping():
    # Invisible ping to the server to keep WebSocket alive
    pass

if st.session_state.session_active:
    keep_alive_ping()

# ─────────────────────────────────────────────────────────────
# UI FRAGMENT: LIVE SESSION (Stops full-page reload lag)
# ─────────────────────────────────────────────────────────────
@st.fragment
def live_session_fragment():
    if not st.session_state.session_active:
        st.markdown("""
        <h1 style='font-size:3rem; font-weight:400; letter-spacing:-1.5px; color:#fff; margin-bottom:4px;'>Terminal.</h1>
        <p style='color:#777; font-size:0.7rem; letter-spacing:4px; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:48px;'>Initialize New Focus State</p>
        """, unsafe_allow_html=True)

        col_a, _, col_b = st.columns([1.2, 0.1, 0.9])
        with col_a:
            subject = st.selectbox("Subject Protocol", list(SUBJECTS.keys()))
            task    = st.text_input("Objective", placeholder="e.g., Optics Chapter 8")
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            zen     = st.toggle("Enable Zen Mode (Hide UI)")

        with col_b:
            dc = sdot(subject)
            st.markdown(f"""
            <div class="glass-card" style='margin-top: 28px; text-align: center; padding: 40px 20px;'>
                <div style='width:12px; height:12px; border-radius:50%; background:{dc}; box-shadow:0 0 20px {dc}; margin: 0 auto 20px auto; animation: pulseGlow 2s infinite;'></div>
                <p style='font-size:1.2rem; font-weight:500; color:#fff; margin-bottom:4px;'>{slabel(subject)}</p>
                <p style='font-size:0.8rem; color:#888; font-family: DM Mono;'>Awaiting execution...</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        _, bc, _ = st.columns([1, 0.8, 1])
        with bc:
            if st.button("Execute Session →"):
                st.session_state.zen_mode = zen
                st.session_state.session_active = True
                st.session_state.start_time = time.time()
                st.session_state.accumulated_time = 0.0
                st.session_state.current_subject = subject
                st.session_state.current_task = task
                st.rerun()

    else:
        dc = sdot(st.session_state.current_subject)
        lbl = slabel(st.session_state.current_subject)
        paused = st.session_state.session_paused

        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:40px;'>
            <div>
                <div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>
                    <div style='width:10px; height:10px; border-radius:50%; background:{dc}; {"" if paused else "box-shadow:0 0 15px " + dc + "; animation: pulseGlow 2s infinite;"}'></div>
                    <p style='font-size:1.1rem; font-weight:500; color:#eee; letter-spacing:0.5px;'>{lbl}</p>
                </div>
                {"<p style='font-size:0.7rem; letter-spacing:4px; color:#f97316; text-transform:uppercase; font-family:DM Mono,monospace;'>System Paused</p>" if paused else "<p style='font-size:0.7rem; letter-spacing:4px; color:#10b981; text-transform:uppercase; font-family:DM Mono,monospace;'>System Active</p>"}
            </div>
            <p style='font-size:1.1rem; color:#888; font-weight:300;'>{st.session_state.current_task}</p>
        </div>
        """, unsafe_allow_html=True)

        sms = int(st.session_state.start_time * 1000)
        ams = int(st.session_state.accumulated_time * 1000)
        pjs = "true" if paused else "false"
        op  = "0.3" if paused else "1"

        components.html(f"""<!DOCTYPE html><html><head>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400&display=swap');
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{background:transparent;display:flex;justify-content:center;align-items:center;height:220px;overflow:hidden;}}
        .w{{display:flex;align-items:center;gap:15px;opacity:{op};transition:opacity 0.6s ease;}}
        .seg{{display:flex;flex-direction:column;align-items:center;gap:10px; background: rgba(20,20,20,0.5); padding: 20px 30px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.03); backdrop-filter: blur(10px); box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);}}
        .n{{font-family:'DM Mono',monospace;font-size:100px;font-weight:300;color:#fff; letter-spacing:-4px;line-height:0.9; text-shadow: 0 0 30px rgba(255,255,255,0.1); transition: opacity 0.1s;}}
        .l{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:4px;color:#666;text-transform:uppercase;}}
        .c{{font-family:'DM Mono',monospace;font-size:70px;font-weight:300;color:#333;margin-bottom:30px;}}
        </style></head><body>
        <div class="w">
            <div class="seg"><span class="n" id="h">00</span><span class="l">Hours</span></div>
            <span class="c">:</span>
            <div class="seg"><span class="n" id="m">00</span><span class="l">Minutes</span></div>
            <span class="c">:</span>
            <div class="seg"><span class="n" id="s">00</span><span class="l">Seconds</span></div>
        </div>
        <script>
        var t0={sms},acc={ams},paused={pjs},prev=-1;
        function pad(n){{return n.toString().padStart(2,'0');}}
        function tick(){{
            var d=paused?acc:acc+(Date.now()-t0);
            var h=Math.floor(d/3600000),m=Math.floor((d%3600000)/60000),s=Math.floor((d%60000)/1000);
            document.getElementById('h').textContent=pad(h);
            document.getElementById('m').textContent=pad(m);
            var el=document.getElementById('s');
            if(s!==prev){{el.style.opacity='0.6';setTimeout(function(){{el.style.opacity='1';}},80);prev=s;}}
            el.textContent=pad(s);
        }}
        tick();
        if(!paused) setInterval(tick,100);
        </script></body></html>""", height=240)

        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        c1, _, c3 = st.columns([1, 0.2, 1])
        with c1:
            if paused:
                if st.button("Resume Protocol"):
                    st.session_state.start_time = time.time()
                    st.session_state.session_paused = False
                    st.rerun()
            else:
                if st.button("Pause Protocol"):
                    st.session_state.accumulated_time += time.time() - st.session_state.start_time
                    st.session_state.session_paused = True
                    st.rerun()
        with c3:
            if st.button("Terminate & Save"):
                if not paused: st.session_state.accumulated_time += time.time() - st.session_state.start_time
                mins = round(st.session_state.accumulated_time / 60, 2)
                h = datetime.now().hour
                tod = "Morning" if h < 12 else "Afternoon" if h < 18 else "Evening/Night"
                supabase.table("study_logs").insert({
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Subject": st.session_state.current_subject,
                    "Task": st.session_state.current_task,
                    "Duration": mins,
                    "Time": tod,
                    "username": st.session_state.username
                }).execute()
                st.session_state.session_active = False
                st.session_state.zen_mode = False
                st.cache_data.clear()
                st.balloons()
                time.sleep(1.2)
                st.rerun()

# ─────────────────────────────────────────────────────────────
# SIDEBAR / NAVIGATION
# ─────────────────────────────────────────────────────────────
if st.session_state.session_active and st.session_state.zen_mode:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"],[data-testid="collapsedControl"],header{display:none!important;}
    .main .block-container{padding:4rem!important; max-width: 900px !important;}
    </style>""", unsafe_allow_html=True)
    page = "Live Session"
else:
    with st.sidebar:
        is_live = st.session_state.session_active
        dot_col = "#10b981" if is_live else "#333"
        st.markdown(f"""
        <div style='margin-bottom:40px; padding: 12px; border-radius: 16px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.03);'>
            <p style='font-size:0.55rem; letter-spacing:2px; color:#666; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:10px;'>ACTIVE USER</p>
            <div style='display:flex; align-items:center; gap:12px;'>
                <div style='width:8px; height:8px; border-radius:50%; background:{dot_col}; {"box-shadow: 0 0 12px " + dot_col if is_live else ""}; transition: all 0.3s ease;'></div>
                <span style='font-size:1.1rem; font-weight:500; color:#eee;'>{st.session_state.username}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.radio("", ["Live Session","Daily Timeline","Deep Analytics"], label_visibility="collapsed")
        
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        if st.button("Sign Out"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
            
        if not db.empty:
            total_all = round(db['Duration'].sum()/60, 1)
            st.markdown(f"""
            <div style='margin-top:auto; padding-top:40px;'>
                <div class="glass-card" style="padding: 20px;">
                    <p style='font-size:0.55rem; letter-spacing:2px; color:#888; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:8px;'>LIFETIME HOURS</p>
                    <p style='font-size:2.2rem; font-weight:400; color:#fff; font-family:DM Mono,monospace; letter-spacing:-1px; margin-bottom:0;'>
                        {total_all}<span style='font-size:1rem; color:#666;'>h</span></p>
                    <p style='font-size:0.7rem; color:#555; margin-top: 4px;'>Across {len(db)} sessions</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────────────────────────
if page == "Live Session":
    live_session_fragment()

elif page == "Daily Timeline":
    st.markdown("""
    <h1 style='font-size:3rem; font-weight:400; letter-spacing:-1.5px; color:#fff; margin-bottom:4px;'>Timeline.</h1>
    <p style='color:#777; font-size:0.7rem; letter-spacing:4px; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:40px;'>Today's Action Log</p>
    """, unsafe_allow_html=True)

    today = pd.Timestamp.now().normalize()
    tdf   = db[db["Date"] == today].copy() if not db.empty else pd.DataFrame()

    if tdf.empty:
        st.markdown("""
        <div style='text-align:center; padding:120px 0;'>
            <p style='font-size:3rem; color:#222; margin-bottom:20px;'>∅</p>
            <p style='font-size:0.7rem; letter-spacing:4px; color:#555; text-transform:uppercase; font-family:DM Mono,monospace;'>Data absent for current cycle</p>
        </div>""", unsafe_allow_html=True)
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Time Invested", f"{round(tdf['Duration'].sum()/60,1)}h")
        c2.metric("Total Blocks", len(tdf))
        c3.metric("Primary Focus", slabel(tdf.groupby('Subject')['Duration'].sum().idxmax()))
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

        for _, row in tdf.sort_values('Duration', ascending=False).iterrows():
            dc      = sdot(row['Subject'])
            dur     = row['Duration']
            dur_str = f"{int(dur)}m" if dur < 60 else f"{dur/60:.1f}h"
            bw      = int(min(100, dur / (tdf['Duration'].max()+0.01) * 100))
            task_s  = str(row.get('Task',''))
            task_s  = "" if task_s in ['nan','None',''] else task_s
            
            st.markdown(f"""
            <div class="list-item">
                <div style='position:absolute; bottom:0; left:0; height:2px; width:{bw}%; background: linear-gradient(90deg, transparent, {dc}); box-shadow: 0 0 10px {dc};'></div>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <div style='display:flex; align-items:center; gap:12px; margin-bottom:6px;'>
                            <div style='width:8px; height:8px; border-radius:50%; background:{dc}; box-shadow: 0 0 8px {dc}88;'></div>
                            <span style='font-size:1rem; font-weight:500; color:#eee;'>{slabel(row["Subject"])}</span>
                        </div>
                        {"<p style='font-size:0.8rem; color:#888; font-weight: 300; padding-left:20px; margin:0;'>" + task_s + "</p>" if task_s else ""}
                    </div>
                    <div style='text-align:right;'>
                        <p style='font-size:1.8rem; font-weight:300; color:#fff; font-family:DM Mono,monospace; letter-spacing:-1.5px; margin-bottom:2px;'>{dur_str}</p>
                        <p style='font-size:0.65rem; color:#666; font-family: DM Mono; text-transform: uppercase; letter-spacing: 1px;'>{row["Time"]}</p>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

elif page == "Deep Analytics":
    st.markdown("""
    <h1 style='font-size:3rem; font-weight:400; letter-spacing:-1.5px; color:#fff; margin-bottom:4px;'>Telemetry.</h1>
    <p style='color:#777; font-size:0.7rem; letter-spacing:4px; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:40px;'>Macro Systems Analysis</p>
    """, unsafe_allow_html=True)

    if db.empty:
        st.markdown("""
        <div style='text-align:center; padding:120px 0;'>
            <p style='font-size:3rem; color:#222; margin-bottom:20px;'>⍉</p>
            <p style='font-size:0.7rem; letter-spacing:4px; color:#555; text-transform:uppercase; font-family:DM Mono,monospace;'>Insufficient data for telemetry</p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    tf  = st.selectbox("", ["Today","Yesterday","This Week","This Month","This Year","All Time"], label_visibility="collapsed")
    now = pd.Timestamp.now().normalize()

    if   tf == "Today":      fdb = db[db['Date'] == now]
    elif tf == "Yesterday":  fdb = db[db['Date'] == now - pd.Timedelta(days=1)]
    elif tf == "This Week":  fdb = db[(db['Date'].dt.isocalendar().week == now.isocalendar().week) & (db['Date'].dt.year == now.year)]
    elif tf == "This Month": fdb = db[(db['Date'].dt.month==now.month)&(db['Date'].dt.year==now.year)]
    elif tf == "This Year":  fdb = db[db['Date'].dt.year == now.year]
    else:                    fdb = db.copy()

    if fdb.empty:
        st.markdown(f"<p style='color:#666; font-size:0.9rem; padding:40px 0; text-align:center;'>No telemetry packets found for {tf}.</p>", unsafe_allow_html=True)
        st.stop()

    streak = 0
    all_dates = set(db['Date'].dt.normalize().unique())
    d = now
    while d in all_dates:
        streak += 1
        d -= pd.Timedelta(days=1)

    total_hrs = round(fdb['Duration'].sum()/60, 1)
    top_s     = fdb.groupby('Subject')['Duration'].sum().idxmax()
    avg_m     = round(fdb['Duration'].mean(), 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cumulative Load", f"{total_hrs}h")
    c2.metric("Primary Vector", slabel(top_s))
    c3.metric("Avg Block Size", f"{int(avg_m)}m")
    c4.metric("Active Chain", f"{streak}d")

    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

    def base_layout(height=280):
        return dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='DM Mono, monospace', color='#888', size=10),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            height=height,
            dragmode=False,
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', gridwidth=1, zeroline=False, showline=False, tickfont=dict(color='#666', size=10)),
            yaxis=dict(showgrid=False, zeroline=False, showline=False, tickfont=dict(color='#666', size=10)),
            hoverlabel=dict(bgcolor="rgba(20,20,20,0.9)", font_size=12, font_family="DM Mono")
        )

    col1, col2 = st.columns([1, 1.1])

    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.6rem; letter-spacing:3px; color:#777; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:20px;'>Allocation Mix</p>", unsafe_allow_html=True)
        ss     = fdb.groupby('Subject')['Duration'].sum().reset_index()
        colors = [sdot(s) for s in ss['Subject']]

        fig_d  = go.Figure(go.Pie(labels=[slabel(s) for s in ss['Subject']], values=ss['Duration'], hole=0.75, marker=dict(colors=colors, line=dict(color='#0c0c0c', width=6)), textinfo='none', hovertemplate='<b>%{label}</b><br>%{value:.0f} min<extra></extra>', sort=True))
        fig_d.add_annotation(text=f"{total_hrs}h", x=0.5, y=0.5, showarrow=False, font=dict(size=32, color='#ffffff', family='DM Mono, monospace'))
        layout_d = base_layout(240)
        layout_d.pop('xaxis', None); layout_d.pop('yaxis', None)
        fig_d.update_layout(**layout_d)
        st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        for _, r in ss.sort_values('Duration', ascending=False).iterrows():
            pct = round(r['Duration']/ss['Duration'].sum()*100, 1)
            dc  = sdot(r['Subject'])
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.03);'><div style='display:flex; align-items:center; gap:12px;'><div style='width:6px; height:6px; border-radius:50%; background:{dc}; box-shadow: 0 0 8px {dc};'></div><span style='font-size:0.85rem; color:#ccc; font-weight: 500;'>{slabel(r['Subject'])}</span></div><span style='font-size:0.8rem; font-family:DM Mono,monospace; color:#888;'>{pct}%</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.6rem; letter-spacing:3px; color:#777; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:20px;'>Volume per Protocol</p>", unsafe_allow_html=True)
        sh       = ss.copy()
        sh['h']  = sh['Duration']/60
        sh['lb'] = sh['Subject'].apply(slabel)
        sh       = sh.sort_values('h', ascending=True)

        fig_b = go.Figure(go.Bar(x=sh['h'], y=sh['lb'], orientation='h', marker=dict(color=[sdot(s) for s in sh['Subject']], opacity=0.8, line=dict(width=0)), hovertemplate='<b>%{y}</b><br>%{x:.1f}h<extra></extra>', width=0.4))
        fig_b.update_layout(**base_layout(380))
        st.plotly_chart(fig_b, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    if tf not in ["Today","Yesterday"]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.6rem; letter-spacing:3px; color:#777; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:20px;'>Temporal Density</p>", unsafe_allow_html=True)
        daily    = fdb.groupby('Date')['Duration'].sum().reset_index()
        daily['h'] = daily['Duration']/60

        fig_a = go.Figure(go.Scatter(x=daily['Date'], y=daily['h'], mode='lines', line=dict(color='#fff', width=2, shape='spline', smoothing=1.3), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)', hovertemplate='%{x|%b %d}  <b>%{y:.1f}h</b><extra></extra>'))
        fig_a.update_layout(**base_layout(220))
        st.plotly_chart(fig_a, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.6rem; letter-spacing:3px; color:#777; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:20px;'>Chronotype Shift</p>", unsafe_allow_html=True)
        tod   = fdb.groupby('Time')['Duration'].sum().reset_index()
        order = ["Morning","Afternoon","Evening/Night"]
        tod['Time'] = pd.Categorical(tod['Time'], categories=order, ordered=True)
        tod   = tod.sort_values('Time')
        tcols = ['#f97316','#a855f7','#3b82f6'][:len(tod)]

        fig_t = go.Figure(go.Bar(x=tod['Time'], y=tod['Duration']/60, marker=dict(color=tcols, opacity=0.8, line=dict(width=0)), hovertemplate='%{x}<br><b>%{y:.1f}h</b><extra></extra>', width=0.3))
        fig_t.update_layout(**base_layout(260))
        st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.6rem; letter-spacing:3px; color:#777; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:20px;'>Recent Operations</p>", unsafe_allow_html=True)
        recent = fdb.sort_values('Date', ascending=False).head(8)
        for _, row in recent.iterrows():
            dc      = sdot(row['Subject'])
            dur     = row['Duration']
            dur_str = f"{int(dur)}m" if dur < 60 else f"{dur/60:.1f}h"
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.03);'><div style='display:flex; align-items:center; gap:12px; padding-left: 8px;'><div style='width:6px; height:6px; border-radius:50%; background:{dc}; box-shadow: 0 0 8px {dc};'></div><span style='font-size:0.85rem; color:#ccc; font-weight:500;'>{slabel(row['Subject'])}</span></div><div style='display:flex; align-items:center; gap:20px; padding-right: 8px;'><span style='font-size:0.65rem; color:#666; font-family:DM Mono,monospace; text-transform: uppercase;'>{row['Date'].strftime('%b %d')}</span><span style='font-size:0.95rem; font-weight:400; color:#fff; font-family:DM Mono,monospace; letter-spacing:-0.5px;'>{dur_str}</span></div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
