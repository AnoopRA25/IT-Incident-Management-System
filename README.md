# 🛠️ IT Incident Management System

A web-based IT Service Management application for tracking, prioritizing, monitoring, and resolving IT incidents.

## 📌 Features

- Create and track IT incidents
- Automatically generate Incident IDs
- Priority calculation using Impact and Urgency
- SLA deadline calculation
- Incident status tracking
- Filter incidents by status and priority
- Root Cause Analysis
- Resolution management
- Dashboard with incident statistics
- SQLite database integration

## 🏗️ Project Architecture

```text
User
  ↓
Streamlit Web Application
  ↓
Priority & SLA Logic
  ↓
SQLite Database
🔄 Incident Workflow
Create Incident
      ↓
Impact + Urgency
      ↓
Priority Calculation
      ↓
SLA Deadline Generation
      ↓
Incident Tracking
      ↓
Investigation
      ↓
Root Cause Analysis
      ↓
Resolution
      ↓
Resolved
🛠️ Technologies Used
Python
Streamlit
SQLite
Pandas
Git & GitHub
📂 Project Structure
IT-Incident-Management-System/
│
├── app.py
├── database.py
├── utils.py
├── requirements.txt
├── README.md
└── .gitignore
🚀 Installation

Clone the repository:

git clone https://github.com/AnoopRA25/IT-Incident-Management-System.git

Go to the project folder:

cd IT-Incident-Management-System

Create a virtual environment:

python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py
📊 Priority Matrix
Impact	Urgency	Priority
High	High	Critical
High	Medium	High
High	Low	Medium
Medium	High	High
Medium	Medium	Medium
Medium	Low	Low
Low	High	Medium
Low	Medium	Low
Low	Low	Low
⏱️ SLA Rules
Priority	SLA Time
Critical	1 Hour
High	4 Hours
Medium	8 Hours
Low	24 Hours
🔮 Future Improvements
User authentication
Role-based access control
Email notifications
Advanced analytics
Real-time monitoring
Cloud database integration
Automated incident alerts
👨‍💻 Author

Anoop R A