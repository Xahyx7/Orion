import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import requests
import streamlit.components.v1 as components

# --- CONFIG & OLED THEME ---
st.set_page_config(page_title="NEON STUDY OS | JEE", page_icon="⚡", layout="wide")

# 👇 PASTE YOUR SHEETDB URL HERE 👇
SHEETDB_URL = "https://sheetdb.io/api/v1/9yl2rjjk03oto" 

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
        color: #ffffff;
    }
    div[data-testid="stMetricValue"] {
        background: #0a0a0a;
        border: 1px solid #333;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 0px 15px rgba(0, 242, 254, 0.1);
        color: #00f2fe !important;
    }
    input, textarea, .stSelectbox {
        background-color: #111 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        color: black !important;
        border-radius: 10px;
        font-weight: 800;
        letter-spacing: 2px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.6);
        transform: scale(1.02);
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'session_active' not in st.session_state:
    st.session_state.session_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = ""
if 'current_task' not in st.session_state:
    st.session_state.current_task = ""
if 'zen_mode' not in st.session_state:
    st.session_state.zen_mode = False

# --- FETCH DATA ---
@st.cache_data(ttl=60)
def load_data():
    try:
        response = requests.get(SHEETDB_URL)
        data = response.json()
        if data and "error" not in data:
            df = pd.DataFrame(data)
            df['Duration'] = pd.to_numeric(df['Duration']) 
            return df
        return pd.DataFrame(columns=["Date", "Subject", "Task", "Duration", "Time"])
    except:
        return pd.DataFrame(columns=["Date", "Subject", "Task", "Duration", "Time"])

db = load_data()

# --- ZEN MODE UI OVERRIDE ---
if st.session_state.session_active and st.session_state.zen_mode:
    st.markdown("""
        <style>
        /* Hides Sidebar and Top Header for true Full Screen */
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 2rem !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.sidebar.title("⚡ SYSTEM MENU")
    page = st.sidebar.radio("Navigation", ["Live Session", "Daily Timeline", "Deep Analytics"])

# ==========================================
# PAGE 1: LIVE SESSION
# ==========================================
if 'page' not in locals() or page == "Live Session" or (st.session_state.session_active and st.session_state.zen_mode):
    
    if not st.session_state.session_active:
        st.markdown("<h1 style='text-align: center; color: #00f2fe;'>START DEEP WORK</h1>", unsafe_allow_html=True)
        
        subject = st.selectbox("Select Subject", [
            "Physical Chemistry", 
            "Organic Chemistry", 
            "Inorganic Chemistry", 
            "Physics", 
            "Mathematics", 
            "Mock Test / Revision"
        ])
        
        task_notes = st.text_input("Session Goal", placeholder="e.g., Solving HC Verma Chapter 8")
        
        # Zen Mode Toggle
        zen_toggle = st.toggle("🌌 Enable Zen Mode (Hides all menus during session)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("START STOPWATCH"):
            st.session_state.zen_mode = zen_toggle
            st.session_state.session_active = True
            st.session_state.start_time = time.time()
            st.session_state.current_subject = subject
            st.session_state.current_task = task_notes
            st.rerun()

    else:
        st.markdown(f"<h3 style='text-align: center; color: #aaaaaa;'>Focusing on: {st.session_state.current_subject}</h3>", unsafe_allow_html=True)
        
        # --- CUSTOM FLIP CLOCK UI ---
        start_time_ms = int(st.session_state.start_time * 1000)
        flip_clock_html = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Inter:wght@400;700&display=swap');
        body {{ background-color: #000; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }}
        .flip-container {{ display: flex; gap: 20px; }}
        .flip-box {{
            background: #0f0f0f;
            border: 2px solid #222;
            border-radius: 12px;
            padding: 20px 30px;
            position: relative;
            box-shadow: 0 10px 30px rgba(0, 242, 254, 0.1);
            min-width: 150px;
            text-align: center;
        }}
        /* The horizontal split line to simulate flip cards */
        .flip-box::after {{
            content: '';
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 3px;
            background: #000;
            transform: translateY(-50%);
            box-shadow: 0 2px 5px rgba(0,0,0,0.8);
        }}
        .flip-number {{
            font-family: 'Oswald', sans-serif;
            font-size: 120px;
            font-weight: 700;
            color: #00f2fe;
            line-height: 1;
            margin: 0;
            text-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        }}
        .flip-label {{
            margin-top: 15px;
            font-family: 'Inter', sans-serif;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 3px;
            font-size: 14px;
            font-weight: bold;
        }}
        </style>
        
        <div style="width: 100%; display: flex; justify-content: center; margin-top: 40px;">
            <div class="flip-container">
                <div class="flip-box"><div class="flip-number" id="h">00</div><div class="flip-label">HOURS</div></div>
                <div class="flip-box"><div class="flip-number" id="m">00</div><div class="flip-label">MINUTES</div></div>
                <div class="flip-box"><div class="flip-number" id="s">00</div><div class="flip-label">SECONDS</div></div>
            </div>
        </div>

        <script>
            var startTime = {start_time_ms};
            setInterval(function() {{
                var now = new Date().getTime();
                var distance = now - startTime;
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
                document.getElementById("h").innerText = (hours < 10) ? "0" + hours : hours;
                document.getElementById("m").innerText = (minutes < 10) ? "0" + minutes : minutes;
                document.getElementById("s").innerText = (seconds < 10) ? "0" + seconds : seconds;
            }}, 1000);
        </script>
        """
        components.html(flip_clock_html, height=350)
        
        st.write("---")
        
        if st.button("⏹️ END SESSION & LOG DATA"):
            end_time = time.time()
            elapsed_seconds = end_time - st.session_state.start_time
            duration_minutes = round(elapsed_seconds / 60, 2)
            
            hour = datetime.now().hour
            time_of_day = "Morning" if hour < 12 else "Afternoon" if hour < 18 else "Evening/Night"
            
            new_data = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Subject": st.session_state.current_subject,
                "Task": st.session_state.current_task,
                "Duration": duration_minutes,
                "Time": time_of_day
            }
            requests.post(SHEETDB_URL, json={"data": new_data})
            
            st.session_state.session_active = False
            st.session_state.start_time = 0
            st.session_state.current_subject = ""
            st.session_state.current_task = ""
            st.session_state.zen_mode = False
            
            st.cache_data.clear()
            st.success(f"Boom. {duration_minutes} minutes logged to your database.")
            st.balloons()
            time.sleep(2)
            st.rerun()

