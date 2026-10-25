import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd

def sync_dataframe_to_sheet(df: pd.DataFrame, sheet_name="Pokemon_Cardmarket_Data"):
    """
    Connecte l'application à Google Sheets via les secrets Streamlit 
    et remplace le contenu de la feuille par le nouveau DataFrame.
    """
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # Récupération sécurisée des accès depuis l'onglet "Secrets" de Streamlit Cloud
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
        client = gspread.authorize(creds)
        
        # Ouverture de la feuille Google Sheets par son nom
        sheet = client.open(sheet_name).sheet1
        
        # Effacement de l'ancien contenu et écriture des nouvelles données
        sheet.clear()
        data_to_send = [df.columns.tolist()] + df.values.tolist()
        sheet.update('A1', data_to_send)
        
        return True
        
    except Exception as e:
        print(f"Erreur de synchronisation Google Sheets : {e}")
        return False
