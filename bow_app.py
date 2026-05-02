import sqlite3
import streamlit as st
import pandas as pd
from bowmatch import find_similar_bows

DB_PATH = "bowsDB.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_models(brand):
    conn = get_connection()
    query = """
    SELECT DISTINCT bs.model
    FROM bow_specs bs
    JOIN manufactures m ON bs.manufacturer_id = m.manufacturer_id
    WHERE m.name = ?
    AND bs.model IS NOT NULL
    ORDER BY bs.model
    """
    df = pd.read_sql_query(query, conn, params=(brand,))
    conn.close()
    return df["model"].tolist()

def get_brands():
    conn = get_connection()
    query = """
    SELECT DISTINCT name
    FROM manufactures
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df["name"].tolist()

def get_years_for_model(model):
    conn = get_connection()
    query = """  
    SELECT DISTINCT year
    FROM bow_specs
    WHERE model = ?
    AND year IS NOT NULL
    ORDER BY year DESC
    """
    df = pd.read_sql_query(query, conn, params=(model,))
    conn.close()
    return df["year"].tolist()

st.title("Apex Bow Matcher")

st.write("Find bows with similar ATA and brace height.")

brands = get_brands()

selected_brand = st.selectbox("Select your bow brand", brands)

models = get_models(selected_brand)

selected_model = st.selectbox("Select your bow model", models)

years = get_years_for_model(selected_model)

selected_year = st.selectbox("Select year", years)

ata_tolerance = st.slider("ATA tolerance", 0.25, 3.0, 1.0, 0.25)
brace_tolerance = st.slider("Brace height tolerance", 0.25, 2.0, 0.5, 0.25)

min_year = st.number_input("Only show bows from year or newer", min_value=1990, max_value=2030, value=int(selected_year))


if st.button("Find similar bows"):
    target, matches = find_similar_bows(
        selected_model,
        selected_year,
        ata_tolerance,
        brace_tolerance,
        min_year
    )
    st.subheader("Your Bow")
    st.dataframe(pd.DataFrame([target]))
    if not matches:
        st.warning("No matches found. Try loosening your tolerances or lowering the year filter.")
    else:
        st.subheader("Top Similar Bows")
        st.dataframe(pd.DataFrame(matches))