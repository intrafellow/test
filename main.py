import json
import psycopg2
import openpyxl
import os


def file_exists(file_path):
    return os.path.exists(file_path) and os.access(file_path, os.R_OK)


config_file_path = 'config.json'
if file_exists(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
else:
    raise FileNotFoundError("Config file not found or not readable.")

conn = psycopg2.connect(
    database=config["database"],
    user=config["user"],
    password=config["password"],
    host=config["host"],
    port=config["port"]
)

cur = conn.cursor()

xlsx_file_path = 'mcc-mnc.xlsx'
if file_exists(xlsx_file_path):
    workbook = openpyxl.load_workbook(xlsx_file_path)
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2):
        mcc, mnc, plmn, region, country, iso, operator, brand, tadig, bands = (cell.value for cell in row)

        cur.execute("SELECT MCC, MNC FROM mcc_mnc_storage WHERE MCC = %s AND MNC = %s", (mcc, mnc))
        existing_record = cur.fetchone()

        if existing_record:
            cur.execute(
                "UPDATE mcc_mnc_storage SET PLMN = %s, Region = %s, Country = %s, ISO = %s, Operator = %s, Brand = %s, TADIG = %s, Bands = %s WHERE MCC = %s AND MNC = %s",
                (plmn, region, country, iso, operator, brand, tadig, bands, mcc, mnc))
        else:
            cur.execute(
                "INSERT INTO mcc_mnc_storage (MCC, MNC, PLMN, Region, Country, ISO, Operator, Brand, TADIG, Bands) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (mcc, mnc, plmn, region, country, iso, operator, brand, tadig, bands))

    conn.commit()
else:
    raise FileNotFoundError("XLSX file not found or not readable.")

cur.close()
conn.close()