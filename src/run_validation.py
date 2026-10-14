import pandas as pd
from sqlalchemy import create_engine

# ---------------------------------------------------------
# NEW: DATABASE EXTRACTION
# ---------------------------------------------------------
print("Connecting to PostgreSQL...")
# Change 'your_password' to your actual pgAdmin password!
engine = create_engine('postgresql://postgres:admin123@localhost:5432/clinical_db')

print("Extracting live clinical data via SQL...")
# Use pandas to run SQL queries and pull the data into Python
dm = pd.read_sql("SELECT * FROM clinical_staging.raw_demographics", engine)
vs = pd.read_sql("SELECT * FROM clinical_staging.raw_vitals", engine)
ae = pd.read_sql("SELECT * FROM clinical_staging.raw_adverse_events", engine)

# Create an empty bucket to hold all the mistakes we find
queries = []

# 2. RUN THE RULEBOOK

# --- DM01: Informed consent date cannot be before birth date ---
dm['brthdat'] = pd.to_datetime(dm['brthdat'])
dm['ic_date'] = pd.to_datetime(dm['ic_date'])
bad_dates = dm[dm['ic_date'] < dm['brthdat']]

for index, row in bad_dates.iterrows():
    queries.append({
        'Check_ID': 'DM01',
        'Subject': row['subjid'],
        'Form': 'Demographics',
        'Message': 'Informed consent date cannot be before birth date.'
    })

# --- VS01: Diastolic BP is greater than Systolic BP ---
bad_bp = vs[vs['vs_diabp'] > vs['vs_sysbp']]

for index, row in bad_bp.iterrows():
    queries.append({
        'Check_ID': 'VS01',
        'Subject': row['subjid'],
        'Form': 'Vital Signs',
        'Message': f"Diastolic BP ({row['vs_diabp']}) > Systolic BP ({row['vs_sysbp']})."
    })

# --- AE01: Severe AE reported but not marked as Serious ---
bad_ae = ae[(ae['ae_sev'] == 'Severe') & (ae['ae_ser'] == 'No')]

for index, row in bad_ae.iterrows():
    queries.append({
        'Check_ID': 'AE01',
        'Subject': row['subjid'],
        'Form': 'Adverse Events',
        'Message': 'Severe AE reported but not marked as Serious.'
    })

# 3. Export the final Discrepancy Log
query_report = pd.DataFrame(queries)
output_path = '../data/output/discrepancy_query_report.csv'
query_report.to_csv(output_path, index=False)

print(f"Validation complete! Found {len(query_report)} clinical discrepancies.")
print(f"Discrepancy log saved to: {output_path}")