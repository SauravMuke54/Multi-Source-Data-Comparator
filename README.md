# 🔍 Multi-Source Table Data Comparator

This is a Streamlit-based application to visually compare tabular data from **two different sources** — including CSV files and SQL databases such as PostgreSQL, MySQL, and Oracle.

It offers column mapping, exclusion rules, formula transformations, row-level diffing, and import/export of the entire configuration.

---

## 🚀 Features

* ✅ Supports CSV, PostgreSQL, MySQL, Oracle
* 📑 Upload CSV files or connect to databases with credentials and custom SQL
* 🔀 Column mapping between sources (e.g., `id` in Source 1 = `user_id` in Source 2)
* 🔑 Define key column(s) for alignment and indexing
* 🔍 Preview data, schema, and mapping interactively
* ❌ Exclude specific columns from comparison
* 🧪 Apply transformation formulas to any column before comparison
* ⚖️ Row-by-row difference detection with highlight
* 🔄 Detect rows missing in one or the other source
* 📤 Export the full configuration as a reusable JSON settings file
* 📥 Reload settings from a saved JSON to resume or automate testing

---

## 📂 Example Use Cases

* Compare raw source CSVs against processed database results
* Validate database migrations (PostgreSQL to MySQL, etc.)
* Reconcile nightly reports
* Check if ETL transformations preserved integrity

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt` should include:

```
streamlit
pandas
sqlalchemy
psycopg2-binary
pymysql
cx_Oracle
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

> Replace `app.py` with your actual file name if different.

---

## 🧪 Column Formula Syntax

You may use valid Python expressions like:

* `value.strip().lower()` – clean & normalize strings
* `float(value) if value else 0` – convert values safely
* `round(float(value), 2)` – rounding

All formulas are applied to both datasets before diffing.

---

## ⚙️ JSON Settings Format

You can export and import full configurations via JSON:

```json
{
  "source1_type": "CSV",
  "source2_type": "PostgreSQL",
  "key_columns": "id",
  "excluded_columns": ["last_updated"],
  "column_mapping": {"user_id": "id"},
  "formulas": {"amount": "round(float(value), 2)"},
  "source1_csv_data": "<base64-encoded-csv>",
  "source2_creds": {
    "host": "localhost",
    "port": "5432",
    "dbname": "mydb",
    "user": "user",
    "password": "pass",
    "query": "SELECT * FROM users"
  }
}
```

This allows resuming past comparisons or batch-testing different environments.

---

## Screenshots 

<img width="1257" height="612" alt="image" src="https://github.com/user-attachments/assets/04875ac2-00b8-404c-adf4-7b144c4e5450" />

<img width="1257" height="612" alt="image" src="https://github.com/user-attachments/assets/d8b61ce3-cc7f-4874-b6ee-e993cc236278" />

<img width="1257" height="612" alt="image" src="https://github.com/user-attachments/assets/e362e41e-2945-44cd-8229-97cd66a29d9c" />

<img width="1257" height="612" alt="image" src="https://github.com/user-attachments/assets/5a563a6d-b553-475f-871d-bd3758a6a5ef" />


## 🤝 Contributing

Feel free to submit issues or open PRs to enhance comparison logic, data visualization, or support for more DBs.

---

## 📬 Contact

Made with ❤️ using [Streamlit](https://streamlit.io).
