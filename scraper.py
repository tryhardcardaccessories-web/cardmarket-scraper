import pandas as pd
from playwright.sync_api import sync_playwright
import urllib.parse

def search_cardmarket_pokemon(card_name: str):
    data = []
    query = urllib.parse.quote(card_name)
    target_url = f"https://www.cardmarket.com/fr/Pokemon/Products/Singles?searchString={query}"

    with sync_playwright() as p:
        # Lancement robuste sans sandbox
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-gpu"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(target_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded")
            
            try:
                cookie_button = page.locator("button:has-text('Accepter'), button:has-text('Accept')")
                if cookie_button.count() > 0:
                    cookie_button.first.click(timeout=3000)
            except:
                pass

            rows = page.locator("div.table-body div.table-row, table.table tr, div.row-product").all()

            for row in rows:
                try:
                    name_element = row.locator("a.no-link-style, a.row-link, td.name a, a").first
                    if name_element.count() == 0:
                        continue
                    
                    name = name_element.inner_text().strip()
                    card_url = name_element.get_attribute("href")
                    if card_url and not card_url.startswith("http"):
                        card_url = "https://www.cardmarket.com" + card_url

                    price_element = row.locator("span.price, span.color-primary, td.price").first
                    price_text = price_element.inner_text().strip() if price_element.count() > 0 else "0"
                    
                    price_clean = (price_text.replace("€", "")
                                              .replace("from", "")
                                              .replace("à partir de", "")
                                              .replace(",", ".")
                                              .strip().split()[0])
                    try:
                        price = float(price_clean)
                    except:
                        price = 0.0

                    if name:
                        data.append({
                            "Nom de la carte": name,
                            "Prix min": price,
                            "Lien": card_url or target_url
                        })
                except:
                    continue

        except Exception as e:
            print(f"Erreur de recherche : {e}")
        finally:
            browser.close()

    return pd.DataFrame(data)
