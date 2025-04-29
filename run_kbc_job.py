import streamlit as st
import streamlit.components.v1 as components
from streamlit_card import card
from kbcstorage.client import Client
import os
import csv
import pandas as pd
import datetime
from datetime import timezone as dttimezone
import time
from pathlib import Path
import re
import json
import numpy as np
import io
from charset_normalizer import from_bytes
import requests

# Setting page config
st.set_page_config(page_title="Keboola Data Editor", page_icon=":robot:", layout="wide")

# Constants
token = st.secrets["kbc_storage_token"]
kbc_url = url = st.secrets["kbc_url"]
kbc_token = st.secrets["kbc_token"]
config_id = st.secrets["config_id"]
LOGO_IMAGE_PATH = os.path.abspath("./app/static/keboola.png")

# Initialize Client
client = Client(kbc_url, token)
kbc_client = Client(kbc_url, kbc_token)

try:
    logged_user = st.secrets["logged_user"]
except:
    logged_user = 'False'

try:
    saving_snapshot = st.secrets["saving_snapshot"]
except:
    saving_snapshot = 'False'

# Fetching data 
@st.cache_data(ttl=60,show_spinner=False)
def get_dataframe(table_name):
    table_detail = client.tables.detail(table_name)

    client.tables.export_to_file(table_id = table_name, path_name='')
    list = client.tables.list()
    
    with open('./' + table_detail['name'], mode='rt', encoding='utf-8') as in_file:
        lazy_lines = (line.replace('\0', '') for line in in_file)
        reader = csv.reader(lazy_lines, lineterminator='\n')
    if os.path.exists('data.csv'):
        os.remove('data.csv')
    else:
        print("The file does not exist")
    
    os.rename(table_detail['name'], 'data.csv')
    df = pd.read_csv('data.csv')
    df = cast_columns(df)
    return df

# Initialization
def init():
    if 'selected-table' not in st.session_state:
        st.session_state['selected-table'] = None

    if 'tables_id' not in st.session_state:
        st.session_state['tables_id'] = pd.DataFrame(columns=['table_id'])
    
    if 'data' not in st.session_state:
        st.session_state['data'] = None 

    if "edited_data" not in st.session_state:
        st.session_state["edited_data"] = None 
    
    if "show_downloads" not in st.session_state:
        st.session_state["show_downloads"] = False

    if "user_name" not in st.session_state:
        st.session_state['user_name'] = None
    
    if "run_job" not in st.session_state:
        st.session_state["run_job"] = False

def update_session_state(table_id):
    with st.spinner('Loading ...'):
        st.session_state['selected-table'] = table_id
        st.session_state['data'] = get_dataframe(st.session_state['selected-table'])
    st.rerun()
     
def display_table_card(row):
    today = datetime.date.today()
    st.write(f"last_import_date_dt: {today}")
    last_import_date_time = row['lastImportDate']
    last_import_date = last_import_date_time.split('T')[0]
    last_import_date_dt = datetime.datetime.strptime(last_import_date, '%Y-%m-%d').date()
    st.write(f"last_import_date_dt: {last_import_date_dt}")

    # Spočítat rozdíl ve dnech
    days_diff = (today - last_import_date_dt).days

    # Připravit text pro tooltip
    if days_diff == 0:
        tooltip_text = "Updated today"
        circle_color = "#00C853"  # zelená
    elif days_diff == 1:
        tooltip_text = f"Updated {days_diff} day ago"
        circle_color = "#D50000"  # červená
    else:
        tooltip_text = f"Updated {days_diff} days ago"
        circle_color = "#D50000"  # červená

    # HTML pro barevné kolečko
    status_dot_html = f'''
        <div title="{tooltip_text}" style="
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: {circle_color};
            margin-right: 8px;
            vertical-align: middle;
            cursor: help;
        "></div>
    '''

    card(
        title=f"{status_dot_html}{row['displayName']}",  # Kolečko + název
        text=[f"Table ID: {row['table_id']}", f"Updated at: {last_import_date}"],
        styles={
            "card": {
                "width": "100%",
                "height": "100px",
                "box-shadow": "2px 2px 12px rgba(0,0,0,0.1)",
                "margin": "0px",
                "flex-direction": "column",
                "align-items": "flex-start",
            },
            "filter": {
                "background-color": "#FFFFFF"
            },
            "div": {
                "padding": "0px",
                "display": "flex",
                "align-items": "flex-start",
            },
            "text": {
                "color": "#999A9F",
                "padding-left": "5%",
                "align-self": "flex-start",
                "font-size": "15px",
                "font-weight": "lighter",
            },
            "title": {
                "font-size": "24px",
                "color": "#1F8FFF",
                "padding-left": "5%",
                "align-self": "flex-start",
            }
        },
        image="https://upload.wikimedia.org/wikipedia/en/4/48/Blank.JPG",
        key=row['table_id'],
        on_click=lambda table_id=row['table_id']: update_session_state(table_id),
        unsafe_allow_html=True,  # Důležité! Povolit HTML v title
    )

