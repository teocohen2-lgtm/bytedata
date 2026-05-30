from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import pandas as pd
from functools import wraps
import webbrowser
from threading import Timer
import json
import os


 
app = Flask(__name__)

all_data = []

PROGRESS_FILE = "progress.json"


app.secret_key = "bytedata_secure_session_key"

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

                "status":"success"

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
# FETCH NEXT ROW
# =====================================

@app.route("/fetch-next-row")
@login_required
def fetch_next_row():

    try:

        logged_user = session.get(
            "username"
        ).lower()

        df = pd.read_csv(
            GOOGLE_SHEET_CSV
        )

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
        port=5000,
        debug=False
    )