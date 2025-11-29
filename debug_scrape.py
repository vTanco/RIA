import requests
from bs4 import BeautifulSoup

def find_official_url(name):
    query = name.replace(" ", "+")
    search_url = f"https://duckduckgo.com/html/?q={query}+journal+publisher+official+site"
    print(f"Searching: {search_url}")

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}

    try:
        r = requests.get(search_url, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Debug: print first few links
        links = soup.find_all("a", href=True)
        print(f"Found {len(links)} links.")
        for i, a in enumerate(links[:10]):
            print(f"{i}: {a['href']} - {a.get_text(strip=True)}")

        results = soup.find_all("a", class_="result__a", href=True)
        print(f"Found {len(results)} result__a links.")

        for a in results:
            url = a["href"]
            print(f"Candidate: {url}")
            if any(bad in url for bad in ["duckduckgo", "bing", "google", "yahoo"]):
                continue
            if url.startswith("http"):
                return url

    except Exception as e:
        print(f"Error: {e}")

    return None

print("Result:", find_official_url("Abstract and Applied Analysis"))
