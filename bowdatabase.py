import json
import pandas as pd
import sqlite3

with open("clean_bows.json","r") as f:
    data = json.load(f)

df=pd.DataFrame(data)

conn = sqlite3.connect('bowsDB.db')
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS bow_specs;
DROP TABLE IF EXISTS manufactures;

CREATE TABLE IF NOT EXISTS manufactures (
manufacturer_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bow_specs (
bow_id INTEGER PRIMARY KEY AUTOINCREMENT,
manufacturer_id INTEGER,
year INTEGER,
variant TEXT,
model TEXT,
ata_length_in REAL,
brace_height_in REAL,
mass_weight_lbs REAL,
draw_length_min_in REAL,
draw_length_max_in REAL,
draw_weight_min_lbs REAL,
draw_weight_max_lbs REAL,
let_off_min_pct REAL,
let_off_max_pct REAL,
ibo_speed_fps REAL,
model_url TEXT,
specs_url TEXT,
FOREIGN KEY(manufacturer_id) REFERENCES manufactures(manufacturer_id)
)
""")

conn.commit()

brands = df["brand"].dropna().unique()
for brand in brands:
    cur.execute("""
    INSERT OR IGNORE INTO manufactures (name)
    VALUES (?)
    """, (brand,))

conn.commit() 
cur.execute('SELECT manufacturer_id, name FROM manufactures')
rows = cur.fetchall()
  
brand_to_id ={name: manufacturer_id for manufacturer_id, name in rows}

for entry in data:
    brand = entry["brand"]
    manufacturer_id = brand_to_id.get(brand)
    model = entry["model"]
    year = entry["year"]
    variant = entry["variant"]
    mass_weight_lbs = entry["mass_weight_lbs"]
    ata_length_in = entry["ata_length_in"]
    brace_height_in = entry['brace_height_in']
    draw_length_min_in = entry['draw_length_min_in']
    draw_length_max_in = entry['draw_length_max_in']
    draw_weight_min_lbs = entry["draw_weight_min_lbs"]
    draw_weight_max_lbs = entry['draw_weight_max_lbs']
    let_off_min_pct = entry['let_off_min_pct']
    let_off_max_pct = entry['let_off_max_pct']
    ibo_speed_fps = entry['ibo_speed_fps']
    model_url = entry["model_url"]
    specs_url = entry["specs_url"]
    
    
    cur.execute("""
    INSERT INTO bow_specs (
    manufacturer_id,
    year,
    variant,
    model,
    ata_length_in,
    brace_height_in,
    mass_weight_lbs,
    draw_length_min_in,
    draw_length_max_in,
    draw_weight_min_lbs,
    draw_weight_max_lbs,
    let_off_min_pct,
    let_off_max_pct,
    ibo_speed_fps,
    model_url,
    specs_url
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """,(manufacturer_id,year,variant,model,ata_length_in,brace_height_in,mass_weight_lbs,draw_length_min_in,draw_length_max_in,draw_weight_min_lbs,draw_weight_max_lbs,let_off_min_pct,let_off_max_pct,ibo_speed_fps,model_url,specs_url))
conn.commit()

cur.execute('SELECT count(*) FROM bow_specs')
#print(cur.fetchall())



