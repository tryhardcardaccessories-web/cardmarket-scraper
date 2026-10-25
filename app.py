import streamlit as st
import urllib.parse

st.set_page_config(page_title="KanedaPk - Recherche Cardmarket", layout="wide")

st.title("🎴 Accès Direct & Recherche Cardmarket")

st.markdown("""
Pour éviter les blocages de sécurité (Erreur 403 de Cloudflare sur les serveurs cloud), 
cette interface génère instantanément le lien de recherche officiel pour le Pokémon de votre choix.
""")

# Saisie du nom du Pokémon
pokemon_query = st.text_input("Nom du Pokémon à rechercher :", value="Dracaufeu")

if st.button("🚀 Générer la recherche Cardmarket"):
    if pokemon_query.strip():
        # Encodage propre du nom pour l'URL Cardmarket
        encoded_query = urllib.parse.quote(pokemon_query.strip())
        search_url = f"https://www.cardmarket.com/fr/Pokemon/Products/Search?category=-1&searchString={encoded_query}&searchMode=v2"
        
        st.success("Lien généré avec succès !")
        
        # Bouton cliquable pour ouvrir la page sur votre propre navigateur
        st.markdown(f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{search_url}" target="_blank" style="background-color: #ff4b4b; color: white; padding: 15px 30px; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                🔗 Ouvrir les résultats pour "{pokemon_query}" sur Cardmarket
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Champ de secours pour copier le lien directement
        st.text_input("URL directe de recherche (copiable) :", value=search_url)
        
    else:
        st.error("Veuillez entrer un nom de Pokémon valide.")
