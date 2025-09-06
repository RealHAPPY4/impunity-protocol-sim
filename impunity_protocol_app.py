import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, io, csv, smtplib
from datetime import datetime
from email.mime.text import MIMEText
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Translation dictionaries
translations = {
    "English": {
        "page_title": "ICU Futuristic MQTT Simulator",
        "interface_language": "🌐 Interface Language",
        "select_patient": "👤 Select Patient",
        "patient_profile": "### Patient Profile",
        "edit_age": "Edit Age",
        "diabetic": "Diabetic",
        "allergies": "Allergies",
        "history": "History",
        "feedback": "💬 Feedback",
        "your_name": "Your Name",
        "your_email": "Your Email",
        "feedback_message": "Feedback Message",
        "submit": "Submit",
        "feedback_saved": "✅ Feedback saved and emailed!",
        "feedback_not_sent": "❌ Feedback saved, but email not sent.",
        "choose_case": "🚑 Futuristic Emergency Simulator\nChoose a case:",
        "actions_taken": "### ✅ Actions Taken",
        "vitals_chart": "### 📈 Vitals Chart",
        "mqtt_flow": "### 🔄 MQTT Flow",
        "protocol_timeline": "### ⏳ Protocol Timeline",
        "risk_prediction": "### 🚦 Risk Prediction",
        "critical_event_probability": "Critical Event Probability",
        "message_log": "### 📜 Message Log",
        "download_pdf": "📄 Download Case Report (PDF)",
        "download_csv": "📥 Download Session Log (CSV)",
        "mqtt_topic": "**📡 MQTT Topic:**",
        "broker_status": "🌐 MQTT Broker Status",
        "latency": "Latency: 100 ms",
        "cluster_mode": "Cluster Mode: Active",
        "throughput": "Throughput: 500 msg/sec",
        "qos": "QoS Level: 2",
        "online_devices": "Device Online: 24",
        "session_expiry": "Session Expiry: 10 min",
        "app_caption": "📡 Futuristic MQTT Brokerage | Smart ICU Simulation | AI & Animated Protocols | Augmented Graphical Engine",
    },
    "हिन्दी": {
        "page_title": "आईसीयू फ्यूचरिस्टिक MQTT सिम्युलेटर",
        "interface_language": "🌐 इंटरफ़ेस भाषा",
        "select_patient": "👤 मरीज चुनें",
        "patient_profile": "### मरीज प्रोफाइल",
        "edit_age": "आयु बदलें",
        "diabetic": "मधुमेही",
        "allergies": "एलर्जी",
        "history": "इतिहास",
        "feedback": "💬 प्रतिक्रिया",
        "your_name": "आपका नाम",
        "your_email": "आपका ईमेल",
        "feedback_message": "संदेश",
        "submit": "जमा करें",
        "feedback_saved": "✅ प्रतिक्रिया सहेज ली गई और ईमेल कर दी गई!",
        "feedback_not_sent": "❌ प्रतिक्रिया सहेज ली गई, लेकिन ईमेल भेजी नहीं गई।",
        "choose_case": "🚑 फ्यूचरिस्टिक इमरजेंसी सिम्युलेटर\nएक केस चुनें:",
        "actions_taken": "### ✅ लिए गए कार्य",
        "vitals_chart": "### 📈 जीवन संकेत चार्ट",
        "mqtt_flow": "### 🔄 MQTT प्रवाह",
        "protocol_timeline": "### ⏳ प्रोटोकॉल टाइमलाइन",
        "risk_prediction": "### 🚦 जोखिम अनुमान",
        "critical_event_probability": "गंभीर घटना की संभावना",
        "message_log": "### 📜 संदेश लॉग",
        "download_pdf": "📄 केस रिपोर्ट डाउनलोड करें (PDF)",
        "download_csv": "📥 सत्र लॉग डाउनलोड करें (CSV)",
        "mqtt_topic": "**📡 MQTT विषय:**",
        "broker_status": "🌐 MQTT दलाल स्थिति",
        "latency": "लेटेंसी: 100 मि.से.",
        "cluster_mode": "क्लस्टर मोड: सक्रिय",
        "throughput": "थ्रूपुट: 500 संदेश/सेकंड",
        "qos": "QoS स्तर: 2",
        "online_devices": "ऑनलाइन डिवाइस: 24",
        "session_expiry": "सत्र समाप्ति: 10 मिनट",
        "app_caption": "📡 फ्यूचरिस्टिक MQTT दलाली | स्मार्ट ICU सिम्युलेशन | एआई और एनिमेटेड प्रोटोकॉल | संवर्धित ग्राफिकल इंजन",
    },
}

