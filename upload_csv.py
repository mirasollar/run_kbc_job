import io
from charset_normalizer import from_bytes
import streamlit as st
import pandas as pd

token = st.secrets["kbc_storage_token"]
kbc_url = url = st.secrets["kbc_url"]
kbc_token = st.secrets["kbc_token"]
streamlit_protected_save = st.secrets["streamlit_protected_save"]

st.write(f"KBC token: {token}")
st.write(f"KBC url: {kbc_url}")
st.write(f"KBC token: {kbc_token}")
st.write(f"Streamlit protected save: {streamlit_protected_save}")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Načti soubor jako bytes
    raw_data = uploaded_file.read()

    try:
        df = pd.read_csv(io.BytesIO(raw_data), sep=None, engine='python', encoding='utf-8-sig')
    except:
        result = from_bytes(raw_data).best()
        detected_encoding = result.encoding
        st.write(f"Detected encoding: {detected_encoding}")
        df = pd.read_csv(io.BytesIO(raw_data), sep=None, engine='python', encoding=detected_encoding)

    st.write(f"Datové typy: {df.dtypes}")

st.data_editor(df)
