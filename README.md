# ⚡ Smart Energy Consumption Tracker

A professional, full-stack **Streamlit** dashboard for appliance-level energy monitoring, analysis, and smart insights.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit) ![Plotly](https://img.shields.io/badge/Plotly-5.18+-blue?logo=plotly) ![Pandas](https://img.shields.io/badge/Pandas-2.0+-green?logo=pandas)

---

## 🚀 Features

| Category | Details |
|---|---|
| **Data Entry** | Daily / Weekly / Monthly modes with appliance-wise inputs |
| **Excel Support** | Upload `.xlsx` / `.csv` with auto-validation & cleaning |
| **Visualizations** | Line, Bar, Pie, Area, Stacked Area, Heatmap, Comparison charts |
| **Analysis** | Total/avg consumption, top appliance, trend detection, cost projection |
| **Smart Insights** | AI-style insights: trends, weekend vs weekday, baseline detection |
| **Alerts** | Spike detection with configurable threshold |
| **Recommendations** | Actionable energy-saving tips |
| **Export** | Download CSV or full Excel report |

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/smart-energy-tracker.git
cd smart-energy-tracker

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📂 Project Structure

```
smart-energy-tracker/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── sample_data.csv     # Sample dataset for reference
└── README.md
```

---

## 📊 Expected Excel Format

| Date | AC | Fan | Refrigerator | Washing Machine | Lights | Others | Total Units |
|---|---|---|---|---|---|---|---|
| 2024-01-01 | 4.5 | 1.2 | 1.5 | 0.8 | 0.6 | 0.3 | 8.9 |

---

## 🌐 Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the entry point
4. Click **Deploy** 🎉

---

## 🛠️ Tech Stack

- **Streamlit** — Web framework & UI
- **Pandas** — Data processing & aggregation
- **Plotly** — Interactive visualizations
- **NumPy** — Numerical computations
- **OpenPyXL** — Excel file handling

---

## 📄 License

MIT License — free to use for academic, personal, and commercial projects.
