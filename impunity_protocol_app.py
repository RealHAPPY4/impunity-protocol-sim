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
import pathlib
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# ---------------- CONFIG ---------------- #
BREVO_API_KEY = "your_brevo_api_key_here"   # replace with your Brevo key
HOSPITAL_EMAIL = "sapban92@gmail.com"

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# ---------------- TRANSLATIONS ---------------- #
translations = {
    "English": {
        "page_title": "ICU Futuristic MQTT Simulator",
        "interface_language": "🌐 Interface Language",
        "select_patient": "👤 Select Patient",
        "edit_age": "Edit Age",
        "diabetic": "Diabetic",
        "allergies": "Allergies",
        "history": "History",
        "feedback": "💬 Feedback",
        "your_name": "Your Name",
        "your_email": "Your Email",
        "feedback_message": "Feedback Message",
        "submit": "Submit",
        "feedback_saved": "✅ Feedback sent & logged!",
        "feedback_not_sent": "❌ Feedback not sent.",
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
        "app_caption": "📡 Futuristic MQTT | Smart ICU Simulation | AI & Animated Protocols | Augmented Graphical Engine",
    },
    "हिन्दी": {
        "page_title": "आईसीयू फ्यूचरिस्टिक MQTT सिम्युलेटर",
        "interface_language": "🌐 इंटरफ़ेस भाषा",
        "select_patient": "👤 मरीज चुनें",
        "edit_age": "आयु बदलें",
        "diabetic": "मधुमेही",
        "allergies": "एलर्जी",
        "history": "इतिहास",
        "feedback": "💬 प्रतिक्रिया",
        "your_name": "आपका नाम",
        "your_email": "आपका ईमेल",
        "feedback_message": "संदेश",
        "submit": "जमा करें",
        "feedback_saved": "✅ प्रतिक्रिया भेज दी गई और लॉग हो गई!",
        "feedback_not_sent": "❌ प्रतिक्रिया भेजने में समस्या।",
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
        "app_caption": "📡 फ्यूचरिस्टिक MQTT | स्मार्ट ICU सिम्युलेशन | एआई और एनिमेटेड प्रोटोकॉल | संवर्धित ग्राफिकल इंजन",
    },
}

