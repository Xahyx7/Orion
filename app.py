import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import requests

# --- CONFIG & OLED THEME ---
st.set_page_config(page_title="NEON STUDY OS", page_icon="⚡", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

# --- FETCH DATA FROM GOOGLE SHEETS ---
@st.cache_data(ttl=60) # Refreshes data every 60 seconds
def load_data():
    try:
        response = requests.get(SHEETDB_URL)
        data = response.json()
        if data and "error" not in data:
            df = pd.DataFrame(data)
            df['Duration'] = pd.to_numeric(df['Duration']) # Ensure duration is a number
            return df
        return pd.DataFrame(columns=["Date", "Subject", "Task", "Duration", "Time"])
    except:
        return pd.DataFrame(columns=["Date", "Subject", "Task", "Duration", "Time"])

db = load_data()

st.sidebar.title("⚡ SYSTEM MENU")
page = st.sidebar.radio("Navigation", ["Live Session", "Daily Timeline", "Deep Analytics"])

# ==========================================
# PAGE 1: LIVE SESSION
# ==========================================
if page == "Live Session":
    st.markdown("<h1 style='text-align: center; color: #00f2fe;'>START DEEP WORK</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("Select Subject", ["Computer Science", "Mathematics", "Physics", "Design", "Reading", "Other"])
    with col2:
        duration = st.slider("Target Duration (Minutes)", 15, 180, 60)
        
    task_notes = st.text_input("What is the exact goal for this session?", placeholder="e.g., Finish Chapter 4 practice problems")
    
    if st.button("INITIATE SESSION"):
        hour = datetime.now().hour
        time_of_day = "Morning" if hour < 12 else "Afternoon" if hour < 18 else "Evening/Night"
        
        timer_placeholder = st.empty()
        for i in range(duration * 60, 0, -1):
            mins, secs = divmod(i, 60)
            timer_placeholder.markdown(f"<h1 style='font-size: 120px; text-align: center; color: #4facfe; text-shadow: 0 0 20px #4facfe;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
            time.sleep(1) 
            
        st.success("SESSION COMPLETE. DATA LOGGED.")
        st.balloons()
        
        # SEND DATA TO GOOGLE SHEETS
        new_data = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Subject": subject,
            "Task": task_notes,
            "Duration": duration,
            "Time": time_of_day
        }
        requests.post(SHEETDB_URL, json={"data": new_data})
        st.cache_data.clear() # Clear cache to show new data immediately

# ==========================================
# PAGE 2: DAILY TIMELINE
# ==========================================
elif page == "Daily Timeline":
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
elif page == "Deep Analytics":
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
