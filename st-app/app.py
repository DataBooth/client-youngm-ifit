##__all__ = ['DATA_INFO', 'AUTHOR_INFO', 'APP_NAME', 
##            'SideBar', 'app_sidebar', 'IMAGE_PATH', 
##           'load_cached_data', 'app_mainscreen', 'sb']

import numpy as np
import pandas as pd
import datetime as dt
import csv

from pathlib import Path
import streamlit as st
from bs4 import BeautifulSoup

from PIL import Image
from IPython.display import display

from databooth.convert_data import set_local_or_remote_data_path, convert_csv_row_to_xml

from databooth.parse_tcx import get_tcx_lap_data, get_tcx_point_data, get_dataframes

# TODO: Link in read .toml config & secrets

DATA_INFO = 'Supplied by Client (YoungM)'
AUTHOR_INFO = 'Aaron Chin @ DataBooth.com.au'
APP_NAME = "iFit Data Conversion app"
CACHED_DATA = 'TODO: Data cache file'
CLIENT_NAME = 'Mick Young'

st.set_page_config(page_title=APP_NAME, layout='wide')

AVATAR_URL = "https://www.w3schools.com/howto/img_avatar.png"
IFIT_BRAND_URL = "https://images.contentstack.io/v3/assets/blt1d89a78b502b83f3/blt000cfbfbc534f253/615468f7c3934450a14e3233/img_bikes_hero_dsk.jpg?q=90"

#IMAGE_PATH = 'st-app/resources'
#IMAGE_PATH = Path.cwd().resolve()/IMAGE_PATH

DATAFILE_PATH = "data"
DATAFILE_CSV  = "2021_09_26_17_09_Chamonix_Ride_Part_1,_France.csv"
DATAFILE_URL_PATH = "https://raw.githubusercontent.com/DataBooth/client-youngm-ifit/main/data/" 
DATAFILE_URL = DATAFILE_URL_PATH + DATAFILE_CSV.replace(",", "%2C")


FILENAME_TCX = "2021_09_26_17_09_Chamonix_Ride_Part_1,_France.tcx"
FILEPATH = "../data"
DATAFILE_TCX = FILEPATH / Path(FILENAME_TCX)

#def ST_APP_CONFIG_TOML = Path().cwd().parent / \"app_secrets.toml\" - TODO: TT to refactor
class SideBar:
    app_name = APP_NAME
    client_name = CLIENT_NAME
    datasource = DATA_INFO
    author = AUTHOR_INFO
    data_title = 'Data details...'
    data_local = False
    file_name = "Select CSV file..."


def app_sidebar(APP_NAME):
    sb = SideBar()
    st.sidebar.info("Menu")
    st.sidebar.image(image=IFIT_BRAND_URL, use_column_width=True, output_format='PNG')
    st.sidebar.markdown(sb.author)
    return sb

def extract_data_from_tcx_with_soup(DATAFILE_TCX, data_cols):
    with open(DATAFILE_TCX.as_posix(), 'r') as myFile:
        soup = BeautifulSoup(myFile, features="lxml-xml")

        data = []
        for item in data_cols:
            data.append(soup(item))
        df_xml = pd.DataFrame(data)
        return df_xml

# @st.cache
def load_and_cache_data():
    data_df = pd.read_feather(CACHED_DATA)   # load cached (downsampled) data
    return data_df

def app_mainscreen(APP_NAME, sb):
    st.header(APP_NAME + " // " + CLIENT_NAME)

    if sb.data_local == True:
        csv_file_name = st.file_uploader("Name of CSV data file to convert?", type=['csv']) # CSV file uploader tool
        tcx_file_name = st.file_uploader("Name of TCX data file you would like to merge", type = ['tcx']) # TCX file uploader tool
    
    else:
        DATASOURCE_TYPE = "gh"
        csv_file_name, tcx_file_name = set_local_or_remote_data_path(DATASOURCE_TYPE, DATAFILE_PATH, DATAFILE_CSV, DATAFILE_URL)
        st.write("CSV: " + csv_file_name)
        st.write("TCX: " + tcx_file_name)

    # Converting the CSV file into a dataframe
    data_df = pd.DataFrame()

    if csv_file_name is not None:
        data_df = pd.read_csv(csv_file_name, skiprows=2)

    data_df.rename(columns={"Relative Resistance": "RelativeResistance"}, inplace=True)

    show_raw_csv = st.checkbox("Show raw CSV data")
    if show_raw_csv:
        st.write(data_df)

    # Converting the TCX file into a dataframe
    if tcx_file_name is not None:
        df_cols = ["DistanceMeters", "Cadence", "Calories", "HeartRateBPM", "Time", "AltitudeMeters", "LongitudeDegrees", "LatitudeDegrees"]

        df_xml = extract_data_from_tcx_with_soup(DATAFILE_TCX, df_cols)
        st.write(df_xml)

        try:    
            df_cols = ["DistanceMeters", "Cadence", "Calories", "HeartRateBPM", "Time", "AltitudeMeters", "LongitudeDegrees", "LatitudeDegrees"]
            rows = []

            tcx_df = extract_data_from_tcx_with_soup(DATAFILE_TCX, data_cols)
            tcx_df2 = tcx_df.T
            tcx_df2.columns = data_cols

            show_raw_xml = st.checkbox("Show raw XML data")
            if show_raw_xml:
                st.write(tcx_df2)

        except Exception as e:
            st.write(e)


    # MERGING THE TWO
    final_df = pd.merge(tcx_df2, data_df, on = "Time")

    # csv counts in seconds
    # tcx time column is the specific time.


    # EXPORTING THE DATAFRAME (CSV, XML)
    export_csv = st.checkbox("Export to CSV")
    if export_csv:
        final_df.to_csv(r'DATAFILE_URL', index = False)

    #export_tcx = st.checkbox("Export to XML")
    #if export_tcx:

sb = app_sidebar(APP_NAME)

app_mainscreen(APP_NAME, sb)

# TODO: display XML bug?
# TODO: join tcx to csv on date/time?
# TODO: define testing
# TODO: do testing
# TODO: complete documentation
# TODO: refactor and retest
