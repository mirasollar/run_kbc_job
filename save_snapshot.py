import streamlit as st
import pandas as pd
import io
import os
from streamlit.web.server.websocket_headers import _get_websocket_headers
from datetime import datetime
from datetime import timezone as dttimezone

now_utc = datetime.now(dttimezone.utc)
str_now_utc = now_utc.strftime('%Y-%m-%d, %H:%M:%S')
str_now_utc

headers = _get_websocket_headers()
st.write(headers["Host"])
st.write(headers["Origin"])

streamlit_protected_save = st.secrets["streamlit_protected_save"]
st.write(f"Streamlit protected save: {streamlit_protected_save}")

df = pd.DataFrame({"advertiser": ["Creditas", "Stavby, Brno"], "client_id": [4, 5]})

df_serialized = df.to_json(orient="records")
df_snapshots = pd.DataFrame({"timestamp": [str_now_utc], "nested_df": [df_serialized]})

df_restored = pd.read_json(df_snapshots.loc[0, "nested_df"])
st.write(df_restored)

# uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
