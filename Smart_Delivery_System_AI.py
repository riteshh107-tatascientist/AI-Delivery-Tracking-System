import streamlit as st
import pandas as pd
import sqlite3
import requests
import time
import random
import os
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# ---------------- 0. SECURITY LAYER ----------------
# Ye line tumhari .env file se keys load karegi
load_dotenv()

def get_secret(key):
    try:
        # Pehle check karo agar streamlit secrets exist karte hain
        if key in st.secrets:
            return st.secrets[key]
    except:
        # Agar error aaye (local machine par), toh pass karo
        pass
    
    # Phir local .env ya environment variables check karo
    return os.getenv(key)
ACCOUNT_SID = get_secret("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = get_secret("TWILIO_AUTH_TOKEN")
WEATHER_API_KEY = get_secret("WEATHER_API_KEY")
FROM_WHATSAPP = "whatsapp:+14155238886"

# ---------------- 1. TWILIO FUNCTION ----------------
def send_whatsapp(msg, to_number):
    if not ACCOUNT_SID or not AUTH_TOKEN:
        st.error("Security Keys Missing!")
        return False
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(
            body=msg,
            from_=FROM_WHATSAPP,
            to=f"whatsapp:{to_number}"
        )
        return True
    except Exception as e:
        return False

# ---------------- 2. CONFIG & NEON UI ----------------
st.set_page_config(page_title="SmartLogistics AI Pro v3.0", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a, #1e3a8a, #020617);
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px);
        border-right: 2px solid rgba(0, 242, 254, 0.3);
    }
    .stButton>button {
        background: linear-gradient(45deg, #00f2fe, #4facfe);
        color: #000; font-weight: bold; border-radius: 12px;
        border: none; transition: 0.4s ease; width: 100%;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.07);
        padding: 25px; border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .icon-label { font-size: 14px; font-weight: bold; color: #00f2fe; text-align: center; }
    h1, h2, h3 { color: #00f2fe !important; text-shadow: 0 0 15px rgba(0, 242, 254, 0.6); }
    
    @keyframes scrollText { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .moving-footer {
        background: rgba(0, 0, 0, 0.3); white-space: nowrap; overflow: hidden;
        padding: 12px 0; border-top: 1px solid rgba(0, 242, 254, 0.3); margin-top: 50px;
    }
    .moving-footer p {
        display: inline-block; padding-left: 100%; animation: scrollText 20s linear infinite;
        color: #00f2fe; font-weight: bold; font-size: 18px; margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- 3. DATABASE ----------------
def get_db_connection():
    conn = sqlite3.connect("smart_logistics_v4.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                  (order_id TEXT PRIMARY KEY, customer TEXT, item TEXT, 
                  dist REAL, status TEXT, time TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_weather(city):
    if not WEATHER_API_KEY:
        return None
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res
    except: return None

# ---------------- 4. SIDEBAR ----------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/825/825590.png", width=90)
    st.title("Logistics Pro")
    
    st.markdown("### 🎵 Pawan Singh Special")
    try:
        audio_file = open(r"D:\Dilebary\pawan_singh.mp3", "rb")
        st.audio(audio_file, format="audio/mp3", loop=True)
    except:
        st.warning("Gana file missing!")

    st.divider()
    role = st.radio("Switch Portal", ["Customer", "Delivery Partner", "Admin"])
    
    if role == "Customer":
        choice = st.selectbox("Menu", ["🏠 Home", "📦 Book Order", "📍 Live Track", "🆘 Help Support"])
    elif role == "Delivery Partner":
        choice = st.selectbox("Menu", ["🚴 Tasks", "🌦️ Weather AI"])
    else:
        choice = st.selectbox("Menu", ["📊 Admin Dashboard"])

# ---------------- 5. PORTAL CONTENT ----------------

if role == "Customer":
    if choice == "🏠 Home":
        st.title("Smart Delivery Dashboard")
        st.markdown('<div class="glass-card"><h3>🚀 Welcome, Ritesh!</h3>AI-powered logistics at your fingertips.</div>', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        icons = [
            ("https://cdn-icons-png.flaticon.com/512/4359/4359635.png", "Top Kitchens"),
            ("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", "Fast Riders"),
            ("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", "AI Vehicles"),
            ("https://cdn-icons-png.flaticon.com/512/854/854878.png", "Live Map")
        ]
        cols = [c1, c2, c3, c4]
        for idx, col in enumerate(cols):
            with col:
                st.image(icons[idx][0], width=75)
                st.markdown(f'<p class="icon-label">{icons[idx][1]}</p>', unsafe_allow_html=True)

    elif choice == "📦 Book Order":
        st.header("New Shipment")
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                u_name = st.text_input("Your Name")
                u_item = st.selectbox("Category", ["Electronics", "Food", "Medical", "Documents"])
                u_phone = st.text_input("WhatsApp Number (for alerts)")
            with col_b:
                u_dist = st.number_input("Distance (km)", 0.1, 100.0, 5.0)
                u_city = st.text_input("Pickup City", "Bhopal")
            
            if st.button("Confirm Booking"):
                if u_name:
                    oid = f"SL-{random.randint(1000, 9999)}"
                    status = "DELAYED ⚠️" if u_dist > 20 else "ON TIME ✅"
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)", 
                              (oid, u_name, u_item, u_dist, status, datetime.now().strftime("%H:%M")))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Order {oid} Confirmed!")
                    st.balloons()
                    
                    if u_phone:
                        send_whatsapp(f"Hi {u_name}, your order {oid} for {u_item} is confirmed! Status: {status}", u_phone)
                else:
                    st.error("Please enter your name.")
            st.markdown('</div>', unsafe_allow_html=True)

    elif choice == "📍 Live Track":
        st.header("Track My Order")
        track_id = st.text_input("Enter Order ID")
        if track_id:
            conn = get_db_connection()
            df = pd.read_sql(f"SELECT * FROM orders WHERE order_id='{track_id}'", conn)
            conn.close()
            if not df.empty:
                st.info(f"📍 Current Status: {df['status'][0]} | Booked at: {df['time'][0]}")
                st.map(pd.DataFrame({'lat': [23.2599], 'lon': [77.4126]}))
            else: st.error("Invalid ID.")

elif role == "Delivery Partner":
    if choice == "🚴 Tasks":
        st.title("Delivery Queue")
        conn = get_db_connection()
        df_tasks = pd.read_sql("SELECT * FROM orders", conn)
        conn.close()
        if not df_tasks.empty:
            st.dataframe(df_tasks, use_container_width=True)
        else:
            st.info("No active tasks.")
    
    elif choice == "🌦️ Weather AI":
        st.title("Weather Risk Analysis")
        w_city = st.text_input("Enter Delivery City", "Bhopal")
        if st.button("Analyze Route"):
            data = get_weather(w_city)
            if data and "main" in data:
                t = data['main']['temp']
                desc = data['weather'][0]['description'].title()
                st.markdown(f'<div class="glass-card"><h4>Condition: {desc}</h4></div>', unsafe_allow_html=True)
                st.metric("Temperature", f"{t}°C")
                if "rain" in desc.lower() or "storm" in desc.lower():
                    st.warning("⚠️ High Risk: Use Waterproof gear and reduce speed.")
                else:
                    st.success("✅ Clear Route: Proceed with standard speed.")
            else:
                st.error("Weather data unavailable. Check City Name.")

elif role == "Admin":
    st.title("Admin Control Center")
    conn = get_db_connection()
    df_admin = pd.read_sql("SELECT * FROM orders", conn)
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Shipments", len(df_admin))
    col2.metric("Revenue (Est)", f"₹{len(df_admin)*150}")
    col3.metric("AI Prediction Accuracy", "94%")
    
    st.markdown("### Recent Order Activity")
    st.dataframe(df_admin, use_container_width=True)
    
    if not df_admin.empty:
        st.markdown("### Distance Analytics")
        st.bar_chart(df_admin.set_index('order_id')['dist'])

st.markdown(f"""
<div class="moving-footer">
    <p>
        🚀 © 2026 SmartLogistics AI Pro | Created by Ritesh Kumar Singh | 
        Technocrats Institute of Technology | BHOPAL | Viksit Bharat Tech Innovation 💡
    </p>
</div>
""", unsafe_allow_html=True)