# Data Cleaner

A straightforward Python tool to clean up messy CSV or Excel datasets — tailored for health and research data, but versatile enough for any tabular data.

This script tackles duplicates, missing values, inconsistent column names, and outliers to deliver analysis-ready data with a clear summary of what’s been done.

Built for researchers, analysts, and data enthusiasts who want clean data without the hassle.

---

## ✅ Features

- Removes **duplicate rows** to ensure data integrity
- Standardizes **column names** to `snake_case` (lowercase, underscores, no special characters)
- Handles **missing values** with flexible options:
  - Delete rows with missing data
  - Fill with zeros
  - Impute with **mean** (for numeric columns)
  - Impute with **mode** (for categorical columns)
  - Default to `"MISSING"` in other cases
- Detects and caps **outliers** in numeric columns using z-score (default threshold: `3`)
- Optimizes **column data types** for seamless use in analysis tools
- Exports cleaned data as a **UTF-8 encoded `.csv`** file
- Provides a **terminal cleaning summary**: duplicates removed, missing values handled, and more

---

## 🛠 Installation

### 1. Clone the repository:

```bash
git clone git clone https://github.com/404Health/universal-dataCleaner.git
cd universal-dataCleaner
```

### 2. Install the required packages:

```bash
pip install -r requirements.txt
```

**Requirements:**  
- `pandas`  
- `numpy`  
- `scipy`  
- `openpyxl`

---

## 🚀 Usage

1. Place your `.csv` or `.xlsx` file in the `sample_data/` folder.

2. Run the cleaner:

```bash
python cleaner.py
```

3. Follow the prompts:
   - Select a file from the listed options
   - Choose a missing data strategy: `delete`, `zero`, `mean`, or `mode`

4. The cleaned file will be saved in the `output/` folder as a `.csv`.

5. A full cleaning summary will be printed to your terminal.

---

## 📂 Project Structure

```
health-data-cleaner/
├── cleaner.py           # Main script for data cleaning
├── sample_data/         # Folder for input data
├── output/              # Folder for cleaned output
├── requirements.txt     # Python dependencies
└── README.md            # This documentation
```

---

## 🙌 Credits

Developed by **Abdullah Albowait** for **404Health**  
GitHub: [404Health](https://github.com/404Health)  
Have feedback or ideas? [Open an issue](https://github.com/404Health/health-data-cleaner/issues) or reach out!

---

## 📄 License

This project is licensed under the **MIT License**.  
Feel free to use, modify, and share. See the `LICENSE` file for full terms.
