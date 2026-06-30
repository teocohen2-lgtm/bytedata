import sqlite3
import os

DB_PATH = os.getenv("BYTEDATA_DB_PATH", "bytedata.db")


ONBOARDING_COLUMNS = [
    "customer_id", "company_name", "contact_person", "email", "phone",
    "country", "subscription_plan", "subscription_amount", "currency",
    "status", "next_payment_date", "days_overdue", "payment_link",
    "last_contact_date", "last_message", "notes", "assigned_to",
    "payment_date", "expiry_date", "days_remaining",
    "subscription_duration", "auto_status", "renewal_amount",
    "payment_stage", "payment_link_status", "payment_sent_date",
    "payment_received_date", "migration_status", "migration_date",
    "payment_reference", "lead_id", "created_date",
    "renewal_followup_created", "last_renewal_date"
]

PAYMENT_FOLLOW_UP_COLUMNS = [
    "lead_id", "company_name", "contact_person", "email", "phone",
    "plan_interested", "payment_referer", "payment_link",
    "payment_status", "attempt_count", "assigned_to",
    "last_contact_date", "issue_type", "notes", "created_date"
]

SUPPORT_TASKS_COLUMNS = [
    "task_id", "conversation_id", "customer_id", "lead_id",
    "company_name", "customer_name", "customer_email", "assigned_to",
    "task_title", "task_description", "priority", "status",
    "created_by", "created_at", "due_date", "resolved_at", "notes"
]

COMMUNICATIONS_COLUMNS = [
    "conversation_id", "message_id", "customer_id", "lead_id",
    "company_name", "customer_name", "customer_email", "customer_phone",
    "sender", "message_type", "subject", "message", "attachment",
    "status", "priority", "assigned_to", "source", "created_at",
    "read_status", "replied_at", "action_required", "payment_status",
    "dataset_status"
]



DATA_OPERATIONS_COLUMNS = [
    "id",
    "product_name",
    "brand",
    "industry",
    "manufacturer",
    "manufacture_country",
    "manufacture_city",
    "supplier_country",
    "warehouse_country",
    "price_usd",
    "bulk_price_usd",
    "currency",
    "china_total_sales",
    "global_total_sales",
    "monthly_sales",
    "rating",
    "review_count",
    "stock_left",
    "launch_year",
    "supplier_email",
    "supplier_phone",
    "warehouse_location",
    "shipping_days",
    "shipping_mode",
    "minimum_order_qty",
    "return_rate_percent",
    "discount_percent",
    "marketplace",
    "top_market_region",
    "fake_or_duplicate_listing_score",
    "certification",
    "payment_terms",
    "product_status",
    "supplier_trust_score",
    "estimated_profit_margin",
    "container_capacity_units",
    "avg_delivery_delay_days",
    "assign",
    "verified"
]

TABLE_COLUMNS = {
    "onboarding": ONBOARDING_COLUMNS,
    "payment_follow_up": PAYMENT_FOLLOW_UP_COLUMNS,
    "support_tasks": SUPPORT_TASKS_COLUMNS,
    "communications": COMMUNICATIONS_COLUMNS,
    "data_operations": DATA_OPERATIONS_COLUMNS

}

# def get_conn():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn
def get_conn():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")

    return conn


def safe_table(table):
    if table not in TABLE_COLUMNS:
        raise ValueError(f"Invalid table name: {table}")
    return table


# def init_db():
#     conn = get_conn()
#     cur = conn.cursor()

#     for table, columns in TABLE_COLUMNS.items():
#         cur.execute(f"""
#             CREATE TABLE IF NOT EXISTS {table} (
#                 {", ".join([col + " TEXT" for col in columns])}
#             )
#         """)

#     conn.commit()
#     conn.close()

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    for table, columns in TABLE_COLUMNS.items():
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                {", ".join([col + " TEXT" for col in columns])}
            )
        """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_onboarding_customer_id
        ON onboarding(customer_id)
    """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_follow_up_lead_id
        ON payment_follow_up(lead_id)
    """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_support_tasks_task_id
        ON support_tasks(task_id)
    """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_communications_message_id
        ON communications(message_id)
    """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_data_operations_id
        ON data_operations(id)
    """)

    conn.commit()
    conn.close()


