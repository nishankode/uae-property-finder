
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

try:
    print("Reading CSV...")
    df = pd.read_csv('data/cleaned_data/uae_realestate_old_cleaned.csv', low_memory=False)
    
    print("Converting object columns to string...")
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)
            
    print("Saving to Parquet...")
    df.to_parquet('data/cleaned_data/uae_realestate.parquet', index=False)
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
