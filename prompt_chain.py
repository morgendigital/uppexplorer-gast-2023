from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os
import csv
import json
import time

# Initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def classify_user_input(user_input):
    chat_completion_1 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Please take the user's query and classify it.\nYour task is to classify if the user wants to do an indoor our outdoor activity, and if it should be kids-friendly or not.\nThe output format should be a JSON, with just these key/value pairs:\nvenue_type: indoor, outdoor\nkids_friendly: true, false\nPlease only output the raw JSON, nothing else!"
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
    )
    return json.loads(chat_completion_1.choices[0].message.content)

def get_filtered_data(venue_type, kids_friendly, csv_data, location_data):
    csv_string = "\n".join([",".join(row) for row in csv_data])
    location_string = "\n".join([",".join(row) for row in location_data])

    chat_completion_2 = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": f"You will get an extensive list of different locations, and some visitor and capacity data during a specific time of the day. Please compile a list of possible locations and times that the user could visit, based on the following preference and kids-friendliness: Preference: {venue_type} activity. Kids friendly: {kids_friendly}. If possible, prefer activities that have lower visitor rates. Make sure to not present outdoor activities if it rains. Also make sure to present enough options so that the user can fill a whole day."
            },
            {
                "role": "user",
                "content": f"{csv_string}\n\nAdditional information (location table that shows you what attributes the locations have):\n{location_string}"
            }
        ],
    )
    return chat_completion_2.choices[0].message.content

def generate_travel_plan(filtered_data):
    chat_completion_3 = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a text to raw JSON converter. You get an input text, and you need to find and output the JSON only based on data provided to you. Not even Markdown, just really the pure JSON. You will get a text with a list of locations and possible visit times. Create a travel plan list with 3 to 5 locations for a user on where to go through that day, based on the data you get. Use the time as your factor on how to plan the day. Please make sure to always leave some time inbetween locations because the user needs some time to get there, at least 30 mins. Remember, you should only output it as raw formatted JSON, with ID, Venue Name and Time and why the location was picked. Do nothing else, no markdown, nothing. No nested, just id, venue name and time."
            },
            {
                "role": "user",
                "content": filtered_data
            }
        ],
    )
    return chat_completion_3.choices[0].message.content

def plan_trip():
    user_input = st.session_state.user_input

    with st.spinner('Classifying user input...'):
        # Classify user input
        classification = classify_user_input(user_input)
        venue_type = classification["venue_type"]
        kids_friendly = str(classification["kids_friendly"])
    with st.spinner('Frantically writing down my findings...'):
        # Read the CSV files
        csv_data = []
        with open('final_data/time_series_data_enriched.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        location_data = []
        with open('final_data/time_series_data_enriched.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        # Get filtered data
        filtered_data = get_filtered_data(venue_type, kids_friendly, csv_data, location_data)
    with st.spinner('Give me a moment to merge everything together... this could take a short while, please be patient.'):
        # Generate travel plan
        travel_plan_json = generate_travel_plan(filtered_data)
        df = pd.read_json(travel_plan_json)
    with st.spinner('Okay, I\'m ready! Gosh, my AI brain hurts...'):
        time.sleep(2)
        st.markdown("### Here we go, here's your trip.")
        st.markdown("This is how you should structure your day today.")
        st.table(df)

# Streamlit UI
st.title("⛰️ Plan your Trip")
user_input = st.text_area("What would you like to do today in the Attersee region?", key="user_input")
if st.button("Plan Trip"):
    plan_trip()
