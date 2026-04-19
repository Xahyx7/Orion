import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
import streamlit.components.v1 as components
import io

# --- CONFIG & OLED THEME ---
st.set_page_config(page_title="NEON STUDY OS | JEE", page_icon="⚡", layout="wide")

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

# --- LOCAL SESSION DATABASE ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Date", "Subject", "Task", "Duration", "Time"])

# --- SESSION STATE (Live Timer) ---
if 'session_active' not in st.session_state: st.session_state.session_active = False
if 'session_paused' not in st.session_state: st.session_state.session_paused = False
if 'start_time' not in st.session_state: st.session_state.start_time = 0.0
if 'accumulated_time' not in st.session_state: st.session_state.accumulated_time = 0.0
if 'current_subject' not in st.session_state: st.session_state.current_subject = ""
if 'current_task' not in st.session_state: st.session_state.current_task = ""
if 'zen_mode' not in st.session_state: st.session_state.zen_mode = False

# --- ZEN MODE UI OVERRIDE ---
if st.session_state.session_active and st.session_state.zen_mode:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 2rem !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.sidebar.title("⚡ SYSTEM MENU")
    page = st.sidebar.radio("Navigation", ["Live Session", "Daily Timeline", "Deep Analytics"])
    
    st.sidebar.divider()
    
    # --- IMPORT / EXPORT VAULT ---
    st.sidebar.title("💾 DATA VAULT")
    st.sidebar.caption("Backup your data to a CSV file to sync across devices.")
    
    # EXPORT
    if not st.session_state.db.empty:
        csv = st.session_state.db.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="⬇️ Export Backup (CSV)",
            data=csv,
            file_name=f"JEE_Study_Backup_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
        )
    else:
        st.sidebar.button("⬇️ Export Backup (CSV)", disabled=True, help="No data to export yet.")
        
    # IMPORT
    uploaded_file = st.sidebar.file_uploader("⬆️ Import Backup", type=["csv"])
    if uploaded_file is not None:
        try:
            imported_df = pd.read_csv(uploaded_file)
            # Ensure proper columns exist
            expected_cols = ["Date", "Subject", "Task", "Duration", "Time"]
            if all(col in imported_df.columns for col in expected_cols):
                imported_df['Date'] = pd.to_datetime(imported_df['Date'])
                st.session_state.db = imported_df
                st.sidebar.success("✅ Database Restored!")
                time.sleep(1)
                st.rerun()
            else:
                st.sidebar.error("Invalid CSV format. Columns must match exactly.")
        except Exception as e:
            st.sidebar.error("Error reading file.")

