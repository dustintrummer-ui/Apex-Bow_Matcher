import json
import re

with open("bows.json", "r") as f:
    data = json.load(f)

records = data[:]

def clean_brace(value):
    if value is None:
        return None
    
    value = value.replace('"', " ")
    value = value.strip()
    
    if value == "":
        return None
    return float(value)

def clean_ata(value):
    if value is None:
        return None
    
    value = value.replace('"', " ")
    value = value.strip()
    
    if value.strip() == "":
        return None
    
    return float(value)

def clean_mass_weight(value):
    if value is None:
        return None
    if "%" in value:
        return None

    value = value.replace("lbs", "")
    value = value.replace(",",".")
    value = value.replace('-',"")
    value = value.strip()
    
    if value in ["", "N/A"]:
        return None
    return float(value)

def clean_draw_length(value):
    if value is None or value.strip() == "":
        return None, None

    numbers = re.findall(r"\d+\.?\d*", value)

    if len(numbers) == 0:
        return None, None

    numbers = [float(n) for n in numbers]

    if len(numbers) == 1:
        return numbers[0], numbers[0]

    return min(numbers), max(numbers)

def clean_draw_weight(value):
    if value is None or value.strip() == "":
        return None, None

    numbers = re.findall(r"\d+\.?\d*", value)

    if len(numbers) == 0:
        return None, None

    numbers = [float(n) for n in numbers]

    if len(numbers) == 1:
        return numbers[0], numbers[0]

    return min(numbers), max(numbers)


def clean_let_off(value):
    if value is None or value.strip() == "":
        return None, None

    numbers = re.findall(r"\d+\.?\d*", value)

    if len(numbers) == 0:
        return None, None

    numbers = [float(n) for n in numbers]

    if len(numbers) == 1:
        return numbers[0], numbers[0]

    return min(numbers), max(numbers)

def fix_version(value):
    if value is None or value.strip() == "":
        return None, None

    value = value.strip()

    match = re.search(r"\d{4}", value)

    if not match:
        return None, value  # no year found

    year = int(match.group())

    # everything after the year is variant
    variant = value.replace(match.group(), "").strip()

    if variant == "":
        variant = None

    return year, variant

clean_bows=[]
for record in records:
    mass = clean_mass_weight(record["mass_weight"]) 
    dl_min, dl_max = clean_draw_length(record["draw_length"]) 
    dw_min, dw_max = clean_draw_weight(record["draw_weight"]) 
    lo_min, lo_max = clean_let_off(record["let_off"])
    bh = clean_brace(record["brace_height"])
    ata = clean_ata(record['ata_length'])
    year, variant = fix_version(record["version"])
    # Fix swapped ATA / Brace Height
    if ata is not None and bh is not None:
        if ata < 15 and bh > 12:
            ata, bh = bh, ata

    # Fix bad draw weight min
    if dw_min == 0:
        dw_min = None
    
    cleaned_record = {
    "brand": record["brand"],
    "model": record["model"],
    "year": year,
    "variant": variant,
    "mass_weight_lbs": mass,
    "ata_length_in": ata,
    "brace_height_in": bh,
    "draw_length_min_in": dl_min,
    "draw_length_max_in": dl_max,
    "draw_weight_min_lbs": dw_min,
    "draw_weight_max_lbs": dw_max,
    "let_off_min_pct": lo_min,
    "let_off_max_pct": lo_max,
    "ibo_speed_fps": record["ibo_speed"],
    "model_url": record["model_url"],
    "specs_url": record["specs_url"],
    
}

    clean_bows.append(cleaned_record)

with open("clean_bows.json", "w")as f:
    json.dump(clean_bows, f, indent=4)