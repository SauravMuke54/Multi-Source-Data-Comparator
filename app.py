import streamlit as st
import pandas as pd
import json
import base64
from sqlalchemy import create_engine
from io import BytesIO, StringIO

st.set_page_config(page_title="Multi-Source Comparator", layout="wide")
st.title("🔍 Multi-Source Table Data Comparator")

# Helper Functions

def load_csv_ui(label):
    return st.file_uploader(f"Upload CSV for {label}", type="csv", key=label)

def load_db_ui(label, default_port, imported_creds=None):
    host = st.text_input(f"{label} Host", value=imported_creds.get("host", "localhost") if imported_creds else "localhost")
    port = st.text_input(f"{label} Port", value=imported_creds.get("port", default_port) if imported_creds else default_port)
    dbname = st.text_input(f"{label} Database Name", value=imported_creds.get("dbname", "") if imported_creds else "")
    user = st.text_input(f"{label} Username", value=imported_creds.get("user", "") if imported_creds else "")
    password = st.text_input(f"{label} Password", type="password", value=imported_creds.get("password", "") if imported_creds else "")
    query = st.text_area(f"{label} Table Name or SQL Query", value=imported_creds.get("query", "") if imported_creds else "")
    return {
        "host": host, "port": port, "dbname": dbname,
        "user": user, "password": password, "query": query
    }

def load_csv(file):
    return pd.read_csv(file)

def load_db(conn_type, creds):
    db_map = {
        "PostgreSQL": "postgresql+psycopg2",
        "MySQL": "mysql+pymysql",
        "Oracle": "oracle+cx_oracle"
    }
    driver = db_map.get(conn_type)
    if not driver:
        raise ValueError("Unsupported DB")

    uri = f"{driver}://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['dbname']}"
    engine = create_engine(uri)
    return pd.read_sql(creds["query"], engine)

# Source Type Selection
source_types = ["CSV", "PostgreSQL", "MySQL", "Oracle"]

st.sidebar.header("🔄 Import/Export Settings")
settings_file = st.sidebar.file_uploader("Import Settings JSON", type="json")
imported_settings = None
if settings_file:
    imported_settings = json.load(settings_file)
    st.sidebar.success("✅ Settings imported")

settings = {}

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔹 Source 1")
    source1_type = st.selectbox("Select Source 1 Type", source_types, key="source1",
                                index=source_types.index(imported_settings["source1_type"]) if imported_settings else 0)
    df1 = None
    creds1 = None
    file1 = None
    if source1_type == "CSV":
        file1 = load_csv_ui("Source 1")
        if file1:
            file1.seek(0)
            df1 = load_csv(file1)
        elif imported_settings and "source1_csv_data" in imported_settings:
            decoded1 = base64.b64decode(imported_settings["source1_csv_data"]).decode('utf-8')
            df1 = pd.read_csv(StringIO(decoded1))
            st.success("✅ Source 1 CSV loaded from settings")
    else:
        creds1 = load_db_ui("Source 1", default_port="5432" if source1_type == "PostgreSQL" else "3306",
                            imported_creds=imported_settings.get("source1_creds") if imported_settings else None)
        if all(creds1.values()):
            try:
                df1 = load_db(source1_type, creds1)
                st.success("✅ Source 1 loaded")
            except Exception as e:
                st.error(f"❌ Failed to load Source 1: {e}")

with col2:
    st.subheader("🔹 Source 2")
    source2_type = st.selectbox("Select Source 2 Type", source_types, key="source2",
                                index=source_types.index(imported_settings["source2_type"]) if imported_settings else 0)
    df2 = None
    creds2 = None
    file2 = None
    if source2_type == "CSV":
        file2 = load_csv_ui("Source 2")
        if file2:
            file2.seek(0)
            df2 = load_csv(file2)
        elif imported_settings and "source2_csv_data" in imported_settings:
            decoded2 = base64.b64decode(imported_settings["source2_csv_data"]).decode('utf-8')
            df2 = pd.read_csv(StringIO(decoded2))
            st.success("✅ Source 2 CSV loaded from settings")
    else:
        creds2 = load_db_ui("Source 2", default_port="5432" if source2_type == "PostgreSQL" else "3306",
                            imported_creds=imported_settings.get("source2_creds") if imported_settings else None)
        if all(creds2.values()):
            try:
                df2 = load_db(source2_type, creds2)
                st.success("✅ Source 2 loaded")
            except Exception as e:
                st.error(f"❌ Failed to load Source 2: {e}")