def select(table, where="", params=None, order_by="", limit=None):
    safe_table(table)

    params = params or []

    sql = f"SELECT * FROM {table}"

    if where:
        sql += f" WHERE {where}"

    if order_by:
        sql += f" ORDER BY {order_by}"

    if limit:
        sql += f" LIMIT {int(limit)}"

    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def select_one(table, where="", params=None, order_by=""):
    rows = select(
        table,
        where=where,
        params=params,
        order_by=order_by,
        limit=1
    )

    return rows[0] if rows else None


def insert(table, data):

    safe_table(table)

    columns = TABLE_COLUMNS[table]

    placeholders = ",".join(["?"] * len(columns))

    sql = f"""
        INSERT OR IGNORE INTO {table}
        ({",".join(columns)})
        VALUES ({placeholders})
    """

    values = [
        str(data.get(col, ""))
        for col in columns
    ]

    conn = get_conn()

    conn.execute(sql, values)

    conn.commit()

    conn.close()


def update(table, updates, where, params=None):
    safe_table(table)

    if not updates:
        return

    params = params or []

    set_clause = ", ".join([
        f"{key} = ?"
        for key in updates.keys()
    ])

    values = [
        str(value)
        for value in updates.values()
    ]

    values.extend(params)

    sql = f"""
        UPDATE {table}
        SET {set_clause}
        WHERE {where}
    """

    conn = get_conn()
    conn.execute(sql, values)
    conn.commit()
    conn.close()


def delete(table, where, params=None):
    safe_table(table)

    params = params or []

    sql = f"""
        DELETE FROM {table}
        WHERE {where}
    """

    conn = get_conn()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


def count(table, where="", params=None):
    safe_table(table)

    params = params or []

    sql = f"SELECT COUNT(*) FROM {table}"

    if where:
        sql += f" WHERE {where}"

    conn = get_conn()
    result = conn.execute(sql, params).fetchone()[0]
    conn.close()

    return result


# Backward-compatible helpers

def get_all(table):
    return select(table)


def insert_row(table, columns, data):
    insert(table, data)


def count_rows(table):
    return count(table)


def find_by_lead_id(table, lead_id):
    return select_one(
        table,
        "lead_id = ?",
        [str(lead_id)]
    )


def find_by_lead_id_all(table, lead_id):
    return select(
        table,
        "lead_id = ?",
        [str(lead_id)]
    )


def find_by_customer_id(table, customer_id):
    return select_one(
        table,
        "customer_id = ?",
        [str(customer_id)]
    )


def delete_by_lead_id(table, lead_id):
    delete(
        table,
        "lead_id = ?",
        [str(lead_id)]
    )


def delete_by_customer_id(table, customer_id):
    delete(
        table,
        "customer_id = ?",
        [str(customer_id)]
    )


def update_by_customer_id(table, customer_id, updates):
    update(
        table,
        updates,
        "customer_id = ?",
        [str(customer_id)]
    )


def update_communications_by_lead_id(lead_id, updates):
    update(
        "communications",
        updates,
        "lead_id = ?",
        [str(lead_id)]
    )


def mark_messages_read_by_lead_id(lead_id):
    update(
        "communications",
        {"read_status": "Read"},
        "lead_id = ? AND lower(sender) = 'customer' AND lower(read_status) = 'unread'",
        [str(lead_id)]
    )

def get_next_numeric_id(table, id_column="id"):

    safe_table(table)

    conn = get_conn()

    row = conn.execute(
        f"""
        SELECT MAX(CAST({id_column} AS INTEGER))
        FROM {table}
        WHERE {id_column} GLOB '[0-9]*'
        """
    ).fetchone()

    conn.close()

    last_id = row[0] if row and row[0] is not None else 0

    return int(last_id) + 1