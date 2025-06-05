import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="ICU Emergency Simulator", layout="wide")

# ---------------- Sidebar ---------------- #
st.sidebar.title("👤 Patient Profile")
patient = {
    "ID": "PATIENT_05",
    "Age": 67,
    "Diabetic": True,
    "Allergies": ["Penicillin"],
    "History": "Coma (3 days)"
}
for k, v in patient.items():
    st.sidebar.markdown(f"**{k}:** {v if not isinstance(v, list) else ', '.join(v)}")
st.sidebar.markdown("---")
st.sidebar.markdown("🔘 Simulate an emergency case:")

# ---------------- Vitals Simulation ---------------- #
def simulate_vitals(case_id):
    return {
        1: {"HR": 82, "SpO2": 96, "Glucose": 61, "Movement": False},  # Insulin Deficiency
        2: {"HR": 38, "SpO2": 80, "Glucose": 112, "Movement": False}, # Drug Not Available
        3: {"HR": 75, "SpO2": 92, "Glucose": 105, "Movement": True},  # Awakening
        4: {"HR": 85, "SpO2": 85, "Glucose": 108, "Movement": False}, # Oxygen Deficiency
        5: {"HR": 28, "SpO2": 76, "Glucose": 114, "Movement": False}, # Cardiac Arrest
    }.get(case_id, {})

# ---------------- Protocol Engine ---------------- #
def generate_case_protocol(case_id, vitals):
    protocols = {
        1: {
            "title": "CASE 1: Insulin Deficiency",
            "explanation": "Low glucose detected in diabetic patient. Emergency insulin protocol initiated.",
            "topic": "/ICU/devices/patient_05/inject_insulin",
            "actions": ["💉 Inject 6 units insulin", "📝 Update EHR", "📡 Notify ICU staff"],
        },
        2: {
            "title": "CASE 2: Drug Not Available",
            "explanation": "Critical cardiac condition. Required drug not available locally. Remote dispatch triggered.",
            "topic": "/ICU/med_alert/adrenaline_request",
            "actions": ["📶 Broadcast MQTT request", "🚁 Drone dispatched from Hospital_B", "📲 ICU notified"],
        },
        3: {
            "title": "CASE 3: Patient Awakens",
            "explanation": "Movement detected in previously comatose patient. Awakening protocol initiated.",
            "topic": "/ICU/alerts/patient_awake",
            "actions": ["📈 Motion match confirmed", "👨‍⚕️ Alert neuro team", "📋 Start assessment"],
        },
        4: {
            "title": "CASE 4: Oxygen Deficiency",
            "explanation": "Low SpO₂ detected. Auto-triggered oxygen valve activation.",
            "topic": "/ICU/devices/oxygen_supply/start",
            "actions": ["🫁 Oxygen supply initiated", "🔔 ICU staff alerted", "📡 Status logged"],
        },
        5: {
            "title": "CASE 5: Cardiac Arrest",
            "explanation": "Cardiac arrest detected. Full Code Blue protocol triggered.",
            "topic": "/ICU/alerts/code_blue",
            "actions": ["🚨 Code Blue alert", "🧬 Cardiac protocol activated", "📞 Team paged"],
        }
    }
    protocol = protocols.get(case_id)
    protocol["critical"] = True
    return protocol

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
    fig.update_layout(template="plotly_white", height=400)
    return fig

# ---------------- PDF Export ---------------- #
def generate_pdf_report(case_id, vitals, protocol):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("🧠 ICU Emergency Report", styles['Title']), Spacer(1, 12)]

    elements += [
        Paragraph(f"<b>Patient ID:</b> {patient['ID']} &nbsp;&nbsp; <b>Age:</b> {patient['Age']}", styles['Normal']),
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

    elements.append(Paragraph(
        "<b>MQTT Explanation:</b><br/>MQTT enables publish-subscribe communication between medical sensors and devices. "
        "The AI engine listens to vitals, detects emergencies, and publishes dynamic emergency topics to which medical IoT devices respond autonomously.",
        styles['BodyText']
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer

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
    for action in protocol["actions"]:
        st.markdown(f"- {action}")

    st.markdown("### 📈 Vitals Chart")
    st.plotly_chart(plot_vitals(vitals), use_container_width=True)

    # 🔊 Auto-play audio if critical
    if protocol["critical"]:
        alarm_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
        st.markdown(f'<audio autoplay src="{alarm_url}" controls hidden></audio>', unsafe_allow_html=True)

    # 📄 PDF Export
    pdf = generate_pdf_report(case_id, vitals, protocol)
    st.download_button("📄 Download Case Report (PDF)", data=pdf,
                       file_name=f"{protocol['title'].replace(' ', '_')}.pdf", mime="application/pdf")

st.markdown("---")
st.caption("📡 Impunity Protocol Engine | Smart ICU Simulation | MQTT-Powered")
