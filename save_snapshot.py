import streamlit as st
import pandas as pd
import io
import os
from streamlit.web.server.websocket_headers import _get_websocket_headers

headers = _get_websocket_headers()
st.write(headers["Host"])

streamlit_protected_save = st.secrets["streamlit_protected_save"]
st.write(f"Streamlit protected save: {streamlit_protected_save}")



headers = _get_websocket_headers()
st.write(headers["Host"])

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
