import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import io

# --- Caching functions for performance ---
@st.cache_data
def load_file(file):
    if file.size > 100 * 1024 * 1024:  # 100 MB limit
        raise ValueError("File size exceeds 100 MB limit.")
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format. Use CSV or Excel (.xlsx, .xls).")
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")

@st.cache_data
def run_cleaning(df, strategy, outlier_method, outlier_threshold, outlier_replacement, categorical_cols):
    return clean_data(df, fill_strategy=strategy, outlier_method=outlier_method,
                     outlier_threshold=outlier_threshold, outlier_replacement=outlier_replacement,
                     categorical_cols=categorical_cols)

# --- Core Data Cleaning Function ---
def clean_data(df, fill_strategy="delete", outlier_method="zscore", outlier_threshold=3, 
               outlier_replacement="median", categorical_cols=None):
    report = {"steps_taken": [], "missing_values": {}}
    categorical_cols = categorical_cols or []

    if df.empty:
        raise ValueError("The uploaded file is empty!")

    # Standardize diagnosis values
    diagnosis_map = {"hypertension": "Hypertension", "high BP": "Hypertension"}
    if "Diagnosis" in df.columns or "diagnosis" in df.columns:
        df["Diagnosis"] = df["Diagnosis"].replace(diagnosis_map) if "Diagnosis" in df.columns else df["diagnosis"].replace(diagnosis_map)
        report['steps_taken'].append("Standardized diagnosis values")

    # Remove duplicates
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    report['steps_taken'].append(f"Removed {before - after} duplicate rows")

    # Clean column names
    df.columns = [col.strip().lower().replace(" ", "_").replace("-", "_").replace("?", "")
                  for col in df.columns]
    report['steps_taken'].append("Column names cleaned (lowercase, underscores, no special chars)")

    # Outlier treatment
    for col in df.select_dtypes(include=[np.number]).columns:
        if outlier_method == "zscore":
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers = z_scores > outlier_threshold
            if outliers.sum() > 0:
                replacement_value = df[col].median() if outlier_replacement == "median" else df[col].mean()
                df.loc[df[col].notnull() & (z_scores > outlier_threshold), col] = replacement_value
                report['steps_taken'].append(f"Capped {outliers.sum()} outliers in {col} to {outlier_replacement} (Z-Score, {replacement_value:.2f})")
        elif outlier_method == "iqr":
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            outliers = (df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))
            if outliers.sum() > 0:
                replacement_value = df[col].median() if outlier_replacement == "median" else df[col].mean()
                df.loc[outliers, col] = replacement_value
                report['steps_taken'].append(f"Capped {outliers.sum()} outliers in {col} to {outlier_replacement} (IQR, {replacement_value:.2f})")

    # Missing value handling
    null_report = {}
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count == 0:
            continue

        if fill_strategy == "delete":
            df = df.dropna(subset=[col])
            null_report[col] = f"Deleted {missing_count} missing values"
        elif fill_strategy == "zero_missing":
            if np.issubdtype(df[col].dtype, np.number):
                df[col] = df[col].fillna(0)
                null_report[col] = f"Filled {missing_count} missing with 0"
            else:
                df[col] = df[col].fillna("MISSING")
                null_report[col] = f"Filled {missing_count} missing with 'MISSING'"
        elif fill_strategy == "mean_or_mode":
            if np.issubdtype(df[col].dtype, np.number):
                fill_value = df[col].median() if outlier_replacement == "median" else df[col].mean()
                df[col] = df[col].fillna(fill_value)
                null_report[col] = f"Filled {missing_count} missing with {outlier_replacement} ({fill_value:.2f})"
            else:
                modes = df[col].mode()
                mode_value = modes.iloc[0] if not modes.empty else "Unknown"
                df[col] = df[col].fillna(mode_value)
                null_report[col] = f"Filled {missing_count} missing with mode ({mode_value})"
        elif fill_strategy == "forward_fill":
            df[col] = df[col].fillna(method="ffill")
            null_report[col] = f"Forward-filled {missing_count} missing values"
        elif fill_strategy == "backward_fill":
            df[col] = df[col].fillna(method="bfill")
            null_report[col] = f"Backward-filled {missing_count} missing values"

        # Handle remaining missing values in categorical columns
        if col in categorical_cols and df[col].isnull().sum() > 0:
            remaining_missing = df[col].isnull().sum()
            df[col] = df[col].fillna("Unknown")
            null_report[col] = f"{null_report.get(col, '')}; Filled remaining {remaining_missing} missing with 'Unknown'"

    report['missing_values'] = null_report
    report['steps_taken'].append(f"Missing values handled: {null_report}")

    # Optimize data types
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")
    df = df.convert_dtypes()
    report['steps_taken'].append(f"Data types optimized: {df.dtypes.to_dict()}")

    return df, report