if df1 is not None and df2 is not None:
    st.markdown("---")
    st.subheader("📋 Columns Preview")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Source 1 Columns:**")
        st.write(list(df1.columns))
    with col2:
        st.markdown("**Source 2 Columns:**")
        st.write(list(df2.columns))

    st.markdown("---")
    st.subheader("🚫 Columns to Exclude from Comparison")
    excluded_cols = st.multiselect(
        "Select columns to exclude from comparison",
        options=list(set(df1.columns).intersection(df2.columns)),
        default=imported_settings.get("excluded_columns", []) if imported_settings else [],
    )

    st.markdown("---")
    st.subheader("🔀 Column Mapping")
    col_mapping = imported_settings.get("column_mapping", {}) if imported_settings else {}
    updated_mapping = {}
    mapping_expander = st.expander("Configure Column Mappings")
    with mapping_expander:
        for i in range(max(len(df1.columns), len(df2.columns))):
            default1 = list(col_mapping.keys())[i] if i < len(col_mapping) else ""
            default2 = list(col_mapping.values())[i] if i < len(col_mapping) else ""
            c1, c2 = st.columns(2)
            src1 = c1.selectbox(f"Source 1 Column {i+1}", [""] + list(df1.columns), index=([""] + list(df1.columns)).index(default1) if default1 else 0, key=f"map1_{i}")
            src2 = c2.selectbox(f"Source 2 Column {i+1}", [""] + list(df2.columns), index=([""] + list(df2.columns)).index(default2) if default2 else 0, key=f"map2_{i}")
            if src1 and src2:
                updated_mapping[src1] = src2

    if updated_mapping:
        df1 = df1.rename(columns=updated_mapping)
        reverse_mapping = {v: k for k, v in updated_mapping.items()}
        df2 = df2.rename(columns=reverse_mapping)

    st.markdown("---")
    st.subheader("🔑 Key Column(s)")
    key_input = st.text_input("Enter key column(s) (comma-separated):",
                              value=imported_settings.get("key_columns") if imported_settings else "")

    if key_input:
        keys = [k.strip() for k in key_input.split(",")]

        if not all(k in df1.columns and k in df2.columns for k in keys):
            st.error("❌ Key column(s) missing in one of the sources.")
        else:
            df1 = df1.set_index(keys).sort_index()
            df2 = df2.set_index(keys).sort_index()

            st.markdown("---")
            st.subheader("🧪 Optional: Apply Formula to Columns")
            formulas = imported_settings.get("formulas", {}) if imported_settings else {}
            full_cols = list(df1.reset_index().columns)
            updated_formulas = {}

            df1_reset = df1.reset_index()
            df2_reset = df2.reset_index()

            for col in full_cols:
                formula = st.text_input(f"Formula for column `{col}`", value=formulas.get(col, ""))
                if formula:
                    try:
                        df1_reset[col] = df1_reset[col].apply(lambda value: eval(formula))
                        df2_reset[col] = df2_reset[col].apply(lambda value: eval(formula))
                        updated_formulas[col] = formula
                    except Exception as e:
                        st.error(f"⚠️ Formula error in column `{col}`: {e}")

            df1 = df1_reset.set_index(keys)
            df2 = df2_reset.set_index(keys)

            common_cols = df1.columns.intersection(df2.columns).difference(excluded_cols)
            shared_index = df1.index.intersection(df2.index)

            df1_common = df1.loc[shared_index, common_cols]
            df2_common = df2.loc[shared_index, common_cols]

            try:
                diff = df1_common.compare(df2_common, align_axis=0)
            except Exception as e:
                st.error(f"⚠️ Comparison error: {e}")
                diff = pd.DataFrame()

            st.markdown("---")
            st.subheader("📊 Preview After Formula Application")
            with st.expander("Source 1 Processed Data"):
                st.dataframe(df1_reset)
            with st.expander("Source 2 Processed Data"):
                st.dataframe(df2_reset)

            if not diff.empty:
                st.subheader("🔁 Differences (highlighted)")

                def highlight_diff(val):
                    return "background-color: lightcoral" if pd.notna(val) else ""

                styled_diff = diff.style.applymap(highlight_diff)
                st.dataframe(styled_diff, use_container_width=True)
            else:
                st.success("✅ No differences found in shared keys and columns.")

            missing_in_df2 = df1.index.difference(df2.index)
            missing_in_df1 = df2.index.difference(df1.index)

            if not missing_in_df2.empty:
                st.subheader("🚫 Rows in Source 1 but missing in Source 2")
                st.dataframe(df1.loc[missing_in_df2])

            if not missing_in_df1.empty:
                st.subheader("🚫 Rows in Source 2 but missing in Source 1")
                st.dataframe(df2.loc[missing_in_df1])

            settings = {
                "source1_type": source1_type,
                "source2_type": source2_type,
                "source1_creds": creds1,
                "source2_creds": creds2,
                "key_columns": key_input,
                "formulas": updated_formulas,
                "excluded_columns": excluded_cols,
                "column_mapping": updated_mapping
            }

            if source1_type == "CSV" and file1:
                file1.seek(0)
                settings["source1_csv_data"] = base64.b64encode(file1.getvalue()).decode('utf-8')

            if source2_type == "CSV" and file2:
                file2.seek(0)
                settings["source2_csv_data"] = base64.b64encode(file2.getvalue()).decode('utf-8')

            if st.button("📄 Export Settings JSON"):
                settings_json = json.dumps(settings, indent=2)
                st.download_button("Download Settings", data=settings_json, file_name="comparator_settings.json", mime="application/json")
