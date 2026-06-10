import pandas as pd
import json
import time

from email_service import send_notification_email


COMMUNICATIONS_SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1CeJ8hxjkKly6Ef5hW1spb5E37F7ANKPp-Bsud5x8hpM/"
    "export?format=csv&gid=1403813074"
)

AGENTS = {
    "Maricar": "maricari.juanico@gmail.com",
    "Maureene": "cohenmaureene@gmail.com"
}

TRACKER_FILE = "notification_tracker.json"


def load_tracker():

    try:

        with open(
            TRACKER_FILE,
            "r"
        ) as f:

            return json.load(f)

    except:

        return {
            "last_message_id": 0
        }


def save_tracker(last_id):

    with open(
        TRACKER_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "last_message_id": int(last_id)
            },
            f
        )


def check_new_tickets():

    print(
    "Checking for new tickets..."
)

    tracker = load_tracker()

    last_id = int(
        tracker["last_message_id"]
    )

    df = pd.read_csv(
        COMMUNICATIONS_SHEET_CSV
    )

    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
    )

    df = df.fillna("")

    new_tickets = df[
        df["message_id"] > last_id
    ]

    if len(new_tickets) == 0:

        print(
            "No New Tickets"
        )

        return

    for _, ticket in new_tickets.iterrows():

        assigned_to = (
            ticket["assigned_to"]
        )

        email = AGENTS.get(
            assigned_to
        )

        if not email:

            continue

        send_notification_email(
            email,
            ticket["company_name"],
            ticket["subject"]
        )

        print(
            f"Notification Sent To {assigned_to}"
        )

        print(
            "Notification Sent To",
            email
        )

    latest_id = (
        df["message_id"].max()
    )

    save_tracker(
        latest_id
    )

 





















 