# --- Missing Value Plot ---
def plot_missing_values_bar(original_df, cleaned_df):
    missing_counts_original = original_df.isnull().sum()
    missing_counts_cleaned = cleaned_df.isnull().sum()
    
    if missing_counts_original.sum() == 0 and missing_counts_cleaned.sum() == 0:
        st.write("No missing values found in original or cleaned dataset.")
        return
    
    # Create Streamlit bar chart
    data = pd.DataFrame({
        "Original": missing_counts_original[missing_counts_original > 0],
        "Cleaned": missing_counts_cleaned[missing_counts_cleaned > 0]
    }).fillna(0)
    
    if not data.empty:
        st.write("### Missing Values Comparison")
        st.bar_chart(data)
    else:
        st.write("No missing values to display in selected columns.")

# --- Streamlit UI ---
st.title("🧼 Universal Data Cleaner")
st.caption("Make your messy data analysis-ready — without code!")

with st.sidebar:
    strategy_label = st.selectbox("Missing Value Strategy", 
                                 ["Delete", "Zero / 'MISSING'", "Mean / Mode", "Forward Fill", "Backward Fill"])
    apply_outliers = st.checkbox("Apply outlier treatment", value=True)
    if apply_outliers:
        outlier_method = st.selectbox("Outlier Detection Method", ["Z-Score", "IQR"])
        outlier_replacement = st.selectbox("Replace outliers with", ["Median", "Mean"])
        outlier_threshold = st.number_input("Outlier threshold (Z-Score or IQR multiplier)", 
                                          min_value=1.0, value=3.0, step=0.5)
    else:
        outlier_method = "zscore"
        outlier_replacement = "median"
        outlier_threshold = 3.0
    categorical_cols = st.multiselect("Select categorical columns", [], key="cat_cols")
    plot_chart = st.checkbox("Generate missing values chart")

strategy_map = {
    "Delete": "delete",
    "Zero / 'MISSING'": "zero_missing",
    "Mean / Mode": "mean_or_mode",
    "Forward Fill": "forward_fill",
    "Backward Fill": "backward_fill"
}
strategy = strategy_map[strategy_label].lower()
outlier_method = "iqr" if outlier_method == "IQR" else "zscore"
outlier_replacement = outlier_replacement.lower()

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file and st.button("Clean Data"):
    try:
        with st.spinner("Loading and cleaning data..."):
            df = load_file(uploaded_file)
            st.write(f"📅 Loaded **{uploaded_file.name}** with **{len(df)} rows** and **{len(df.columns)} columns**.")
            
            # Update categorical columns options after file upload
            st.sidebar.multiselect("Select categorical columns", df.columns, 
                                  default=[col for col in df.columns if df[col].dtype == "object"],
                                  key="cat_cols")
            categorical_cols = st.session_state.cat_cols

            cleaned_df, report = run_cleaning(df, strategy, outlier_method, outlier_threshold, 
                                           outlier_replacement, categorical_cols)
        
        st.success("✅ Cleaning complete!")

        st.write("### Cleaning Summary")
        st.table(pd.DataFrame([[i + 1, step] for i, step in enumerate(report['steps_taken'])], 
                             columns=["Step", "Description"]))

        if report['missing_values']:
            st.write("### Missing Value Handling Details")
            st.table(pd.DataFrame(report['missing_values'].items(), columns=["Column", "Action"]))

        base_name = uploaded_file.name.rsplit(".", 1)[0]
        csv_buffer = io.BytesIO()
        cleaned_df.to_csv(csv_buffer, index=False)
        st.download_button("⬇️ Download CSV", data=csv_buffer.getvalue(), 
                         file_name=f"cleaned_{base_name}.csv", mime="text/csv")

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            cleaned_df.to_excel(writer, index=False, sheet_name='CleanedData')
        st.download_button("⬇️ Download Excel", data=excel_buffer.getvalue(), 
                         file_name=f"cleaned_{base_name}.xlsx", 
                         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.write("### Preview of Cleaned Data")
        st.dataframe(cleaned_df)

        if plot_chart:
            with st.spinner("Generating missing values chart..."):
                plot_missing_values_bar(df, cleaned_df)

    except Exception as e:
        st.error(f"❌ Error: {e}")