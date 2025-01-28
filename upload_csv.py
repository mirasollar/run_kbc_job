import csv
import pandas as pd
import io
import streamlit as st

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:


    # Načti soubor do paměti a dekóduj jako text
    raw_data = uploaded_file.read().decode("windows-1250", errors="replace")  # Nahraď špatné znaky
    
    # Zobraz prvních pár znaků souboru pro debugging
    st.write("File content preview (first 500 chars):")
    st.text(raw_data[:500])  # Ukázka prvních 500 znaků pro zjištění, co je na začátku

    # Použij StringIO pro vytvoření in-memory textového souboru
    converted_file = io.StringIO(raw_data)

    try:
        # Načti obsah jako seznam řádků pomocí knihovny csv
        reader = csv.reader(converted_file, delimiter=";")  # Přizpůsob oddělovač
        data = list(reader)  # Obsah celého CSV jako seznam seznamů
        
        if len(data) < 2:
            st.error("The file does not contain enough rows to extract data and header.")
        else:
            # První řádek je hlavička
            header = data[0]
            rows = data[1:]  # Všechny ostatní řádky

            # Vytvoř DataFrame
            df = pd.DataFrame(rows, columns=header)

    except Exception as e:
        st.error(f"Error while processing the file: {e}")
            

    st.write("DataFrame preview:")
    st.write(df)
