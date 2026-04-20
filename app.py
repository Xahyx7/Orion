import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import streamlit.components.v1 as components
from supabase import create_client, Client

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Study OS",
    page_icon="○",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# Pure black OLED · DM Sans + DM Mono · muted dot accents only
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=DM+Mono:wght@300;400&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
section[data-testid="stSidebar"],
.main .block-container {
    background-color: #000 !important;
    color: #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.main .block-container { padding: 2.5rem 3.5rem !important; max-width: 1300px !important; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: #161616; }

section[data-testid="stSidebar"] {
    border-right: 1px solid #0d0d0d !important;
    background: #000 !important;
}
section[data-testid="stSidebar"] > div { padding: 2rem 1.5rem !important; }

[data-testid="stSidebar"] .stRadio label {
    color: #2a2a2a !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    padding: 9px 0 !important;
    transition: color 0.2s !important;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #888 !important; }

input, textarea {
    background: #080808 !important;
    color: #e8e8e8 !important;
    border: 1px solid #161616 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s !important;
}
input:focus, textarea:focus { border-color: #2e2e2e !important; outline: none !important; }
input::placeholder { color: #252525 !important; }

[data-testid="stSelectbox"] > div > div {
    background: #080808 !important;
    border: 1px solid #161616 !important;
    border-radius: 10px !important;
    color: #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
}

label[data-testid="stWidgetLabel"] p {
    color: #282828 !important;
    font-size: 0.6rem !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    font-family: 'DM Mono', monospace !important;
}

.stButton > button {
    background: #0a0a0a !important;
    color: #c0c0c0 !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.2px !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    transition: background 0.2s, border-color 0.2s, color 0.2s !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #141414 !important;
    border-color: #2a2a2a !important;
    color: #fff !important;
    box-shadow: none !important;
    transform: none !important;
}

[data-testid="stMetric"] {
    background: #050505 !important;
    border: 1px solid #0d0d0d !important;
    border-radius: 14px !important;
    padding: 1.4rem 1.6rem !important;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-family: 'DM Mono', monospace !important;
    font-weight: 300 !important;
    font-size: 1.9rem !important;
    letter-spacing: -1px !important;
}
[data-testid="stMetricLabel"] p {
    color: #252525 !important;
    font-size: 0.58rem !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    font-family: 'DM Mono', monospace !important;
}

[data-testid="stToggle"] p { font-size: 0.78rem !important; color: #2e2e2e !important; }

hr { border-color: #0d0d0d !important; margin: 2rem 0 !important; }

#MainMenu { display: none !important; }
footer { display: none !important; }
[data-testid="stDeployButton"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SUBJECTS
# ─────────────────────────────────────────────────────────────
SUBJECTS = {
    "Physical Chemistry":   {"dot": "#5b8cff", "label": "Phys Chem"},
    "Organic Chemistry":    {"dot": "#c084fc", "label": "Org Chem"},
    "Inorganic Chemistry":  {"dot": "#34d399", "label": "Inorg Chem"},
    "Physics":              {"dot": "#fb923c", "label": "Physics"},
    "Mathematics":          {"dot": "#f472b6", "label": "Maths"},
    "Mock Test / Revision": {"dot": "#64748b", "label": "Mock / Rev"},
}
def sdot(s):   return SUBJECTS.get(s, {}).get("dot", "#555")
def slabel(s): return SUBJECTS.get(s, {}).get("label", s)

# ─────────────────────────────────────────────────────────────
# SUPABASE
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

@st.cache_data(ttl=5)
def load_data(user):
    try:
        r = supabase.table("study_logs").select("*").eq("username", user).execute()
        if r.data:
            df = pd.DataFrame(r.data)
            df['Date'] = pd.to_datetime(df['Date'])
            df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce').fillna(0)
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=["Date","Subject","Task","Duration","Time","username"])

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
for k, v in dict(
    session_active=False, session_paused=False,
    start_time=0.0, accumulated_time=0.0,
    current_subject="", current_task="", zen_mode=False
).items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────
if 'username' not in st.session_state:
    st.markdown("<div style='height:20vh'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <p style='font-size:0.55rem; letter-spacing:5px; color:#1a1a1a;
                  text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:20px;'>STUDY OS</p>
        <h1 style='font-size:3rem; font-weight:300; letter-spacing:-2px;
                   color:#fff; line-height:1.1; margin-bottom:44px;'>Good to<br>see you.</h1>
        """, unsafe_allow_html=True)
        name = st.text_input("", placeholder="Enter your name")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Continue →"):
            if name.strip():
                st.session_state.username = name.strip()
                st.rerun()
    st.stop()

db = load_data(st.session_state.username)

# ─────────────────────────────────────────────────────────────
# ZEN MODE
# ─────────────────────────────────────────────────────────────
if st.session_state.session_active and st.session_state.zen_mode:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"],[data-testid="collapsedControl"],header{display:none!important;}
    .main .block-container{padding:2rem!important;}
    </style>""", unsafe_allow_html=True)
    page = "Live Session"
else:
    with st.sidebar:
        is_live = st.session_state.session_active
        dot_col = "#fb923c" if is_live else "#1c1c1c"
        st.markdown(f"""
        <div style='margin-bottom:32px;'>
            <p style='font-size:0.5rem; letter-spacing:3px; color:#1a1a1a;
                      text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:8px;'>LOGGED IN</p>
            <div style='display:flex; align-items:center; gap:9px;'>
                <div style='width:6px; height:6px; border-radius:50%; background:{dot_col};
                            {"box-shadow:0 0 6px " + dot_col if is_live else ""}'></div>
                <span style='font-size:0.95rem; font-weight:500; color:#d0d0d0;'>{st.session_state.username}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign out"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        page = st.radio("", ["Live Session","Daily Timeline","Deep Analytics"],
                        label_visibility="collapsed")
        if not db.empty:
            total_all = round(db['Duration'].sum()/60, 1)
            st.markdown(f"""
            <div style='margin-top:48px; padding-top:20px; border-top:1px solid #0d0d0d;'>
                <p style='font-size:0.5rem; letter-spacing:3px; color:#1a1a1a;
                          text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:12px;'>ALL TIME</p>
                <p style='font-size:2rem; font-weight:300; color:#fff;
                          font-family:DM Mono,monospace; letter-spacing:-1px; margin-bottom:4px;'>
                    {total_all}<span style='font-size:0.9rem; color:#282828;'>h</span></p>
                <p style='font-size:0.65rem; color:#1e1e1e;'>{len(db)} sessions</p>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — LIVE SESSION
# ══════════════════════════════════════════════════════════════
if page == "Live Session":

    if not st.session_state.session_active:
        st.markdown("""
        <h1 style='font-size:2.5rem; font-weight:300; letter-spacing:-1.5px; color:#fff; margin-bottom:6px;'>New Session</h1>
        <p style='color:#222; font-size:0.6rem; letter-spacing:3px; text-transform:uppercase;
                  font-family:DM Mono,monospace; margin-bottom:44px;'>SET YOUR FOCUS</p>
        """, unsafe_allow_html=True)

        col_a, _, col_b = st.columns([1.1, 0.08, 0.9])
        with col_a:
            subject = st.selectbox("Subject", list(SUBJECTS.keys()))
            task    = st.text_input("Goal", placeholder="e.g. HC Verma Ch.8 — Optics")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            zen     = st.toggle("Focus mode  ·  hide navigation")

        with col_b:
            dc = sdot(subject)
            st.markdown(f"""
            <div style='margin-top:26px; background:#040404; border:1px solid #0d0d0d;
                        border-radius:14px; padding:24px 26px;'>
                <div style='width:8px; height:8px; border-radius:50%; background:{dc};
                            box-shadow:0 0 12px {dc}33; margin-bottom:14px;'></div>
                <p style='font-size:1rem; font-weight:400; color:#c0c0c0; margin-bottom:3px;'>{slabel(subject)}</p>
                <p style='font-size:0.65rem; color:#1e1e1e;'>ready to track</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        _, bc, _ = st.columns([1, 0.75, 1])
        with bc:
            if st.button("Start →"):
                st.session_state.zen_mode         = zen
                st.session_state.session_active   = True
                st.session_state.start_time       = time.time()
                st.session_state.accumulated_time = 0.0
                st.session_state.current_subject  = subject
                st.session_state.current_task     = task
                st.rerun()

    else:
        dc     = sdot(st.session_state.current_subject)
        lbl    = slabel(st.session_state.current_subject)
        paused = st.session_state.session_paused

        st.markdown(f"""
        <div style='margin-bottom:28px;'>
            <div style='display:flex; align-items:center; gap:9px; margin-bottom:5px;'>
                <div style='width:6px; height:6px; border-radius:50%; background:{dc};
                            {"" if paused else "box-shadow:0 0 8px " + dc + "55;"}'></div>
                <p style='font-size:0.72rem; color:#2e2e2e; letter-spacing:0.5px;'>{lbl}</p>
            </div>
            {"<p style='font-size:0.58rem; letter-spacing:3px; color:#fb923c; text-transform:uppercase; font-family:DM Mono,monospace;'>Paused</p>" if paused else ""}
        </div>
        """, unsafe_allow_html=True)

        sms = int(st.session_state.start_time * 1000)
        ams = int(st.session_state.accumulated_time * 1000)
        pjs = "true" if paused else "false"
        op  = "0.2" if paused else "1"

        components.html(f"""<!DOCTYPE html><html><head>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300&display=swap');
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{background:#000;display:flex;justify-content:center;align-items:center;height:180px;overflow:hidden;}}
        .w{{display:flex;align-items:flex-end;gap:2px;opacity:{op};transition:opacity 0.5s;}}
        .seg{{display:flex;flex-direction:column;align-items:center;gap:7px;}}
        .n{{font-family:'DM Mono',monospace;font-size:90px;font-weight:300;color:#fff;
             letter-spacing:-6px;line-height:1;transition:opacity 0.08s;}}
        .l{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:3px;color:#1c1c1c;text-transform:uppercase;}}
        .c{{font-family:'DM Mono',monospace;font-size:64px;font-weight:300;color:#141414;margin-bottom:20px;line-height:1;}}
        </style></head><body>
        <div class="w">
            <div class="seg"><span class="n" id="h">00</span><span class="l">hr</span></div>
            <span class="c">:</span>
            <div class="seg"><span class="n" id="m">00</span><span class="l">min</span></div>
            <span class="c">:</span>
            <div class="seg"><span class="n" id="s">00</span><span class="l">sec</span></div>
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
            if(s!==prev){{el.style.opacity='0.3';setTimeout(function(){{el.style.opacity='1';}},70);prev=s;}}
            el.textContent=pad(s);
        }}
        tick();
        if(!paused) setInterval(tick,250);
        </script></body></html>""", height=195)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        c1, _, c3 = st.columns([1, 0.12, 1])
        with c1:
            if paused:
                if st.button("Resume"):
                    st.session_state.start_time     = time.time()
                    st.session_state.session_paused = False
                    st.rerun()
            else:
                if st.button("Pause"):
                    st.session_state.accumulated_time += time.time() - st.session_state.start_time
                    st.session_state.session_paused    = True
                    st.rerun()
        with c3:
            if st.button("Save & End"):
                if not paused:
                    st.session_state.accumulated_time += time.time() - st.session_state.start_time
                mins = round(st.session_state.accumulated_time / 60, 2)
                h    = datetime.now().hour
                tod  = "Morning" if h < 12 else "Afternoon" if h < 18 else "Evening/Night"
                supabase.table("study_logs").insert({
                    "Date":     datetime.now().strftime("%Y-%m-%d"),
                    "Subject":  st.session_state.current_subject,
                    "Task":     st.session_state.current_task,
                    "Duration": mins,
                    "Time":     tod,
                    "username": st.session_state.username
                }).execute()
                st.session_state.session_active   = False
                st.session_state.zen_mode         = False
                st.cache_data.clear()
                st.balloons()
                time.sleep(1.2)
                st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE 2 — DAILY TIMELINE
# ══════════════════════════════════════════════════════════════
elif page == "Daily Timeline":
    st.markdown("""
    <h1 style='font-size:2.5rem; font-weight:300; letter-spacing:-1.5px; color:#fff; margin-bottom:6px;'>Today</h1>
    <p style='color:#1e1e1e; font-size:0.6rem; letter-spacing:3px; text-transform:uppercase;
              font-family:DM Mono,monospace; margin-bottom:40px;'>SESSION LOG</p>
    """, unsafe_allow_html=True)

    today = pd.Timestamp.now().normalize()
    tdf   = db[db["Date"] == today].copy() if not db.empty else pd.DataFrame()

    if tdf.empty:
        st.markdown("""
        <div style='text-align:center; padding:100px 0;'>
            <p style='font-size:2.5rem; color:#111; margin-bottom:14px;'>○</p>
            <p style='font-size:0.6rem; letter-spacing:3px; color:#181818;
                      text-transform:uppercase; font-family:DM Mono,monospace;'>Nothing logged today</p>
        </div>""", unsafe_allow_html=True)
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Today",      f"{round(tdf['Duration'].sum()/60,1)}h")
        c2.metric("Sessions",   len(tdf))
        c3.metric("Top",        slabel(tdf.groupby('Subject')['Duration'].sum().idxmax()))
        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

        for _, row in tdf.sort_values('Duration', ascending=False).iterrows():
            dc      = sdot(row['Subject'])
            dur     = row['Duration']
            dur_str = f"{int(dur)}m" if dur < 60 else f"{dur/60:.1f}h"
            bw      = int(min(100, dur / (tdf['Duration'].max()+0.01) * 100))
            task_s  = str(row.get('Task',''))
            task_s  = "" if task_s in ['nan','None',''] else task_s
            st.markdown(f"""
            <div style='background:#040404; border:1px solid #0d0d0d; border-radius:12px;
                        padding:18px 22px; margin-bottom:8px; position:relative; overflow:hidden;'>
                <div style='position:absolute; bottom:0; left:0; height:1px;
                            width:{bw}%; background:{dc}; opacity:0.35;'></div>
                <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                    <div>
                        <div style='display:flex; align-items:center; gap:8px; margin-bottom:5px;'>
                            <div style='width:5px; height:5px; border-radius:50%; background:{dc};'></div>
                            <span style='font-size:0.8rem; color:#c0c0c0;'>{slabel(row["Subject"])}</span>
                        </div>
                        {"<p style='font-size:0.72rem; color:#282828; padding-left:13px;'>" + task_s + "</p>" if task_s else ""}
                    </div>
                    <div style='text-align:right;'>
                        <p style='font-size:1.25rem; font-weight:300; color:#fff;
                                  font-family:DM Mono,monospace; letter-spacing:-1px;'>{dur_str}</p>
                        <p style='font-size:0.58rem; color:#1e1e1e;'>{row["Time"]}</p>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 3 — DEEP ANALYTICS
# ══════════════════════════════════════════════════════════════
elif page == "Deep Analytics":
    st.markdown("""
    <h1 style='font-size:2.5rem; font-weight:300; letter-spacing:-1.5px; color:#fff; margin-bottom:6px;'>Analytics</h1>
    <p style='color:#1e1e1e; font-size:0.6rem; letter-spacing:3px; text-transform:uppercase;
              font-family:DM Mono,monospace; margin-bottom:32px;'>STUDY INTELLIGENCE</p>
    """, unsafe_allow_html=True)

    if db.empty:
        st.markdown("""
        <div style='text-align:center; padding:100px 0;'>
            <p style='font-size:2.5rem; color:#111; margin-bottom:14px;'>◌</p>
            <p style='font-size:0.6rem; letter-spacing:3px; color:#181818;
                      text-transform:uppercase; font-family:DM Mono,monospace;'>Start a session to see data</p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    tf  = st.selectbox("", ["Today","Yesterday","This Week","This Month","This Year","All Time"],
                       label_visibility="collapsed")
    now = pd.Timestamp.now().normalize()

    if   tf == "Today":      fdb = db[db['Date'] == now]
    elif tf == "Yesterday":  fdb = db[db['Date'] == now - pd.Timedelta(days=1)]
    elif tf == "This Week":
        fdb = db[(db['Date'].dt.isocalendar().week == now.isocalendar().week)
                 & (db['Date'].dt.year == now.year)]
    elif tf == "This Month": fdb = db[(db['Date'].dt.month==now.month)&(db['Date'].dt.year==now.year)]
    elif tf == "This Year":  fdb = db[db['Date'].dt.year == now.year]
    else:                    fdb = db.copy()

    if fdb.empty:
        st.markdown(f"<p style='color:#222; font-size:0.82rem; padding:40px 0;'>No data for {tf}.</p>",
                    unsafe_allow_html=True)
        st.stop()

    # Streak
    streak    = 0
    all_dates = set(db['Date'].dt.normalize().unique())
    d = now
    while d in all_dates:
        streak += 1
        d -= pd.Timedelta(days=1)

    total_hrs = round(fdb['Duration'].sum()/60, 1)
    top_s     = fdb.groupby('Subject')['Duration'].sum().idxmax()
    avg_m     = round(fdb['Duration'].mean(), 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Hours",       f"{total_hrs}h")
    c2.metric("Top subject", slabel(top_s))
    c3.metric("Avg session", f"{int(avg_m)}m")
    c4.metric("Streak",      f"{streak}d")

    st.markdown("<div style='height:44px'></div>", unsafe_allow_html=True)

    # ── Chart base layout (no **kwargs conflict) ──
    def base_layout(height=260):
        return dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='DM Mono, monospace', color='#1e1e1e', size=9),
            margin=dict(l=0, r=0, t=8, b=0),
            showlegend=False,
            height=height,
            xaxis=dict(
                showgrid=True, gridcolor='#080808', gridwidth=1,
                zeroline=False, showline=False,
                tickfont=dict(color='#252525', size=9),
            ),
            yaxis=dict(
                showgrid=False, zeroline=False, showline=False,
                tickfont=dict(color='#252525', size=9),
            ),
        )

    # ── ROW 1: Donut + Bar ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<p style='font-size:0.5rem; letter-spacing:3px; color:#181818; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:10px;'>MIX</p>", unsafe_allow_html=True)
        ss     = fdb.groupby('Subject')['Duration'].sum().reset_index()
        colors = [sdot(s) for s in ss['Subject']]

        fig_d  = go.Figure(go.Pie(
            labels=[slabel(s) for s in ss['Subject']],
            values=ss['Duration'],
            hole=0.74,
            marker=dict(colors=colors, line=dict(color='#000', width=4)),
            textinfo='none',
            hovertemplate='<b>%{label}</b><br>%{value:.0f} min<extra></extra>',
            sort=True,
        ))
        fig_d.add_annotation(
            text=f"{total_hrs}h", x=0.5, y=0.5, showarrow=False,
            font=dict(size=28, color='#ffffff', family='DM Mono, monospace')
        )
        layout_d = base_layout(240)
        # Pie doesn't use xaxis/yaxis — remove them
        layout_d.pop('xaxis', None)
        layout_d.pop('yaxis', None)
        fig_d.update_layout(**layout_d)
        st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})

        for _, r in ss.sort_values('Duration', ascending=False).iterrows():
            pct = round(r['Duration']/ss['Duration'].sum()*100, 1)
            dc  = sdot(r['Subject'])
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        padding:6px 0; border-bottom:1px solid #080808;'>
                <div style='display:flex; align-items:center; gap:9px;'>
                    <div style='width:5px; height:5px; border-radius:50%; background:{dc};'></div>
                    <span style='font-size:0.72rem; color:#333;'>{slabel(r["Subject"])}</span>
                </div>
                <span style='font-size:0.65rem; font-family:DM Mono,monospace; color:#252525;'>{pct}%</span>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("<p style='font-size:0.5rem; letter-spacing:3px; color:#181818; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:10px;'>HOURS BY SUBJECT</p>", unsafe_allow_html=True)
        sh       = ss.copy()
        sh['h']  = sh['Duration']/60
        sh['lb'] = sh['Subject'].apply(slabel)
        sh       = sh.sort_values('h', ascending=True)

        fig_b = go.Figure(go.Bar(
            x=sh['h'], y=sh['lb'], orientation='h',
            marker=dict(color=[sdot(s) for s in sh['Subject']], opacity=0.65, line=dict(width=0)),
            hovertemplate='<b>%{y}</b><br>%{x:.1f}h<extra></extra>',
        ))
        fig_b.update_layout(**base_layout(300))
        st.plotly_chart(fig_b, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── Area trend ──
    if tf not in ["Today","Yesterday"]:
        st.markdown("<p style='font-size:0.5rem; letter-spacing:3px; color:#181818; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:10px;'>DAILY HOURS</p>", unsafe_allow_html=True)
        daily    = fdb.groupby('Date')['Duration'].sum().reset_index()
        daily['h'] = daily['Duration']/60

        fig_a = go.Figure(go.Scatter(
            x=daily['Date'], y=daily['h'],
            mode='lines',
            line=dict(color='#ffffff', width=1.2),
            fill='tozeroy', fillcolor='rgba(255,255,255,0.025)',
            hovertemplate='%{x|%b %d}  <b>%{y:.1f}h</b><extra></extra>',
        ))
        fig_a.update_layout(**base_layout(170))
        st.plotly_chart(fig_a, use_container_width=True, config={'displayModeBar': False})
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Time of day + Recent log ──
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("<p style='font-size:0.5rem; letter-spacing:3px; color:#181818; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:10px;'>TIME OF DAY</p>", unsafe_allow_html=True)
        tod   = fdb.groupby('Time')['Duration'].sum().reset_index()
        order = ["Morning","Afternoon","Evening/Night"]
        tod['Time'] = pd.Categorical(tod['Time'], categories=order, ordered=True)
        tod   = tod.sort_values('Time')
        tcols = ['#fb923c','#c084fc','#5b8cff'][:len(tod)]

        fig_t = go.Figure(go.Bar(
            x=tod['Time'], y=tod['Duration']/60,
            marker=dict(color=tcols, opacity=0.6, line=dict(width=0)),
            hovertemplate='%{x}<br><b>%{y:.1f}h</b><extra></extra>',
        ))
        fig_t.update_layout(**base_layout(220))
        st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False})

    with col4:
        st.markdown("<p style='font-size:0.5rem; letter-spacing:3px; color:#181818; text-transform:uppercase; font-family:DM Mono,monospace; margin-bottom:10px;'>RECENT</p>", unsafe_allow_html=True)
        recent = fdb.sort_values('Date', ascending=False).head(10)
        for _, row in recent.iterrows():
            dc      = sdot(row['Subject'])
            dur     = row['Duration']
            dur_str = f"{int(dur)}m" if dur < 60 else f"{dur/60:.1f}h"
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center;
                        padding:7px 0; border-bottom:1px solid #080808;'>
                <div style='display:flex; align-items:center; gap:9px;'>
                    <div style='width:5px; height:5px; border-radius:50%; background:{dc};'></div>
                    <span style='font-size:0.72rem; color:#303030;'>{slabel(row["Subject"])}</span>
                </div>
                <div style='display:flex; align-items:center; gap:14px;'>
                    <span style='font-size:0.58rem; color:#181818; font-family:DM Mono,monospace;'>{row["Date"].strftime("%b %d")}</span>
                    <span style='font-size:0.8rem; font-weight:300; color:#aaa; font-family:DM Mono,monospace; letter-spacing:-0.5px;'>{dur_str}</span>
                </div>
            </div>""", unsafe_allow_html=True)
