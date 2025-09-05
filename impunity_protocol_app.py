import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, io, csv, smtplib
from email.mime.text import MIMEText
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="ICU MQTT Emergency Simulator", layout="wide")

# ---------------- Patient Profiles ---------------- #
patients = {
    "PATIENT_05": {"Age": 67, "Diabetic": True, "Allergies": ["Penicillin"], "History": "Coma (3 days)"},
    "PATIENT_12": {"Age": 54, "Diabetic": False, "Allergies": [], "History": "Hypertension"},
    "PATIENT_21": {"Age": 73, "Diabetic": True, "Allergies": ["Sulfa"], "History": "Post-surgery"}
}
selected_patient = st.sidebar.selectbox("👤 Select Patient", list(patients.keys()))
patient = patients[selected_patient]
st.sidebar.markdown("### Patient Profile")
for k, v in patient.items():
    st.sidebar.markdown(f"**{k}:** {v if not isinstance(v, list) else ', '.join(v)}")

# ---------------- Feedback Form ---------------- #
st.sidebar.markdown("---")
st.sidebar.subheader("💬 Feedback")
with st.sidebar.form("feedback_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Feedback Message")
    submitted = st.form_submit_button("Submit")
    if submitted:
        with open("feedback_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, email, message])
        st.sidebar.success("✅ Feedback saved!")

# ---------------- Vitals Simulation ---------------- #
def simulate_vitals(case_id):
    return {
        1: {"HR": 82, "SpO2": 96, "Glucose": 61, "Movement": False},
        2: {"HR": 38, "SpO2": 80, "Glucose": 112, "Movement": False},
        3: {"HR": 75, "SpO2": 92, "Glucose": 105, "Movement": True},
        4: {"HR": 85, "SpO2": 85, "Glucose": 108, "Movement": False},
        5: {"HR": 28, "SpO2": 76, "Glucose": 114, "Movement": False},
    }.get(case_id, {})

# ---------------- Protocol Engine ---------------- #
def generate_case_protocol(case_id, vitals):
    protocols = {
        1: {"title": "CASE 1: Insulin Deficiency",
            "explanation": "Low glucose detected in diabetic patient. Emergency insulin protocol initiated.",
            "topic": "/ICU/devices/patient/inject_insulin",
            "actions": ["💉 Inject 6 units insulin", "📝 Update EHR", "📡 Notify ICU staff"]},
        2: {"title": "CASE 2: Drug Not Available",
            "explanation": "Critical cardiac condition. Drug unavailable locally. Remote dispatch triggered.",
            "topic": "/ICU/med_alert/adrenaline_request",
            "actions": ["📶 Broadcast MQTT request", "🚁 Drone dispatched", "📲 ICU notified"]},
        3: {"title": "CASE 3: Patient Awakens",
            "explanation": "Movement detected in previously comatose patient.",
            "topic": "/ICU/alerts/patient_awake",
            "actions": ["📈 Motion confirmed", "👨‍⚕️ Alert neuro team", "📋 Start assessment"]},
        4: {"title": "CASE 4: Oxygen Deficiency",
            "explanation": "Low SpO₂ detected. Oxygen valve activated.",
            "topic": "/ICU/devices/oxygen_supply/start",
            "actions": ["🫁 Oxygen supply started", "🔔 Staff alerted", "📡 Status logged"]},
        5: {"title": "CASE 5: Cardiac Arrest",
            "explanation": "Cardiac arrest detected. Full Code Blue triggered.",
            "topic": "/ICU/alerts/code_blue",
            "actions": ["🚨 Code Blue alert", "🧬 Cardiac protocol activated", "📞 Team paged"]}
    }
    p = protocols.get(case_id)
    p["critical"] = True
    return p

# ---------------- Vitals Chart ---------------- #
def plot_vitals(vitals):
    df = pd.DataFrame({
        "Time": [f"T-{i}" for i in range(9, -1, -1)],
        "Heart Rate": [random.randint(70, 100)] * 9 + [vitals["HR"]],
        "SpO₂": [random.randint(90, 99)] * 9 + [vitals["SpO2"]],
        "Glucose": [random.randint(80, 130)] * 9 + [vitals["Glucose"]],
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Heart Rate"], name="Heart Rate", line=dict(color="red")))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["SpO₂"], name="SpO₂", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df["Time"], y=df["Glucose"], name="Glucose", line=dict(color="green")))
    fig.update_layout(template="plotly_white", height=350)
    return fig

# ---------------- MQTT Flow Diagram ---------------- #
def mqtt_flow_diagram(case, protocol):
    labels = ["Sensor", "MQTT Broker", "AI Engine", "IoT Device/Hospital"]
    sources = [0, 1, 2]
    targets = [1, 2, 3]
    values = [1, 1, 1]
    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20,
                  line=dict(color="black", width=0.5),
                  label=labels, color="lightblue"),
        link=dict(source=sources, target=targets, value=values,
                  label=[f"{case} vitals", "Protocol Trigger", protocol["topic"]])
    )])
    fig.update_layout(title_text="🔄 MQTT Protocol Flow", font_size=12)
    return fig

