import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, io, csv
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pathlib, requests, os

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

# --- Styles (glassmorphism + metrics)
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
.metric-green { background:#c8ffc8; }
.metric-yellow { background:#ffffc8; }
.metric-red { background:#ffc8c8; }
</style>
""", unsafe_allow_html=True)

# Language selector
current_lang = st.sidebar.selectbox("🌐 Interface Language", list(translations.keys()), key="lang_select")
t = translations[current_lang]

st.title(t["page_title"])

# --- Patients
BASE_DIR = pathlib.Path(__file__).parent.resolve()
patients = {
    "PATIENT_05": {"Age": 67, "Diabetic": True, "Allergies": ["Penicillin"], "History": "Coma (3 days)", "Avatar": BASE_DIR / "avatars" / "avatar1.png"},
    "PATIENT_12": {"Age": 54, "Diabetic": False, "Allergies": [], "History": "Hypertension", "Avatar": BASE_DIR / "avatars" / "avatar2.png"},
    "PATIENT_21": {"Age": 73, "Diabetic": True, "Allergies": ["Sulfa"], "History": "Post-surgery", "Avatar": BASE_DIR / "avatars" / "avatar3.png"},
}
selected_patient = st.sidebar.selectbox(t["select_patient"], list(patients.keys()))
new_age = st.sidebar.number_input(t["edit_age"], min_value=1, max_value=120, value=patients[selected_patient]["Age"])
patients[selected_patient]["Age"] = new_age
patient = patients[selected_patient]

# Avatar
try:
    img = Image.open(patient["Avatar"])
    st.sidebar.image(img, width=70)
except Exception as e:
    fallback_avatar = "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_placeholder.png"
    st.sidebar.image(fallback_avatar, width=70)
    st.sidebar.error(f"Avatar image failed to load: {e}")

# Patient info
st.sidebar.markdown(f"""
<div class="glass-card">
<b>Patient ID:</b> {selected_patient}<br>
<b>{t['edit_age']}:</b> {patient['Age']}<br>
<b>{t['diabetic']}:</b> {"Yes" if patient['Diabetic'] else "No"}<br>
<b>{t['allergies']}:</b> {', '.join(patient['Allergies']) if patient['Allergies'] else 'None'}<br>
<b>{t['history']}:</b> {patient['History']}
</div>
""", unsafe_allow_html=True)

# --- Feedback email function (Brevo API)
def send_feedback_email(name, email, message):
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = os.getenv("BREVO_API_KEY")  # Streamlit Secrets
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": "ICU Simulator", "email": "no-reply@icu-sim.com"},
        "to": [{"email": "sapban92@gmail.com"}],
        "subject": "ICU Simulator Feedback Received",
        "htmlContent": f"<p><b>Name:</b> {name}<br><b>Email:</b> {email}<br><b>Message:</b> {message}</p>"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 201
    except Exception as e:
        st.sidebar.error(f"Error sending email: {e}")
        return False

# --- Feedback form
with st.sidebar.form("feedback_form"):
    st.subheader(t["feedback"])
    name = st.text_input(t["your_name"])
    email = st.text_input(t["your_email"])
    message = st.text_area(t["feedback_message"])
    submitted = st.form_submit_button(t["submit"])
    if submitted:
        # Save to CSV
        with open("feedback_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, email, message, datetime.now().isoformat()])
        # Send via Brevo
        sent = send_feedback_email(name, email, message)
        if sent:
            st.sidebar.success(t["feedback_saved"])
        else:
            st.sidebar.error(t["feedback_not_sent"])

# --- Functions for vitals, protocols etc.
def predict_risk(vitals, patient):
    risk = 0
    risk += 1 if patient["Diabetic"] and vitals["Glucose"] < 70 else 0
    risk += 1 if vitals["HR"] < 40 or vitals["SpO2"] < 85 else 0
    risk += 1 if vitals["Movement"] and "Coma" in str(patient["History"]) else 0
    return min(risk, 3)

def simulate_vitals(case_id):
    return {
        1: {"HR": 82, "SpO2": 96, "Glucose": 61, "Movement": False},
        2: {"HR": 38, "SpO2": 80, "Glucose": 112, "Movement": False},
        3: {"HR": 75, "SpO2": 92, "Glucose": 105, "Movement": True},
        4: {"HR": 85, "SpO2": 85, "Glucose": 108, "Movement": False},
        5: {"HR": 28, "SpO2": 76, "Glucose": 114, "Movement": False},
    }.get(case_id, {})

def generate_case_protocol(case_id, vitals):
    protocols = {
        1: {"title": "CASE 1: Insulin Deficiency", "explanation": "Low glucose detected in diabetic patient. Emergency insulin protocol initiated.", "topic": "/ICU/devices/patient/inject_insulin", "actions": ["💉 Inject 6 units insulin", "📝 Update EHR", "📡 Notify ICU staff"]},
        2: {"title": "CASE 2: Drug Not Available", "explanation": "Critical cardiac condition. Drug unavailable locally. Remote dispatch triggered.", "topic": "/ICU/med_alert/adrenaline_request", "actions": ["📶 Broadcast MQTT request", "🚁 Drone dispatched", "📲 ICU notified"]},
        3: {"title": "CASE 3: Patient Awakens", "explanation": "Movement detected in previously comatose patient.", "topic": "/ICU/alerts/patient_awake", "actions": ["📈 Motion confirmed", "👨‍⚕️ Alert neuro team", "📋 Start assessment"]},
        4: {"title": "CASE 4: Oxygen Deficiency", "explanation": "Low SpO₂ detected. Oxygen valve activated.", "topic": "/ICU/devices/oxygen_supply/start", "actions": ["🫁 Oxygen supply started", "🔔 Staff alerted", "📡 Status logged"]},
        5: {"title": "CASE 5: Cardiac Arrest", "explanation": "Cardiac arrest detected. Full Code Blue triggered.", "topic": "/ICU/alerts/code_blue", "actions": ["🚨 Code Blue alert", "🧬 Cardiac protocol activated", "📞 Team paged"]},
    }
    p = protocols.get(case_id)
    p["critical"] = True
    return p

def plot_vitals(vitals):
    df = pd.DataFrame({
        "Time": [f"T-{i}" for i in range(9, -1, -1)],
        "Heart Rate": [random.randint(70, 100)]*9 + [vitals["HR"]],
        "SpO₂": [random.randint(90, 99)]*9 + [vitals["SpO2"]],
        "Glucose": [random.randint(80, 130)]*9 + [vitals["Glucose"]],
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Heart Rate"], name="Heart Rate", line=dict(color="red")))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["SpO₂"], name="SpO₂", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Glucose"], name="Glucose", line=dict(color="green")))
    fig.update_layout(template="plotly_white", height=350, transition_duration=400)
    return fig

def mqtt_stats_panel():
    st.markdown(f"<div class='glass-card'><h4>{t['broker_status']}</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<span class='metric-badge metric-green'>{t['latency']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='metric-badge metric-green'>{t['cluster_mode']}</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<span class='metric-badge metric-yellow'>{t['throughput']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='metric-badge metric-green'>{t['qos']}</span>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<span class='metric-badge metric-green'>{t['online_devices']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='metric-badge metric-yellow'>{t['session_expiry']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def mqtt_flow_diagram(case, protocol):
    labels = ["Sensor", "MQTT Broker", "AI Engine", "IoT Device/Hospital"]
    sources = [0, 1, 2]
    targets = [1, 2, 3]
    values = [1, 1, 1]
    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels, color="lightblue"),
        link=dict(source=sources, target=targets, value=values, label=[f"{case} vitals", "Protocol Trigger", protocol["topic"]])
    )])
    fig.update_layout(title_text="🔄 MQTT Protocol Flow", font_size=12)
    return fig

def protocol_timeline(case, protocol, vitals):
    timeline = [
        {"Event": "Sensor Trigger", "Time": datetime.now().strftime("%H:%M:%S"), "Desc": f"Vitals: {vitals}"},
        {"Event": "Broker Receive", "Time": (datetime.now()).strftime("%H:%M:%S"), "Desc": "MQTT Broker received sensor packet"},
        {"Event": "AI Protocol", "Time": (datetime.now()).strftime("%H:%M:%S"), "Desc": f"AI Engine generated: {protocol['title']}"},
        {"Event": "Device Action", "Time": (datetime.now()).strftime("%H:%M:%S"), "Desc": ', '.join(protocol["actions"])},
    ]
    timeline_df = pd.DataFrame(timeline)
    st.table(timeline_df)

def generate_pdf_report(case_id, vitals, protocol):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("🧠 ICU Emergency Report", styles['Title']), Spacer(1, 12)]
    elements += [
        Paragraph(f"<b>Patient ID:</b> {selected_patient} &nbsp;&nbsp; <b>Age:</b> {patients[selected_patient]['Age']}", styles['Normal']),
        Spacer(1, 12),
        Paragraph(f"<b>Case:</b> {protocol['title']}", styles['Heading3']),
        Paragraph(protocol['explanation'], styles['BodyText']),
        Spacer(1, 12),
        Paragraph(f"<b>MQTT Topic:</b> {protocol['topic']}", styles['BodyText']),
        Spacer(1, 12),
    ]
    vitals_data = [["Heart Rate", "SpO₂", "Glucose", "Movement"],
                   [f"{vitals['HR']} bpm", f"{vitals['SpO2']}%", f"{vitals['Glucose']} mg/dL", "Yes" if vitals["Movement"] else "No"]]
    table = Table(vitals_data, hAlign='LEFT')
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                               ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(table)
    elements.append(Spacer(1, 18))
    elements.append(Paragraph("<b>Actions Taken:</b>", styles['Heading4']))
    for action in protocol["actions"]:
        elements.append(Paragraph(f"• {action}", styles['BodyText']))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def download_csv_log():
    df = pd.DataFrame({"Timestamp": [datetime.now().isoformat()],
                       "Patient": [selected_patient],
                       "Case": [st.session_state.get('current_case', 'N/A')],
                       "Vitals": [st.session_state.get('last_vitals', {})],
                       "Protocol": [st.session_state.get('last_protocol', {}).get('title', 'N/A')]})
    return df.to_csv(index=False).encode("utf-8")

# --- Case selection
case_options = {1: "Case 1: Insulin Deficiency", 2: "Case 2: Drug Not Available", 3: "Case 3: Patient Awakens", 4: "Case 4: Oxygen Deficiency", 5: "Case 5: Cardiac Arrest"}
case_id = st.selectbox(t["choose_case"], list(case_options.keys()), format_func=lambda x: case_options[x])

if case_id:
    vitals = simulate_vitals(case_id)
    st.session_state['last_vitals'] = vitals
    protocol = generate_case_protocol(case_id, vitals)
    st.session_state['last_protocol'] = protocol
    st.session_state['current_case'] = case_id
    st.markdown(f"### {protocol['title']}")
    st.write(protocol["explanation"])
    st.markdown(t["actions_taken"])
    for action in protocol["actions"]:
        st.write(action)
    st.markdown(t["vitals_chart"])
    st.plotly_chart(plot_vitals(vitals), use_container_width=True)
    st.markdown(t["mqtt_flow"])
    st.plotly_chart(mqtt_flow_diagram(case_id, protocol), use_container_width=True)
    st.markdown(t["protocol_timeline"])
    protocol_timeline(case_id, protocol, vitals)
    st.markdown(t["risk_prediction"])
    st.metric(label=t["critical_event_probability"], value=f"{predict_risk(vitals, patient)}/3 Risk Level")
    st.markdown(t["mqtt_topic"])
    st.code(protocol["topic"], language="plaintext")
    mqtt_stats_panel()
    st.markdown(t["download_pdf"])
    st.download_button(label="📄 Download PDF", data=generate_pdf_report(case_id, vitals, protocol), file_name="ICU_Case_Report.pdf", mime="application/pdf")
    st.markdown(t["download_csv"])
    st.download_button(label="📥 Download CSV", data=download_csv_log(), file_name="ICU_Session_Log.csv", mime="text/csv")

st.caption(t["app_caption"])
