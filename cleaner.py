import pandas as pd
import numpy as np
import os
from scipy import stats  

# This script cleans up messy health data to make it analysis-ready.

# Step 1: Load the data
def load_data(file_path):

    # Check if the file exists to avoid headaches
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Oops, couldn't find {file_path}! Check the path.")

    ext = os.path.splitext(file_path)[1].lower()

    # Support CSV and Excel for now
    if ext == '.csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Sorry, {ext} files aren't supported yet. Stick to CSV or Excel!")
    
    print(f"📥 Loaded {file_path} with {len(df)} rows and {len(df.columns)} columns.")
    return df

# Step 2: Clean the data 
def clean_data(df, fill_strategy="delete", outlier_threshold=3):
    report = {"steps_taken": []}  # Let's keep track of what we did

    # Remove duplicates
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    duplicates_removed = before - after
    report['steps_taken'].append(f"Removed {duplicates_removed} duplicate rows")

    # Clean up column names to make them analysis-friendly
    df.columns = [col.strip().lower().replace(" ", "_").replace("-", "_").replace("?", "") 
                  for col in df.columns]
    report['steps_taken'].append("Column names cleaned (lowercase, underscores, no special chars)")

    # Handle missing values based on user's choice
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

    # Handle outliers for numeric columns (using z-score)
    for col in df.select_dtypes(include=[np.number]).columns:
        z_scores = np.abs(stats.zscore(df[col].dropna()))
        outliers = z_scores > outlier_threshold
        if outliers.sum() > 0:
            df.loc[df[col].notnull() & (z_scores > outlier_threshold), col] = df[col].median()
            report['steps_taken'].append(f"Capped {outliers.sum()} outliers in {col} to median")

    # Ensure proper data types
    df = df.convert_dtypes()
    report['steps_taken'].append(f"Data types optimized: {df.dtypes.to_dict()}")

    return df, report

# Step 3: Save the cleaned data
def export_data(df, output_path="output/cleaned_data.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"💾 Saved cleaned data to {os.path.abspath(output_path)}")
    return output_path

if __name__ == "__main__":
    print(" Welcome to the Data Cleaner! ")
    print("Let's tidy up your data and make it analysis-ready!\n")

    # Step 1: Pick a file
    sample_folder = "sample_data"
    files = [f for f in os.listdir(sample_folder) if f.endswith((".csv", ".xls", ".xlsx"))]

    if not files:
        print("No data files found in sample_data/. Please add some CSVs or Excel files!")
        exit()

    print("Here's what we found:")
    for i, f in enumerate(files, start=1):
        print(f"  {i}. {f}")

    file_choice = input("\nPick a file by number: ")
    try:
        file_choice = int(file_choice)
        path = os.path.join(sample_folder, files[file_choice - 1])
    except:
        print("Invalid choice. Try running again and pick a valid number!")
        exit()

    # Step 2: Choose how to handle missing values
    strategies = ["delete", "zero", "mean", "mode"]
    print("\n🧩 How do you want to handle missing values?")
    for i, s in enumerate(strategies, start=1):
        print(f"  {i}. {s.capitalize()} (e.g., {s} missing values)")

    strat_choice = input("\nChoose an option (1–4): ")
    try:
        strat_choice = int(strat_choice)
        strategy = strategies[strat_choice - 1]
    except:
        print("Invalid choice. Going with 'delete' as a safe default.")
        strategy = "delete"

    # Step 3: Do the cleaning magic
    try:
        df = load_data(path)
        cleaned_df, summary = clean_data(df, fill_strategy=strategy)
        out_path = export_data(cleaned_df)

        print("\n🎉 All done! Your data is squeaky clean!")
        print(" Here's what we did:")
        for step in summary['steps_taken']:
            print(f"  • {step}")
    except Exception as e:
        print(f"Something went wrong: {e}")
        print("Check your file or settings and try again!")