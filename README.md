# 🚀 Automated Data Cleaning & EDA Pipeline
An all-in-one data preprocessing & exploratory data analysis tool — Upload your dataset, let the pipeline handle the cleaning, and get a ready-to-use EDA report in just a few clicks.

## File Stucture
```
data-cleaning-pipeline/
│
├── frontend/                     # Web interface (HTML, CSS, JS)
│   ├── templates/                     # Input data files
│   │   └── index.html
│   ├── static/
│   │   └── style.css
│   │   └── script.js
│
├── backend/                      # All backend logic and Python code
│   ├── upload/                     # Input data files
│   │   └── test_dataset.csv
│
│   ├── outputs/                  # Cleaned data, reports, and logs
│   │   ├── cleaned_data.csv
│   │   ├── eda_report.html
│
│   ├── src/                      # Core backend logic
│   │   ├── main.py                   # Runs the full pipeline
│   │   ├── data_loader.py            # load_data
│   │   ├── data_types.py             # fix_data_types, identify_columns
│   │   ├── data_cleaning.py          # handle_missing_values, remove_duplicates, handle_outliers, normalize_text_columns
│   │   ├── feature_scaling.py        # scale_numerical_columns
│   │   ├── reporting.py              # log_cleaning_report, save_cleaned_data
│   │   ├── eda/                      # Shared helpers
│   │       └── config.py             # summary stats, plots, missing value analysis
│   │   └── utils/                    # Shared helpers
│   │       └── config.py             # Constants and thresholds
│
│   ├── requirements.txt              # Python dependencies
│
├── README.md                         # Project documentation
```

## 🧹 Automated Data Cleaning

- Auto-correct data types
- Identify numerical & categorical columns for EDA
- Normalize text columns
- Handle missing values
- Remove duplicates
- Scale numeric features
- Detect & treat outliers
- Save cleaned data to /cleaned_data/
- Logs & unit tests for reliability

## 📊 EDA & Visualization

- Generate summary statistics
- Create correlation heatmaps
- Plot distribution graphs
- Export HTML report to /reports/eda_report.html

## 🖥 Backend API (Flask / FastAPI)

- /upload → Upload dataset & trigger pipeline
- /outputs → Get cleaned dataset
- /eda → View HTML EDA report
- Built-in error handling & logging

## 🎨 Frontend UI
- File upload interface
- EDA report preview & download link
- Responsive design & loading indicators

## 📂 Tech Stack
- Component	Technology
- Backend:	Python, Flask
- Data:	Pandas, NumPy
- Viz:	Seaborn, Matplotlib
- Frontend:	HTML, CSS, JavaScript

## 📌 Scope & Limitations
- Max file size: 20 MB
- Supported formats: .csv, .xlsx, .xls

## ⚡ Quick Start
### 1. Clone repository
```bash
git clone https://github.com/Priyanshugupta20/Auto_EDA.git
cd Auto_EDA
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run backend/src/main.py
```bash
cd backend/src
python main.py
```

### 4. Open frontend
Open index.html in your browser