# ==========================================
# PAGE 1: LIVE SESSION
# ==========================================
if 'page' not in locals() or page == "Live Session" or (st.session_state.session_active and st.session_state.zen_mode):
    
    if not st.session_state.session_active:
        st.markdown("<h1 style='text-align: center; color: #00f2fe;'>START DEEP WORK</h1>", unsafe_allow_html=True)
        
        subject = st.selectbox("Select Subject", [
            "Physical Chemistry", "Organic Chemistry", "Inorganic Chemistry", 
            "Physics", "Mathematics", "Mock Test / Revision"
        ])
        
        task_notes = st.text_input("Session Goal", placeholder="e.g., Solving HC Verma Chapter 8")
        zen_toggle = st.toggle("🌌 Enable Zen Mode (Hides all menus during session)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶️ START STOPWATCH"):
            st.session_state.zen_mode = zen_toggle
            st.session_state.session_active = True
            st.session_state.session_paused = False
            st.session_state.start_time = time.time()
            st.session_state.accumulated_time = 0.0
            st.session_state.current_subject = subject
            st.session_state.current_task = task_notes
            st.rerun()

    else:
        st.markdown(f"<h3 style='text-align: center; color: #aaaaaa;'>Focusing on: {st.session_state.current_subject}</h3>", unsafe_allow_html=True)
        
        if st.session_state.session_paused:
            st.markdown("<h4 style='text-align: center; color: #ffae00; letter-spacing: 5px;'>⏸ PAUSED</h4>", unsafe_allow_html=True)
        
        # --- SMART FLIP CLOCK UI ---
        start_time_ms = int(st.session_state.start_time * 1000)
        accumulated_ms = int(st.session_state.accumulated_time * 1000)
        is_paused_js = "true" if st.session_state.session_paused else "false"
        
        flip_clock_html = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Inter:wght@400;700&display=swap');
        body {{ background-color: #000; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }}
        .flip-container {{ display: flex; gap: 20px; opacity: {"0.5" if st.session_state.session_paused else "1.0"}; transition: 0.3s; }}
        .flip-box {{ background: #0f0f0f; border: 2px solid #222; border-radius: 12px; padding: 20px 30px; position: relative; box-shadow: 0 10px 30px rgba(0, 242, 254, 0.1); min-width: 150px; text-align: center; }}
        .flip-box::after {{ content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 3px; background: #000; transform: translateY(-50%); box-shadow: 0 2px 5px rgba(0,0,0,0.8); }}
        .flip-number {{ font-family: 'Oswald', sans-serif; font-size: 120px; font-weight: 700; color: #00f2fe; line-height: 1; margin: 0; text-shadow: 0 0 15px rgba(0, 242, 254, 0.4); }}
        .flip-label {{ margin-top: 15px; font-family: 'Inter', sans-serif; color: #555; text-transform: uppercase; letter-spacing: 3px; font-size: 14px; font-weight: bold; }}
        </style>
        <div style="width: 100%; display: flex; justify-content: center; margin-top: 10px;">
            <div class="flip-container">
                <div class="flip-box"><div class="flip-number" id="h">00</div><div class="flip-label">HOURS</div></div>
                <div class="flip-box"><div class="flip-number" id="m">00</div><div class="flip-label">MINUTES</div></div>
                <div class="flip-box"><div class="flip-number" id="s">00</div><div class="flip-label">SECONDS</div></div>
            </div>
        </div>
        <script>
            var startTime = {start_time_ms};
            var accumulatedMs = {accumulated_ms};
            var isPaused = {is_paused_js};
            
            function updateDisplay(distance) {{
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                document.getElementById("h").innerText = (hours < 10) ? "0" + hours : hours;
                document.getElementById("m").innerText = (minutes < 10) ? "0" + minutes : minutes;
                document.getElementById("s").innerText = (seconds < 10) ? "0" + seconds : seconds;
            }}

            if (isPaused) {{
                updateDisplay(accumulatedMs);
            }} else {{
                setInterval(function() {{
                    var now = new Date().getTime();
                    var distance = accumulatedMs + (now - startTime);
                    updateDisplay(distance);
                }}, 1000);
            }}
        </script>
        """
        components.html(flip_clock_html, height=350)
        
        st.write("---")
        
        # --- PAUSE & STOP BUTTONS ---
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.session_state.session_paused:
                if st.button("▶️ RESUME SESSION"):
                    st.session_state.start_time = time.time()
                    st.session_state.session_paused = False
                    st.rerun()
            else:
                if st.button("⏸️ PAUSE SESSION"):
                    st.session_state.accumulated_time += (time.time() - st.session_state.start_time)
                    st.session_state.session_paused = True
                    st.rerun()
                    
        with col_btn2:
            if st.button("⏹️ END & LOG DATA"):
                if not st.session_state.session_paused:
                    st.session_state.accumulated_time += (time.time() - st.session_state.start_time)
                
                duration_minutes = round(st.session_state.accumulated_time / 60, 2)
                hour = datetime.now().hour
                time_of_day = "Morning" if hour < 12 else "Afternoon" if hour < 18 else "Evening/Night"
                
                # Append to Local DataFrame
                new_row = pd.DataFrame([{
                    "Date": pd.to_datetime(datetime.now().strftime("%Y-%m-%d")),
                    "Subject": st.session_state.current_subject,
                    "Task": st.session_state.current_task,
                    "Duration": duration_minutes,
                    "Time": time_of_day
                }])
                
                st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                
                # Reset System
                st.session_state.session_active = False
                st.session_state.session_paused = False
                st.session_state.start_time = 0.0
                st.session_state.accumulated_time = 0.0
                st.session_state.current_subject = ""
                st.session_state.current_task = ""
                st.session_state.zen_mode = False
                
                st.success(f"Boom. {duration_minutes} minutes logged locally! Remember to Export Backup later.")
                st.balloons()
                time.sleep(2)
                st.rerun()

# ==========================================
# PAGE 2: DAILY TIMELINE
# ==========================================
elif page == "Daily Timeline" and not (st.session_state.session_active and st.session_state.zen_mode):
    st.title("📅 Today's Log")
    db = st.session_state.db
    today = pd.Timestamp.now().normalize()
    
    if not db.empty:
        todays_data = db[db["Date"] == today]
    else:
        todays_data = pd.DataFrame()
    
    if todays_data.empty:
        st.info("No sessions logged today yet. Go to 'Live Session' to start.")
    else:
        display_df = todays_data.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True)
        total_mins = todays_data["Duration"].sum()
        st.metric("Total Time Today", f"{round(total_mins/60, 1)} Hours")

# ==========================================
# PAGE 3: DEEP ANALYTICS
# ==========================================
elif page == "Deep Analytics" and not (st.session_state.session_active and st.session_state.zen_mode):
    st.title("📊 The Command Center")
    db = st.session_state.db
    
    if db.empty:
        st.warning("No data found. Upload a backup or complete a session to generate analytics.")
    else:
        st.markdown("### ⏱️ Select Timeframe")
        timeframe = st.selectbox("Analyze your performance for:", ["Today", "Yesterday", "This Week", "This Month", "This Year"])
        
        today = pd.Timestamp.now().normalize()
        
        if timeframe == "Today":
            filtered_db = db[db['Date'] == today]
        elif timeframe == "Yesterday":
            yesterday = today - pd.Timedelta(days=1)
            filtered_db = db[db['Date'] == yesterday]
        elif timeframe == "This Week":
            filtered_db = db[db['Date'].dt.isocalendar().week == today.isocalendar().week]
            filtered_db = filtered_db[filtered_db['Date'].dt.year == today.year]
        elif timeframe == "This Month":
            filtered_db = db[(db['Date'].dt.month == today.month) & (db['Date'].dt.year == today.year)]
        elif timeframe == "This Year":
            filtered_db = db[db['Date'].dt.year == today.year]

        if filtered_db.empty:
            st.info(f"No study data found for {timeframe}.")
        else:
            total_hours = round(filtered_db['Duration'].sum() / 60, 1)
            top_subject = filtered_db['Subject'].mode()[0]
            best_time = filtered_db['Time'].mode()[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric(f"Total Hours ({timeframe})", f"{total_hours} hrs")
            col2.metric("Top Subject", top_subject)
            col3.metric("Productive Zone", best_time)

            st.divider()
            
            if timeframe in ["Today", "Yesterday"]:
                st.subheader("Subject Distribution")
                fig1 = px.pie(filtered_db, values='Duration', names='Subject', hole=0.7, 
                              color_discrete_sequence=px.colors.sequential.Teal)
                fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig1, use_container_width=True)

            elif timeframe in ["This Week", "This Month"]:
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.subheader("Daily Burn Rate")
                    daily_summary = filtered_db.groupby('Date')['Duration'].sum().reset_index()
                    daily_summary['Duration (Hours)'] = daily_summary['Duration'] / 60
                    fig_days = px.bar(daily_summary, x='Date', y='Duration (Hours)', color_discrete_sequence=['#00f2fe'])
                    fig_days.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig_days, use_container_width=True)
                with col_chart2:
                    st.subheader("Subject Distribution")
                    fig_pie = px.pie(filtered_db, values='Duration', names='Subject', hole=0.7, color_discrete_sequence=px.colors.sequential.Teal)
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig_pie, use_container_width=True)

            elif timeframe == "This Year":
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.subheader("Weekly Burn Rate")
                    yearly_summary = filtered_db.copy()
                    yearly_summary['Week'] = yearly_summary['Date'].dt.isocalendar().week
                    weekly_grouped = yearly_summary.groupby('Week')['Duration'].sum().reset_index()
                    weekly_grouped['Duration (Hours)'] = weekly_grouped['Duration'] / 60
                    fig_weeks = px.bar(weekly_grouped, x='Week', y='Duration (Hours)', title="Total Hours per Week", color_discrete_sequence=['#00f2fe'])
                    fig_weeks.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Week Number")
                    st.plotly_chart(fig_weeks, use_container_width=True)
                with col_chart2:
                    st.subheader("Yearly Subject Focus")
                    fig_pie_yr = px.pie(filtered_db, values='Duration', names='Subject', hole=0.7, color_discrete_sequence=px.colors.sequential.Teal)
                    fig_pie_yr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig_pie_yr, use_container_width=True)
