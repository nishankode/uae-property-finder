import pandas as pd
import numpy as np
import streamlit as st
import warnings

# Configuration
st.set_page_config(layout="wide", page_title="UAE Real Estate Search")
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)

@st.cache_data
def load_and_clean_data():
    """
    Loads and cleans the real estate data.
    """
    file_path = 'data/cleaned_data/uae_realestate_old_cleaned.csv'
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return None

    # Renaming column names to snake case
    rename_map = {
        "Regis": "reg_date",
        "ProcedureValue": "procedure_value",
        "Master Project": "master_project",
        "Master Project Land": "master_project_land",
        "Project": "project",
        "Project Lnd": "project_land",
        "Building No": "building_no",
        "BuildingNameEn": "building_name_en",
        "Size": "size_sqmt",
        "UnitNumber": "unit_number",
        "DmSubNo": "dm_sub_no",
        "PropertyTypeEn": "property_type_en",
        "LandNumber": "land_number",
        "ProcedurePartyTypeNameEn": "procedure_type",
        "NameEn": "name_en",
        "Mobile": "mobile",
        "ProcedureNameEn": "procedure_name",
        "CountryNameEn": "country",
        "IdNumber": "id_number",
        "UaeIdNumber": "uae_id_number",
        "BirthDate": "birth_date"
    }
    df = df.rename(columns=rename_map)

    # Cleaning Mobile Numbers
    # (Note: This creates a separate dataframe in the original snippet, 
    # but the search functions use 'mobile' column in the main df. 
    # We include logic here in case future extensions need it, but main df is returned.)
    # The snippet logic filters a separate 'all_mobiles' DF. 
    # The main 'df' 'mobile' column is unmodified in the snippet except for being read.
    
    # Cleaning Date
    df['reg_date'] = pd.to_datetime(df['reg_date'])

    # Creating size_sqft
    df['size_sqft'] = df['size_sqmt'].apply(lambda x: round(x * 10.76391, 2))
    
    return df

# Helper Search Functions (as provided in snippet)
def search_name(name, df):
    matches = df[df['name_en'] == name]
    return matches

def search_id(_id, df):
    matches = df[(df['id_number'] == _id) | (df['uae_id_number'] == _id)]
    return matches

def search_phone(mobile, df):
    matches = df[df['mobile'] == mobile]
    return matches

def search_property(property_name=None, df=None, size_sqmt=None, size_sqft=None, transaction_date=None, unit_number=None):
    all_matches = df[
        (df['master_project'] == property_name) |
        (df['master_project_land'] == property_name) |
        (df['project'] == property_name) |
        (df['project_land'] == property_name) |
        (df['building_name_en'] == property_name)
    ]

    if size_sqmt:
        all_matches = all_matches[all_matches['size_sqmt'] == size_sqmt]

    if size_sqft:
        all_matches = all_matches[all_matches['size_sqft'] == size_sqft]
    
    if transaction_date:
        # Ensuring transaction_date is comparable (timestamp)
        transaction_date = pd.to_datetime(transaction_date)
        all_matches = all_matches[all_matches['reg_date'] == transaction_date]

    if unit_number:
        # Using string conversion for safety
        all_matches = all_matches[all_matches['unit_number'].astype(str).str.endswith(str(unit_number), na=False)]

    return all_matches

# Main App
def main():
    st.title("UAE Real Estate Data Search")

    with st.spinner("Loading data..."):
        df = load_and_clean_data()

    if df is None:
        st.error("Could not load data. Please ensure 'data/cleaned_data/uae_realestate_old_cleaned.csv' exists.")
        return

    # Sidebar Navigation
    st.sidebar.title("Search Options")
    search_type = st.sidebar.radio(
        "Choose a search method:",
        ("Name Search", "ID Search", "Phone Number Search", "Property Search")
    )

    results = pd.DataFrame()
    search_performed = False

    if search_type == "Name Search":
        st.subheader("Search by Name")
        name_input = st.text_input("Enter Name (Exact Match)", placeholder="e.g., DAOUD YAQUB")
        if st.button("Search Name"):
            search_performed = True
            if name_input:
                results = search_name(name_input, df)
            else:
                st.warning("Please enter a name.")

    elif search_type == "ID Search":
        st.subheader("Search by ID")
        id_input = st.text_input("Enter ID Number", placeholder="e.g., 530946649")
        if st.button("Search ID"):
            search_performed = True
            if id_input:
                results = search_id(id_input, df)
            else:
                st.warning("Please enter an ID.")

    elif search_type == "Phone Number Search":
        st.subheader("Search by Phone Number")
        phone_input = st.text_input("Enter Mobile Number", placeholder="e.g., 971-50-6544384")
        if st.button("Search Phone"):
            search_performed = True
            if phone_input:
                results = search_phone(phone_input, df)
            else:
                st.warning("Please enter a phone number.")

    elif search_type == "Property Search":
        st.subheader("Search by Property Details")
        
        prop_name = st.text_input("Property Name (Master Project, Project, or Building)", placeholder="e.g., OCEAN HEIGHTS")
        
        col1, col2 = st.columns(2)
        with col1:
            enable_sqmt = st.checkbox("Filter by Size (SqMt)")
            sqmt = st.number_input("Size (SqMt)", min_value=0.0, step=0.01, disabled=not enable_sqmt)
        
        with col2:
            enable_sqft = st.checkbox("Filter by Size (SqFt)")
            sqft = st.number_input("Size (SqFt)", min_value=0.0, step=0.01, disabled=not enable_sqft)

        col3, col4 = st.columns(2)
        with col3:
            enable_date = st.checkbox("Filter by Date")
            trans_date = st.date_input("Transaction Date", disabled=not enable_date)
        
        with col4:
            unit_no = st.text_input("Unit Number (Ends with)", placeholder="e.g., 06")

        if st.button("Search Property"):
            search_performed = True
            if prop_name:
                # Prepare arguments
                _sqmt = sqmt if enable_sqmt else None
                _sqft = sqft if enable_sqft else None
                _date = trans_date if enable_date else None
                _unit = unit_no if unit_no else None
                
                results = search_property(
                    property_name=prop_name, 
                    df=df, 
                    size_sqmt=_sqmt, 
                    size_sqft=_sqft, 
                    transaction_date=_date, 
                    unit_number=_unit
                )
            else:
                st.warning("Property Name is required for this search.")

    # Display Results
    if search_performed:
        st.markdown("---")
        st.subheader("Results")
        if not results.empty:
            st.success(f"Found {len(results)} records.")
            
            # Format Result Columns as requested
            desired_columns = [
                "reg_date", "procedure_value", "master_project", "master_project_land", 
                "project", "project_land", "building_no", "building_name_en", "size_sqmt", 
                "unit_number", "dm_sub_no", "property_type_en", "land_number", "procedure_type", 
                "name_en", "mobile", "procedure_name", "country", "id_number", "uae_id_number", 
                "birth_date", "size_sqft"
            ]
            # Select only existing columns
            cols_to_display = [c for c in desired_columns if c in results.columns]
            
            st.dataframe(results[cols_to_display])
        else:
            st.info("No matching records found.")

if __name__ == "__main__":
    main()