# --- Styles
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.glass-card {
    background: rgba(255, 255, 255, 0.22);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    padding: 18px 20px;
    margin-top: 12px;
    margin-bottom: 12px;
}
.metric-badge {
    border-radius: 10px;
    padding: 5px 15px;
    font-size: 18px;
}
.metric-green {
    background:#c8ffc8;
}
.metric-yellow {
    background:#ffffc8;
}
.metric-red {
    background:#ffc8c8;
}
</style>
""", unsafe_allow_html=True)

# Language selector
current_lang = st.sidebar.selectbox(
    "🌐 Interface Language",
    list(translations.keys()),
    key="lang_select"
)
t = translations[current_lang]

st.title(t["page_title"])

# Patient profiles without avatars
patients = {
    "PATIENT_05": {"Age": 67, "Diabetic": True, "Allergies": ["Penicillin"], "History": "Coma (3 days)"},
    "PATIENT_12": {"Age": 54, "Diabetic": False, "Allergies": [], "History": "Hypertension"},
    "PATIENT_21": {"Age": 73, "Diabetic": True, "Allergies": ["Sulfa"], "History": "Post-surgery"},
}

selected_patient = st.sidebar.selectbox(t["select_patient"], list(patients.keys()))
new_age = st.sidebar.number_input(t["edit_age"], min_value=1, max_value=120, value=patients[selected_patient]["Age"])
patients[selected_patient]["Age"] = new_age
patient = patients[selected_patient]

# Show patient profile text only
st.sidebar.markdown(f"""
<div class="glass-card">
<b>Patient ID:</b> {selected_patient}<br>
<b>{t['edit_age']}:</b> {patient['Age']}<br>
<b>{t['diabetic']}:</b> {"Yes" if patient['Diabetic'] else "No"}<br>
<b>{t['allergies']}:</b> {', '.join(patient['Allergies']) if patient['Allergies'] else 'None'}<br>
<b>{t['history']}:</b> {patient['History']}
</div>
""", unsafe_allow_html=True)

# Feedback email function
def send_feedback_email(name, email, message):
    subject = "ICU Simulator Feedback Received"
    body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    sender = "your_email@gmail.com"          # Replace with your Gmail address
    recipient = "sapban92@gmai.com"
    password = "your_app_password_here"      # Replace with your Gmail app password

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.sidebar.error(f"Email send error: {e}")
        return False

# Feedback form
with st.sidebar.form("feedback_form"):
    st.subheader(t["feedback"])
    name = st.text_input(t["your_name"])
    email = st.text_input(t["your_email"])
    message = st.text_area(t["feedback_message"])
    submitted = st.form_submit_button(t["submit"])
    if submitted:
        with open("feedback_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, email, message, datetime.now().isoformat()])
        sent = send_feedback_email(name, email, message)
        if sent:
            st.sidebar.success(t["feedback_saved"])
        else:
            st.sidebar.error(t["feedback_not_sent"])

# Rest of the functions and main interface remain the same...
# (Keep functions: predict_risk, simulate_vitals, generate_case_protocol, plot_vitals, mqtt_stats_panel, mqtt_flow_diagram, protocol_timeline, generate_pdf_report)
# And the main interface logic as before, just without any avatar code.

# For brevity, please use your existing function implementations unchanged from before.

# Main interface code with UI and charts goes here...

# Call your existing main interface code below to complete the app.

