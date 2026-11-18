
import connector as c


def pause():
    input("\nPress Enter to continue...")


def get_number(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("Please enter a valid number.")


def get_amount(message):
    while True:
        try:
            amount = float(input(message))
            if amount < 0:
                print("Amount cannot be negative.")
            else:
                return amount
        except ValueError:
            print("Please enter a valid amount.")


def display_tours():
    sql = """
        SELECT id, title, detail, start_date, days,
               adult_rate, child_rate
        FROM tour
        WHERE is_deleted = 0
        ORDER BY id
    """
    tours = c.fetchData(sql)

    print("\n---------------- TOUR LIST ----------------")
    print(f"{'ID':<5}{'TITLE':<25}{'START DATE':<15}{'DAYS':<8}{'ADULT':<12}{'CHILD':<12}")
    print("-" * 80)

    for tour in tours:
        print(
            f"{tour['id']:<5}"
            f"{tour['title']:<25}"
            f"{str(tour['start_date']):<15}"
            f"{str(tour['days']):<8}"
            f"{str(tour['adult_rate']):<12}"
            f"{str(tour['child_rate']):<12}"
        )

    if len(tours) == 0:
        print("No tours found.")

    return tours


def tour_exists(tourid):
    sql = "SELECT id FROM tour WHERE id = %s AND is_deleted = 0"
    result = c.fetchData(sql, (tourid,))
    return len(result) > 0


def display_transactions():
    sql = """
        SELECT t.id, t.tourid, tr.title, t.amount,
               t.flag, t.description, t.challanno, t.trandate
        FROM `transaction` t
        LEFT JOIN tour tr ON t.tourid = tr.id
        WHERE t.is_deleted = 0
        ORDER BY t.id DESC
    """
    transactions = c.fetchData(sql)

    print("\n---------------- TRANSACTION LIST ----------------")
    print(f"{'ID':<5}{'TOUR ID':<10}{'TOUR':<20}{'AMOUNT':<12}{'TYPE':<12}{'DATE':<15}")
    print("-" * 80)

    for row in transactions:
        if row['flag'] == 1:
            transaction_type = "Income"
        else:
            transaction_type = "Expense"

        print(
            f"{row['id']:<5}"
            f"{str(row['tourid']):<10}"
            f"{str(row['title'] or '')[:19]:<20}"
            f"{str(row['amount']):<12}"
            f"{transaction_type:<12}"
            f"{str(row['trandate']):<15}"
        )

    if len(transactions) == 0:
        print("No transactions found.")

    return transactions


# ---------------- TOUR MANAGEMENT ----------------

def insert_tour():
    print("\n--------- INSERT TOUR ---------")

    title = input("Enter tour title: ")
    detail = input("Enter tour detail: ")
    start_date = input("Enter start date (YYYY-MM-DD): ")
    days = get_number("Enter number of days: ")
    adult_rate = get_amount("Enter adult rate: ")
    child_rate = get_amount("Enter child rate: ")

    sql = """
        INSERT INTO tour
        (title, detail, start_date, days, adult_rate, child_rate)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (title, detail, start_date, days, adult_rate, child_rate)

    if c.runSQL(sql, values):
        print("Tour inserted successfully.")


def update_tour():
    display_tours()

    tourid = get_number("\nEnter tour ID to update: ")

    if not tour_exists(tourid):
        print("Tour not found.")
        return

    title = input("Enter new title: ")
    detail = input("Enter new detail: ")
    start_date = input("Enter new start date (YYYY-MM-DD): ")
    days = get_number("Enter new number of days: ")
    adult_rate = get_amount("Enter new adult rate: ")
    child_rate = get_amount("Enter new child rate: ")

    sql = """
        UPDATE tour
        SET title = %s, detail = %s, start_date = %s,
            days = %s, adult_rate = %s, child_rate = %s
        WHERE id = %s AND is_deleted = 0
    """

    values = (
        title, detail, start_date, days,
        adult_rate, child_rate, tourid
    )

    if c.runSQL(sql, values):
        print("Tour updated successfully.")
    else:
        print("Tour not updated.")


def delete_tour():
    display_tours()

    tourid = get_number("\nEnter tour ID to delete: ")

    if not tour_exists(tourid):
        print("Tour not found.")
        return

    sql = """
        SELECT id FROM `transaction`
        WHERE tourid = %s AND is_deleted = 0
    """

    transactions = c.fetchData(sql, (tourid,))

    if len(transactions) > 0:
        print("This tour has transactions. Delete those transactions first.")
        return

    sql = "UPDATE tour SET is_deleted = 1 WHERE id = %s"

    if c.runSQL(sql, (tourid,)):
        print("Tour deleted successfully.")


def tour_management():
    while True:
        print("\n========== TOUR MANAGEMENT ==========")
        print("1. Insert Tour")
        print("2. Update Tour")
        print("3. Delete Tour")
        print("4. View Tours")
        print("5. Back to Main Menu")

        choice = get_number("Enter your choice: ")

        if choice == 1:
            insert_tour()
            pause()
        elif choice == 2:
            update_tour()
            pause()
        elif choice == 3:
            delete_tour()
            pause()
        elif choice == 4:
            display_tours()
            pause()
        elif choice == 5:
            break
        else:
            print("Invalid choice.")


# ---------------- TRANSACTION MANAGEMENT ----------------

def insert_transaction():
    print("\n--------- INSERT TRANSACTION ---------")

    display_tours()

    tourid = get_number("\nEnter tour ID: ")

    if not tour_exists(tourid):
        print("Invalid tour ID.")
        return

    amount = get_amount("Enter amount: ")

    print("\n1. Income")
    print("2. Expense")

    flag = get_number("Enter transaction type: ")

    if flag not in [1, 2]:    
        print("Invalid transaction type.")
        return

    description = input("Enter description: ")
    challanno = input("Enter challan number: ")
    trandate = input("Enter transaction date (YYYY-MM-DD): ")

    sql = """
        INSERT INTO `transaction`
        (tourid, amount, flag, description, challanno, trandate)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        tourid, amount, flag, description,
        challanno, trandate
    )

    if c.runSQL(sql, values):
        print("Transaction inserted successfully.")


