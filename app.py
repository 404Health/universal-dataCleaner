import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import io

# Configure the Streamlit page
st.set_page_config(page_title="Universal Data Cleaner", layout="centered")

# --- Cleaner Logic ---
def clean_data(df, fill_strategy="delete", outlier_threshold=3):
    report = {"steps_taken": []}

    # Remove duplicates
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    duplicates_removed = before - after
    report['steps_taken'].append(f"Removed {duplicates_removed} duplicate rows")

    # Standardize column names
    df.columns = [col.strip().lower().replace(" ", "_").replace("-", "_").replace("?", "") 
                  for col in df.columns]
    report['steps_taken'].append("Column names cleaned (lowercase, underscores, no special chars)")

    # Handle missing values
    null_report = {}
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count == 0:
            continue

        if fill_strategy == "delete":
            df = df.dropna(subset=[col])
            null_report[col] = f"Deleted {missing_count} missing"
        elif fill_strategy == "zero":
            df[col] = df[col].fillna(0)
            null_report[col] = f"Filled {missing_count} missing with 0"
        elif fill_strategy == "mean" and np.issubdtype(df[col].dtype, np.number):
            mean_value = df[col].mean()
            df[col] = df[col].fillna(mean_value)
            null_report[col] = f"Filled {missing_count} missing with mean ({mean_value:.2f})"
        elif fill_strategy == "mode":
            mode_value = df[col].mode().iloc[0]
            df[col] = df[col].fillna(mode_value)
            null_report[col] = f"Filled {missing_count} missing with mode ({mode_value})"
        else:
            df[col] = df[col].fillna("MISSING")
            null_report[col] = f"Filled {missing_count} missing with 'MISSING'"

    report['steps_taken'].append(f"Missing values handled: {null_report}")

    # Handle outliers
    for col in df.select_dtypes(include=[np.number]).columns:
        z_scores = np.abs(stats.zscore(df[col].dropna()))
        outliers = z_scores > outlier_threshold
        if outliers.sum() > 0:
            df.loc[df[col].notnull() & outliers, col] = df[col].median()
            report['steps_taken'].append(f"Capped {outliers.sum()} outliers in {col} to median")

    # Optimize data types
    df = df.convert_dtypes()
    report['steps_taken'].append(f"Data types optimized: {df.dtypes.to_dict()}")

    return df, report

# --- Streamlit Interface ---
st.title("🧼 Universal Data Cleaner")
st.caption("Make your messy data analysis-ready — without code!")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

strategy = st.selectbox("Missing Value Strategy", ["delete", "zero", "mean", "mode"])

if uploaded_file and st.button("Clean Data"):
    try:
        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Clean data
        cleaned_df, report = clean_data(df, fill_strategy=strategy)

        st.success("✅ Cleaning complete!")

        st.write("### Summary:")
        for step in report['steps_taken']:
            st.markdown(f"- {step}")

        st.write("### Preview of Cleaned Data")
        st.dataframe(cleaned_df.head())

        # Prepare file for download
        buffer = io.BytesIO()
        cleaned_df.to_csv(buffer, index=False)
        buffer.seek(0)

        st.download_button(
            "⬇️ Download Cleaned File",
            buffer,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")
