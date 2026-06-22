from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import pandas as pd
from functools import wraps
import webbrowser
from threading import Timer
import json
import os
from notification_service import check_new_tickets
from apscheduler.schedulers.background import BackgroundScheduler
import time
import gspread
from google.oauth2.service_account import Credentials
from pandasql import sqldf


 
app = Flask(__name__)

cached_df = None
last_load = 0

# if os.environ.get(
#     "WERKZEUG_RUN_MAIN"
# ) == "true":

app.secret_key = "bytedata_secure_session_key"

SCOPES = [

    "https://www.googleapis.com/auth/spreadsheets",

    "https://www.googleapis.com/auth/drive"

]

creds = Credentials.from_service_account_file(

    "credentials.json",

    scopes=SCOPES

)

gc = gspread.authorize(
    creds
)

scheduler = BackgroundScheduler()

scheduler.add_job(
    check_new_tickets,
    "interval",
    seconds=60
)

scheduler.start()

print(
    "Notification Scheduler Started"
)

all_data = []

PROGRESS_FILE = "progress.json"


app.secret_key = "bytedata_secure_session_key"

def get_sheet_data():

    global cached_df
    global last_load

    current_time = time.time()

    if (
        cached_df is None
        or
        current_time - last_load > 60
    ):

        print(
            "Refreshing Sheet..."
        )

        cached_df = pd.read_csv(
            GOOGLE_SHEET_CSV
        )

        cached_df.columns = (
            cached_df.columns
            .str.lower()
        )

        last_load = current_time

    return cached_df

def get_main_sheet():

    spreadsheet = gc.open_by_key(

        "1CeJ8hxjkKly6Ef5hW1spb5E37F7ANKPp-Bsud5x8hpM"

    )

    worksheet = spreadsheet.get_worksheet(
        0
    )

    return worksheet

def load_progress():

    if not os.path.exists(PROGRESS_FILE):
        return {}

    try:

        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)

    except:
        return {}


def save_progress(progress_data):

    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress_data, f)
 
# =====================================
# VERIFIED DATA
# =====================================

all_data = []

# =====================================
# SHEETS
# =====================================

GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1CeJ8hxjkKly6Ef5hW1spb5E37F7ANKPp-Bsud5x8hpM/export?format=csv"

LOGIN_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1CeJ8hxjkKly6Ef5hW1spb5E37F7ANKPp-Bsud5x8hpM/export?format=csv&gid=265750894"

CUSTOMERS_SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1CeJ8hxjkKly6Ef5hW1spb5E37F7ANKPp-Bsud5x8hpM/"
    "export?format=csv&gid=501341251"
)

COMMUNICATIONS_SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1CeJ8hxjkKly6Ef5hW1spb5E37F7ANKPp-Bsud5x8hpM/"
    "export?format=csv&gid=1403813074"
)

PAYMENTS_SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1CeJ8hxjkKly6Ef5hW1spb5E37F7ANKPp-Bsud5x8hpM/"
    "export?format=csv&gid=755595798"
)
# =====================================
# LOGIN REQUIRED
# =====================================

def login_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if not session.get("logged_in"):

            return redirect(
                url_for("login_page")
            )

        return f(*args, **kwargs)

    return decorated_function

# =====================================
# LOGIN PAGE
# =====================================

@app.route("/login")
def login_page():

    return render_template(
        "login.html"
    )

# =====================================
# LOGIN USER
# =====================================

@app.route("/login-user", methods=["POST"])
def login_user():

    try:

        username = request.json.get(
            "username"
        )

        password = request.json.get(
            "password"
        )

        df = pd.read_csv(
            LOGIN_SHEET_CSV
        )

        df.columns = df.columns.str.lower()

        user_row = df[
            (df["user"].astype(str).str.lower() == str(username).lower()) &
            (df["pass"].astype(str) == str(password))
        ]

        if len(user_row) > 0:

            # session["logged_in"] = True

            # session["username"] = username.lower()

            # # RESET POINTER

            # session["current_index"] = 0
            session["logged_in"] = True

            session["username"] = username.lower()

            progress = load_progress()

            session["current_index"] = progress.get(
                username.lower(),
                0
            )

            return jsonify({

                "status":"success",
                "redirect": "/dashboard"

            })

        return jsonify({

            "status":"error",

            "message":"Invalid Login"

        })

    except Exception as e:

        return jsonify({

            "status":"error",

            "message":str(e)

        })

# =====================================
# HOME
# =====================================

@app.route("/")
@login_required
def home():

    return render_template(
        "index.html"
    )

# =====================================
# DASHBOARD
# =====================================

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html"
    )




@app.route("/operations")
@login_required
def operations():
    return render_template(
        "operations.html"
    )

