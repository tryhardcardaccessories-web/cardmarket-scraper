import time
import bs4
from playwright.sync_api import sync_playwright
import pandas as pd

def scrape_cardmarket_extension(base_url, lang_code=None, cond_code=None):
    """
    Scrape une extension Cardmarket complète en appliquant 
    les filtres de langue et d'état minimum choisis.
    """
    # Construction dynamique des paramètres de l'URL
    params = []
    if lang_code:
        params.append(f"language={lang_code}")
    if cond_code:
        params.append(f"minCondition={cond_code}")
    
    separator = "&" if "?" in base_url else "?"
    target_url = base_url + separator + "&".join(params) if params else base_url

    results = []

    with sync_playwright() as p:
        # Lancement du navigateur en arrière-plan (headless)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="fr-FR"
        )
        page = context.new_page()

        try:
            print(f"Connexion à Cardmarket : {target_url}")
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)  # Pause pour laisser le contenu dynamique et Cloudflare charger

            soup = bs4.BeautifulSoup(page.content(), "html.parser")

            # Ciblage des lignes du tableau de l'extension sur Cardmarket
            rows = soup.select("div.table-body div.row") or soup.select("table tbody tr")

            for row in rows:
                try:
                    # 1. Extraction du nom et du lien de la carte
                    link_elem = row.find("a", href=True)
                    if not link_elem:
                        continue
                    
                    card_name = link_elem.text.strip().split('\n')[0]
                    href = link_elem["href"]
                    card_url = "https://www.cardmarket.com" + href if not href.startswith("http") else href

                    # 2. Détection de la variante (Standard vs Reverse Holo)
                    variant = "Reverse Holo" if "reverse" in card_name.lower() else "Standard"

                    # 3. Extraction des colonnes de prix (Prix Min / Tendance)
                    cols = row.find_all("div", class_="col") or row.find_all("td")
                    
                    trend_price = 0.0
                    min_price = 0.0

                    # Nettoyage et récupération des montants en euros présents dans la ligne
                    prices = []
                    for c in cols:
                        text = c.text.strip()
                        if "€" in text:
                            clean_val = text.replace("€", "").replace(",", ".").strip()
                            try:
                                prices.append(float(clean_val))
                            except ValueError:
                                pass

                    # Attribution selon la structure classique des tableaux Cardmarket
                    if len(prices) >= 2:
                        min_price = prices[0]     # Premier prix affiché
                        trend_price = prices[-1]  # Prix tendance global
                    elif len(prices) == 1:
                        min_price = prices[0]

                    results.append({
                        "Nom de la carte": card_name,
                        "Variante": variant,
                        "Prix Tendance (€)": trend_price,
                        "Prix Min (€)": min_price,
                        "URL": card_url
                    })

                except Exception:
                    continue

        except Exception as e:
            print(f"Erreur lors du scraping : {e}")
        finally:
            browser.close()

    return pd.DataFrame(results)
