import requests
from datetime import datetime, timedelta
import time
import os

def get_target_date_for_date(d):
    """
    Given a datetime d, return d if it is Monday-Friday.
    If d is Saturday, return d - 1 day (Friday).
    If d is Sunday, return d - 2 days (Friday).
    """
    weekday = d.weekday()  # Monday=0, Tuesday=1, ... Sunday=6
    if weekday == 5:   # Saturday
        return d - timedelta(days=1)
    elif weekday == 6:  # Sunday
        return d - timedelta(days=2)
    else:
        return d

def daterange(start_date, end_date):
    """Generator yielding dates from start_date up to and including end_date."""
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)

# Set up date range: last 5 years from today
end_date = datetime.today()
start_date = end_date - timedelta(days=5*365)  # approximate 5 years

# Build a set of unique target dates (as DDMMYYYY strings)
unique_dates = set()
for d in daterange(start_date, end_date):
    target = get_target_date_for_date(d)
    # Only add if target is a weekday (Monday-Friday)
    if target.weekday() < 5:
        unique_dates.add(target.strftime("%d%m%Y"))

# Sort the dates (oldest first)
unique_dates = sorted(unique_dates)

print(f"Found {len(unique_dates)} unique trading dates in the last 5 years.")

# URL pattern (from the snippet):
# https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_<DDMMYYYY>.csv
def build_url(ddmmyyyy):
    return f'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{ddmmyyyy}.csv'

# Create a session to persist cookies and headers
session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                  'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                  'Chrome/90.0.4430.93 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

# Step 1: Visit the NSE homepage to establish session cookies
home_url = 'https://www.nseindia.com'
print("Accessing NSE homepage to establish session...")
home_response = session.get(home_url, headers=headers)
if home_response.status_code != 200:
    print("Failed to access NSE homepage. Status Code:", home_response.status_code)
    exit(1)
time.sleep(1)  # mimic human delay

# Set Referer header (if needed)
headers['Referer'] = 'https://www.nseindia.com/all-reports'

# Loop over each unique trading date and download the file into a folder for its year
for ddmmyyyy in unique_dates:
    # Parse the date to get the year
    target_date = datetime.strptime(ddmmyyyy, "%d%m%Y")
    year = target_date.strftime("%Y")
    
    # Create a directory for the year if it doesn't exist
    if not os.path.exists(year):
        os.makedirs(year)
        print(f"Created directory for year {year}")
    
    url = build_url(ddmmyyyy)
    file_path = os.path.join(year, f"sec_bhavdata_full_{ddmmyyyy}.csv")
    
    print(f"\nAttempting to download file for {ddmmyyyy} from: {url}")
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"SUCCESS: File saved as {file_path}")
    else:
        print(f"FAILED: HTTP Status Code {response.status_code} for date {ddmmyyyy}")
    
    # Wait 2 seconds before the next download
    time.sleep(2)
