import streamlit as st
from scraper import extraire_prix_cartes_pokemon_online
from google_sheets import sync_dataframe_to_sheet

st.set_page_config(page_title="KanedaPk - Extraction Cardmarket Online", layout="wide")

st.title("🎴 Extraction Automatique des Prix par Pokémon (Online)")

st.markdown("""
Entrez le nom d'un Pokémon. L'application va rechercher ses cartes sur Cardmarket, 
récupérer leurs liens individuels et extraire automatiquement leurs premiers prix.
""")

# Barre latérale pour Google Sheets
st.sidebar.header("Paramètres")
sheet_name_input = st.sidebar.text_input("Nom de la Google Sheet", value="Pokemon_Cardmarket_Data")

# Champ de recherche
pokemon_query = st.text_input("Nom du Pokémon à rechercher (ex: Dracaufeu, Pikachu) :", value="Dracaufeu")

if st.button("🚀 Lancer l'extraction en ligne"):
    if pokemon_query.strip():
        with st.spinner(f"Recherche et extraction en cours pour '{pokemon_query}'... (Patientez quelques secondes)"):
            df_result, error_msg = extraire_prix_cartes_pokemon_online(pokemon_query)
            
            if error_msg:
                st.error(f"Erreur : {error_msg}")
            elif not df_result.empty:
                st.success(f"Extraction réussie ! {len(df_result)} cartes analysées.")
                
                # Affichage du tableau interactif
                st.dataframe(df_result, use_container_width=True)
                
                # Option de synchronisation vers Google Sheets
                if st.button("📥 Synchroniser vers Google Sheets"):
                    with st.spinner("Envoi vers Google Sheets..."):
                        success = sync_dataframe_to_sheet(df_result, sheet_name=sheet_name_input)
                        if success:
                            st.success("Synchronisation réussie avec succès !")
                        else:
                            st.error("Échec de la synchronisation (vérifiez vos clés Google Cloud).")
            else:
                st.warning("Aucune donnée récupérée pour cette recherche.")
    else:
        st.error("Veuillez entrer un nom valide.")
