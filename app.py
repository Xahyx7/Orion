import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import streamlit.components.v1 as components
from supabase import create_client, Client

# --- CONFIG & OLED THEME ---
st.set_page_config(page_title="NEON STUDY OS | JEE", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #000000 !important; color: #ffffff; }
    div[data-testid="stMetricValue"] { background: #0a0a0a; border: 1px solid #333; border-radius: 15px; padding: 20px; box-shadow: 0px 0px 15px rgba(0, 242, 254, 0.1); color: #00f2fe !important; }
    input, textarea, .stSelectbox { background-color: #111 !important; color: white !important; border-radius: 10px !important; }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); color: black !important; border-radius: 10px; font-weight: 800; letter-spacing: 2px; transition: 0.3s; }
    .stButton>button:hover { box-shadow: 0 0 20px rgba(0, 242, 254, 0.6); transform: scale(1.02); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- INIT SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- LOGIN SYSTEM ---
if 'username' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #00f2fe; margin-top: 50px;'>NEON OS LOGIN</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='max-width: 400px; margin: 0 auto;'>", unsafe_allow_html=True)
        user_input = st.text_input("Enter Username:", placeholder="e.g. Rahul_JEE")
        if st.button("AUTHENTICATE"):
            if user_input:
                # IMPORTANT: .lower() was removed here so it matches your CSV exactly
                st.session_state.username = user_input.strip()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- FETCH DATA (FILTERED BY USER) ---
@st.cache_data(ttl=5)
def load_data(user):
    try:
        response = supabase.table("study_logs").select("*").eq("username", user).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=["Date", "Subject", "Task", "Duration", "Time", "username"])

db = load_data(st.session_state.username)

# --- SESSION STATE (Live Timer) ---
if 'session_active' not in st.session_state: st.session_state.session_active = False
if 'session_paused' not in st.session_state: st.session_state.session_paused = False
if 'start_time' not in st.session_state: st.session_state.start_time = 0.0
if 'accumulated_time' not in st.session_state: st.session_state.accumulated_time = 0.0
if 'current_subject' not in st.session_state: st.session_state.current_subject = ""
if 'current_task' not in st.session_state: st.session_state.current_task = ""
if 'zen_mode' not in st.session_state: st.session_state.zen_mode = False

# --- ZEN MODE OVERRIDE ---
if st.session_state.session_active and st.session_state.zen_mode:
    st.markdown("<style>[data-testid='stSidebar'], [data-testid='collapsedControl'], header { display: none !important; }</style>", unsafe_allow_html=True)
else:
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("Logout"):
        del st.session_state.username
        st.rerun()
    st.sidebar.divider()
    page = st.sidebar.radio("Navigation", ["Live Session", "Daily Timeline", "Deep Analytics"])

# ==========================================
# PAGE 1: LIVE SESSION (STOPWATCH + FLIP CLOCK)
# ==========================================
if 'page' not in locals() or page == "Live Session" or (st.session_state.session_active and st.session_state.zen_mode):
    if not st.session_state.session_active:
        st.markdown("<h1 style='text-align: center; color: #00f2fe;'>START DEEP WORK</h1>", unsafe_allow_html=True)
        subject = st.selectbox("Select Subject", ["Physical Chemistry", "Organic Chemistry", "Inorganic Chemistry", "Physics", "Mathematics", "Mock Test / Revision"])
        task_notes = st.text_input("Session Goal", placeholder="e.g., Solving HC Verma Chapter 8")
        zen_toggle = st.toggle("🌌 Enable Zen Mode (Distraction-Free)")
        if st.button("▶️ START STOPWATCH"):
            st.session_state.zen_mode = zen_toggle
            st.session_state.session_active = True
            st.session_state.start_time = time.time()
            st.session_state.accumulated_time = 0.0
            st.session_state.current_subject = subject
            st.session_state.current_task = task_notes
            st.rerun()
    else:
        st.markdown(f"<h3 style='text-align: center; color: #aaaaaa;'>Focusing on: {st.session_state.current_subject}</h3>", unsafe_allow_html=True)
        if st.session_state.session_paused: st.markdown("<h4 style='text-align: center; color: #ffae00; letter-spacing: 5px;'>⏸ PAUSED</h4>", unsafe_allow_html=True)
        
        start_time_ms = int(st.session_state.start_time * 1000)
        accumulated_ms = int(st.session_state.accumulated_time * 1000)
        is_paused_js = "true" if st.session_state.session_paused else "false"
        
        flip_clock_html = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap');
        body {{ background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
        .flip-container {{ display: flex; gap: 15px; opacity: {"0.5" if st.session_state.session_paused else "1.0"}; transition: 0.3s; }}
        .flip-box {{ background: #0f0f0f; border: 2px solid #222; border-radius: 12px; padding: 20px; min-width: 130px; text-align: center; position: relative; box-shadow: 0 10px 30px rgba(0, 242, 254, 0.1); }}
        .flip-box::after {{ content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: #000; }}
        .flip-num {{ font-family: 'Oswald', sans-serif; font-size: 100px; color: #00f2fe; margin: 0; text-shadow: 0 0 15px rgba(0, 242, 254, 0.4); }}
        .flip-label {{ font-family: sans-serif; color: #555; font-size: 12px; letter-spacing: 2px; margin-top: 10px; font-weight: bold; }}
        </style>
        <div class="flip-container">
            <div class="flip-box"><div class="flip-num" id="h">00</div><div class="flip-label">HOURS</div></div>
            <div class="flip-box"><div class="flip-num" id="m">00</div><div class="flip-label">MINS</div></div>
            <div class="flip-box"><div class="flip-num" id="s">00</div><div class="flip-label">SECS</div></div>
        </div>
        <script>
            var startTime = {start_time_ms}; var acc = {accumulated_ms}; var isPaused = {is_paused_js};
            function up(d) {{
                var h = Math.floor(d/3600000); var m = Math.floor((d%3600000)/60000); var s = Math.floor((d%60000)/1000);
                document.getElementById("h").innerText = h.toString().padStart(2, '0');
                document.getElementById("m").innerText = m.toString().padStart(2, '0');
                document.getElementById("s").innerText = s.toString().padStart(2, '0');
            }}
            if(isPaused) {{ up(acc); }} else {{ setInterval(function(){{ up(acc + (new Date().getTime() - startTime)); }}, 1000); }}
        </script>
        """
        components.html(flip_clock_html, height=280)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.session_state.session_paused:
                if st.button("▶️ RESUME"):
                    st.session_state.start_time = time.time()
                    st.session_state.session_paused = False
                    st.rerun()
            else:
                if st.button("⏸️ PAUSE"):
                    st.session_state.accumulated_time += (time.time() - st.session_state.start_time)
                    st.session_state.session_paused = True
                    st.rerun()
        with c2:
            if st.button("⏹️ END & SAVE"):
                if not st.session_state.session_paused: st.session_state.accumulated_time += (time.time() - st.session_state.start_time)
                duration_mins = round(st.session_state.accumulated_time / 60, 2)
                h = datetime.now().hour
                time_of_day = "Morning" if h < 12 else "Afternoon" if h < 18 else "Evening/Night"
                new_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Subject": st.session_state.current_subject, "Task": st.session_state.current_task, "Duration": duration_mins, "Time": time_of_day, "username": st.session_state.username}
                supabase.table("study_logs").insert(new_row).execute()
                st.session_state.session_active = False
                st.cache_data.clear()
                st.balloons()
                time.sleep(2)
                st.rerun()

# ==========================================
# PAGE 2: TIMELINE
# ==========================================
elif page == "Daily Timeline":
    st.title("📅 Today's Log")
    today = pd.Timestamp.now().normalize()
    todays_data = db[db["Date"] == today] if not db.empty else pd.DataFrame()
    
    if todays_data.empty: st.info("No study sessions logged today yet.")
    else:
        st.dataframe(todays_data[['Subject', 'Task', 'Duration', 'Time']], use_container_width=True)
        st.metric("Total Hours Today", f"{round(todays_data['Duration'].sum()/60, 1)}")

# ==========================================
# PAGE 3: ANALYTICS
# ==========================================
elif page == "Deep Analytics":
    st.title("📊 Analysis Dashboard")
    if db.empty: st.warning("No data recorded yet. Hit the stopwatch!")
    else:
        tf = st.selectbox("⏱️ Select Timeframe:", ["Today", "Yesterday", "This Week", "This Month", "This Year"])
        now = pd.Timestamp.now().normalize()
        
        if tf == "Today": fdb = db[db['Date'] == now]
        elif tf == "Yesterday": fdb = db[db['Date'] == (now - pd.Timedelta(days=1))]
        elif tf == "This Week": fdb = db[(db['Date'].dt.isocalendar().week == now.isocalendar().week) & (db['Date'].dt.year == now.year)]
        elif tf == "This Month": fdb = db[(db['Date'].dt.month == now.month) & (db['Date'].dt.year == now.year)]
        else: fdb = db[db['Date'].dt.year == now.year]

        if fdb.empty: st.info(f"No data for {tf}.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric(f"Total Hours ({tf})", f"{round(fdb['Duration'].sum()/60, 1)}")
            col2.metric("Top Subject", fdb['Subject'].mode()[0])
            col3.metric("Peak Time", fdb['Time'].mode()[0])
            st.divider()
            
            fig = px.pie(fdb, values='Duration', names='Subject', hole=0.6, color_discrete_sequence=px.colors.sequential.Teal)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
