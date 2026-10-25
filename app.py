import streamlit as st
from scraper import search_cardmarket_pokemon

st.set_page_config(page_title="KanedaPk - Recherche de Cartes", layout="wide")

st.title("🎴 Recherche Rapide de Cartes Pokémon")

# Barre de recherche textuelle simple
search_query = st.text_input("Entrez le nom d'un Pokémon ou d'une carte à chercher :", "Pikachu ex")

if st.button("🔍 Rechercher sur Cardmarket"):
    if search_query.strip():
        with st.spinner(f"Recherche de '{search_query}' en cours..."):
            df_res = search_cardmarket_pokemon(search_query)
            
            if not df_res.empty:
                st.success(f"{len(df_res)} résultats trouvés !")
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("Aucun résultat trouvé pour cette recherche.")
    else:
        st.error("Veuillez entrer un nom valide.")
