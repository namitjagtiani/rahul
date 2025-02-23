import requests
import pandas as pd
from datetime import datetime
import time
import os

def download_file_for_date(date_str):
    """
    Given a date string in DDMMYYYY format, builds the URL, downloads the CSV file,
    and saves it as sec_bhavdata_full_<date_str>.csv.
    Returns the file name if successful.
    """
    url = f'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv'
    file_name = f"sec_bhavdata_full_{date_str}.csv"
    
    # Create a session and headers
    session = requests.Session()
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/90.0.4430.93 Safari/537.36'),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    # Establish a session by visiting the homepage
    home_url = 'https://www.nseindia.com'
    print("Accessing NSE homepage to establish session...")
    home_response = session.get(home_url, headers=headers)
    if home_response.status_code != 200:
        print("Failed to access NSE homepage. Status Code:", home_response.status_code)
        return None
    time.sleep(1)
    headers['Referer'] = 'https://www.nseindia.com/all-reports'
    
    print(f"Downloading file for date {date_str} from:\n{url}")
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        with open(file_name, "wb") as f:
            f.write(response.content)
        print(f"File downloaded and saved as: {file_name}")
        return file_name
    else:
        print(f"Failed to download file. HTTP Status Code: {response.status_code}")
        return None

def modify_csv(file_path):
    """
    Opens the CSV file, modifies it by:
      - Retaining columns: A, B, C, E, F, G, I, N (indices 0,1,2,4,5,6,8,13)
      - Filtering rows where column B contains "EQ"
      - Converting column C to YYYYMMDD format
      - Removing column B after filtering
    Saves the modified CSV to the same file_path.
    """
    # Define the columns to retain (0-indexed)
    cols_to_keep = [0, 1, 2, 4, 5, 6, 8, 13]
    
    try:
        df = pd.read_csv(file_path)
        print(f"Original CSV shape: {df.shape}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Check if file has enough columns
    if df.shape[1] < max(cols_to_keep)+1:
        print("File does not have enough columns. Skipping modification.")
        return
    
    # Retain only specified columns
    df_mod = df.iloc[:, cols_to_keep].copy()
    
    # Filter rows: keep only rows where column B (index 1) contains "EQ" (case-insensitive)
    df_mod = df_mod[df_mod.iloc[:, 1].astype(str).str.strip().str.upper().str.contains("EQ")]
    
    # Convert the date in column C (index 2) to YYYYMMDD format
    try:
        df_mod.iloc[:, 2] = pd.to_datetime(df_mod.iloc[:, 2], errors='coerce').dt.strftime('%Y%m%d')
    except Exception as e:
        print(f"Error converting date format: {e}")
    
    # Remove column B (the second column in the subset)
    df_mod.drop(df_mod.columns[1], axis=1, inplace=True)
    
    # Save the modified CSV back to the file
    try:
        df_mod.to_csv(file_path, index=False)
        print(f"Modified CSV saved: {file_path}")
        print(f"New CSV shape: {df_mod.shape}")
    except Exception as e:
        print(f"Error saving modified CSV: {e}")

def main():
    # Ask user for a date in DDMMYYYY format
    date_input = input("Enter the date (DDMMYYYY): ").strip()
    try:
        # Validate the date by attempting to parse it
        datetime.strptime(date_input, "%d%m%Y")
    except ValueError:
        print("The date format is incorrect. Please enter the date as DDMMYYYY.")
        return
    
    # Download the file for the given date
    file_path = download_file_for_date(date_input)
    if file_path:
        # Modify the CSV file according to the specified rules
        modify_csv(file_path)
    else:
        print("Download failed. Exiting.")

if __name__ == "__main__":
    main()
