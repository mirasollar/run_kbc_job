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
from streamlit_js_eval import streamlit_js_eval

CORRECT_PASSWORD = "tajneheslo"

# Získání hodnoty z Local Storage
auth_state = streamlit_js_eval(js_expressions="localStorage.getItem('authenticated') || 'false'", key="get_auth")

# Konverze na bool
is_authenticated = auth_state == "true"

# Pokud uživatel není přihlášen
if not is_authenticated:
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if password == CORRECT_PASSWORD:
            # Uložení do Local Storage
            streamlit_js_eval(js_expressions="localStorage.setItem('authenticated', 'true')", key="set_auth")
            st.rerun()
        else:
            st.error("❌ Incorrect password!")

# Pokud je přihlášený
if is_authenticated:
    st.success("✅ You are logged in!")
    if st.button("Save Table"):
        st.success("Table saved successfully!")

kbc_url = url = st.secrets["kbc_url"]
kbc_token = st.secrets["kbc_token"]
kbc_client = Client(kbc_url, kbc_token)

try:
    streamlit_protected_save = st.secrets["streamlit_protected_save"]
except:
    streamlit_protected_save = 'False'

def get_now_utc():
    now_utc = datetime.now(dttimezone.utc)
    return now_utc.strftime('%Y-%m-%d, %H:%M:%S')

def get_table_name_suffix():
    headers = st.context.headers
    return re.sub('-', '_', headers['Host'].split('.')[0])

def get_password_dataframe(table_name):
    kbc_client.tables.export_to_file(table_id = table_name, path_name='.')
    return pd.read_csv(f"./{table_name.split('.')[2]}", low_memory=False)

def get_username_by_password(password, df_passwords):
    match = df_passwords.loc[df_passwords['password'] == password, 'name']
    return match.iloc[0] if not match.empty else None

def write_snapshot_to_keboola(df_to_write):
    df_to_write.to_csv('snapshot_data.csv.gz', index=False, compression='gzip')
    kbc_client.tables.load(
        table_id=f"in.c-reference_tables_metadata.snapshots_{get_table_name_suffix()}",
        file_path='snapshot_data.csv.gz',
        is_incremental=True)

df = pd.DataFrame({'advertiser': ['Creditas', 'Stavby "Domů", Brno'], 'client_id': [4, 5]})
st.write(f"Dataframe s daty: {df}")

if "user_name" not in st.session_state:
    st.session_state['user_name'] = None
    
# password_input = st.text_input("Enter password:", type="password")
password_input = ''
if st.button("Submit"):
    if "passwords" not in st.session_state:
        st.session_state['passwords'] = get_password_dataframe(f"in.c-reference_tables_metadata.passwords_{get_table_name_suffix()}")
    st.session_state['user_name'] = get_username_by_password(password_input, st.session_state['passwords'])
    st.write(f"User name: {st.session_state['user_name']}")
    if st.session_state['user_name'] != None:
        st.write(f"Password is correct. Hello, {st.session_state['user_name']}!")
        df_serialized = df.to_json(orient="records")
        df_snapshot = pd.DataFrame({"name": [st.session_state['user_name']], "timestamp": [get_now_utc()], "table": [df_serialized]})
        st.write(df_snapshot)
        write_snapshot_to_keboola(df_snapshot)
    else:
        st.error("Invalid password")
