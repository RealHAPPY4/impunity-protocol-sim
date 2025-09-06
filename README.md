# 🧠 Impunity Protocol Engine – ICU Emergency Simulator

This is a **Streamlit-based ICU Emergency Simulator** that mimics real-time ICU scenarios using MQTT-style autonomous protocol handling. It integrates a **Brevo (Sendinblue) feedback system** to collect user feedback without needing any email credentials.  

---

## 🚀 Features

- Simulates **5 ICU emergency cases**:
  - Insulin deficiency in diabetic patients
  - Critical drug unavailability
  - Awakening from coma
  - Oxygen deficiency
  - Cardiac arrest
- Publishes and subscribes ICU vitals over **MQTT broker**
- Triggers **automated actions** based on patient vitals
- Displays **protocol reasoning** and actions taken
- Plays **audio alert** for critical conditions
- Generates **downloadable PDF case reports**
- Logs **session and feedback data** to CSV
- Feedback sent directly via **Brevo API**  

---

## 🛠 Installation (Local)

1. **Clone the repository**

```bash
git clone https://github.com/RealHAPPY4/impunity-protocol-sim.git
cd impunity-protocol-sim
pip install -r requirements.txt
