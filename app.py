import streamlit as st


st.set_page_config(
    page_title="Data Exporter",
    page_icon="📚",
    layout="wide"
)

st.title("Data Exporter")

st.write(
    """
    Application d'extraction de données d'articles.

    Pages disponibles :
    
    - ClinicalTrials.gov : récupération et export de données d'essais cliniques
    - Pubmed.ncbi.nlm.nih.gov : récupération et export d'articles scientifiques
    """
)