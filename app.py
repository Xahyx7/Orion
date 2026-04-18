import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# --- CONFIG & OLED THEME ---
st.set_page_config(page_title="NEON STUDY OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* OLED True Black Background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
        color: #ffffff;
    }
    
    /* Neon Glassmorphism Cards */
    div[data-testid="stMetricValue"] {
        background: #0a0a0a;
        border: 1px solid #333;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 0px 15px rgba(0, 242, 254, 0.1);
        color: #00f2fe !important;
    }
    
    /* Sleek Inputs */
    input, textarea, .stSelectbox {
        background-color: #111 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* Neon Button */
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

# --- FAKE DATABASE (Until you link Google Sheets) ---
# This ensures the app works immediately so you can test the UI
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Date", "Subject", "Task", "Duration (Mins)", "Time of Day"])

st.sidebar.title("⚡ SYSTEM MENU")
page = st.sidebar.radio("Navigation", ["Live Session", "Daily Timeline", "Deep Analytics"])

# ==========================================
# PAGE 1: LIVE SESSION (THE HUD)
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
        # Determine Time of Day
        hour = datetime.now().hour
        time_of_day = "Morning" if hour < 12 else "Afternoon" if hour < 18 else "Evening/Night"
        
        # Simulated Timer
        timer_placeholder = st.empty()
        for i in range(duration * 60, 0, -1):
            mins, secs = divmod(i, 60)
            timer_placeholder.markdown(f"<h1 style='font-size: 120px; text-align: center; color: #4facfe; text-shadow: 0 0 20px #4facfe;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
            time.sleep(1) # In real life, you wouldn't sit here, but this is for the effect!
            
        st.success("SESSION COMPLETE. DATA LOGGED.")
        st.balloons()
        
        # Save to our "Database"
        new_data = pd.DataFrame([{
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Subject": subject,
            "Task": task_notes,
            "Duration (Mins)": duration,
            "Time of Day": time_of_day
        }])
        st.session_state.db = pd.concat([st.session_state.db, new_data], ignore_index=True)

# ==========================================
# PAGE 2: DAILY TIMELINE
# ==========================================
elif page == "Daily Timeline":
    st.title("📅 Today's Log")
    today = datetime.now().strftime("%Y-%m-%d")
    todays_data = st.session_state.db[st.session_state.db["Date"] == today]
    
    if todays_data.empty:
        st.info("No sessions logged today yet. Go to 'Live Session' to start.")
    else:
        st.dataframe(todays_data, use_container_width=True)
        
        # Quick stat
        total_mins = todays_data["Duration (Mins)"].sum()
        st.metric("Total Time Today", f"{round(total_mins/60, 1)} Hours")

# ==========================================
# PAGE 3: DEEP ANALYTICS (COMMAND CENTER)
# ==========================================
elif page == "Deep Analytics":
    st.title("📊 The Command Center")
    
    if st.session_state.db.empty:
        st.warning("Complete a session to generate analytics.")
    else:
        # Mock Data Injection (So you can see the beautiful charts immediately)
        mock_data = pd.DataFrame([
            {"Date": "2023-10-01", "Subject": "Computer Science", "Duration (Mins)": 120, "Time of Day": "Morning"},
            {"Date": "2023-10-02", "Subject": "Mathematics", "Duration (Mins)": 90, "Time of Day": "Afternoon"},
            {"Date": "2023-10-03", "Subject": "Design", "Duration (Mins)": 60, "Time of Day": "Evening/Night"},
            {"Date": "2023-10-04", "Subject": "Computer Science", "Duration (Mins)": 150, "Time of Day": "Morning"},
        ])
        df = pd.concat([mock_data, st.session_state.db], ignore_index=True)

        # Top Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("All-Time Hours", f"{round(df['Duration (Mins)'].sum() / 60, 1)}")
        col2.metric("Top Subject", df['Subject'].mode()[0])
        col3.metric("Most Productive Time", df['Time of Day'].mode()[0])

        st.divider()

        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Subject Distribution")
            fig1 = px.pie(df, values='Duration (Mins)', names='Subject', hole=0.7, 
                          color_discrete_sequence=px.colors.sequential.Teal)
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            st.subheader("Time of Day Focus")
            fig2 = px.bar(df.groupby('Time of Day').sum().reset_index(), 
                          x='Time of Day', y='Duration (Mins)', 
                          color='Time of Day', color_discrete_sequence=px.colors.sequential.Teal)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig2, use_container_width=True)
