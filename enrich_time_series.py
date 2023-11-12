# Sample on how to enrich data with extra data points

from dotenv import load_dotenv
import os
import pandas as pd
import requests
from datetime import datetime, timedelta

load_dotenv()  # This loads the environment variables from .env

# Load CSV
csv_file = 'final_data/time_series_data.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# Setup for API call
base_url = 'http://api.weatherapi.com/v1/forecast.json'
weather_api_key = os.getenv('WEATHER_API_KEY')
country = 'Austria'
hardcoded_date = '2023-11-12'  # Hardcoded date

# Function to round up time to the next hour
def round_up_time(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M')
    if time_obj.minute > 0:
        time_obj += timedelta(hours=1)
    rounded_time = time_obj.strftime('%H:%M')
    print(f"Original Time: {time_str}, Rounded Time: {rounded_time}")  # Debugging line
    return rounded_time

def round_down_time(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M')
    # Reset minutes to 00 if there are any minutes
    if time_obj.minute > 0:
        time_obj -= timedelta(minutes=time_obj.minute)
    rounded_time = time_obj.strftime('%H:%M')
    print(f"Original Time: {time_str}, Rounded Time: {rounded_time}")  # Debugging line
    return rounded_time


# Function to make API call
def fetch_weather_data(feature_id):
    query = f"{feature_id},{country}"
    params = {
        'key': weather_api_key,
        'q': query,
        'dt': hardcoded_date,  # Use hardcoded date in the query
        'aqi': 'no',
        'alerts': 'no'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {feature_id} on: {response.text}")
        return None

# Grouping requests by feature_id
grouped_data = df.groupby(['feature_id'])

for feature_id, group in grouped_data:
    weather_data = fetch_weather_data(feature_id)
    # Initialize hours_data as an empty list
    hours_data = []

    if weather_data:
        # Check if 'forecastday' data is available
        if 'forecastday' in weather_data['forecast'] and weather_data['forecast']['forecastday']:
            hours_data = weather_data['forecast']['forecastday'][0]['hour']
        else:
            print(f"Forecast data is not available or in an unexpected format for {feature_id}.")

    # Process each row in the group
    for index, row in group.iterrows():
        hour_str = round_down_time(row['time'])
        datetime_str = f"{hardcoded_date} {hour_str}"
        hour_data = next((h for h in hours_data if h['time'] == datetime_str), None)
            
        if hour_data:
            df.at[index, 'will_it_rain'] = hour_data['will_it_rain']
            df.at[index, 'chance_of_rain'] = hour_data['chance_of_rain']
            df.at[index, 'condition_text'] = hour_data['condition']['text']
        else:
            print(f"No data found for {datetime_str}")

# Sort the DataFrame by 'feature_id' and then by 'time'
df.sort_values(by=['feature_id', 'time'], inplace=True)
# Add a new column 'ID' as a primary key
df.insert(0, 'ID', range(1, len(df) + 1))

# Save the enriched CSV
df.to_csv('final_data/time_series_data_enriched.csv', index=False)  # Provide a path for the enriched CSV file