# ---------------- STYLES ---------------- #
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
.metric-badge { border-radius: 10px; padding: 5px 15px; font-size: 18px; }
.metric-green { background:#c8ffc8; }
.metric-yellow { background:#ffffc8; }
.metric-red { background:#ffc8c8; }
</style>
""", unsafe_allow_html=True)

# ---------------- LANGUAGE ---------------- #
current_lang = st.sidebar.selectbox("🌐 Interface Language", list(translations.keys()), key="lang_select")
t = translations[current_lang]
st.title(t["page_title"])

# ---------------- PATIENTS ---------------- #
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
try:
    img = Image.open(patient["Avatar"])
    st.sidebar.image(img, width=70)
except:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_placeholder.png", width=70)

st.sidebar.markdown(f"""
<div class="glass-card">
<b>Patient ID:</b> {selected_patient}<br>
<b>{t['edit_age']}:</b> {patient['Age']}<br>
<b>{t['diabetic']}:</b> {"Yes" if patient['Diabetic'] else "No"}<br>
<b>{t['allergies']}:</b> {', '.join(patient['Allergies']) if patient['Allergies'] else 'None'}<br>
<b>{t['history']}:</b> {patient['History']}
</div>
""", unsafe_allow_html=True)

# ---------------- FEEDBACK EMAIL ---------------- #
def send_feedback_email(name, user_email, message):
    try:
        # hospital
        hospital_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": HOSPITAL_EMAIL}],
            sender={"email": HOSPITAL_EMAIL, "name": "ICU Feedback System"},
            subject=f"New Feedback from {name}",
            html_content=f"<h3>Feedback</h3><b>Name:</b> {name}<br><b>Email:</b> {user_email}<br><b>Message:</b><br>{message}"
        )
        api_instance.send_transac_email(hospital_email)
        # user acknowledgment
        ack_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": user_email}],
            sender={"email": HOSPITAL_EMAIL, "name": "ICU Smart Protocol Team"},
            subject="✅ Thank you for your feedback!",
            html_content=f"Dear {name},<br>Thank you for using our Hospital ICU Emergency System.<br>We have received your feedback."
        )
        api_instance.send_transac_email(ack_email)
        return True
    except ApiException as e:
        st.sidebar.error(f"Email error: {e}")
        return False

with st.sidebar.form("feedback_form"):
    st.subheader(t["feedback"])
    name = st.text_input(t["your_name"])
    user_email = st.text_input(t["your_email"])
    message = st.text_area(t["feedback_message"])
    submitted = st.form_submit_button(t["submit"])
    if submitted:
        with open("feedback_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, user_email, message, datetime.now().isoformat()])
        sent = send_feedback_email(name, user_email, message)
        if sent: st.sidebar.success(t["feedback_saved"])
        else: st.sidebar.error(t["feedback_not_sent"])

# ---------------- FUNCTIONS ---------------- #
def predict_risk(vitals, patient):
    risk = 0
    if patient["Diabetic"] and vitals["Glucose"] < 70: risk += 1
    if vitals["HR"] < 40 or vitals["SpO2"] < 85: risk += 1
    if vitals["Movement"] and "Coma" in str(patient["History"]): risk += 1
    return min(risk, 3)

def simulate_vitals(case_id):
    return {
        1: {"HR": 82,"SpO2":96,"Glucose":61,"Movement":False},
        2: {"HR": 38,"SpO2":80,"Glucose":112,"Movement":False},
        3: {"HR": 75,"SpO2":92,"Glucose":105,"Movement":True},
        4: {"HR": 85,"SpO2":85,"Glucose":108,"Movement":False},
        5: {"HR": 28,"SpO2":76,"Glucose":114,"Movement":False},
    }.get(case_id,{})

def generate_case_protocol(case_id,vitals):
    protocols={
        1:{"title":"CASE 1: Insulin Deficiency","explanation":"Low glucose detected. Emergency insulin protocol initiated.","topic":"/ICU/devices/patient/inject_insulin","actions":["💉 Inject 6 units insulin","📝 Update EHR","📡 Notify ICU staff"]},
        2:{"title":"CASE 2: Drug Not Available","explanation":"Critical cardiac condition. Remote dispatch triggered.","topic":"/ICU/med_alert/adrenaline_request","actions":["📶 Broadcast MQTT request","🚁 Drone dispatched","📲 ICU notified"]},
        3:{"title":"CASE 3: Patient Awakens","explanation":"Movement detected in comatose patient.","topic":"/ICU/alerts/patient_awake","actions":["📈 Motion confirmed","👨‍⚕️ Alert neuro team","📋 Start assessment"]},
        4:{"title":"CASE 4: Oxygen Deficiency","explanation":"Low SpO₂ detected. Oxygen valve activated.","topic":"/ICU/devices/oxygen_supply/start","actions":["🫁 Oxygen supply started","🔔 Staff alerted","📡 Status logged"]},
        5:{"title":"CASE 5: Cardiac Arrest","explanation":"Cardiac arrest detected. Code Blue triggered.","topic":"/ICU/alerts/code_blue","actions":["🚨 Code Blue alert","🧬 Cardiac protocol activated","📞 Team paged"]},
    }
    p=protocols.get(case_id); p["critical"]=True; return p

def plot_vitals(vitals):
    df=pd.DataFrame({
        "Time":[f"T-{i}" for i in range(9,-1,-1)],
        "Heart Rate":[random.randint(70,100)]*9+[vitals["HR"]],
        "SpO₂":[random.randint(90,99)]*9+[vitals["SpO2"]],
        "Glucose":[random.randint(80,130)]*9+[vitals["Glucose"]],
    })
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df["Time"],y=df["Heart Rate"],name="Heart Rate",line=dict(color="red")))
    fig.add_trace(go.Scatter(x=df["Time"],y=df["SpO₂"],name="SpO₂",line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df["Time"],y=df["Glucose"],name="Glucose",line=dict(color="green")))
    fig.update_layout(template="plotly_white",height=350,transition_duration=400)
    return fig

def mqtt_stats_panel():
    st.markdown(f"<div class='glass-card'><h4>{t['broker_status']}</h4>",unsafe_allow_html=True)
    col1,col2,col3=st.columns(3)
    with col1: st.markdown(f"<span class='metric-badge metric-green'>{t['latency']}</span>",unsafe_allow_html=True); st.markdown(f"<span class='metric-badge metric-green'>{t['cluster_mode']}</span>",unsafe_allow_html=True)
    with col2: st.markdown(f"<span class='metric-badge metric-yellow'>{t['throughput']}</span>",unsafe_allow_html=True); st.markdown(f"<span class='metric-badge metric-green'>{t['qos']}</span>",unsafe_allow_html=True)
    with col3: st.markdown(f"<span class='metric-badge metric-green'>{t['online_devices']}</span>",unsafe_allow_html=True); st.markdown(f"<span class='metric-badge metric-yellow'>{t['session_expiry']}</span>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

def mqtt_flow_diagram(case,protocol):
    labels=["Sensor","MQTT Broker","AI Engine","IoT Device/Hospital"]
    sources=[0,1,2]; targets=[1,2,3]; values=[1,1,1]
    fig=go.Figure(data=[go.Sankey(node=dict(pad=15,thickness=20,line=dict(color="black",width=0.5),label=labels,color="lightblue"),link=dict(source=sources,target=targets,value=values,label=[f"{case} vitals","Protocol Trigger",protocol["topic"]]))])
    fig.update_layout(title_text="🔄 MQTT Protocol Flow",font_size=12); return fig

def protocol_timeline(case,protocol,vitals):
    timeline=[{"Event":"Sensor Trigger","Time":datetime.now().strftime("%H:%M:%S"),"Desc":f"Vitals: {vitals}"},
              {"Event":"Broker Receive","Time":datetime.now().strftime("%H:%M:%S"),"Desc":"MQTT Broker received sensor packet"},
              {"Event":"AI Protocol","Time":datetime.now().strftime("%H:%M:%S"),"Desc":f"AI generated: {protocol['title']}"},
              {"Event":"Device Action","Time":datetime.now().strftime("%H:%M:%S"),"Desc":', '.join(protocol["actions"])}]
    st.table(pd.DataFrame(timeline))

def generate_pdf_report(case_id,vitals,protocol):
    buffer=io.BytesIO(); doc=SimpleDocTemplate(buffer,pagesize=A4); styles=getSampleStyleSheet()
    elements=[Paragraph("🧠 ICU Emergency Report",styles['Title']),Spacer(1,12)]
    elements+=[Paragraph(f"<b>Patient ID:</b> {selected_patient} &nbsp;&nbsp; <b>Age:</b> {patients[selected_patient]['Age']}",styles['Normal']),Spacer(1,12)]
    elements+=[Paragraph(f"<b>Case:</b> {protocol['title']}",styles['Heading3']),Paragraph(protocol['explanation'],styles['BodyText']),Spacer(1,12)]
    elements+=[Paragraph(f"<b>MQTT Topic:</b> {protocol['topic']}",styles['BodyText']),Spacer(1,12)]
    vitals_data=[["Heart Rate","SpO₂","Glucose","Movement"],[f"{vitals['HR']} bpm",f"{vitals['SpO2']}%",f"{vitals['Glucose']} mg/dL","Yes" if vitals["Movement"] else "No"]]
    table=Table(vitals_data,hAlign='LEFT'); table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightblue),('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
    elements.append(table); elements.append(Spacer(1,18)); elements.append(Paragraph("<b>Actions Taken:</b>",styles['Heading4']))
    for action in protocol["actions"]: elements.append(Paragraph(f"• {action}",styles['Normal']))
    elements.append(Spacer(1,18)); elements.append(Paragraph("<b>MQTT Explanation:</b><br/>MQTT ensures low-latency emergency response.",styles['BodyText']))
    doc.build(elements); buffer.seek(0); return buffer

# ---------------- MAIN ---------------- #
st.markdown(f"<div class='glass-card'><h3>{t['choose_case']}</h3></div>",unsafe_allow_html=True)
cols=st.columns(5); labels=["🩺 Case 1","💊 Case 2","🧠 Case 3","🫁 Case 4","💔 Case 5"]; case_id=None
for i,col in enumerate(cols):
    if col.button(labels[i]): case_id=i+1

if case_id:
    vitals=simulate_vitals(case_id); protocol=generate_case_protocol(case_id,vitals); risk=predict_risk(vitals,patient)
    st.markdown(f"<div class='glass-card'><h3>{protocol['title']}</h3><p style='color:green;'>{protocol['explanation']}</p></div>",unsafe_allow_html=True)
    st.markdown(f"{t['mqtt_topic']} `{protocol['topic']}`"); mqtt_stats_panel()
    st.markdown(t["actions_taken"]); [st.markdown(f"{i}. {a}") for i,a in enumerate(protocol["actions"],1)]
    st.markdown(t["vitals_chart"]); st.plotly_chart(plot_vitals(vitals),use_container_width=True)
    st.markdown(t["mqtt_flow"]); st.plotly_chart(mqtt_flow_diagram(protocol["title"],protocol),use_container_width=True)
    st.markdown(t["protocol_timeline"]); protocol_timeline(protocol["title"],protocol,vitals)
    st.markdown(t["risk_prediction"]); st.metric(t["critical_event_probability"],["Low","Moderate","High","Critical"][risk])
    st.markdown(t["message_log"]); st.code(f"[Sensor] Published → {vitals}\n[Broker] Delivered to AI Engine\n[AI Engine] Generated Protocol → {protocol['title']}\n[Broker] Published to {protocol['topic']}\n[Device] Actions → {', '.join(protocol['actions'])}")
    if protocol["critical"]: st.markdown(f'<audio autoplay src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3" controls hidden></audio>',unsafe_allow_html=True)
    pdf=generate_pdf_report(case_id,vitals,protocol); st.download_button(t["download_pdf"],data=pdf,file_name=f"{protocol['title']}.pdf",mime="application/pdf")
    log_data=pd.DataFrame([{"Patient":selected_patient,"Case":protocol["title"],"Topic":protocol["topic"],"HR":vitals["HR"],"SpO2":vitals["SpO2"],"Glucose":vitals["Glucose"],"Movement":vitals["Movement"],"Risk":["Low","Moderate","High","Critical"][risk],"Age":patients[selected_patient]["Age"]}])
    csv_buf=io.StringIO(); log_data.to_csv(csv_buf,index=False); st.download_button(t["download_csv"],data=csv_buf.getvalue(),file_name="icu_log.csv",mime="text/csv")

st.markdown("---"); st.caption(t["app_caption"])
