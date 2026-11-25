import csv
import os
from datetime import date

file_name = "expenses.csv"

print("\nSTUDENT EXPENSE & BUDGET ASSISTANT")
print("=" * 45)

# Get monthly budget
budget = float(input("\nEnter your monthly budget (₹): "))

while True:
    print("\n---------- MENU ----------")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. View Budget Summary")
    print("4. Category Summary")
    print("5. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":
        category = input("Enter expense category: ")
        amount = float(input("Enter expense amount (₹): "))
        description = input("Enter expense description: ")

        file_exists = os.path.exists(file_name)

        with open(file_name, "a", newline="") as file:
            writer = csv.writer(file)

            if not file_exists or os.path.getsize(file_name) == 0:
                writer.writerow([
                    "Date",
                    "Category",
                    "Amount",
                    "Description"
                ])

            writer.writerow([
                date.today(),
                category,
                amount,
                description
            ])

        print("\nExpense saved successfully! ✅")

    elif choice == "2":
        print("\n---------- ALL EXPENSES ----------")

        if not os.path.exists(file_name):
            print("No expenses found.")
        else:
            with open(file_name, "r", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    print(
                        row["Date"],
                        "|",
                        row["Category"],
                        "| ₹",
                        row["Amount"],
                        "|",
                        row["Description"]
                    )

    elif choice == "3":
        total_expenses = 0

        if os.path.exists(file_name):
            with open(file_name, "r", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    total_expenses += float(row["Amount"])

        remaining_balance = budget - total_expenses

        print("\n---------- BUDGET SUMMARY ----------")
        print("Monthly Budget: ₹", budget)
        print("Total Expenses: ₹", total_expenses)
        print("Remaining Balance: ₹", remaining_balance)

        if remaining_balance < 0:
            print("\n⚠️ Warning: You have exceeded your budget!")
        else:
            print("\nYou are within your budget. ✅")

    elif choice == "4":
        print("\n---------- CATEGORY SUMMARY ----------")

        category_totals = {}

        if not os.path.exists(file_name):
            print("No expenses found.")
        else:
            with open(file_name, "r", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    category = row["Category"].strip().title()
                    amount = float(row["Amount"])

                    if category in category_totals:
                        category_totals[category] += amount
                    else:
                        category_totals[category] = amount
            if len(category_totals) == 0:
                print("No expenses found.")
            else:
                for category, total in category_totals.items():
                    print(category, ": ₹", total)
    elif choice == "5":
        print("\nThank you for using Student Expense Assistant! 👋")
        break
