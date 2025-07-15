import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import io
import os

# Step 1: Load the data
def load_data(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(uploaded_file)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return df

# Step 2: Clean the data
def clean_data(df, fill_strategy="delete"):
    report = {"steps_taken": []}

    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    report['steps_taken'].append(f"Removed {before - after} duplicate rows")

    df.columns = [col.strip().lower().replace(" ", "_").replace("-", "_").replace("?", "")
                  for col in df.columns]
    report['steps_taken'].append("Column names cleaned")

    null_report = {}
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count == 0:
            continue

        if fill_strategy == "delete":
            df = df.dropna(subset=[col])
            null_report[col] = f"Deleted {missing_count} missing values"
        elif fill_strategy == "zero":
            df[col] = df[col].fillna(0)
            null_report[col] = f"Filled {missing_count} missing values with 0"
        elif fill_strategy == "mean" and np.issubdtype(df[col].dtype, np.number):
            mean_value = df[col].mean()
            df[col] = df[col].fillna(mean_value)
            null_report[col] = f"Filled {missing_count} missing values with mean ({mean_value:.2f})"
        elif fill_strategy == "mode":
            mode_value = df[col].mode().iloc[0]
            df[col] = df[col].fillna(mode_value)
            null_report[col] = f"Filled {missing_count} missing values with mode ({mode_value})"
        else:
            df[col] = df[col].fillna("MISSING")
            null_report[col] = f"Filled {missing_count} missing values with 'MISSING'"

    report['steps_taken'].append(f"Missing values handled: {null_report}")

    df = df.convert_dtypes()
    report['steps_taken'].append(f"Data types optimized")

    return df, report

# Streamlit UI
st.title("🧼 Simple Data Cleaner App")
st.caption("Upload your health dataset and clean it up in seconds!")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xls", "xlsx"])
strategy = st.selectbox("Missing value strategy", ["delete", "zero", "mean", "mode"])

if uploaded_file and st.button("Clean Data"):
    try:
        df = load_data(uploaded_file)
        cleaned_df, summary = clean_data(df, fill_strategy=strategy)

        st.success("✅ Data cleaned successfully!")
        st.write("### Cleaning Summary")
        st.table(pd.DataFrame(summary['steps_taken'], columns=["Step Description"]))

        st.write("### Preview of Cleaned Data")
        st.dataframe(cleaned_df.head())

        output = io.BytesIO()
        cleaned_df.to_csv(output, index=False)
        st.download_button("⬇️ Download Cleaned CSV", data=output.getvalue(), file_name="cleaned_data.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Error: {e}")
