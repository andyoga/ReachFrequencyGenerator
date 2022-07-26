import pandas as pd
import numpy as np
#import bamboolib as bam
import datetime
import time
import csv
import streamlit as st
import openpyxl

st.title('Reach Frequency Export File Generator')
st.write('Please input original file with filename as ReachFreq.xlsx.')
st.write('Main tab containing data to be converted should be named as Main. Lookup tab containing station lookup codes should be named as Lookup.')
st.write('Main data tab should include the following columns: Station Name, Name, Date, and Time Real.')

# configuration
st.set_option('deprecation.showfileUploaderEncoding', False)

uploaded_file = st.file_uploader(label="Upload your xlsx file here.", type=['xlsx'])


global df_main_raw
global df_lookup_raw

if uploaded_file is not None:
    print(uploaded_file)
    # try:
    df_main_raw = pd.read_excel(uploaded_file, 'Main', dtype = str, engine='openpyxl')
    df_lookup_raw = pd.read_excel(uploaded_file, 'Lookup', dtype = str, engine='openpyxl')
    # except Exception as e:
    #     print(e)
        
st.write('Main Data Table')
st.dataframe(df_main_raw)
st.write('Station Code Lookup Table')
st.dataframe(df_lookup_raw)


df_main_raw = df_main_raw[['Station Name', 'Name', 'Date     ', 'Time Real']]
df_main_raw = df_main_raw[df_main_raw['Time Real'].notnull()]
df_main_raw['Date     '] = df_main_raw['Date     '].astype('string')
df_main_raw['Time Real'] = df_main_raw['Time Real'].astype('string')
df_main_raw["StartTime"] = df_main_raw['Date     ']+" "+df_main_raw['Time Real']
df_main_raw['StartTime'] = pd.to_datetime(df_main_raw['StartTime'], infer_datetime_format=True)
df_main_raw["EndTime"] = df_main_raw['StartTime']+datetime.timedelta(0,30)
df_main_raw['StartTime'] = df_main_raw['StartTime'].astype('string')
df_main_raw['EndTime'] = df_main_raw['EndTime'].astype('string')
split_df = df_main_raw['StartTime'].str.split('\ ', expand=True)
split_df.columns = ['StartTime' + f"_{id_}" for id_ in range(len(split_df.columns))]
df_main_raw = pd.merge(df_main_raw, split_df, how="left", left_index=True, right_index=True)
split_df = df_main_raw['EndTime'].str.split('\ ', expand=True)
split_df.columns = ['EndTime' + f"_{id_}" for id_ in range(len(split_df.columns))]
df_main_raw = pd.merge(df_main_raw, split_df, how="left", left_index=True, right_index=True)
df_main_raw = df_main_raw.drop(columns=['Date     ', 'Time Real', 'StartTime', 'EndTime', 'EndTime_0'])
df_main_raw["StartTime_0"] = df_main_raw["StartTime_0"].str.replace('-', '', regex=False)
df_main_raw["StartTime_1"] = df_main_raw["StartTime_1"].str.replace(':', '', regex=False)
df_main_raw["EndTime_1"] = df_main_raw["EndTime_1"].str.replace(':', '', regex=False)
df_main_raw = df_main_raw.rename(columns={'StartTime_0': 'Date'})
df_main_raw = df_main_raw.rename(columns={'StartTime_1': 'StartTime'})
df_main_raw = df_main_raw.rename(columns={'EndTime_1': 'EndTime'})
df_main_raw = pd.merge(df_main_raw, df_lookup_raw, how='inner', left_on=['Station Name'], right_on=['Station'])
df_main_raw['Name'] = df_main_raw['Name'].str.strip()
# # #df_main_raw



df_main_raw = df_main_raw[['Date', 'Code', 'StartTime', 'EndTime', 'Name']]
st.write('Joined table to be exported')
st.dataframe(df_main_raw)


timestr = time.strftime("%Y%m%d-%H%M%S")
df_main_raw = df_main_raw.applymap(lambda x: str(x).replace(' ', u"\u00A0"))
# # df_main_raw.to_csv(r'ReachFrequency_'+timestr+'.txt', header=None, index=None, sep=' ', mode='a') 

st.download_button(label = "Download File", 
                     data = df_main_raw.to_csv(header=None, index=None, sep=' ', mode='a'),
                     file_name='output_'+timestr+'.txt',
                     mime = 'text/csv')

