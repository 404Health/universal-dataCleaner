# 🧼 Universal Data Cleaner

A straightforward Streamlit app to clean up messy CSV or Excel datasets — tailored for health and research data, but versatile enough for any tabular data.

This app tackles duplicates, missing values, and inconsistent column names to deliver analysis-ready data with a clear summary of what’s been done.

Built for researchers, analysts, and data enthusiasts who want clean data without the hassle — now with a web interface!

---

## ✅ Features

- Removes **duplicate rows** to ensure data integrity
- Standardizes **column names** to `snake_case` (lowercase, underscores, no special characters)
- Handles **missing values** with flexible options:
  - Delete rows with missing data
  - Fill with zeros
  - Impute with **mean** (for numeric columns)
  - Impute with **mode** (for categorical columns)
  - Fallback to `"MISSING"` for others
- Optimizes **column data types** for seamless use in analysis tools
- Offers **CSV download** of cleaned data
- Provides a **cleaning summary** on screen

---

## 🛠 Installation

### 1. Clone the repository

```bash
git clone https://github.com/404Health/universal-dataCleaner.git
cd universal-dataCleaner
```

**Requirements:**  
streamlit
pandas
numpy
scipy
openpyxl
tabulate
XlsxWriter

---

## 🚀 Usage

1. Run locally:

```bash
streamlit run app.py
```
2. Then:
Upload a .csv or .xlsx file

Choose how you want to handle missing values

Preview the cleaned data

Download the cleane

## 📂 Project Structure

```
universal-dataCleaner/
├── app.py              # Streamlit app
├── requirements.txt    # Python dependencies
└── README.md           # You're reading this!
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