def delete_transaction():
    display_transactions()

    transaction_id = get_number("\nEnter transaction ID to delete: ")

    sql = """
        UPDATE `transaction`
        SET is_deleted = 1
        WHERE id = %s AND is_deleted = 0
    """

    if c.runSQL(sql, (transaction_id,)):
        print("Transaction deleted successfully.")
    else:
        print("Transaction not found.")


def search_transactions():
    print("\n--------- SEARCH TRANSACTIONS ---------")
    print("1. Search by Tour ID")
    print("2. Search by Transaction Type")
    print("3. Search by Date")

    choice = get_number("Enter your choice: ")

    if choice == 1:
        tourid = get_number("Enter tour ID: ")

        sql = """
            SELECT id, tourid, amount, flag, description,
                   challanno, trandate
            FROM `transaction`
            WHERE tourid = %s AND is_deleted = 0
            ORDER BY trandate
        """
        values = (tourid,)

    elif choice == 2:
        print("1. Income")
        print("2. Expense")

        flag = get_number("Enter type: ")

        if flag not in [1, 2]:
            print("Invalid type.")
            return

        sql = """
            SELECT id, tourid, amount, flag, description,
                   challanno, trandate
            FROM `transaction`
            WHERE flag = %s AND is_deleted = 0
            ORDER BY trandate
        """
        values = (flag,)

    elif choice == 3:
        trandate = input("Enter date (YYYY-MM-DD): ")

        sql = """
            SELECT id, tourid, amount, flag, description,
                   challanno, trandate
            FROM `transaction`
            WHERE trandate = %s AND is_deleted = 0
            ORDER BY id
        """
        values = (trandate,)

    else:
        print("Invalid choice.")
        return

    rows = c.fetchData(sql, values)

    print("\nID | Tour ID | Amount | Type | Date | Description")
    print("-" * 75)

    for row in rows:
        if row['flag'] == 1:
            transaction_type = "Income"
        else:
            transaction_type = "Expense"

        print(
            row['id'], "|",
            row['tourid'], "|",
            row['amount'], "|",
            transaction_type, "|",
            row['trandate'], "|",
            row['description']
        )

    if len(rows) == 0:
        print("No matching transactions found.")


def transaction_management():
    while True:
        print("\n======= TRANSACTION MANAGEMENT =======")
        print("1. Insert Transaction")
        print("2. View Transactions")
        print("3. Delete Transaction")
        print("4. Search Transactions")
        print("5. Back to Main Menu")

        choice = get_number("Enter your choice: ")

        if choice == 1:
            insert_transaction()
            pause()
        elif choice == 2:
            display_transactions()
            pause()
        elif choice == 3:
            delete_transaction()
            pause()
        elif choice == 4:
            search_transactions()
            pause()
        elif choice == 5:
            break
        else:
            print("Invalid choice.")


# ---------------- REPORT MANAGEMENT ----------------

def show_report(rows):
    print("\n---------------- REPORT ----------------")
    print(f"{'TOUR ID':<10}{'AMOUNT':<15}{'TYPE':<12}{'DATE':<15}{'DESCRIPTION'}")
    print("-" * 85)

    total_income = 0
    total_expense = 0

    for row in rows:
        if row['flag'] == 1:
            transaction_type = "Income"
            total_income += float(row['amount'])
        else:
            transaction_type = "Expense"
            total_expense += float(row['amount'])

        print(
            f"{str(row['tourid']):<10}"
            f"{str(row['amount']):<15}"
            f"{transaction_type:<12}"
            f"{str(row['trandate']):<15}"
            f"{str(row['description'] or '')}"
        )

    print("-" * 85)
    print("Total Income :", round(total_income, 2))
    print("Total Expense:", round(total_expense, 2))
    print("Net Balance  :", round(total_income - total_expense, 2))


