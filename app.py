import streamlit as st
from scraper import scrape_pokemon_search_results
from google_sheets import sync_dataframe_to_sheet

st.set_page_config(page_title="KanedaPk - Recherche Pokémon par Prix", layout="wide")

st.title("🎴 Recherche Automatique & Extraction des Prix par Pokémon")

st.markdown("""
Tapez le nom d'un Pokémon (ex: *Dracaufeu*, *Pikachu*, *Mewtwo*) pour lancer instantanément 
la recherche sur Cardmarket et extraire **toutes** ses cartes avec leur premier prix.
""")

# Paramètres dans la barre latérale
st.sidebar.header("Paramètres")
sheet_name_input = st.sidebar.text_input("Nom de la Google Sheet", value="Pokemon_Cardmarket_Data")

# Champ de saisie unique pour le Pokémon
pokemon_query = st.text_input("Nom du Pokémon à rechercher :", value="Dracaufeu")

if st.button("🚀 Lancer la recherche et l'extraction"):
    if pokemon_query.strip():
        with st.spinner(f"Recherche et extraction de toutes les cartes pour '{pokemon_query}' en cours..."):
            df_result, error_msg = scrape_pokemon_search_results(pokemon_query)
            
            if error_msg:
                st.error(f"Une erreur est survenue : {error_msg}")
            elif not df_result.empty:
                st.success(f"Extraction réussie ! {len(df_result)} cartes trouvées pour '{pokemon_query}'.")
                
                # Affichage du tableau interactif
                st.dataframe(df_result, use_container_width=True)
                
                # Bouton de synchronisation vers Google Sheets
                if st.button("📥 Synchroniser ces résultats vers Google Sheets"):
                    with st.spinner("Envoi vers Google Sheets..."):
                        success = sync_dataframe_to_sheet(df_result, sheet_name=sheet_name_input)
                        if success:
                            st.success("Synchronisation réussie !")
                        else:
                            st.error("Échec de la synchronisation (vérifiez vos secrets Google Cloud).")
            else:
                st.warning(f"Aucune carte trouvée pour '{pokemon_query}'. Vérifiez l'orthographe.")
    else:
        st.error("Veuillez entrer un nom de Pokémon valide.")
