import streamlit as st
import pandas as pd
import mysql.connector
from datetime import date

# ----------------------- SETUP -----------------------
st.set_page_config(page_title="NASA Asteroid Tracker", layout="wide")

# Database connection
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ShaYug",
        database="project_nasa_neo"
    )

conn = get_connection()

# ----------------------- HEADER -----------------------
st.markdown("<h1 style='text-align: center;'>🚀 NASA Asteroid Tracker 🛰️</h1>", unsafe_allow_html=True)
st.markdown("---")



q1 = "Count how many times each asteroid has approached Earth"
q2 = "Average velocity of each asteroid over multiple approaches"
q3 = "Top 10 fastest asteroids"
q4 = "Potentially hazardous asteroids that have approached Earth more than 3 times"
q5 = "Month with the most asteroid approaches"
q6 = "Asteroid with the fastest ever approach speed"
q7 = "Sort asteroids by maximum estimated diameter (descending)"
q8 = "Asteroids whose closest approach is getting nearer over time"
q9 = "Display name and miss distance of closest approach"
q10 = "Asteroids with velocity > 50,000 km/h"
q11 = "Count how many approaches happened per month"
q12 = "Asteroid with the highest brightness (lowest magnitude value)"
q13 = "Count of hazardous vs non-hazardous asteroids"
q14 = "Asteroids that passed closer than the Moon (< 1 LD)"
q15 = "Asteroids that came within 0.05 AU"
q16 = "Custom Query"


# ----------------------- SIDEBAR -----------------------
with st.sidebar:
    show_filters = st.checkbox("Show Filter Criteria", value=True)

apply_filter = False

if show_filters:
    st.markdown("### Filter Criteria")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", date(2020, 1, 1))
        min_mag, max_mag = st.slider("Min Magnitude", -5.0, 50.0, (-5.0, 50.0))
        min_vel, max_vel = st.slider("Relative Velocity (km/h)", 0.0, 150000.0, (0.0, 150000.0))
        hazardous = st.selectbox("Only Show Potentially Hazardous", ["All", "Yes", "No"])

    with col2:
        end_date = st.date_input("End Date", date(2025, 5, 13))
        min_dia, max_dia = st.slider("Estimated Diameter (km)", 0.0, 10.0, (0.0, 10.0))
        min_au, max_au = st.slider("Astronomical Unit", 0.0, 1.0, (0.0, 1.0))

    apply_filter = st.button("Apply Filter")


with st.sidebar.expander("📊 Queries", expanded=False):
    query_names = ["Choose Filter from the list", q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, "Custom Query"]
    selected_query = st.selectbox("Choose a predefined query", query_names)

# ----------------------- QUERY EXECUTION -----------------------
def run_query(query):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(results)


query1 = """
SELECT a.name, COUNT(*) as approach_count
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
GROUP BY a.name
ORDER BY approach_count DESC;
"""

# Query 2: Average velocity of each asteroid over multiple approaches
query2 = """
SELECT a.name, AVG(c.relative_velocity_kmph) AS avg_velocity
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
GROUP BY a.name
ORDER BY avg_velocity DESC;
"""

### Query 3: Top 10 fastest asteroids
query3 = """
SELECT a.name, MAX(c.relative_velocity_kmph) AS max_velocity
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
GROUP BY a.name
ORDER BY max_velocity DESC
LIMIT 10;
"""

### Query 4: Potentially hazardous asteroids that have approached Earth more than 3 times
query4 = """
SELECT a.name, COUNT(*) as approach_count
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
WHERE a.is_potentially_hazardous_asteroid = TRUE
GROUP BY a.name
HAVING approach_count > 3;
"""

### Query 5: Month with the most asteroid approaches
query5 = """
SELECT MONTH(close_approach_date) AS month, COUNT(*) AS count
FROM close_approach
GROUP BY month
ORDER BY count DESC
LIMIT 1;
"""

### Query 6: Asteroid with the fastest ever approach speed
query6 = """
SELECT a.name, c.relative_velocity_kmph
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
ORDER BY c.relative_velocity_kmph DESC
LIMIT 1;
"""

### Query 7: Sort asteroids by maximum estimated diameter (descending)
query7 = """
SELECT name, estimated_diameter_max_km
FROM asteroids
ORDER BY estimated_diameter_max_km DESC;
"""

### Query 8: Asteroids whose closest approach is getting nearer over time
query8 = """
SELECT a.name, c.close_approach_date, c.miss_distance_km
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
ORDER BY a.name, c.close_approach_date ASC, c.miss_distance_km ASC;
"""

### Query 9: Display name and miss distance of closest approach
query9 = """
SELECT a.name, c.close_approach_date, c.miss_distance_km
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
ORDER BY c.miss_distance_km ASC;
"""

### Query 10: Asteroids with velocity > 50,000 km/h
query10 = """
SELECT a.name, c.relative_velocity_kmph
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
WHERE c.relative_velocity_kmph > 50000;
"""