# ==========================================
# PAGE 2: DAILY TIMELINE
# ==========================================
elif page == "Daily Timeline" and not (st.session_state.session_active and st.session_state.zen_mode):
    st.title("📅 Today's Log")
    today = datetime.now().strftime("%Y-%m-%d")
    todays_data = db[db["Date"] == today]
    
    if todays_data.empty:
        st.info("No sessions logged today yet. Go to 'Live Session' to start.")
    else:
        st.dataframe(todays_data, use_container_width=True)
        total_mins = todays_data["Duration"].sum()
        st.metric("Total Time Today", f"{round(total_mins/60, 1)} Hours")

# ==========================================
# PAGE 3: DEEP ANALYTICS
# ==========================================
elif page == "Deep Analytics" and not (st.session_state.session_active and st.session_state.zen_mode):
    st.title("📊 The Command Center")
    
    if db.empty:
        st.warning("Complete a session to generate analytics.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("All-Time Hours", f"{round(db['Duration'].sum() / 60, 1)}")
        col2.metric("Top Subject", db['Subject'].mode()[0] if not db.empty else "N/A")
        col3.metric("Most Productive Time", db['Time'].mode()[0] if not db.empty else "N/A")

        st.divider()
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Subject Distribution")
            fig1 = px.pie(db, values='Duration', names='Subject', hole=0.7, 
                          color_discrete_sequence=px.colors.sequential.Teal)
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            st.subheader("Time of Day Focus")
            fig2 = px.bar(db.groupby('Time').sum(numeric_only=True).reset_index(), 
                          x='Time', y='Duration', 
                          color='Time', color_discrete_sequence=px.colors.sequential.Teal)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig2, use_container_width=True)
