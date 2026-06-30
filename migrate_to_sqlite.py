import gspread
from google.oauth2.service_account import Credentials
from db import (
    init_db,
    insert_row,
    ONBOARDING_COLUMNS,
    PAYMENT_FOLLOW_UP_COLUMNS
)
from db import COMMUNICATIONS_COLUMNS

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

init_db()



for sheet_name, table, columns in [
    ("Onboarding", "onboarding", ONBOARDING_COLUMNS),
    ("Payment_Follow_Up", "payment_follow_up", PAYMENT_FOLLOW_UP_COLUMNS),
]:
    
    sheet = spreadsheet.worksheet(sheet_name)
    rows = sheet.get_all_records()

    for row in rows:

        # if table == "onboarding":
        #     if find_by_customer_id("onboarding", row.get("customer_id", "")):
        #         continue

        # if table == "payment_follow_up":
        #     if find_by_lead_id("payment_follow_up", row.get("lead_id", "")):
        #         continue
            
        insert_row(table, columns, row)

    print(f"Migrated {len(rows)} rows from {sheet_name}")


sheet = spreadsheet.worksheet("Communications")
rows = sheet.get_all_records()

for row in rows:
    insert_row(
        "communications",
        COMMUNICATIONS_COLUMNS,
        row
    )

print(f"Migrated {len(rows)} rows from Communications")