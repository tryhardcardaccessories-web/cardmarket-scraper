import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse

def scrape_pokemon_search_results(pokemon_name: str):
    """
    Recherche un Pokémon sur Cardmarket et extrait toutes les cartes correspondantes
    avec leur premier prix et leur lien direct.
    """
    encoded_query = urllib.parse.quote(pokemon_name.strip())
    search_url = f"https://www.cardmarket.com/fr/Pokemon/Products/Search?category=-1&searchString={encoded_query}&searchMode=v2"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=20)
        if response.status_code != 200:
            return pd.DataFrame(), f"Erreur HTTP : {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')
        cards_data = []

        # Ciblage des lignes de produits dans les résultats de recherche Cardmarket
        rows = soup.select("div.table-body div.table-row, div.row-product, tr")

        for row in rows:
            try:
                # Extraction du nom et du lien de la carte
                link_elem = row.select_one("a.no-link-style, a.row-link, a")
                if not link_elem or not link_elem.has_attr('href'):
                    continue
                    
                card_name = link_elem.get_text(strip=True)
                card_url = link_elem['href']
                if not card_url.startswith("http"):
                    card_url = "https://www.cardmarket.com" + card_url

                # Extraction du premier prix (prix de départ)
                price_elem = row.select_one("span.price, span.color-primary, td.price")
                price_text = price_elem.get_text(strip=True) if price_elem else "0"
                
                # Nettoyage et conversion du prix en float
                price_clean = (price_text.replace("€", "")
                                          .replace("from", "")
                                          .replace("à partir de", "")
                                          .replace(",", ".")
                                          .strip().split()[0])
                try:
                    price = float(price_clean)
                except:
                    price = 0.0

                if card_name and card_name != "Inconnu" and len(card_name) > 2:
                    cards_data.append({
                        "Nom de la carte": card_name,
                        "Premier Prix (€)": price,
                        "Lien Cardmarket": card_url
                    })
            except Exception:
                continue

        df = pd.DataFrame(cards_data)
        if not df.empty:
            # Suppression des doublons potentiels
            df = df.drop_duplicates(subset=["Nom de la carte"]).reset_index(drop=True)
            
        return df, None

    except Exception as e:
        return pd.DataFrame(), str(e)
