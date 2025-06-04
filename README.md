# 🧠 Impunity Protocol Engine – ICU Emergency Simulator

This Streamlit app simulates real-time ICU scenarios using MQTT-style autonomous protocol handling.

## 🚀 Features
- Simulates 3 ICU emergencies (insulin deficiency, drug unavailable, awakening from coma)
- Triggers MQTT-style responses based on vitals
- Displays actions taken + reasoning
- Plays sound alert on critical conditions
- Downloadable case report

## 📦 Install (For Local)
```bash
pip install -r requirements.txt
streamlit run impunity_protocol_streamlit.py
