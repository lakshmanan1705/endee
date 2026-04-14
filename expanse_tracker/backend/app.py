from __future__ import annotations

import io
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expenses.db"
VALID_TRANSACTION_TYPES = {"expense", "income"}


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    init_db()

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/api/expenses")
    def get_expenses():
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, title, amount, category, expense_date, notes, transaction_type, created_at
                FROM expenses
                ORDER BY expense_date DESC, id DESC
                """
            ).fetchall()
            summary = get_summary(connection)

        return jsonify({"expenses": [dict(row) for row in rows], "summary": summary})

    @app.post("/api/expenses")
    def create_expense():
        payload = request.get_json(silent=True) or {}
        title = (payload.get("title") or "").strip()
        category = (payload.get("category") or "").strip()
        notes = (payload.get("notes") or "").strip()
        expense_date = payload.get("expense_date")
        transaction_type = (payload.get("transaction_type") or "expense").strip().lower()

        if not title:
            return jsonify({"message": "Title is required."}), 400

        if not category:
            return jsonify({"message": "Category is required."}), 400

        if transaction_type not in VALID_TRANSACTION_TYPES:
            return jsonify({"message": "Transaction type must be expense or income."}), 400

        try:
            amount = float(payload.get("amount"))
        except (TypeError, ValueError):
            return jsonify({"message": "Amount must be a valid number."}), 400

        if amount <= 0:
            return jsonify({"message": "Amount must be greater than zero."}), 400

        if not is_valid_date(expense_date):
            return jsonify({"message": "Expense date must be in YYYY-MM-DD format."}), 400

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO expenses (title, amount, category, expense_date, notes, transaction_type)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (title, amount, category, expense_date, notes, transaction_type),
            )
            connection.commit()

            created = connection.execute(
                """
                SELECT id, title, amount, category, expense_date, notes, transaction_type, created_at
                FROM expenses
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()

        return jsonify({"expense": dict(created)}), 201

    @app.delete("/api/expenses/<int:expense_id>")
    def delete_expense(expense_id: int):
        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Entry not found."}), 404

        return jsonify({"message": "Entry deleted successfully."})

    @app.get("/api/report")
    def generate_report():
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT title, category, amount, expense_date, notes, transaction_type
                FROM expenses
                ORDER BY expense_date DESC, id DESC
                """
            ).fetchall()
            totals = get_summary(connection)

        pdf_buffer = build_pdf(rows, totals)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"expense_report_{timestamp}.pdf",
        )

    return app


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                notes TEXT,
                transaction_type TEXT NOT NULL DEFAULT 'expense',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        ensure_transaction_type_column(connection)
        connection.commit()


def ensure_transaction_type_column(connection: sqlite3.Connection) -> None:
    columns = connection.execute("PRAGMA table_info(expenses)").fetchall()
    column_names = {column["name"] for column in columns}
    if "transaction_type" not in column_names:
        connection.execute(
            """
            ALTER TABLE expenses
            ADD COLUMN transaction_type TEXT NOT NULL DEFAULT 'expense'
            """
        )


def get_summary(connection: sqlite3.Connection) -> dict[str, float | int]:
    summary = connection.execute(
        """
        SELECT
            COUNT(*) AS total_entries,
            COALESCE(SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
        FROM expenses
        """
    ).fetchone()

    total_income = float(summary["total_income"])
    total_expense = float(summary["total_expense"])
    return {
        "total_entries": summary["total_entries"],
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
    }


def is_valid_date(value: str | None) -> bool:
    if not value:
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False

    return True


def ellipsize(text: str, max_width: float, font_name: str = "Helvetica", font_size: int = 9) -> str:
    if stringWidth(text, font_name, font_size) <= max_width:
        return text

    suffix = "..."
    available_width = max_width - stringWidth(suffix, font_name, font_size)
    trimmed = text
    while trimmed and stringWidth(trimmed, font_name, font_size) > available_width:
        trimmed = trimmed[:-1]
    return f"{trimmed}{suffix}"


def build_pdf(rows: list[sqlite3.Row], totals: dict[str, float | int]) -> io.BytesIO:
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    content = []
    generated_at = datetime.now().strftime("%d %b %Y, %I:%M %p")
    table_data = [["Title", "Type", "Category", "Date", "Amount", "Notes"]]

    for row in rows:
        table_data.append(
            [
                ellipsize(row["title"], 70),
                row["transaction_type"].title(),
                ellipsize(row["category"], 55),
                row["expense_date"],
                f"Rs. {row['amount']:.2f}",
                ellipsize(row["notes"] or "-", 120),
            ]
        )

    if len(table_data) == 1:
        table_data.append(["No records found", "-", "-", "-", "Rs. 0.00", "-"])

    header = Table(
        [
            ["Expense Tracker Report", f"Generated: {generated_at}"],
            [f"Total Entries: {totals['total_entries']}", f"Balance: Rs. {totals['balance']:.2f}"],
            [
                f"Total Income: Rs. {totals['total_income']:.2f}",
                f"Total Expense: Rs. {totals['total_expense']:.2f}",
            ],
        ],
        colWidths=[90 * mm, 70 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ]
        )
    )

    expense_table = Table(
        table_data,
        colWidths=[32 * mm, 20 * mm, 26 * mm, 22 * mm, 24 * mm, 47 * mm],
    )
    expense_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eff6ff")]),
            ]
        )
    )

    content.append(header)
    content.append(Spacer(1, 12))
    content.append(expense_table)
    document.build(content)
    buffer.seek(0)
    return buffer


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