@app.route("/operations-data")
@login_required
def operations_data():

    try:

        df = pd.read_csv(
            CUSTOMERS_SHEET_CSV
        )

        df.columns = (
            df.columns
            .str.lower()
            .str.strip()
        )

        df = df.fillna("")

        customers = []

        for _, row in df.iterrows():

            status = (
                str(
                    row["status"]
                )
                .strip()
                .lower()
            )

            if status == "active":

                service_status = "Running"

                health = "🟢"

                payment_status = "Paid"

            elif status == "due today":

                service_status = "Running"

                health = "🟠"

                payment_status = "Pending"

            elif status == "overdue":

                service_status = "Stopped"

                health = "🔴"

                payment_status = "Not Received"

            else:

                service_status = "Unknown"

                health = "⚪"

                payment_status = "Unknown"

            customers.append({

                "customer_id":
                    row.get(
                        "customer_id",
                        ""
                    ),

                "company_name":
                    row.get(
                        "company_name",
                        ""
                    ),

                "status":
                    row.get(
                        "status",
                        ""
                    ),

                "payment_status":
                    payment_status,

                "service_status":
                    service_status,

                "health":
                    health,

                "payment_date":
                    row.get(
                        "payment_date",
                        ""
                    ),

                "days_remaining":
                    row.get(
                        "days_remaining",
                        ""
                    )

            })

        return jsonify(
            customers
        )

    except Exception as e:

        return jsonify({

            "error":
                str(e)

        })






@app.route("/communications")
@login_required
def communications():
    return render_template("communications.html")


@app.route("/communications-data")
@login_required
def communications_data():

    try:

        df = pd.read_csv(
            COMMUNICATIONS_SHEET_CSV
        )

        df.columns = (
            df.columns
            .str.lower()
            .str.strip()
        )

        df = df.fillna("")

        # df = df[
        #     df["status"]
        #     .astype(str)
        #     .str.lower()
        #     != "closed"
        # ]

        messages = df.to_dict(
            orient="records"
        )

        # try:
        #     check_new_tickets()
        # except Exception as e:
        #      print(
        #     "Notification Error:",
        #     e
        # )

        return jsonify(
            messages
        )

    except Exception as e:

        return jsonify({

            "error": str(e)

        })


# =====================================
# CUSTOMERS PAGE
# =====================================

@app.route("/customers")
@login_required
def customers():

    return render_template(
        "customers.html"
    )

# =====================================
# CUSTOMERS DATA API
# =====================================

@app.route("/customers-data")
@login_required
def customers_data():

    try:

        df = pd.read_csv(
            CUSTOMERS_SHEET_CSV
        )

        df.columns = (
            df.columns
            .str.lower()
            .str.strip()
        )

        df = df.fillna("")

        customers = df.to_dict(
            orient="records"
        )

        return jsonify(
            customers
        )

    except Exception as e:

        return jsonify({

            "error":
                str(e)

        })

# =====================================
# DASHBOARD DATA
# =====================================

@app.route("/dashboard-data")
@login_required
def dashboard_data():

    try:

        df = pd.read_csv(
            CUSTOMERS_SHEET_CSV
        )

        df.columns = (
            df.columns
            .str.lower()
            .str.strip()
        )

        total_customers = len(df)

        active_customers = len(
            df[
                df["status"]
                .astype(str)
                .str.lower()
                == "active"
            ]
        )

        due_today = len(
            df[
                df["status"]
                .astype(str)
                .str.lower()
                == "due today"
            ]
        )

        overdue_customers = len(
            df[
                df["status"]
                .astype(str)
                .str.lower()
                == "overdue"
            ]
        )

        total_revenue = (
            pd.to_numeric(
                df[
                    "subscription_amount"
                ],
                errors="coerce"
            )
            .fillna(0)
            .sum()
        )

        customers = (
            df.head(10)
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

        return jsonify({

            "total_customers":
                int(
                    total_customers
                ),

            "active_customers":
                int(
                    active_customers
                ),

            "due_today":
                int(
                    due_today
                ),

            "overdue_customers":
                int(
                    overdue_customers
                ),

            "total_revenue":
                float(
                    total_revenue
                ),

            "customers":
                customers

        })

    except Exception as e:

        return jsonify({

            "error":
                str(e)

        })




@app.route("/dashboard-analytics")
@login_required
def dashboard_analytics():

    df = pd.read_csv(
        CUSTOMERS_SHEET_CSV
    )

    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
    )

    return jsonify({

        "countries":
            df["country"]
            .value_counts()
            .to_dict(),

        "assigned":
            df["assigned_to"]
            .value_counts()
            .to_dict(),

        "status":
            df["status"]
            .value_counts()
            .to_dict()

    })



@app.route("/analytics")
@login_required
def analytics():
    return render_template(
        "analytics.html"
    )


@app.route("/reports")
@login_required
def reports():
    return render_template(
        "reports.html"
    )


@app.route("/settings")
@login_required
def settings():
    return render_template(
        "settings.html"
    )



# =====================================
# FETCH NEXT ROW
# =====================================

