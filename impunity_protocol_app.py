import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Page config
st.set_page_config(page_title="ICU Emergency Simulator", layout="wide")

# -------------------
# Sidebar - Patient Info
# -------------------
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

# -------------------
# Simulate Vitals
# -------------------
def simulate_vitals(case_id):
    if case_id == 1:
        return {"HR": 82, "SpO2": 96, "Glucose": 61, "Movement": False}
    elif case_id == 2:
        return {"HR": 38, "SpO2": 80, "Glucose": 112, "Movement": False}
    elif case_id == 3:
        return {"HR": 75, "SpO2": 92, "Glucose": 105, "Movement": True}
    else:
        return {}

# -------------------
# Protocol Decision Logic
# -------------------
def generate_case_protocol(case_id, vitals):
    if case_id == 1:
        return {
            "title": "CASE 1: Insulin Deficiency",
            "explanation": "Detected low glucose in diabetic patient. Emergency insulin protocol triggered.",
            "topic": "/ICU/devices/patient_05/inject_insulin",
            "actions": [
                "💉 Auto-injection: 6 units insulin",
                "📝 EHR updated",
                "📡 Notified remote ICU monitor"
            ],
            "critical": True
        }
    elif case_id == 2:
        return {
            "title": "CASE 2: Drug Not Available",
            "explanation": "Low HR & SpO₂ detected. Required drug unavailable. Request sent to nearby hospitals.",
            "topic": "/ICU/med_alert/adrenaline_request",
            "actions": [
                "❗ Adrenaline unavailable locally",
                "📶 MQTT broadcast to network",
                "🚁 Drone dispatched from Hospital_B",
                "📲 ICU updated with ETA"
            ],
            "critical": True
        }
    elif case_id == 3:
        return {
            "title": "CASE 3: Patient Awakens",
            "explanation": "Detected movement from unconscious patient. Awakening protocol started.",
            "topic": "/ICU/alerts/patient_awake",
            "actions": [
                "📈 Movement matched awakening pattern",
                "📬 Alert sent to ICU team",
                "🧠 Neurological eval initiated"
            ],
            "critical": True
        }
    else:
        return {
            "title": "Monitoring Mode",
            "explanation": "All vitals normal. No intervention required.",
            "topic": "/ICU/monitoring/passive",
            "actions": ["🟢 Passive monitoring", "📊 No emergency triggered"],
            "critical": False
        }

# -------------------
# Graph of Vitals
# -------------------
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

# -------------------
# Generate PDF Report
# -------------------
def generate_pdf_report(case_id, vitals, protocol):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("🧠 ICU Emergency Report", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Patient ID:</b> {patient['ID']} &nbsp;&nbsp;&nbsp;&nbsp; <b>Age:</b> {patient['Age']}", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Case:</b> {protocol['title']}", styles['Heading3']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(protocol['explanation'], styles['BodyText']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>MQTT Topic Triggered:</b> {protocol['topic']}", styles['BodyText']))
    elements.append(Spacer(1, 12))

    vitals_data = [
        ["Heart Rate", "SpO₂", "Glucose", "Movement"],
        [f"{vitals['HR']} bpm", f"{vitals['SpO2']}%", f"{vitals['Glucose']} mg/dL", "Yes" if vitals['Movement'] else "No"]
    ]
    table = Table(vitals_data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d0e0f0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("<b>Actions Taken:</b>", styles['Heading4']))
    for action in protocol["actions"]:
        elements.append(Paragraph(f"• {action}", styles['Normal']))
    elements.append(Spacer(1, 18))

    explanation = (
        "<b>How MQTT Broker Works:</b><br/>"
        "MQTT is a lightweight publish-subscribe protocol for IoT. "
        "Sensors publish vitals to topics. The protocol engine subscribes to these, analyzes the data, and publishes emergency commands to other topics. "
        "Subscribed IoT devices (e.g., injectors or drones) act in real time — enabling autonomous critical care."
    )
    elements.append(Paragraph(explanation, styles['BodyText']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -------------------
# Case Selection Buttons
# -------------------
col1, col2, col3 = st.columns(3)
selected_case = 0
if col1.button("🩺 Case 1: Insulin Deficiency"):
    selected_case = 1
elif col2.button("💊 Case 2: Drug Unavailable"):
    selected_case = 2
elif col3.button("🧠 Case 3: Patient Awakens"):
    selected_case = 3

# -------------------
# Display Simulation
# -------------------
if selected_case > 0:
    vitals = simulate_vitals(selected_case)
    protocol = generate_case_protocol(selected_case, vitals)

    st.header(protocol["title"])
    st.success(protocol["explanation"])
    st.markdown(f"**📡 MQTT Topic:** `{protocol['topic']}`")

    st.markdown("### ✅ Actions Taken")
    for action in protocol["actions"]:
        st.markdown(f"- {action}")

    st.markdown("### 📈 Vitals Over Time")
    st.plotly_chart(plot_vitals(vitals), use_container_width=True)

    # Play sound if critical
    if protocol["critical"]:
        st.audio("https://assets.mixkit.co/sfx/preview/mixkit-classic-alarm-995.mp3")

    # 📄 Download PDF
    pdf_buffer = generate_pdf_report(selected_case, vitals, protocol)
    st.download_button("📄 Download Report (PDF)", data=pdf_buffer,
                       file_name=f"{protocol['title'].replace(' ', '_')}.pdf", mime="application/pdf")

st.markdown("---")
st.caption("💡 Impunity Protocol Engine | Smart ICU Simulation | MQTT Powered")
