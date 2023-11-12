import pandas as pd
import json

# Read the CSV files - These were the samples used (unfortunately we are not allowed to share it)
print("Remember: Unfortunately, we are not able to share them publicly, so this aggregation script will only work with the Hackathon data")
arriving_departing_df = pd.read_csv('sample_data/POIs_2022-08-22_arrivingAndDepartingVisitors.csv')
total_visitors_df = pd.read_csv('sample_data/POIs_2022-08-22_totalVisitors.csv')
origin_analysis_df = pd.read_csv('sample_data/POIs_2022-08-22_originAnalysis.csv')
duration_of_stays_df = pd.read_csv('sample_data/POIs_2022-08-22_averageDurationOfStay.csv')
visits_over_time_df = pd.read_csv('sample_data/POIs_2022-08-22_visitsOverTime.csv')

# Aggregated Table
# Merge the total visitors and average duration csv dataframes
aggregated_df = pd.merge(total_visitors_df, duration_of_stays_df, on=['date', 'feature_id'])

# Pivot origin analysis data and merge it into the aggregated dataframe
origin_groups = origin_analysis_df.groupby(['date', 'feature_id'])
origin_data = {}
for group, data in origin_groups:
    origin_dict = data.set_index('origin_layer')['visitors'].to_dict()
    origin_data[group] = json.dumps(origin_dict)

# origin_df = pd.DataFrame.from_dict(origin_data, orient='index', columns=['origin_data'])
# origin_df.index = pd.MultiIndex.from_tuples(origin_df.index)
# origin_df.reset_index(inplace=True)
# origin_df.rename(columns={'level_0': 'date', 'level_1': 'feature_id'}, inplace=True)
# aggregated_df = pd.merge(aggregated_df, on=['date', 'feature_id'], how='left')

# Time Series Table
time_series_df = arriving_departing_df[['date', 'feature_id', 'time', 'arriving_visitors', 'departing_visitors']].copy()
time_series_df = pd.merge(time_series_df, visits_over_time_df[['date', 'feature_id', 'time', 'visitors', 'fraction_of_total_visitors(%)']], on=['date', 'feature_id', 'time'], how='outer')

# Convert 'arriving_visitors' and 'departing_visitors' from float to int
time_series_df['arriving_visitors'] = time_series_df['arriving_visitors']
time_series_df['departing_visitors'] = time_series_df['departing_visitors']

# Coerce fractional columns to proper percentages - WAS AN ERROR, NOT NEEDED! Dirty fix: 100 -> 1
time_series_df['fraction_of_total_visitors(%)'] *= 1

# Save the dataframes to new CSV files
aggregated_df.to_csv('final_data/poi_data.csv', index=False)
time_series_df.to_csv('final_data/time_series_data.csv', index=False)

print("Aggregated data and time series tables have been saved as 'poi_data.csv' and 'time_series_data.csv' respectively.")