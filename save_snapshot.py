import io
from charset_normalizer import from_bytes
import streamlit as st
import pandas as pd

streamlit_protected_save = st.secrets["streamlit_protected_save"]
st.write(f"Streamlit protected save: {streamlit_protected_save}")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
