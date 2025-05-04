import streamlit as st
import matplotlib.pyplot as plt
import requests
import pandas as pd
from io import StringIO
import json
import chardet
import geopandas as gpd


st.header('Natural Increase of the Population in Estonia by Region')


STATISTIKAAMETI_API_URL = "https://andmed.stat.ee/api/v1/et/stat/RV032"

JSON_PAYLOAD_STR =""" {
  "query": [
    {
      "code": "Aasta",
      "selection": {
        "filter": "item",
        "values": [
          "2014",
          "2015",
          "2016",
          "2017",
          "2018",
          "2019",
          "2020",
          "2021",
          "2022",
          "2023"
        ]
      }
    },
    {
      "code": "Maakond",
      "selection": {
        "filter": "item",
        "values": [
          "37",
          "44",
          "49",
          "51",
          "57",
          "59",
          "65",
          "67",
          "70",
          "74",
          "78",
          "82",
          "84",
          "86"
        ]
      }
    },
    {
      "code": "Sugu",
      "selection": {
        "filter": "item",
        "values": [
          "2",
          "3"
        ]
      }
    }
  ],
  "response": {
    "format": "csv"
  }
}
"""

geojson = "maakonnad.geojson"


#@st.cache_data
def import_data():
    headers = {
        'Content-Type': 'application/json'
    }
    parsed_payload = json.loads(JSON_PAYLOAD_STR)
    response = requests.post(STATISTIKAAMETI_API_URL, json=parsed_payload, headers=headers)

    if response.status_code == 200:
        print("Request successful.")
        text = response.content.decode('utf-8-sig')
        df = pd.read_csv(StringIO(text))
    else:
        print(f"Failed with status code: {response.status_code}")
        print(response.text)
    return df


#@st.cache_data
def import_geojson():
    gdf = gpd.read_file(geojson)
    return gdf
    

def get_data_for_year(df, year):
    year_data = df[df.Aasta==year]
    return year_data
    

def plot(df):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    df.plot(column='Loomulik iive', 
                ax=ax,
                legend=True,
                cmap='coolwarm',
                legend_kwds={'label': "Natural Increase"})

    for idx, row in df.iterrows():
        centroid = row['geometry'].centroid
        iive_value = row['Loomulik iive']
        ax.text(centroid.x, centroid.y, f"{int(iive_value)}", fontsize = 12, ha='center', color='black')
    
    plt.axis('off')
    plt.tight_layout()
    st.pyplot(fig)

#########################################

# Data load
df = import_data()
gdf = import_geojson()

merged_data = gdf.merge(df, left_on='MNIMI', right_on='Maakond') 
merged_data["Loomulik iive"] = merged_data["Mehed Loomulik iive"] + merged_data["Naised Loomulik iive"]

merged_data["Aasta"] = merged_data["Aasta"].astype(int)
year_list = sorted(merged_data["Aasta"].unique())

# Select year, Streamlit dropdown list
selected_year = st.selectbox("Select year:", year_list, index = len(year_list)-1)

# Graph
plot(get_data_for_year(merged_data, selected_year))

st.write("Data source: [here](https://andmed.stat.ee/api/v1/et/stat/RV032)")
