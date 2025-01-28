import csv
import pandas as pd
import io
import streamlit as st

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    file_content = uploaded_file.read()
    try:
        df = pd.read_csv(io.BytesIO(file_content), sep=None, engine='python', encoding='utf-8-sig')
    except:
        raw_data = file_content.decode("windows-1250", errors="replace")  # Nahraď špatné znaky
        # Zobraz prvních pár znaků souboru pro debugging
        st.write("File content preview (first 500 chars):")
        st.text(raw_data[:500])  # Ukázka prvních 500 znaků pro zjištění, co je na začátku
        converted_file = io.StringIO(raw_data)
        try:v
            reader = csv.reader(converted_file, delimiter=";")  # Přizpůsob oddělovač
            data = list(reader)
            if len(data) < 2:
                st.error("The file does not contain enough rows to extract data and header.")
            else:
                header = data[0]
                rows = data[1:]
                df = pd.DataFrame(rows, columns=header)
        except Exception as e:
            st.error(f"Error while processing the file: {e}")        

    st.write(df)
