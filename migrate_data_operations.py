import gspread
from google.oauth2.service_account import Credentials
from db import (
    init_db,
    insert,
    get_next_numeric_id,
    DATA_OPERATIONS_COLUMNS
)

SPREADSHEET_ID = "1CeJ8hxjkKly6Ef5hW1spb5E37F7ANKPp-Bsud5x8hpM"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)

spreadsheet = gc.open_by_key(SPREADSHEET_ID)

sheet = spreadsheet.worksheet("Sheet1")

init_db()

rows = sheet.get_all_records()

next_id = get_next_numeric_id("data_operations")

imported = 0

for row in rows:

    data = {}

    for col in DATA_OPERATIONS_COLUMNS:

        if col == "id":
            data[col] = str(next_id)

        elif col == "assign":
            data[col] = str(row.get("assign", "")).strip()

        elif col == "verified":
            data[col] = str(row.get("verified", "")).strip()

        else:
            data[col] = str(row.get(col, "")).strip()

    insert(
        "data_operations",
        data
    )

    next_id += 1
    imported += 1

print("================================")
print("DATA OPERATIONS MIGRATION DONE")
print("Rows imported:", imported)
print("Next ID:", next_id)
print("================================")