@app.route("/fetch-next-row")
@login_required
def fetch_next_row():

    try:

        logged_user = session.get(
            "username"
        ).lower()

        # df = pd.read_csv(
        #     GOOGLE_SHEET_CSV
        # )

        df = get_sheet_data()

        df.columns = df.columns.str.lower()

        # FILTER USER ROWS

        user_rows = df[
            df["assign"].astype(str).str.lower() == logged_user
        ]

        user_rows = user_rows.fillna("")

        # GET POINTER

        current_index = session.get(
            "current_index",
            0
        )

        # NO MORE ROWS

        if current_index >= len(user_rows):

            return jsonify({

                "status":"finished",

                "message":"No More Rows"

            })

        # GET ROW

        row = user_rows.iloc[
            current_index
        ].to_dict()

        # INCREASE POINTER

        # session["current_index"] = current_index + 1

        new_index = current_index + 1

        session["current_index"] = new_index

        progress = load_progress()

        progress[logged_user] = new_index

        save_progress(progress)

        return jsonify({

            "status":"success",

            "row":row

        })

    except Exception as e:

        return jsonify({

            "status":"error",

            "message":str(e)

        })





# =====================================
# SAVE VERIFIED
# =====================================

@app.route("/save-verified", methods=["POST"])
@login_required
def save_verified():

    try:

        data = request.json

        data["verified_by"] = session.get(
            "username"
        )

        all_data.append(
            data
        )

        return jsonify({

            "status":"success"

        })

    except Exception as e:

        return jsonify({

            "status":"error",

            "message":str(e)

        })

# =====================================
# EXPORT
# =====================================

@app.route("/export-excel")
@login_required
def export_excel():

    logged_user = session.get(
        "username"
    )

    export_rows = []

    for row in all_data:

        if row.get(
            "verified_by"
        ) == logged_user:

            export_rows.append(
                row
            )

    if len(export_rows) == 0:

        return "No Verified Data"

    df = pd.DataFrame(
        export_rows
    )

    file_name = f"{logged_user}_verified.xlsx"

    df.to_excel(

        file_name,

        index=False
    )

    return send_file(

        file_name,

        as_attachment=True
    )


@app.route("/payments")
@login_required
def payments():
    return render_template(
        "payments.html"
    )

payments_cache = None
payments_cache_time = 0

def get_payments_data():

    global payments_cache
    global payments_cache_time

    now = time.time()

    if (
        payments_cache is None
        or
        now - payments_cache_time > 60
    ):

        payments_cache = pd.read_csv(
            PAYMENTS_SHEET_CSV
        )

        payments_cache.columns = (
            payments_cache.columns
            .str.lower()
            .str.strip()
        )

        payments_cache = payments_cache.fillna("")

        payments_cache_time = now

    return payments_cache

@app.route("/payments-data")
@login_required
def payments_data():

    df = pd.read_csv(PAYMENTS_SHEET_CSV)

    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
    )

    df = df.fillna("")

    return jsonify(
        df.to_dict(
            orient="records"
        )
    )

@app.route(
    "/update-sheet-row",
    methods=["POST"]
)
@login_required
def update_sheet_row():

    try:

        data = request.json

        row_id = str(
            data.get("id")
        )

        sheet = get_main_sheet()

        records = sheet.get_all_records()

        target_row = None

        for index, row in enumerate(records):

            if str(row.get("id")) == row_id:

                target_row = index + 2

                break

        if not target_row:

            return jsonify({

                "status":"error",

                "message":"Row not found"

            })

        headers = sheet.row_values(1)

        updates = []

        for col_index, header in enumerate(headers):

            value = data.get(
                header,
                ""
            )

            updates.append({
                "range":
                    gspread.utils.rowcol_to_a1(
                        target_row,
                        col_index + 1
                    ),
                "values":
                    [[str(value)]]
            })

        sheet.batch_update(updates)

        return jsonify({

            "status":"success"

        })

    except Exception as e:

        return jsonify({

            "status":"error",

            "message":str(e)

        })
    
@app.route(
    "/run-query",
    methods=["POST"]
)
@login_required
def run_query():

    try:

        query = request.json.get(
            "query"
        )

        df = get_sheet_data()

        result = sqldf(
            query,
            {
                "data": df
            }
        )

        return jsonify({

            "status":"success",

            "rows":
                result.fillna("")
                .to_dict(
                    orient="records"
                )

        })

    except Exception as e:

        return jsonify({

            "status":"error",

            "message":str(e)

        })
    


# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login_page")
    )

# =====================================
# AUTO OPEN
# =====================================

def open_browser():

    webbrowser.open_new(
        "http://127.0.0.1:5000"
    )

# =====================================
# RUN
# =====================================

if __name__ == "__main__":

    Timer(
        1,
        open_browser
    ).start()

    app.run(
        host="127.0.0.1",
        port=5005,
        debug=False
    )