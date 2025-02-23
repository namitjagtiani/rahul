import os
import pandas as pd
from datetime import datetime, timedelta

# Update this base folder to where your 5-year folders reside.
base_folder = r"./"

# Define the indices to keep from the original file (0-based):
# A -> 0, B -> 1, C -> 2, E -> 4, F -> 5, G -> 6, I -> 8, N -> 13
cols_to_keep = [0, 1, 2, 4, 5, 6, 8, 13]

# Process every folder (assumed to be named by year) under the base folder
for year_folder in os.listdir(base_folder):
    year_path = os.path.join(base_folder, year_folder)
    if os.path.isdir(year_path):
        print(f"\nProcessing folder: {year_folder}")
        for file in os.listdir(year_path):
            if file.lower().endswith(".csv"):
                file_path = os.path.join(year_path, file)
                print(f"  Processing file: {file_path}")
                try:
                    # Read the CSV file (assuming header row exists)
                    df = pd.read_csv(file_path)
                    print(f"    Original columns: {df.columns.tolist()} (total: {df.shape[1]})")
                    
                    # Check if there are enough columns
                    if df.shape[1] < max(cols_to_keep) + 1:
                        print("    Skipping file because it has fewer columns than expected.")
                        continue

                    # Retain only the specified columns
                    df_new = df.iloc[:, cols_to_keep].copy()
                    
                    # Filter rows: keep only rows where column B (index 1) contains "EQ"
                    df_new = df_new[df_new.iloc[:, 1].astype(str).str.strip().str.upper().str.contains("EQ")]
                    
                    # Convert the date in column C (index 2) to YYYYMMDD format.
                    df_new.iloc[:, 2] = pd.to_datetime(df_new.iloc[:, 2], errors='coerce').dt.strftime('%Y%m%d')
                    
                    # Remove column B (the second column in the subset)
                    # This drops the column at position 1 in df_new.
                    df_new.drop(df_new.columns[1], axis=1, inplace=True)
                    
                    # Save the updated DataFrame back to CSV (overwriting the original file)
                    df_new.to_csv(file_path, index=False)
                    print(f"    Updated file saved: {file_path}")
                except Exception as e:
                    print(f"    Error processing file: {e}")
