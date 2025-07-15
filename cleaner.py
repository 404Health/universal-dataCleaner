import pandas as pd
import numpy as np
import os
from scipy import stats
from tabulate import tabulate

def load_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Oops, couldn't find {file_path}! Check the path.")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Sorry, {ext} files aren't supported yet. Stick to CSV or Excel!")

    if df.empty:
        raise ValueError("The loaded file is empty!")

    print(f"📥 Loaded {file_path} with {len(df)} rows and {len(df.columns)} columns.")
    return df

def clean_data(df, fill_strategy="delete", outlier_threshold=3, apply_outliers=True, outlier_replacement="median"):
    report = {"steps_taken": [], "missing_values": {}}

    # Remove duplicates
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    report['steps_taken'].append(f"Removed {before - after} duplicate rows")

    # Standardize column names
    df.columns = [col.strip().lower().replace(" ", "_").replace("-", "_").replace("?", "") for col in df.columns]
    report['steps_taken'].append("Column names cleaned (lowercase, underscores, no special chars)")

    # Handle outliers before missing values
    if apply_outliers:
        for col in df.select_dtypes(include=[np.number]).columns:
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers = z_scores > outlier_threshold
            if outliers.sum() > 0:
                if outlier_replacement == "median":
                    replacement_value = df[col].median()
                elif outlier_replacement == "mean":
                    replacement_value = df[col].mean()
                else:  # Default to median
                    replacement_value = df[col].median()
                df.loc[df[col].notnull() & (z_scores > outlier_threshold), col] = replacement_value
                report['steps_taken'].append(f"Capped {outliers.sum()} outliers in {col} to {outlier_replacement} ({replacement_value:.2f})")

    # Handle missing values
    null_report = {}
    for col in df.columns:
        missing = df[col].isnull().sum()
        if missing == 0:
            continue

        if fill_strategy == "delete":
            df = df.dropna(subset=[col])
            null_report[col] = f"Deleted {missing} missing values"

        elif fill_strategy == "zero_missing":
            if np.issubdtype(df[col].dtype, np.number):
                df[col] = df[col].fillna(0)
                null_report[col] = f"Filled {missing} missing with 0"
            else:
                df[col] = df[col].fillna("MISSING")
                null_report[col] = f"Filled {missing} missing with 'MISSING'"

        elif fill_strategy == "mean_or_mode":
            if np.issubdtype(df[col].dtype, np.number):
                mean_val = df[col].mean()
                df[col] = df[col].fillna(mean_val)
                null_report[col] = f"Filled {missing} missing with mean ({mean_val:.2f})"
            else:
                mode_val = df[col].mode().iloc[0]
                df[col] = df[col].fillna(mode_val)
                null_report[col] = f"Filled {missing} missing with mode ({mode_val})"

        else:
            df[col] = df[col].fillna("MISSING")
            null_report[col] = f"Filled {missing} missing with 'MISSING'"

    report['missing_values'] = null_report
    report['steps_taken'].append(f"Missing values handled: {null_report}")

    df = df.convert_dtypes()
    report['steps_taken'].append(f"Data types optimized: {df.dtypes.to_dict()}")

    return df, report

def export_data(df, input_path, output_dir="output"):
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"cleaned_{base_name}.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"💾 Saved cleaned data to {os.path.abspath(output_path)}")
    return output_path

def generate_missing_values_chart(df, report):
    missing_counts = {col: df[col].isnull().sum() for col in df.columns}
    missing_counts = {k: v for k, v in missing_counts.items() if v > 0}
    if not missing_counts:
        return None

    labels = list(missing_counts.keys())
    values = list(missing_counts.values())

    chart_config = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Missing Values",
                "data": values,
                "backgroundColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0", "#9966FF"],
                "borderColor": ["#2E86C1", "#E74C3C", "#F1C40F", "#3EACAA", "#7D3C98"],
                "borderWidth": 1
            }]
        },
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "title": {"display": True, "text": "Number of Missing Values"}
                },
                "x": {
                    "title": {"display": True, "text": "Columns"}
                }
            },
            "plugins": {
                "legend": {"display": False},
                "title": {"display": True, "text": "Missing Values by Column"}
            }
        }
    }
    return chart_config

if __name__ == "__main__":
    print(" Welcome to the Data Cleaner! ")
    print("Let's tidy up your data and make it analysis-ready!\n")

    sample_folder = "sample_data"
    if not os.path.exists(sample_folder):
        print(f"Directory {sample_folder} does not exist! Please create it and add files.")
        exit()

    files = [f for f in os.listdir(sample_folder) if f.endswith((".csv", ".xls", ".xlsx"))]
    if not files:
        print("No data files found in sample_data/. Please add some CSVs or Excel files!")
        exit()

    for i, f in enumerate(files, start=1):
        print(f"  {i}. {f}")

    while True:
        try:
            file_choice = int(input("\nPick a file by number: "))
            if file_choice < 1 or file_choice > len(files):
                raise ValueError
            path = os.path.join(sample_folder, files[file_choice - 1])
            break
        except ValueError:
            print(f"Invalid choice. Please enter a number between 1 and {len(files)}")

    strategies = ["delete", "zero_missing", "mean_or_mode"]
    for i, s in enumerate(strategies, start=1):
        print(f"  {i}. {s}")

    while True:
        try:
            strat_choice = int(input("\nChoose missing value strategy (1–3): "))
            if strat_choice < 1 or strat_choice > len(strategies):
                raise ValueError
            strategy = strategies[strat_choice - 1]
            break
        except ValueError:
            print(f"Invalid choice. Please enter a number between 1 and {len(strategies)}")
            strategy = "delete"

    apply_outliers = input("Apply outlier treatment? (yes/no): ").strip().lower() == "yes"
    if apply_outliers:
        outlier_replacement = input("Replace outliers with (median/mean): ").strip().lower()
        if outlier_replacement not in ["median", "mean"]:
            outlier_replacement = "median"
        try:
            outlier_threshold = float(input("Enter z-score threshold for outliers (default 3): ") or 3)
        except ValueError:
            outlier_threshold = 3

    plot_chart = input("Generate a chart of missing values? (yes/no): ").strip().lower() == "yes"

try:
    df = load_data(path)
    cleaned_df, summary = clean_data(df, fill_strategy=strategy, apply_outliers=apply_outliers, 
                                    outlier_threshold=outlier_threshold, outlier_replacement=outlier_replacement)
    out_path = export_data(cleaned_df, path)

    print("\n🎉 Cleaning komplet!")
    headers = ["Step", "Description"]
    table_data = [[i + 1, step] for i, step in enumerate(summary['steps_taken'])]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    if plot_chart:
        chart = generate_missing_values_chart(df, summary)
        if chart:
            print("\n📊 Missing Values Chart:")
            print("```chartjs")  # Fixed syntax: separate opening backticks
            print(chart)
            print("```")  # Fixed syntax: closing backticks
        else:
            print("No missing values to plot.")
        
except Exception as e:
    print(f"❌ Error: {e}")