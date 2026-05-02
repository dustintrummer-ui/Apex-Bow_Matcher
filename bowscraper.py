import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

base_url = "https://compoundbowchoice.com"
brands_url = f"{base_url}/brands/"
HEADERS = [
    "version",
    "brace_height",
    "ata_length",
    "draw_length",
    "draw_weight",
    "ibo_speed",
    "mass_weight",
    "let_off"
]
def extract_number(value):
    match=re.search(r"\d+\.?\d*",value)
    return float(match.group()) if match else None

def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def get_brand_links():
    soup = get_soup(brands_url)
    links = soup.find_all("a")

    brand_links = []

    for link in links:
        text = link.get_text(strip=True)
        href = link.get("href")

        if text.lower() == "crossbows":
            break

        if href and "/brands/" in href:
            brand_links.append((text, urljoin(brands_url, href)))

    return brand_links

def get_model_links(brand_name,brand_url):
    response=requests.get(brand_url)
    soup = BeautifulSoup(response.text,"html.parser")
    
    links = soup.find_all('a')
    bad_paths = ['reviews','for-sale']
    models=[]
    
    for link in links:
        text = link.get_text(strip=True)
        href = link.get('href')
        
        if not href:
            continue
      
        if any(bad in href for bad in bad_paths):
            continue
        if "/brands/" not in href:
            continue
        if href.startswith(f"/brands/{brand_name.lower().replace(' ','-')}/") and href.count("/") == 4:
            full_url = urljoin(brand_url, href)
            models.append((text, full_url))    
    return models

def get_specs_url(model_url):
    return model_url.rstrip("/")+'/specs/'

def get_bow_specs(brand_name, model_name, model_url):
    specs_url = get_specs_url(model_url)
    soup = get_soup(specs_url)
    
    bow_versions = []
    rows = soup.find_all("tr")
    
    for row in rows:
        first_cell = row.find("td", class_="full-view")
        
        if not first_cell:
            continue
        cells = row.find_all('td')
        values = [cell.get_text(" ", strip=True) for cell in cells]
        
        if len(values) != len(HEADERS):
            continue
        bow_data = dict(zip(HEADERS, values))
        
        bow_data["brand"]= brand_name
        bow_data["model"]=model_name
        bow_data["ibo_speed"] = extract_number(bow_data["ibo_speed"])
        bow_data["model_url"]= model_url
        bow_data["id"] = f"{brand_name}_{model_name}_{bow_data['version']}_{bow_data['ibo_speed']}_{bow_data['let_off']}"
        bow_data["specs_url"]= specs_url
        if not has_real_specs(bow_data):
            continue 
        bow_versions.append(bow_data)
    return bow_versions

def main():
    brand_links = get_brand_links()
    all_specs = []

    for brand_name, brand_url in brand_links:
        print(f"processing brand: {brand_name}")

        models = get_model_links(brand_name, brand_url)

        for model_name, model_url in models:
            print(f" Processing model: {model_name}")

            try:
                bow_specs = get_bow_specs(brand_name, model_name, model_url)
                all_specs.extend(bow_specs)
            except Exception as e:
                print(f" Failed on {brand_name} - {model_name}: {e}")

    print(f"Total records: {len(all_specs)}")

    with open("bows.json", "w") as f:
        json.dump(all_specs, f, indent=4)
def has_real_specs(bow_data):
    empty_values = {'"', "lbs", "fps", "", None}

    spec_fields = [
        "brace_height",
        "ata_length",
        "draw_length",
        "draw_weight",
        "ibo_speed",
        "mass_weight",
        "let_off"
    ]

    return any(bow_data[field] not in empty_values for field in spec_fields)    

if __name__ == "__main__":
    main()
                    

 