# ---------------- PDF Report ---------------- #
def generate_pdf_report(case_id, vitals, protocol):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("🧠 ICU Emergency Report", styles['Title']), Spacer(1, 12)]
    elements += [
        Paragraph(f"<b>Patient ID:</b> {selected_patient} &nbsp;&nbsp; <b>Age:</b> {patient['Age']}", styles['Normal']),
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
        elements.append(Paragraph(f"• {action}", styles['Normal']))
    elements.append(Spacer(1, 18))
    elements.append(Paragraph("<b>MQTT Explanation:</b><br/>"
        "MQTT enables publish-subscribe communication between sensors, AI engine, and IoT devices. "
        "This ensures low-latency emergency response in ICU.", styles['BodyText']))
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------- Email Alerts ---------------- #
def send_email(subject, body, to_email):
    from_email = "your_email@gmail.com"
    password = "your_app_password"  # Use Gmail App Password
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        st.info("📧 Email alert sent successfully!")
    except Exception as e:
        st.error(f"❌ Email not sent: {e}")

# ---------------- Main Interface ---------------- #
cols = st.columns(5)
labels = ["🩺 Case 1", "💊 Case 2", "🧠 Case 3", "🫁 Case 4", "💔 Case 5"]
case_id = 0
for i, col in enumerate(cols):
    if col.button(labels[i]):
        case_id = i + 1

if case_id:
    vitals = simulate_vitals(case_id)
    protocol = generate_case_protocol(case_id, vitals)
    st.header(protocol["title"])
    st.success(protocol["explanation"])
    st.markdown(f"**📡 MQTT Topic:** `{protocol['topic']}`")

    st.markdown("### ✅ Actions Taken")
    for i, action in enumerate(protocol["actions"], 1):
        st.markdown(f"{i}. {action}")

    st.markdown("### 📈 Vitals Chart")
    st.plotly_chart(plot_vitals(vitals), use_container_width=True)

    st.markdown("### 🔄 MQTT Flow")
    st.plotly_chart(mqtt_flow_diagram(protocol["title"], protocol), use_container_width=True)

    st.markdown("### 📜 Message Log")
    st.code(f"""
    [Sensor] Published → {vitals}
    [Broker] Delivered to AI Engine
    [AI Engine] Generated Protocol → {protocol['title']}
    [Broker] Published to {protocol['topic']}
    [Device] Actions Taken → {', '.join(protocol['actions'])}
    """)

    if protocol["critical"]:
        alarm_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
        st.markdown(f'<audio autoplay src="{alarm_url}" controls hidden></audio>', unsafe_allow_html=True)

    if st.checkbox("📧 Send Email Alert to Doctor"):
        send_email(protocol["title"], protocol["explanation"], "doctor_email@hospital.com")

    pdf = generate_pdf_report(case_id, vitals, protocol)
    st.download_button("📄 Download Case Report (PDF)", data=pdf,
                       file_name=f"{protocol['title'].replace(' ', '_')}.pdf", mime="application/pdf")

    log_data = pd.DataFrame([{"Patient": selected_patient, "Case": protocol["title"],
                              "Topic": protocol["topic"], "HR": vitals["HR"],
                              "SpO2": vitals["SpO2"], "Glucose": vitals["Glucose"],
                              "Movement": vitals["Movement"]}])
    csv_buf = io.StringIO()
    log_data.to_csv(csv_buf, index=False)
    st.download_button("📥 Download Session Log (CSV)", data=csv_buf.getvalue(),
                       file_name="icu_log.csv", mime="text/csv")

st.markdown("---")
st.caption("📡 Impunity Protocol Engine | Smart ICU Simulation | MQTT-Powered | Enhanced Graphical Features")

