import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import timedelta
from sqlalchemy import create_engine

# 1. Setup the factory and make it predictable (seed=42)
fake = Faker()
Faker.seed(42)
np.random.seed(42)
NUM_SUBJECTS = 500

# 2. Build Demographics with a 5% chance of a Date error (DM01)
def generate_demographics():
    data = []
    for i in range(1, NUM_SUBJECTS + 1):
        subjid = f"{i:03d}"
        brthdat = fake.date_of_birth(minimum_age=18, maximum_age=80)
        
        if random.random() < 0.05:
            ic_date = brthdat - timedelta(days=random.randint(10, 100)) # Error!
        else:
            ic_date = fake.date_between(start_date='-2y', end_date='today')
            
        data.append({'subjid': subjid, 'brthdat': brthdat, 'ic_date': ic_date})
    return pd.DataFrame(data)

# 3. Build Vitals with a 10% chance of a Blood Pressure error (VS01)
def generate_vitals(dm_df):
    data = []
    for _, row in dm_df.iterrows():
        sys_bp = random.randint(90, 160)
        dia_bp = random.randint(60, 100)
        
        if random.random() < 0.10:
            sys_bp, dia_bp = dia_bp, sys_bp  # Error: Swapped!
            
        data.append({'subjid': row['subjid'], 'vs_sysbp': sys_bp, 'vs_diabp': dia_bp})
    return pd.DataFrame(data)

# 4. Build Adverse Events with a 15% chance of a Severity error (AE01)
def generate_adverse_events(dm_df):
    data = []
    ae_terms = ['Nausea', 'Fatigue', 'Headache', 'Anemia', 'Neutropenia']
    subjects_with_aes = dm_df.sample(frac=0.4)['subjid'] # Only 40% get sick
    
    for subj in subjects_with_aes:
        severity = random.choice(['Mild', 'Moderate', 'Severe'])
        
        if severity == 'Severe' and random.random() < 0.15:
            serious = 'No' # Error!
        else:
            serious = 'Yes' if severity == 'Severe' else 'No'
            
        data.append({'subjid': subj, 'ae_term': random.choice(ae_terms), 'ae_sev': severity, 'ae_ser': serious})
    return pd.DataFrame(data)

# 5. Run the factory to generate the data
print(f"Generating data for {NUM_SUBJECTS} patients...")
dm = generate_demographics()
vs = generate_vitals(dm)
ae = generate_adverse_events(dm)

# ---------------------------------------------------------
# 6. NEW: DATABASE INJECTION
# ---------------------------------------------------------
print("Connecting to PostgreSQL...")
# IMPORTANT: Change 'your_password' to your actual pgAdmin password!
engine = create_engine('postgresql://postgres:admin123@localhost:5432/clinical_db')

# Push the data directly into the pgAdmin tables
print("Pushing data to clinical_staging schema...")
dm.to_sql('raw_demographics', engine, schema='clinical_staging', if_exists='replace', index=False)
vs.to_sql('raw_vitals', engine, schema='clinical_staging', if_exists='replace', index=False)
ae.to_sql('raw_adverse_events', engine, schema='clinical_staging', if_exists='replace', index=False)

print("Success! 500 patients injected directly into PostgreSQL.")