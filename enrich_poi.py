import csv
import random

# Function to generate random coordinates near Austria, randomly generated
# TODO: not randomly generated ;)
def random_coordinates():
    lat = random.uniform(46.5, 49.0)  # Austria's latitude roughly ranges from 46.5 to 49.0 degrees
    long = random.uniform(9.5, 17.2)  # Austria's longitude roughly ranges from 9.5 to 17.2 degrees
    return lat, long

# Read the existing CSV and append the new columns with random data
enriched_data = []
with open('final_data/poi_data.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        row['venue_type'] = random.choice(['indoor', 'outdoor'])
        row['kids_friendly'] = random.choice([True, False])
        row['lat'], row['long'] = random_coordinates()
        enriched_data.append(row)

# Write the updated data to a new CSV file
with open('final_data/poi_data_enriched.csv', 'w', newline='') as file:
    fieldnames = ['date', 'feature_id', 'total_visitors', 'average_duration_of_stay(s)', 'venue_type', 'kids_friendly', 'lat', 'long']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    writer.writeheader()
    for row in enriched_data:
        writer.writerow(row)
