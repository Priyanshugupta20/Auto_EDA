import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import uuid
from ydata_profiling import ProfileReport
from pathlib import Path
from datetime import datetime
from utils.config import OUTPUT_FOLDER

# =========================================
#  3. Data Overview
# =========================================

def data_overview(df):
    try:
        overview = {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicates": int(df.duplicated().sum()),
            "memory_usage": df.memory_usage(deep=True).to_dict(),
        }

        return overview

    except Exception as e:
        logging.exception(f"Failed to generate data overview or EDA report: {e}")
        raise


# =========================================
#  4. Univariate Analysis
# =========================================

def univariate_analysis(df, num_cols, cat_cols, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "histograms": [],
        "countplots": []
    }

    try:
        # Histograms for numerical columns
        hist_path = output_dir / f"histogram_{uuid.uuid4().hex}.png"
        df[num_cols].hist(figsize=(15, 10), bins=20)
        plt.title("Histograms for numerical columns")
        plt.tight_layout()
        plt.savefig(hist_path)
        plt.close()
        result['histograms'].append(hist_path.name)
    except Exception as e:
        logging.error(f"Failed to create histogram: {e}")

    # Countplots for categorical columns
    for col in cat_cols:
        try:
            countplot_path = output_dir / f"countplot_{col}_{uuid.uuid4().hex}.png"
            plt.figure(figsize=(8, 4))
            sns.countplot(x=df[col], order=df[col].value_counts().index)
            plt.xticks(rotation=45)
            plt.title(f"Count Plot of {col}")
            plt.tight_layout()
            plt.savefig(countplot_path)
            plt.close()
            result['countplots'].append(countplot_path.name)
        except Exception as e:
            logging.error(f"Failed to create countplot for {col}: {e}")

    return result


def bivariate_analysis(df, num_cols, cat_cols, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "correlation_matrix": None,
        "correlation_heatmap": None,
        "pairplot": None,
        "boxplots": []
    }

    # Correlation heatmap
    if len(num_cols) > 1:
        try:
            corr_matrix = df[num_cols].corr().round(2).to_dict()
            result["correlation_matrix"] = corr_matrix

            heatmap_path = output_dir / f"correlation_heatmap_{uuid.uuid4().hex}.png"
            plt.figure(figsize=(10, 6))
            sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm")
            plt.title("Correlation Matrix")
            plt.tight_layout()
            plt.savefig(heatmap_path)
            plt.close()
            result["correlation_heatmap"] = heatmap_path.name
        except Exception as e:
            logging.error(f"Failed to create correlation heatmap: {e}")

    # Pairplot
    if df.shape[0] <= 1000 and len(num_cols) <= 5:
        try:
            pairplot_path = output_dir / f"pairplot_{uuid.uuid4().hex}.png"
            sns.pairplot(df[num_cols])
            plt.tight_layout()
            plt.savefig(pairplot_path)
            plt.close()
            result["pairplot"] = pairplot_path.name
        except Exception as e:
            logging.error(f"Failed to create pairplot: {e}")

    # Boxplots (numerical vs categorical)
    for num_col in num_cols:
        for cat_col in cat_cols:
            try:
                boxplot_path = output_dir / f"boxplot_{num_col}_vs_{cat_col}_{uuid.uuid4().hex}.png"
                plt.figure(figsize=(8, 4))
                sns.boxplot(x=df[cat_col], y=df[num_col])
                plt.xticks(rotation=45)
                plt.title(f"{num_col} vs {cat_col}")
                plt.tight_layout()
                plt.savefig(boxplot_path)
                plt.close()
                result["boxplots"].append(boxplot_path.name)
            except Exception as e:
                logging.error(f"Failed to create boxplot for {num_col} vs {cat_col}: {e}")

    return result


# =========================================
#  6. Data Quality Warnings
# =========================================

def data_quality_warnings(df, num_cols, cat_cols):
    warnings = {
        "high_cardinality": [],
        "skewed_columns": {},
        "too_many_missing": [],
        "low_variance": []
    }

    try:
        # High cardinality
        warnings["high_cardinality"] = [col for col in cat_cols if df[col].nunique() > 50]

        # Skewed numerical columns
        skewed = df[num_cols].skew()
        warnings["skewed_columns"] = skewed[abs(skewed) > 1].round(2).to_dict()

        # Too many missing values (>40%)
        warnings["too_many_missing"] = [col for col in df.columns if df[col].isnull().mean() > 0.4]

        # Low variance
        warnings["low_variance"] = [col for col in df.columns if df[col].nunique() <= 1]

    except Exception as e:
        logging.error(f"Error in data quality checks: {e}")

    return warnings



# =========================================
#  8. Generate HTML Report
# =========================================
def generate_report(df):
    report_filename = f'eda_report.html'
    report_path = OUTPUT_FOLDER / report_filename
    profile = ProfileReport(df, title=f"EDA Report", explorative=True)
    profile.to_file(str(report_path))
    logging.info(f"EDA Report generated - {report_filename}")
    return report_filename
