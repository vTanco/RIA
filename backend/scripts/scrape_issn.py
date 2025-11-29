import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import pandas as pd
import time
import os

requests.packages.urllib3.disable_warnings()

from duckduckgo_search import DDGS

# ---------------------------------------------------
# 1. Buscar URL oficial usando DuckDuckGo (library)
# ---------------------------------------------------
def find_official_url(name):
    query = f"{name} journal publisher official site"
    try:
        results = DDGS().text(query, max_results=1)
        if results:
            return results[0]['href']
    except Exception as e:
        print(f"Error searching for {name}: {e}")
    return None


# ---------------------------------------------------
# 2. Detectar ISSN
# ---------------------------------------------------
def extract_issn(text):
    text = text.lower()
    issn_pattern = r"([0-9]{4}-[0-9]{3}[0-9x])"
    candidates = re.findall(issn_pattern, text)

    online = set()
    printing = set()

    for issn in candidates:
        idx = text.find(issn.lower())
        context = text[max(0, idx-40): idx+40]

        if "online" in context or "e-issn" in context:
            online.add(issn.upper())
        elif "print" in context or "p-issn" in context:
            printing.add(issn.upper())
        else:
            printing.add(issn.upper())

    return list(online), list(printing)


# ---------------------------------------------------
# 3. Descargar HTML
# ---------------------------------------------------
def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)"}
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            return r.text
    except:
        return None
    return None


# ---------------------------------------------------
# 4. Extraer enlaces internos
# ---------------------------------------------------
def get_internal_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        full = urljoin(base_url, a["href"])
        if urlparse(full).netloc == domain:
            links.add(full)

    return list(links)


# ---------------------------------------------------
# 5. Scraping profundo (3 niveles)
# ---------------------------------------------------
def deep_scrape(url, max_depth=3):
    visited = set()
    queue = [(url, 0)]
    issn_online = set()
    issn_print = set()

    while queue:
        current, depth = queue.pop(0)

        if current in visited or depth > max_depth:
            continue

        visited.add(current)

        html = get_html(current)
        if not html:
            continue

        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

        online_found, print_found = extract_issn(text)
        issn_online.update(online_found)
        issn_print.update(print_found)

        if depth < max_depth:
            internal = get_internal_links(html, current)
            for link in internal:
                if link not in visited:
                    queue.append((link, depth + 1))

        time.sleep(0.3)

    return list(issn_online), list(issn_print)


# ---------------------------------------------------
# 6. Cargar el Full Database
# ---------------------------------------------------
def main():
    # Define input files
    files = [
        {"path": "RESOURCES/The Predatory Journals List 2025.xlsx", "type": "Journal"},
        {"path": "RESOURCES/The Predatory Publishers List 2025-2.xlsx", "type": "Publisher"}
    ]
    
    data_frames = []
    
    for f in files:
        file_path = f["path"]
        # Handle relative paths if running from backend/scripts or root
        if not os.path.exists(file_path):
             if os.path.exists(os.path.join("..", "..", file_path)):
                 file_path = os.path.join("..", "..", file_path)
             elif os.path.exists(os.path.join("..", file_path)):
                 file_path = os.path.join("..", file_path)
        
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found.")
            continue
            
        print(f"Loading {file_path}...")
        try:
            # Read without header, assuming col 1 is name
            df_temp = pd.read_excel(file_path, header=None)
            # Rename columns: 0 -> ID, 1 -> Name
            if len(df_temp.columns) >= 2:
                df_temp = df_temp.iloc[:, :2]
                df_temp.columns = ["id", "name"]
                df_temp["type"] = f["type"]
                df_temp["url"] = None
                data_frames.append(df_temp)
            else:
                print(f"Warning: {file_path} has unexpected format.")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if not data_frames:
        print("No data loaded. Exiting.")
        return

    df = pd.concat(data_frames, ignore_index=True)
    print(f"Total records loaded: {len(df)}")

    # ---------------------------------------------------
    # 7. Encontrar URLs automáticamente
    # ---------------------------------------------------
    for i, row in df.iterrows():
        if pd.notna(row.get("url")) and str(row["url"]).startswith("http"):
            continue # Skip if URL already exists

        name = row["name"]
        print(f"\n🔍 Buscando URL oficial para: {name}")

        found_url = find_official_url(str(name))
        df.loc[i, "url"] = found_url

        print(f"➡️  URL encontrada: {found_url}")

        time.sleep(1)


    # ---------------------------------------------------
    # 8. Hacer scraping profundo de ISSN
    # ---------------------------------------------------
    issn_results = []

    for i, row in df.iterrows():
        name = row["name"]
        type_ = row.get("type", "Unknown")
        url = row["url"]

        print(f"\n📘 Scrapeando ISSN de: {name}")
        print(f"URL: {url}")

        if pd.isna(url) or not str(url).startswith("http"):
            issn_results.append([name, type_, url, None, None])
            continue

        online, printing = deep_scrape(url)

        issn_results.append([name, type_, url, ", ".join(online), ", ".join(printing)])


    # ---------------------------------------------------
    # 9. Crear DataFrame final
    # ---------------------------------------------------
    final_df = pd.DataFrame(
        issn_results,
        columns=["name", "type", "url", "issn_online", "issn_print"]
    )

    output_file = "full_database_with_issn.xlsx"
    final_df.to_excel(output_file, index=False)

    print("\n🎉 TODO COMPLETADO")
    print(f"Archivo final generado: {output_file}")
    print(final_df.head())

if __name__ == "__main__":
    main()