def month_wise_report():
    year = get_number("Enter year (YYYY): ")
    month = get_number("Enter month (1-12): ")

    if month < 1 or month > 12:
        print("Invalid month.")
        return

    sql = """
        SELECT tourid, amount, flag, description, trandate
        FROM `transaction`
        WHERE YEAR(trandate) = %s
          AND MONTH(trandate) = %s
          AND is_deleted = 0
        ORDER BY trandate
    """

    rows = c.fetchData(sql, (year, month))
    show_report(rows)


def quarter_wise_report():
    year = get_number("Enter year (YYYY): ")
    quarter = get_number("Enter quarter (1-4): ")

    if quarter < 1 or quarter > 4:
        print("Invalid quarter.")
        return

    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2

    sql = """
        SELECT tourid, amount, flag, description, trandate
        FROM `transaction`
        WHERE YEAR(trandate) = %s
          AND MONTH(trandate) BETWEEN %s AND %s
          AND is_deleted = 0
        ORDER BY trandate
    """

    rows = c.fetchData(sql, (year, start_month, end_month))
    show_report(rows)


def year_wise_report():
    year = get_number("Enter year (YYYY): ")

    sql = """
        SELECT tourid, amount, flag, description, trandate
        FROM `transaction`
        WHERE YEAR(trandate) = %s
          AND is_deleted = 0
        ORDER BY trandate
    """

    rows = c.fetchData(sql, (year,))
    show_report(rows)


def tour_wise_report():
    display_tours()

    tourid = get_number("\nEnter tour ID: ")

    if not tour_exists(tourid):
        print("Tour not found.")
        return

    sql = """
        SELECT tourid, amount, flag, description, trandate
        FROM `transaction`
        WHERE tourid = %s AND is_deleted = 0
        ORDER BY trandate
    """

    rows = c.fetchData(sql, (tourid,))
    show_report(rows)


def all_tours_report():
    sql = """
        SELECT
            tr.id,
            tr.title,
            COALESCE(SUM(
                CASE WHEN t.flag = 1 THEN t.amount ELSE 0 END
            ), 0) AS income,
            COALESCE(SUM(
                CASE WHEN t.flag = 2 THEN t.amount ELSE 0 END
            ), 0) AS expense
        FROM tour tr
        LEFT JOIN `transaction` t
            ON tr.id = t.tourid AND t.is_deleted = 0
        WHERE tr.is_deleted = 0
        GROUP BY tr.id, tr.title
        ORDER BY tr.id
    """

    rows = c.fetchData(sql)

    print("\n------------- ALL TOURS REPORT -------------")
    print(f"{'ID':<8}{'TOUR TITLE':<25}{'INCOME':<15}{'EXPENSE':<15}{'BALANCE':<15}")
    print("-" * 78)

    for row in rows:
        income = float(row['income'])
        expense = float(row['expense'])
        balance = income - expense

        print(
            f"{row['id']:<8}"
            f"{row['title'][:24]:<25}"
            f"{income:<15.2f}"
            f"{expense:<15.2f}"
            f"{balance:<15.2f}"
        )

    if len(rows) == 0:
        print("No tours found.")


def report_management():
    while True:
        print("\n=========== REPORT MANAGEMENT ===========")
        print("1. Month Wise Income Expense Report")
        print("2. Quarter Wise Income Expense Report")
        print("3. Year Wise Income Expense Report")
        print("4. Tour Wise Income Expense Report")
        print("5. All Tours Income Expense Report")
        print("6. Back to Main Menu")

        choice = get_number("Enter your choice: ")

        if choice == 1:
            month_wise_report()
            pause()
        elif choice == 2:
            quarter_wise_report()
            pause()
        elif choice == 3:
            year_wise_report()
            pause()
        elif choice == 4:
            tour_wise_report()
            pause()
        elif choice == 5:
            all_tours_report()
            pause()
        elif choice == 6:
            break
        else:
            print("Invalid choice.")


# ---------------- MAIN MENU ----------------

def main():
    print("Trip Income Expense Tracker Started")

    while True:
        print("\n========================================")
        print("      TRIP INCOME EXPENSE TRACKER")
        print("========================================")
        print("1. Tour Management")
        print("2. Transaction Management")
        print("3. Report Management")
        print("4. Exit")

        choice = get_number("Enter your choice: ")

        if choice == 1:
            tour_management()
        elif choice == 2:
            transaction_management()
        elif choice == 3:
            report_management()
        elif choice == 4:
            print("Thank you for using Trip Income Expense Tracker.")
            break
        else:
            print("Invalid choice. Please try again.")


main()
