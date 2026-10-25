from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

def extraire_prix_cartes_pokemon_online(pokemon_name: str):
    """
    Scrape en ligne les liens /Singles/ d'un Pokémon sur Cardmarket 
    en utilisant curl_cffi pour simuler un vrai navigateur et éviter le 403.
    """
    encoded_query = urllib.parse.quote(pokemon_name.strip())
    search_url = f"https://www.cardmarket.com/fr/Pokemon/Products/Search?category=-1&searchString={encoded_query}&searchMode=v2"

    try:
        # Utilisation de l'émulation Chrome pour contourner les filtres Cloudflare en ligne
        response = requests.get(search_url, impersonate="chrome120", timeout=25)
        
        if response.status_code != 200:
            return pd.DataFrame(), f"Erreur HTTP lors de la recherche : {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Récupération de tous les liens uniques contenant /Singles/
        liens_cartes = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "/Pokemon/Products/Singles/" in href:
                if not href.startswith("http"):
                    href = "https://www.cardmarket.com" + href
                liens_cartes.add(href)

        if not liens_cartes:
            return pd.DataFrame(), "Aucun lien de carte trouvé pour ce Pokémon."

        resultats = []

        # Limitation pour éviter le timeout de l'application en ligne (max 15-20 cartes par recherche)
        liens_limites = list(liens_cartes)[:20]

        for url_carte in liens_limites:
            try:
                res_carte = requests.get(url_carte, impersonate="chrome120", timeout=10)
                if res_carte.status_code != 200:
                    continue
                
                soup_carte = BeautifulSoup(res_carte.text, 'html.parser')
                
                # Nom de la carte
                nom_elem = soup_carte.select_one("h1")
                nom_carte = nom_elem.get_text(strip=True) if nom_elem else "Inconnu"

                # Extraction du premier prix
                prix_elem = soup_carte.select_one("span.price, .price-container")
                prix_text = prix_elem.get_text(strip=True) if prix_elem else "0"
                
                prix_clean = (prix_text.replace("€", "")
                                      .replace("from", "")
                                      .replace("à partir de", "")
                                      .replace(",", ".")
                                      .strip().split()[0])
                try:
                    prix = float(prix_clean)
                except:
                    prix = 0.0

                resultats.append({
                    "Nom de la carte": nom_carte,
                    "Premier Prix (€)": prix,
                    "Lien Cardmarket": url_carte
                })
            except Exception:
                continue

        df = pd.DataFrame(resultats)
        return df, None

    except Exception as e:
        return pd.DataFrame(), str(e)
