import os
import streamlit as st
import pandas as pd
from scraper import scrape_cardmarket_extension
from google_sheets import sync_dataframe_to_sheet

# --- INSTALLATION AUTOMATIQUE DE PLAYWRIGHT ---
@st.cache_resource
def install_playwright():
    os.system("playwright install chromium")

install_playwright()

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="KanedaPk - Cardmarket Scanner", layout="wide")

st.title("🎴 Cardmarket Scanner & Google Sheets Sync")

# --- BARRE LATÉRALE DE CONFIGURATION ---
st.sidebar.header("🎯 Paramètres de Recherche")

# 1. Extension
extensions_dict = {
    "Pokémon 151": "https://www.cardmarket.com/fr/Pokemon/Products/Singles/151",
    "Évolutions à Paldéa": "https://www.cardmarket.com/fr/Pokemon/Products/Singles/Paldean-Fates",
    "Flammes Obsidiennes": "https://www.cardmarket.com/fr/Pokemon/Products/Singles/Obsidian-Flames"
}
selected_extension = st.sidebar.selectbox("1. Extension", list(extensions_dict.keys()))
target_url = extensions_dict[selected_extension]

# 2. Langue
languages_dict = {
    "Toutes langues": None,
    "Français": 2,
    "Anglais": 1,
    "Allemand": 3
}
selected_lang_label = st.sidebar.selectbox("2. Langue", list(languages_dict.keys()))
lang_code = languages_dict[selected_lang_label]

# 3. État minimum
conditions_dict = {
    "Tous les états": None,
    "Near Mint (NM)": 2,
    "Excellent (EX)": 3,
    "Good (GD)": 4,
}
selected_cond_label = st.sidebar.selectbox("3. État minimum", list(conditions_dict.keys()))
cond_code = conditions_dict[selected_cond_label]

# 4. Reverse / Non-reverse
variant_option = st.sidebar.radio(
    "4. Type de carte",
    options=["Toutes", "Standard (Non-Reverse)", "Reverse Holo"]
)

# Seuil d'alerte bonnes affaires
seuil_sous_cote = st.sidebar.slider("Seuil d'alerte 'Sous-côté' (% sous la tendance)", 10, 50, 20)

sheet_name_input = st.sidebar.text_input("Nom de la Google Sheet", value="Pokemon_Cardmarket_Data")

# --- ZONE PRINCIPALE ---
st.subheader(f"Extension : {selected_extension}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Langue", selected_lang_label)
c2.metric("État Min.", selected_cond_label)
c3.metric("Variante", variant_option)
c4.metric("Alerte", f"-{seuil_sous_cote}%")

st.markdown("---")

if st.button("🚀 Lancer le Scraping de l'Extension"):
    with st.spinner(f"Extraction en cours pour {selected_extension}..."):
        
        # Appel du scraper
        df_result = scrape_cardmarket_extension(target_url, lang_code, cond_code)
        
        if not df_result.empty:
            # Filtrage selon le choix Reverse / Non-reverse
            if variant_option == "Standard (Non-Reverse)":
                df_result = df_result[df_result["Variante"] == "Standard"]
            elif variant_option == "Reverse Holo":
                df_result = df_result[df_result["Variante"] == "Reverse Holo"]

            st.success(f"Scraping terminé ! {len(df_result)} cartes trouvées.")
            st.dataframe(df_result, use_container_width=True)
            
            # Synchronisation Google Sheets directe
            if st.button("📥 Synchroniser vers Google Sheets"):
                with st.spinner("Envoi vers Google Sheets..."):
                    success = sync_dataframe_to_sheet(df_result, sheet_name=sheet_name_input)
                    if success:
                        st.success("Synchronisation réussie !")
                    else:
                        st.error("Échec de la synchronisation (vérifiez vos secrets Google Cloud sur Streamlit).")
        else:
            st.warning("Aucune donnée retournée. Vérifiez les URLs ou les sélecteurs.")
