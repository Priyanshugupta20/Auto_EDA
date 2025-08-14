#🚀 Automated Data Cleaning & EDA Pipeline
An all-in-one data preprocessing & exploratory data analysis tool — Upload your dataset, let the pipeline handle the cleaning, and get a ready-to-use EDA report in just a few clicks.

## File Stucture
```
data-cleaning-pipeline/
│
├── data/                         # Input data files (CSV, Excel, etc.)
│   └── sample.csv
│
├── outputs/                      # Final cleaned data, reports, and logs
│   ├── cleaned_data.csv
│   ├── eda_report.html
│   └── cleaning_log.json
│
├── frontend/                     # Optional frontend UI (if using)
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── src/                          # Core backend logic (your main focus)
│   ├── __init__.py
│   ├── main.py                   # Main entry point for the pipeline
│   ├── data_loader.py            # load_data
│   ├── data_types.py             # fix_data_types, identify_columns
│   ├── data_cleaning.py          # handle_missing_values, remove_duplicates, 
│   │                             # handle_outliers, normalize_text_columns
│   ├── feature_scaling.py        # scale_numerical_columns
│   ├── eda.py                    # summary stats, missing data plot, distributions
│   ├── reporting.py              # log_cleaning_report, save_cleaned_data
│
│   └── utils/                    # Helper functions and shared utilities
│       ├── __init__.py
│       ├── file_utils.py         # file extension, file reading, API fetch
│       ├── type_utils.py         # reusable data type checks
│       └── config.py             # constants and thresholds
│
├── README.md                     # Project overview, setup, usage
├── requirements.txt              # Python packages required
└── run.py                        # (Optional) wrapper to execute pipeline easily
```

##🧹 Automated Data Cleaning

- Handle missing values
- Remove duplicates
- Normalize text columns
- Scale numeric features
- Detect & treat outliers
- Auto-correct data types
- Identify numerical & categorical columns for EDA
- Save cleaned data to /cleaned_data/
- Logs & unit tests for reliability

## 📊 EDA & Visualization

- Generate summary statistics
Create correlation heatmaps
Plot distribution graphs
Export HTML report to /reports/eda_report.html

## 🖥 Backend API (Flask / FastAPI)

/upload → Upload dataset & trigger pipeline

/download → Get cleaned dataset

/eda → View HTML EDA report

Built-in error handling & logging

## 🎨 Frontend UI

File upload interface

EDA report preview & download link

Responsive design & loading indicators

## 📂 Tech Stack
- Component	Technology
- Backend:	Python, Flask / FastAPI
- Data:	Pandas, NumPy
- Viz:	Seaborn, Matplotlib
- Frontend:	HTML, CSS, JavaScript

## 📌 Scope & Limitations

Max file size: 20 MB
Supported formats: .csv, .xlsx, Dataset API

## ⚡ Quick Start
### 1️⃣ Clone repository
git clone https://github.com/yourusername/automated-cleaning-eda.git
cd automated-cleaning-eda

### 2️⃣ Install dependencies
pip install -r requirements.txt

### 3️⃣ Run backend
python app.py

### 4️⃣ Open frontend
Open index.html in your browser
