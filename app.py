import csv
import json
import os
from datetime import date

import streamlit as st
import pandas as pd

# ---------------- FILES ----------------

EXPENSE_FILE = "expenses.csv"
BUDGET_FILE = "budget.json"

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Student Expense & Budget Assistant",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Student Expense & Budget Assistant")
st.write("Manage your monthly budget and track your expenses.")

# ---------------- LOAD BUDGET ----------------

def load_budget():
    if os.path.exists(BUDGET_FILE):
        try:
            with open(BUDGET_FILE, "r") as file:
                data = json.load(file)
                return float(data.get("budget", 10000))
        except (json.JSONDecodeError, ValueError):
            return 10000.0

    return 10000.0


def save_budget(budget):
    with open(BUDGET_FILE, "w") as file:
        json.dump({"budget": budget}, file, indent=4)


# ---------------- LOAD EXPENSES ----------------

def load_expenses():
    if not os.path.exists(EXPENSE_FILE):
        return pd.DataFrame(
            columns=["Date", "Category", "Amount", "Description"]
        )

    try:
        df = pd.read_csv(EXPENSE_FILE)

        required_columns = [
            "Date",
            "Category",
            "Amount",
            "Description"
        ]

        for column in required_columns:
            if column not in df.columns:
                df[column] = ""

        df["Amount"] = pd.to_numeric(
            df["Amount"], errors="coerce"
        ).fillna(0)

        return df[required_columns]

    except pd.errors.EmptyDataError:
        return pd.DataFrame(
            columns=["Date", "Category", "Amount", "Description"]
        )


def save_expense(expense_date, category, amount, description):
    file_exists = (
        os.path.exists(EXPENSE_FILE)
        and os.path.getsize(EXPENSE_FILE) > 0
    )

    with open(EXPENSE_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date",
                "Category",
                "Amount",
                "Description"
            ])

        writer.writerow([
            expense_date,
            category,
            amount,
            description
        ])


# ---------------- BUDGET SETTINGS ----------------

st.sidebar.header("⚙️ Monthly Budget")

current_budget = load_budget()

with st.sidebar.form("budget_form"):
    new_budget = st.number_input(
        "Enter your monthly budget (₹)",
        min_value=0.0,
        value=float(current_budget),
        step=500.0
    )

    save_budget_button = st.form_submit_button(
        "Save Budget"
    )

if save_budget_button:
    save_budget(new_budget)
    st.sidebar.success("Budget saved successfully!")
    st.rerun()

budget = load_budget()

# ---------------- LOAD DATA ----------------

df = load_expenses()

if not df.empty:
    df["Date"] = pd.to_datetime(
        df["Date"], errors="coerce"
    )

    df["Category"] = (
        df["Category"].astype(str).str.strip().str.title()
    )

    df["Description"] = (
        df["Description"].fillna("").astype(str)
    )

# Current month expenses
today = date.today()

if not df.empty:
    monthly_df = df[
        (df["Date"].dt.month == today.month)
        & (df["Date"].dt.year == today.year)
    ].copy()
else:
    monthly_df = df.copy()

total_expenses = float(monthly_df["Amount"].sum())

remaining_balance = budget - total_expenses

# ---------------- SUMMARY CARDS ----------------

st.subheader("📊 Monthly Budget Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Monthly Budget",
    f"₹{budget:,.2f}"
)

col2.metric(
    "Total Expenses",
    f"₹{total_expenses:,.2f}"
)

col3.metric(
    "Remaining Balance",
    f"₹{remaining_balance:,.2f}"
)

if remaining_balance < 0:
    st.error("⚠️ Warning! You have exceeded your monthly budget.")
elif budget > 0 and remaining_balance <= budget * 0.2:
    st.warning("⚠️ You have used most of your monthly budget.")
else:
    st.success("✅ You are within your monthly budget.")

if budget > 0:
    progress = min(total_expenses / budget, 1.0)

    st.write("Budget Usage")
    st.progress(progress)

    st.caption(
        f"You have used {progress * 100:.1f}% of your budget."
    )

# ---------------- ADD EXPENSE ----------------

st.divider()

st.subheader("➕ Add New Expense")

with st.form("expense_form", clear_on_submit=True):

    expense_date = st.date_input(
        "Expense Date",
        value=date.today()
    )

    category = st.selectbox(
        "Expense Category",
        [
            "Food",
            "Travel",
            "Education",
            "Shopping",
            "Entertainment",
            "Bills",
            "Health",
            "Other"
        ]
    )

    amount = st.number_input(
        "Expense Amount (₹)",
        min_value=0.0,
        step=10.0
    )

    description = st.text_input(
        "Expense Description",
        placeholder="Example: Lunch, bus ticket, books"
    )

    add_button = st.form_submit_button(
        "Add Expense"
    )

if add_button:

    if amount <= 0:
        st.error("Please enter an amount greater than zero.")

    else:
        save_expense(
            expense_date.strftime("%Y-%m-%d"),
            category,
            amount,
            description
        )

        st.success("Expense added successfully!")
        st.rerun()

# ---------------- ALL EXPENSES ----------------

st.divider()

st.subheader("📋 All Expenses")

if df.empty:

    st.info("No expenses recorded yet. Add your first expense above.")

else:

    st.dataframe(
        df.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ---------------- CATEGORY SUMMARY ----------------

st.divider()

st.subheader("📁 Category Summary")

if monthly_df.empty:

    st.info("No expenses found for this month.")

else:

    category_summary = (
        monthly_df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=False)
    )

    st.dataframe(
        category_summary,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        category_summary.set_index("Category")["Amount"]
    )

    st.subheader("🥧 Expense Distribution")

    st.dataframe(
        category_summary,
        use_container_width=True,
        hide_index=True
    )

# ---------------- DOWNLOAD CSV ----------------

st.divider()

st.subheader("📥 Download Expenses")

if not df.empty:

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Expenses CSV",
        data=csv_data,
        file_name="student_expenses.csv",
        mime="text/csv"
    )

else:
    st.caption("Add expenses to enable CSV download.")

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Student Expense & Budget Assistant | "
    "Built using Python, Streamlit and Pandas"
)