### Query 11: Count how many approaches happened per month
query11 = """
SELECT MONTH(close_approach_date) AS month, COUNT(*) AS approach_count
FROM close_approach
GROUP BY month
ORDER BY month;
"""

### Query 12: Asteroid with the highest brightness (lowest magnitude value)
query12 = """
SELECT name, absolute_magnitude_h
FROM asteroids
ORDER BY absolute_magnitude_h ASC
LIMIT 1;
"""

### Query 13: Count of hazardous vs non-hazardous asteroids
query13 = """
SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count
FROM asteroids
GROUP BY is_potentially_hazardous_asteroid;
"""

### Query 14: Asteroids that passed closer than the Moon (< 1 LD)
query14 = """
SELECT a.name, c.close_approach_date, c.miss_distance_lunar
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
WHERE c.miss_distance_lunar < 1;
"""

### Query 15: Asteroids that came within 0.05 AU
query15 = """
SELECT a.name, c.close_approach_date, c.astronomical
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
WHERE c.astronomical < 0.05;
"""

### Query 16: Slowest Asteroids by Average Speed
query16 = """
SELECT a.name, ROUND(AVG(c.relative_velocity_kmph), 2) AS avg_velocity_kmph
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
GROUP BY a.name
ORDER BY avg_velocity_kmph ASC
LIMIT 10;
"""

### Query 17: Closest Hazardous Asteroid Approaches
query17 = """
SELECT a.name, c.close_approach_date, c.miss_distance_km
FROM asteroids a
JOIN close_approach c ON a.id = c.neo_reference_id
WHERE a.is_potentially_hazardous_asteroid = TRUE
ORDER BY c.miss_distance_km ASC
LIMIT 10;
"""

### Query 18: Annual Close approach Count
query18 = """
SELECT YEAR(close_approach_date) AS year, COUNT(*) AS approach_count
FROM close_approach
GROUP BY year
ORDER BY year;
"""

### Query 19: Top 5 Largest Hazardous Asteroids
query19 = """
SELECT name, estimated_diameter_max_km
FROM asteroids
WHERE is_potentially_hazardous_asteroid = TRUE
ORDER BY estimated_diameter_max_km DESC
LIMIT 5;
"""

### Query 20: 5 Non Hazardous Asteroids
query20 = """
SELECT name, estimated_diameter_max_km
FROM asteroids
WHERE is_potentially_hazardous_asteroid = FALSE
ORDER BY estimated_diameter_max_km DESC
LIMIT 5;
"""

predefined_queries = {
    q1 : query1,
    q2 : query2,
    q3 : query3,
    q4 : query4,
    q5 : query5,
    q6 : query6,
    q7 : query7,
    q8 : query8,
    q9 : query9,
    q10 : query10,
    q11 : query11,
    q12 : query12,
    q13 : query13,
    q14 : query14,
    q15 : query15
}

if selected_query == "Custom Query":
    custom_query_text = st.text_area("Enter your custom SQL query:")
    run_custom = st.button("Run Custom Query")

    if run_custom and custom_query_text.strip():
        try:
            df = run_query(custom_query_text)
        except Exception as e:
            st.error(f"❌ Error running your query: {e}")
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

elif selected_query in predefined_queries:
    df = run_query(predefined_queries[selected_query])
else:
    # Default: Show all asteroid + approach data
    df = run_query("""
        SELECT a.*, c.*
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
    """)

# ----------------------- FILTERING -----------------------
if apply_filter:
    df['close_approach_date'] = pd.to_datetime(df['close_approach_date'], errors='ignore')

    if 'close_approach_date' in df.columns:
        df = df[
            (df['close_approach_date'] >= pd.to_datetime(start_date)) &
            (df['close_approach_date'] <= pd.to_datetime(end_date))
        ]

    if 'absolute_magnitude_h' in df.columns:
        df = df[(df['absolute_magnitude_h'] >= min_mag) & (df['absolute_magnitude_h'] <= max_mag)]

    if 'estimated_diameter_min_km' in df.columns and 'estimated_diameter_max_km' in df.columns:
        df = df[
            (df['estimated_diameter_min_km'] >= min_dia) &
            (df['estimated_diameter_max_km'] <= max_dia)
        ]

    if 'relative_velocity_kmph' in df.columns:
        df = df[
            (df['relative_velocity_kmph'] >= min_vel) &
            (df['relative_velocity_kmph'] <= max_vel)
        ]

    if 'miss_distance_au' in df.columns:
        df = df[
            (df['miss_distance_au'] >= min_au) &
            (df['miss_distance_au'] <= max_au)
        ]

    if 'is_potentially_hazardous_asteroid' in df.columns:
        if hazardous == "Yes":
            df = df[df['is_potentially_hazardous_asteroid'] == 1]
        elif hazardous == "No":
            df = df[df['is_potentially_hazardous_asteroid'] == 0]

# ----------------------- DISPLAY RESULTS -----------------------
st.subheader("Filtered Asteroids")
st.dataframe(df, use_container_width=True)