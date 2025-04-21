import pandas as pd

# Load the dataset
df = pd.read_excel('DK_BW2022.xlsx')

# 1. Remove or handle missing data
# Drop rows with missing lat or lon
df = df.dropna(subset=['lat', 'lon'])

# Fill missing values in 'groupIdentifier' with 'Unknown'
df = df.fillna({'groupIdentifier': 'Unknown'})

# 2. Ensure valid geographical coordinates
# Filter rows where lat and lon are within valid ranges
df = df[(df['lat'] >= -90) & (df['lat'] <= 90)]
df = df[(df['lon'] >= -180) & (df['lon'] <= 180)]

# 3. Remove duplicates
# Remove rows with duplicate lat, lon values
df = df.drop_duplicates(subset=['lat', 'lon'])

# 4. Ensure lat and lon are numeric (if necessary)
df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

# 5. Save the cleaned dataset to a new CSV file
df.to_csv('cleaned_DKBW_2022.xlsx', index=False)

print("Data cleaned and saved to 'cleaned_DKBW_2022.xlsx'")
