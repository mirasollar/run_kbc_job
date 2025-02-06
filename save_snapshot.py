import streamlit as st
import pandas as pd
import io
import os
import csv
# from streamlit.web.server.websocket_headers import _get_websocket_headers
from datetime import datetime
from datetime import timezone as dttimezone
from kbcstorage.client import Client

kbc_url = url = st.secrets["kbc_url"]
kbc_token = st.secrets["kbc_token"]
st.write(f"KBC token: {kbc_token}")
kbc_client = Client(kbc_url, kbc_token)

now_utc = datetime.now(dttimezone.utc)
str_now_utc = now_utc.strftime('%Y-%m-%d, %H:%M:%S')

name = 'mirda'

headers = st.context.headers
st.write(headers["Host"])
st.write(headers["Origin"])

streamlit_protected_save = st.secrets["streamlit_protected_save"]
st.write(f"Streamlit protected save: {streamlit_protected_save}")

def get_password_dataframe(table_name):
    kbc_client.tables.export_to_file(table_id = table_name, path_name='.')
    df = pd.read_csv(f"./{table_name.split('.')[2]}", low_memory=False)
    return df

def verify_password(password, df_password):
    return df_password[df_password["password"] == password].loc[1, "name"]

def write_to_keboola(data, table_name, table_path, incremental):
    data.to_csv(table_path, index=False, compression='gzip')
    client.tables.load(
        table_id=table_name,
        file_path=table_path,
        is_incremental=incremental
    )

st.session_state['passwords_table_id'] = 'in.c-reference_tables_metadata.passwords_mso_dev_839334747'
# st.session_state['passwords_data'] = get_password_dataframe(st.session_state['passwords_table_id'])
# st.write(f"Passwords data: {st.session_state['passwords_data']}, data type: {type(st.session_state['passwords_data'])}")

# st.data_editor(st.session_state['passwords_data'])

# df = pd.DataFrame({"advertiser": ["Creditas", "Stavby, Brno"], "client_id": [4, 5]})

# df_serialized = df.to_json(orient="records")
# df_snapshots = pd.DataFrame({"name": [name], "timestamp": [str_now_utc], "nested_df": [df_serialized]})
# st.write(df_snapshots)

# df_restored = pd.read_json(df_snapshots.loc[0, "nested_df"])
# st.write(df_restored)

if "passwords" not in st.session_state:
    st.session_state.passwords = get_password_dataframe(st.session_state['passwords_table_id'])

def get_name_by_password(password: str) -> str | None:
    df = st.session_state.passwords
    match = df.loc[df['password'] == password, 'name']
    return match.iloc[0] if not match.empty else None

st.title("Login:")

password_input = st.text_input("Enter password:", type="password")
if st.button("Submit"):
    name = get_name_by_password(password_input)
    if name:
        st.success(f"Welcome, {name}!")
    else:
        st.error("Invalid password")


# write_to_keboola(edited_data, st.session_state["selected-table"],f'updated_data.csv.gz', False)

# uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
