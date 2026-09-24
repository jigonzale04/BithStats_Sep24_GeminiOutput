# Provisional Natality Analytics Dashboard (2025)

A modular, production-ready Streamlit application built for exploring 2025 CDC provisional birth counts across states, months, and infant sexes.

## Project Structure
```text
├── .streamlit/
│   └── config.toml
├── data/
│   └── Provisional_Natality_2025_CDC.csv
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── metrics.py
│   ├── components.py
│   └── visualizations.py
├── requirements.txt
├── app.py
└── README.md
```

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
streamlit run app.py
```
