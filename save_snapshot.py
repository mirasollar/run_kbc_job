import streamlit as st
import pandas as pd
import re
import io
import os
import csv
from datetime import datetime
from datetime import timezone as dttimezone
from kbcstorage.client import Client
import numpy as np

kbc_url = url = st.secrets["kbc_url"]
kbc_token = st.secrets["kbc_token"]
kbc_client = Client(kbc_url, kbc_token)

def get_now_utc():
    now_utc = datetime.now(dttimezone.utc)
    return now_utc.strftime('%Y-%m-%d, %H:%M:%S')

def get_table_name_suffix():
    headers = st.context.headers
    return re.sub('-', '_', headers['Host'].split('.')[0])

def get_password_dataframe(table_name):
    kbc_client.tables.export_to_file(table_id = table_name, path_name='.')
    return pd.read_csv(f"./{table_name.split('.')[2]}", low_memory=False)

# def verify_password(password, df_password):
#    return df_password[df_password["password"] == password].loc[1, "name"]

def get_username_by_password(password, df_passwords):
    match = df_passwords.loc[df_passwords['password'] == password, 'name']
    return match.iloc[0] if not match.empty else None

def write_snapshot_to_keboola(df_to_write):
    df_to_write.to_csv('snapshot_data.csv.gz', index=False, compression='gzip')
    kbc_client.tables.load(
        table_id=f"in.c-reference_tables_metadata.snapshots_{get_table_name_suffix()}",
        file_path='snapshot_data.csv.gz',
        is_incremental=True)

try:
    streamlit_protected_save = st.secrets["streamlit_protected_save"]
except:
    streamlit_protected_save = 'False'

password_input = st.text_input("Enter password:", type="password")
if st.button("Submit"):
    if "passwords" not in st.session_state:
        st.session_state.passwords = get_password_dataframe(f"in.c-reference_tables_metadata.passwords_{get_table_name_suffix()}")
    name = get_username_by_password(password_input, st.session_state.passwords)
    if name:
        st.write(f"Password is correct. Hello, {name}!")
        # df = pd.DataFrame({'advertiser': ['Creditas', 'Stavby "Domů", Brno'], 'client_id': [4, 5]})
        df = pd.DataFrame(np.random.randn(100, 5), columns = list("abcde"))
        df_serialized = df.to_json(orient="records")
        df_snapshot = pd.DataFrame({"name": [name], "timestamp": [get_now_utc()], "table": [df_serialized]})
        st.write(df_snapshot)
        write_snapshot_to_keboola(df_snapshot)
    else:
        st.error("Invalid password")
