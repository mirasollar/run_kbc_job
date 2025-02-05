import streamlit as st
import pandas as pd
import io
import os
from streamlit.web.server.websocket_headers import _get_websocket_headers
from datetime import datetime
from datetime import timezone as dttimezone

def write_to_keboola(data, table_name, table_path, incremental):
    data.to_csv(table_path, index=False, compression='gzip')
    client.tables.load(
        table_id=table_name,
        file_path=table_path,
        is_incremental=incremental
    )


now_utc = datetime.now(dttimezone.utc)
str_now_utc = now_utc.strftime('%Y-%m-%d, %H:%M:%S')

name = 'mirda'

headers = _get_websocket_headers()
st.write(headers["Host"])
st.write(headers["Origin"])

streamlit_protected_save = st.secrets["streamlit_protected_save"]
st.write(f"Streamlit protected save: {streamlit_protected_save}")

df = pd.DataFrame({"advertiser": ["Creditas", "Stavby, Brno"], "client_id": [4, 5]})

df_serialized = df.to_json(orient="records")
df_snapshots = pd.DataFrame({"name": [name], "timestamp": [str_now_utc], "nested_df": [df_serialized]})
st.write(df_snapshots)

df_restored = pd.read_json(df_snapshots.loc[0, "nested_df"])
st.write(df_restored)

# write_to_keboola(edited_data, st.session_state["selected-table"],f'updated_data.csv.gz', False)

# uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
