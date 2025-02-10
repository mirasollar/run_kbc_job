import streamlit as st
import pandas as pd
import re
import io
import os
import csv
# from streamlit.web.server.websocket_headers import _get_websocket_headers
from datetime import datetime
from datetime import timezone as dttimezone
from kbcstorage.client import Client

kbc_url = url = st.secrets["kbc_url"]
kbc_token = st.secrets["kbc_token"]
kbc_client = Client(kbc_url, kbc_token)

now_utc = datetime.now(dttimezone.utc)
str_now_utc = now_utc.strftime('%Y-%m-%d, %H:%M:%S')

name = 'mirda'

headers = st.context.headers
table_name_suffix = re.sub('-', '_', headers['Host'].split('.')[0])
st.write(f"table_name_suffix: {table_name_suffix}")

try:
    streamlit_protected_save = st.secrets["streamlit_protected_save"]
except:
    streamlit_protected_save = 'False'
    
st.write(f"Streamlit protected save: {streamlit_protected_save}")

def get_password_dataframe(table_name):
    kbc_client.tables.export_to_file(table_id = table_name, path_name='.')
    df = pd.read_csv(f"./{table_name.split('.')[2]}", low_memory=False)
    return df

def verify_password(password, df_password):
    return df_password[df_password["password"] == password].loc[1, "name"]

def write_snapshot_to_keboola():
    df_snapshots.to_csv('snapshot_data.csv.gz', index=False, compression='gzip')
    kbc_client.tables.load(
        table_id=st.session_state['snapshots_table_id'],
        file_path='snapshot_data.csv.gz',
        is_incremental=True
    )

st.session_state['passwords_table_id'] = f"in.c-reference_tables_metadata.passwords_{table_name_suffix}"
st.session_state['snapshots_table_id'] = f"in.c-reference_tables_metadata.snapshots_{table_name_suffix}"

if "passwords" not in st.session_state:
    st.session_state.passwords = get_password_dataframe(st.session_state['passwords_table_id'])

def get_username_by_password(password):
    df = st.session_state.passwords
    match = df.loc[df['password'] == password, 'name']
    return match.iloc[0] if not match.empty else None

st.write(f"All files: {os.listdir()}")

password_input = st.text_input("Enter password:", type="password")
if st.button("Submit"):
    name = get_username_by_password(password_input)
    if name:
        st.write("success")
        df = pd.DataFrame({'advertiser': ['Creditas', 'Stavby, Brno'], 'client_id': [4, 5]})
        df_serialized = df.to_json(orient="records")
        df_snapshots = pd.DataFrame({"name": [name], "timestamp": [str_now_utc], "table": [df_serialized]})
        st.write(df_snapshots)
        write_snapshot_to_keboola()
    else:
        st.error("Invalid password")


# uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
