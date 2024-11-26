# Location Tracking Application

A Streamlit-based application for visualizing location tracking data with interactive map and time-based filtering.

## Features

- Interactive map visualization
- Hour-based data filtering
- Multiple hour selection
- Route visualization with color coding
- Data export functionality

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Data Format

The application expects a CSV file with the following columns:
- timestamp
- latitude
- longitude
- zip_file
