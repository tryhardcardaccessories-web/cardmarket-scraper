import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_cardmarket_extension(target_url: str, lang_code: int = None, min_condition: int = None):
    """
    Scrape les cartes d'une extension Cardmarket avec Playwright en mode headless,
    en appliquant les filtres de langue et d'état.
    """
    data = []

    with sync_playwright() as p:
        # Lancement de Chromium avec les arguments de sécurité pour le Cloud
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print(f"Ouverture de l'URL : {target_url}")
            page.goto(target_url, timeout=60000)
            page.wait_for_load_selector = "body"
            
            # Gestion des cookies si la popup apparaît
            try:
                cookie_button = page.locator("button:has-text('Accepter'), button:has-text('Accept')")
                if cookie_button.count() > 0:
                    cookie_button.first.click(timeout=3000)
            except:
                pass

            # Récupération des lignes de cartes dans le tableau Cardmarket
            # (S'adapte à la structure standard des listes de prix de cartes singles)
            rows = page.locator("div.table-body div.table-row").all()
            
            if not rows:
                # Fallback sur les tableaux classiques HTML si le DOM est différent
                rows = page.locator("table.table tr").all()

            print(f"{len(rows)} éléments bruts trouvés sur la page.")

            for row in rows:
                try:
                    # Extraction basique du nom et des prix (à adapter selon les classes exactes ciblées)
                    cols = row.locator("td").all()
                    if len(cols) < 3:
                        # Si le design utilise des div flex
                        cols = row.locator("div.col").all()

                    if len(cols) >= 2:
                        # Exemple d'extraction de texte (Nom, Prix, etc.)
                        name_element = row.locator("a.no-link-style, a").first
                        name = name_element.inner_text().strip() if name_element.count() > 0 else "Inconnu"
                        
                        price_element = row.locator("span.price, price-container").first
                        price_text = price_element.inner_text().strip() if price_element.count() > 0 else "0"
                        
                        # Nettoyage du prix (ex: "1,50 €" -> 1.50)
                        price_clean = price_text.replace("€", "").replace(",", ".").strip()
                        try:
                            price = float(price_clean)
                        except:
                            price = 0.0

                        # Détection de la variante (Standard ou Reverse)
                        variant = "Reverse Holo" if "reverse" in row.inner_text().lower() else "Standard"

                        data.append({
                            "Nom": name,
                            "Prix": price,
                            "Variante": variant,
                            "Lien": name_element.get_attribute("href") if name_element.count() > 0 else target_url
                        })
                except Exception as row_err:
                    continue

        except Exception as e:
            print(f"Erreur lors du scraping : {e}")
        finally:
            browser.close()

    # Transformation en DataFrame Pandas
    df = pd.DataFrame(data)
    return df