def ChangeButtonColour(widget_label, font_color, background_color, border_color):
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.color ='{font_color}';
                    elements[i].style.background = '{background_color}';
                    elements[i].style.borderColor = '{border_color}';
                }}
            }}
        </script>
        """
    components.html(f"{htmlstr}", height=0, width=0)

# Fetch and prepare table IDs and short description
@st.cache_data(ttl=60)

def fetch_all_ids():
    df = pd.DataFrame()
    bucket_ids = [bucket["id"] for bucket in client.buckets.list()]
    all_tables_in_buckets = [client.buckets.list_tables(bucket_id) for bucket_id in bucket_ids]
    for tables in all_tables_in_buckets:
        ids_list = [{
            'table_id': table["id"],
            'displayName': table["displayName"],
            'lastImportDate': table['lastImportDate'],
            'created': table['created']
        } for table in tables]
        df_stage = pd.DataFrame(ids_list)
        df = pd.concat([df, df_stage])
    return df

# Definujte callback funkci pro tlačítko
def on_click_update_data():
    st.session_state["run_job"] = True

# Definujte callback funkci pro tlačítko
def on_click_back():
    st.session_state["run_job"] = False

# Function to display a table section
# table_name, table_id ,updated,created
def display_table_section(row):
    with st.container():
        display_table_card(row)

def display_footer_section():
    left_aligned, space_col, right_aligned = st.columns((2,7,1))
    with left_aligned:
        st.caption(f"© Keboola & Seznam.cz {datetime.datetime.now().year}")
    # with right_aligned:
    #    st.caption("Version 2.0")

def write_to_keboola(data, table_name, table_path, purpose):
    """
    Writes the provided data to the specified table in Keboola Connection, updating existing records as needed.

    Args:
        data (pandas.DataFrame): The data to write to the table.
        table_name (str): The name of the table to write the data to.
        table_path (str): The local file path to write the data to before uploading.
    """

    # Write the DataFrame to a CSV file with compression
    data.to_csv(table_path, index=False, compression='gzip')

    # Load the CSV file into Keboola, updating existing records
    if purpose == "reference_table":
        client.tables.load(
            table_id=table_name,
            file_path=table_path,
            is_incremental=False
        )
    elif purpose == "snapshot":
        kbc_client.tables.load(
            table_id=table_name,
            file_path=table_path,
            is_incremental=True
        )

def resetSetting():
    st.session_state['selected-table'] = None
    st.session_state['data'] = None
    st.session_state["show_downloads"] = False

def toggle_downloads():
    st.session_state["show_downloads"] = not st.session_state["show_downloads"]

def cast_columns(df):
    """Ensure that columns that should be boolean are explicitly cast to boolean."""
    for col in df.columns:
        # If a column in the DataFrame has only True/False values, cast it to bool, NaN cast to string
        if df[col].dropna().isin([True, False]).all() and not df[col].dropna().isin([np.nan]).all():
            df[col] = df[col].astype(bool)
            # df[col] = pd.Series(df[col], dtype="string")
        elif df[col].dropna().isin([np.nan]).all():
            df[col] = pd.Series(df[col], dtype="string")
    return df

def split_table_id(selected_table_id):
    table_id_split = selected_table_id.split('.')
    bucket_name = table_id_split[0] + '.' + table_id_split[1]
    table_name = table_id_split[2]
    return bucket_name, table_name

def split_datetime(dt):
    return f"Date: {dt.split('T')[0]}, Time: {dt.split('T')[1]}"

def create_column_config(df_to_edit):
    column_config = {}
    col_types_dict = df_to_edit.dtypes.astype(str).to_dict()
    for k, v in col_types_dict.items():
        if v == 'int64':
            column_config[k] = st.column_config.NumberColumn(format="%d")
    return column_config

def create_table_info(json_data):
    table_id = json_data['id']
    display_name = json_data['displayName']
    last_import_date = json_data['lastImportDate']
    data = {
        'table_id': [table_id],
        'displayName': [display_name],
        'lastImportDate': [last_import_date],
    }
    df = pd.DataFrame(data)
    return df

def prepare_downloaded_data():
    downloaded_data = st.session_state['data']
    # downloaded_data = cast_columns(st.session_state['data'])
    # downloaded_data = modifying_nas(downloaded_data)
    # downloaded_data = delete_decimal_zero(downloaded_data)
    return downloaded_data

def generate_download_file(data, file_format):
    buffer = io.BytesIO() if file_format == "xlsx" else io.StringIO()
    if file_format == "csv":
        data.to_csv(buffer, index=False)
        mime = 'text/csv'
        ext = "csv"
    elif file_format == "tsv":
        data.to_csv(buffer, sep='\t', index=False)
        mime = 'text/tab-separated-values'
        ext = "txt"
    elif file_format == "xlsx":
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data.to_excel(writer, index=False)
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ext = "xlsx"
    else:
        return None, None, None
    return buffer.getvalue(), mime, ext

def run_transformation(config_id):
    body = {"mode":"run","component":"keboola.python-transformation-v2","config":config_id}
    try:
        res = requests.post('https://queue.eu-central-1.keboola.com/jobs', headers={"content-type": "application/json", "x-storageapi-token":token},
                  json=body)
        print(res.status_code)
        res.raise_for_status()
        data_json = res.json()
        try:
            return data_json["id"]
        except:
            logging.error(f"Error: {data_json}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Status Code: {e.response.status_code}, Message: {e}")
    except Exception as e:
        logging.error(f"An unexpected error has occurred (get_users): {e}")


def get_job_status(job_id):
    try:
        res = requests.get(f'https://queue.eu-central-1.keboola.com/jobs/{job_id}', headers={"content-type": "application/json", "x-storageapi-token":token})
        print(res.status_code)
        res.raise_for_status()
        data_json = res.json()
        try:
            return data_json["status"]
        except:
            logging.error(f"Error: {data_json}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Status Code: {e.response.status_code}, Message: {e}")
    except Exception as e:
        logging.error(f"An unexpected error has occurred (get_users): {e}")
        
# Display tables
init()
st.session_state["tables_id"] = fetch_all_ids()

if st.session_state['selected-table'] is None and (st.session_state['run_job'] is None or st.session_state['run_job'] == False):
    #LOGO
      # Place an image in the first column
    col1, col2, col3 = st.columns((1,7,2))
    with col1:
        st.image(LOGO_IMAGE_PATH)

        hide_img_fs = '''
        <style>
        button[title="View fullscreen"]{
            visibility: hidden;}
        </style>
        '''

        st.markdown(hide_img_fs, unsafe_allow_html=True)

    #Keboola title
    st.markdown("""<h1><span style="color:#1F8FFF;">Keboola</span> Data Editor</h1>""", unsafe_allow_html=True)
    st.info('Select the table you want to view.', icon="ℹ️")

    # Title of the Streamlit app
    st.subheader("Tables")

    # Search bar and sorting options
    search_col, sort_col, but_col1, col_upload = st.columns((50,25,10,15))

    # with but_col1:
    #     if st.button("Reload Data", key="reload-tables", use_container_width = True, type="secondary"):
    #         st.session_state["tables_id"] = fetch_all_ids()
    #         st.toast('Tables List Reloaded!', icon = "✅")

    with search_col:
        search_query = st.text_input("Search for table", placeholder="Table Search",label_visibility="collapsed")

    with sort_col:
        sort_option = st.selectbox("Sort By Name", ["Sort By Name", "Sort By Date Created", "Sort By Date Updated"],label_visibility="collapsed")
    
    with col_upload:
        if st.button("Update Data", on_click=on_click_update_data, use_container_width = True):
            pass

    # Filtrace dat podle vyhledávacího dotazu
    if search_query:
        filtered_df = st.session_state["tables_id"][st.session_state["tables_id"].apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]
    else:
        filtered_df = st.session_state["tables_id"]
    
    # Třídění dat
    if sort_option == "Sort By Name":
        filtered_df = filtered_df.sort_values(by="displayName", ascending=True)
    elif sort_option == "Sort By Date Created":
        filtered_df = filtered_df.sort_values(by="created", ascending=False)
    elif sort_option == "Sort By Date Updated":
        filtered_df = filtered_df.sort_values(by="lastImportDate", ascending=False)

    # Looping through each row of the Tables ID
    for index, row in filtered_df.iterrows():
        display_table_section(row)
        # row['displayName'], row['table_id'],row['lastImportDate'],row['created']

elif st.session_state['selected-table'] is not None:
    col1,col2,col4= st.columns((2,7,2))
    with col1:
        st.button(":gray[:arrow_left: Back to Tables]", on_click=resetSetting, type="secondary")

    # Data Editor
    st.title("Data Editor")
  
    # Info
    st.info('After clicking on download data, you will see the option to download data in XLSX, TSV and CSV.', icon="ℹ️")

    #Select Box
    option = st.selectbox("Select Table", st.session_state["tables_id"], index=None, placeholder="Select table",label_visibility="collapsed")
    if option:
        st.session_state['selected-table'] = option
        st.session_state['data'] = get_dataframe(st.session_state['selected-table'])
       
    # Expander with info about table
    with st.expander("Table Info"):
        # Filter the DataFrame to find the row for the selected table_id
        table_detail_json = client.tables.detail(st.session_state['selected-table'])
        selected_row = create_table_info(table_detail_json)
        # Convert the row to a Series to facilitate access
        selected_row = selected_row.iloc[0]
        st.markdown(f"**Table ID:** {selected_row['table_id']}")
        st.markdown(f"**Updated at:** {split_datetime(selected_row['lastImportDate'])}")

    st.button("Download Data", on_click=toggle_downloads, help="Click to show download options")

    # and st.session_state.get('data') is not None:
    if st.session_state["show_downloads"]:
        downloaded_file_name = split_table_id(st.session_state['selected-table'])[1]
        col5, col6, col7 = st.columns([1, 1, 6])
        with col5:
            data, mime, ext = generate_download_file(prepare_downloaded_data(), "csv")
            st.download_button(label="Download CSV", data=data, file_name=f"{downloaded_file_name}.{ext}", mime=mime)
    
        with col6:
            data, mime, ext = generate_download_file(prepare_downloaded_data(), "tsv")
            st.download_button(label="Download TSV", data=data, file_name=f"{downloaded_file_name}.{ext}", mime=mime)
    
        with col7:
            data, mime, ext = generate_download_file(prepare_downloaded_data(), "xlsx")
            st.download_button(label="Download XLSX", data=data, file_name=f"{downloaded_file_name}.{ext}", mime=mime)

    
    edited_data = st.data_editor(st.session_state['data'], num_rows="dynamic", height=500, use_container_width=True,
                                 column_config=create_column_config(st.session_state['data']))

    ChangeButtonColour('Save Data', '#FFFFFF', '#1EC71E','#1EC71E')
elif st.session_state['run_job']:
    if st.button(":gray[:arrow_left: Go back]", on_click=on_click_back):
        pass

    st.title("Update data")

    if st.button("Update"):
        with st.spinner("Updating data..."):
            job_id = run_transformation(config_id)
            status = 'processing'
            with st.empty():
                while status == 'processing' or status == 'created':
                    status = get_job_status(job_id)
                    st.markdown("🔄 Waiting for completion...")
                    time.sleep(2)
                    
        if status == 'success':
            msg_placeholder = st.empty()
            msg_placeholder.success("✅ Data is now up to date")
            time.sleep(5)
            msg_placeholder.empty()
            st.session_state['run_job'] = False
            st.cache_data.clear()
            st.rerun()

        if status == 'error' or status == 'warning':
            msg_placeholder = st.empty()
            msg_placeholder.error("🚨 The update ended with an error. Contact support: (miroslav.sollar@firma.seznam.cz).")

display_footer_section()
