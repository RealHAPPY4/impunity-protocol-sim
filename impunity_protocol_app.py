# impunity_protocol_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import csv
import io
from datetime import datetime
import paho.mqtt.client as mqtt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sendinblue import Client  # Brevo SDK
from dotenv import load_dotenv
import os

# ---------------- Load API Key ----------------
load_dotenv()
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

# ---------------- MQTT Setup ----------------
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "/icu/bed"

client = mqtt.Client("ICU_Simulator_Client")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC)
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()}")

client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT)
client.loop_start()

# ---------------- Helper Functions ----------------
def generate_vitals():
    return {
        "Heart Rate": random.randint(60, 140),
        "Oxygen": random.randint(85, 100),
        "Blood Pressure": f"{random.randint(80,120)}/{random.randint(50,90)}",
        "Glucose": random.randint(70, 200)
    }

def log_session(patient_name, vitals, case):
    filename = "icu_data.csv"
    fieldnames = ["Timestamp", "Patient", "Case", "Heart Rate", "Oxygen", "Blood Pressure", "Glucose"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"Timestamp": now, "Patient": patient_name, "Case": case, **vitals}
    try:
        with open(filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        st.error(f"Error logging session: {e}")

def generate_pdf(patient_name, vitals, case):
    filename = f"{patient_name}_case_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"ICU Case Report - {patient_name}", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Case: {case}", styles['Heading2']))
    story.append(Spacer(1, 12))

    for k, v in vitals.items():
        story.append(Paragraph(f"{k}: {v}", styles['Normal']))
        story.append(Spacer(1, 6))

    doc.build(story)
    return filename

# ---------------- Brevo Feedback ----------------
def send_feedback(name, email, message):
    try:
        client_api = Client(api_key=BREVO_API_KEY)
        data = {
            "sender": {"name": "ICU Simulator", "email": "no-reply@simulator.com"},
            "to": [{"email": "sapban92@gmail.com"}],
            "subject": f"Feedback from {name}",
            "textContent": f"Name: {name}\nEmail: {email}\nMessage: {message}"
        }
        response = client_api.smtp_send_transac_email(data)
        st.success("Feedback sent successfully!")
    except Exception as e:
        st.error(f"Failed to send feedback: {e}")

def log_feedback(name, email, message):
    filename = "feedback_log.csv"
    fieldnames = ["Timestamp", "Name", "Email", "Message"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"Timestamp": now, "Name": name, "Email": email, "Message": message}
    try:
        with open(filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        st.error(f"Error logging feedback: {e}")

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="ICU Emergency Simulator", layout="wide")
st.title("🧠 Impunity Protocol Engine – ICU Emergency Simulator")

# Sidebar for Feedback
st.sidebar.header("💬 Send Feedback")
with st.sidebar.form("feedback_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message")
    submitted = st.form_submit_button("Send Feedback")
    if submitted:
        if name and message:
            log_feedback(name, email, message)
            send_feedback(name, email, message)
        else:
            st.error("Please provide at least your name and message.")

# Main UI
st.header("🩺 ICU Case Simulation")
patient_name = st.text_input("Patient Name", "John Doe")
age = st.number_input("Age", min_value=0, max_value=120, value=30)
case = st.selectbox("Select ICU Case", [
    "Insulin deficiency",
    "Critical drug unavailability",
    "Awakening from coma",
    "Oxygen deficiency",
    "Cardiac arrest"
])

simulate = st.button("Simulate Case")

if simulate:
    vitals = generate_vitals()
    st.subheader("Generated Vitals")
    st.table(vitals)

    # Publish vitals to MQTT
    client.publish(TOPIC, str(vitals))
    st.info("Vitals published to MQTT broker.")

    # Log session
    log_session(patient_name, vitals, case)

    # Generate PDF report
    pdf_file = generate_pdf(patient_name, vitals, case)
    st.success(f"PDF Case Report Generated: {pdf_file}")
    with open(pdf_file, "rb") as f:
        st.download_button("Download PDF", f, file_name=pdf_file)

    # Simple Alert
    if vitals["Oxygen"] < 90 or vitals["Heart Rate"] > 120:
        st.audio("alert_sound.mp3")  # Make sure alert_sound.mp3 exists
        st.warning("Critical alert triggered! Check vitals.")

st.markdown("---")
st.caption("Made with ❤️ by Saptarshi Banerjee")
