import json
import psycopg2
import openpyxl

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

conn = psycopg2.connect(
    database=config["database"],
    user=config["user"],
    password=config["password"],
    host=config["host"],
    port=config["port"]
)

cur = conn.cursor()

workbook = openpyxl.load_workbook('mcc-mnc.xlsx')
sheet = workbook.active

for row in sheet.iter_rows(min_row=2, values_only=True):
    mcc, mnc, plmn, region, country, iso, operator, brand, tadig, bands = row
    cur.execute("INSERT INTO mcc_mnc_storage (MCC, MNC, PLMN, Region, Country, ISO, Operator, Brand, TADIG, Bands) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (mcc, mnc, plmn, region, country, iso, operator, brand, tadig, bands))

conn.commit()
cur.close()
conn.close()