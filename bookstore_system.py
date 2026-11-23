import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class Bookstore:

    def __init__(self):
        self.inventory = pd.read_csv("inventory.csv")
        self.sales = pd.read_csv("sales.csv")

    
    def save_inventory(self):
        self.inventory.to_csv("inventory.csv", index=False)

    def save_sales(self):
        self.sales.to_csv("sales.csv", index=False)
    
    def show_books(self):
        print("\n----- BOOK INVENTOREY -----")
        print(self.inventory.to_string(index=False))

    def add_book(self, title, author, price, quantity, genre):

        if price <= 0 or quantity < 0:
            print("Invalid price or quantity")
            return

        if title.lower() in self.inventory["Title"].str.lower().values:
            print("Book already exists")
            return

        new_book = {
            "Title": title,
            "Author": author,
            "Genre": genre,
            "Price": price,
            "Quantity": quantity
        }

        self.inventory.loc[len(self.inventory)] = new_book
        self.save_inventory()

        print("Book Added successfully!")


    
    def remove_book(self, title):

        found = False

        for i in range(len(self.inventory)):
            if self.inventory.loc[i, "Title"].lower() == title.lower():
                self.inventory = self.inventory.drop(i)
                found = True
                break

        if found:
            self.inventory = self.inventory.reset_index(drop=True)
            self.save_inventory()
            print("Book removed successfully")
        else:
            print("Book not found!")


    
    def update_inventory(self, title, quantity):

        if quantity < 0:
            print("Quantity cannot negative")
            return

        found = False

        for i in range(len(self.inventory)):
            if self.inventory.loc[i, "Title"].lower() == title.lower():
                self.inventory.loc[i, "Quantity"] = quantity
                found = True
                break

        if found:
            self.save_inventory()
            print("Quantity updated successfully!!")
        else:
            print("Book not found!")


    
    def record_sale(self, title, quantity):

        if quantity <= 0:
            print("Enter valid quantity!")
            return

        found = False

        for i in range(len(self.inventory)):
            if self.inventory.loc[i, "Title"].lower() == title.lower():
                found = True
                break

        if not found:
            print("Book not found")
            return

        available = int(self.inventory.loc[i, "Quantity"])

        if quantity > available:
            print("Not enough stock available")
            return

        price = float(self.inventory.loc[i, "Price"])
        revenue = price * quantity

        self.inventory.loc[i, "Quantity"] = available - quantity

        new_sale = {
            "Date": pd.Timestamp.today().strftime("%Y-%m-%d"),
            "Title": title,
            "Quantity Sold": quantity,
            "Total revenue": revenue
        }

        self.sales.loc[len(self.sales)] = new_sale

        self.save_inventory()
        self.save_sales()

        print("Sale recorded successfully.")
        print("Total Revenue: Rs.", revenue)


    
    def generate_report(self):

        print("\n----- BOOKSTORE REPORT -----")

        total_books = np.sum(self.inventory["Quantity"])
        total_value = np.sum(self.inventory["Price"] * self.inventory["Quantity"])


        print("Total Book Titles:", len(self.inventory))
        print("Total Books Available:", total_books)
        print("Inventory Value: Rs.", total_value)


        if len(self.sales) == 0:
            print("No sales recorded")
            return

        revenue = np.array(self.sales["Total Revenue"])
        quantity = np.array(self.sales["Quantity Sold"])

        print("Total Books Sold:", np.sum(quantity))
        print("Total Revenue: Rs.", np.sum(revenue))
        print("Average Book Price: Rs.",
            np.mean(self.inventory["Price"]))


        best_seller = self.sales.groupby("Title")["Quantity Sold"].sum().idxmax()

        print("Best-Selling Book:", best_seller)

       
        data = pd.merge(
            self.sales,
            self.inventory[["Title", "Genre", "Author"]],
            on="Title",
            how="left"
        )

        print("\nSales by Genre:")
        print(data.groupby("Genre")["Quantity Sold"].sum())

        print("\nSales by Author:")
        print(data.groupby("Author")["Quantity Sold"].sum())

        
        self.sales["Date"] = pd.to_datetime(self.sales["Date"])

        monthly = self.sales.groupby(
            self.sales["Date"].dt.to_period("M"))["Total Revenue"].sum()

        if len(monthly) >= 2 and monthly.iloc[2] != 0:

            growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] )*100

            print("Monthly sales growth:", round(growth, 2), "%")
        else:
            print("Not enough monthly data to calculate growth")


    
    def show_charts(self):

            if len(self.sales) == 0:
                print("No sales data available.")
                return

            while True:

                print("\n---- GRAPH MENU ----")
                print()
                print("1. Bar Chart - sales by genre")
                print("2. Line Graph - Monthly Sales")
                print("3. Pie Chart - Revenue Genre")
                print("4. Heatmap - Price  and Sales")
                print("5. Exit")

                choice = input("Select a graph: ")

            
                data = pd.merge(
                    self.sales,
                    self.inventory[["Title", "Genre", "Price"]],
                    on="Title",
                    how="left"
                )

                if choice == "1":
                    genre_sales = data.groupby("Genre")["Quantity Sold"].sum()

                    genre_sales.plot(kind="bar")

                    plt.title("Sales by Genre")
                    plt.xlabel("Genre")
                    plt.ylabel("Books Sold")
                    plt.tight_layout()
                    plt.show()

                elif choice == "2":
                    data["Date"] = pd.to_datetime(data["Date"])
                    monthly = data.groupby(data["Date"].dt.to_period("M"))["Total Revenue"].sum()
                    monthly.index = monthly.index.astype(str)

                    monthly.plot(kind="line", marker="o")

                    plt.title("Monthly Sales Trends")
                    plt.xlabel("Month")
                    plt.ylabel("Revenue")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.show()

                elif choice == "3":
                    genre_revenue = data.groupby("Genre")["Total Revenue"].sum()
                    genre_revenue.plot(
                        kind="pie",
                        autopct="%1.1f%%"
                    )
                    plt.title("Revenue by Genre")
                    plt.ylabel("")
                    plt.tight_layout()
                    plt.show()

                elif choice == "4":
                    book_data = data.groupby("Title").agg(
                        Price=("Price", "mean"),
                        Sales=("Quantity Sold", "sum")
                    )

                    if len(book_data) >= 2:

                        correlation = book_data.corr()
                        sns.heatmap(
                            correlation,
                            annot=True,
                            cmap="coolwarm"
                        )  
                        plt.title("Price and Sales Correlation")
                        plt.tight_layout()
                        plt.show()
                    else:
                        print("At least two books are required")


                elif choice == "5":
                    print("Back to Main Menu...")
                    break
                else:
                    print("Invalid choice")


def get_number(message, allow_zero=False):

    while True:
        try:
            number = float(input(message))

            if number < 0:
                print("Enter a positive number")
            elif number == 0 and not allow_zero:
                print("Number must be greater than zero")
            else:
                return number

        except ValueError:
            print("Please enter valid number")


def main():

    bookstore = Bookstore()

    while True:

        print("\n===== BOOKSTORE MENU =====")
        print("1. Show All Books")
        print("2. Add New Book")
        print("3. Remove Book")
        print("4. Update Book Quantity")
        print("5. Record Book Sale")
        print("6. Generate Report(Based for Author)")
        print("7. Show Charts")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            bookstore.show_books()

        elif choice == "2":

            title = input("Enter Book Title: ")
            author = input("Enter Author: ")
            genre = input("Enter Genre: ")
            price = get_number("enter Price: ")
            quantity = int(get_number("Enter quantity: ", True))

            bookstore.add_book(title, author, price, quantity, genre)

        elif choice == "3":

            title = input("Enter Book title: ")
            bookstore.remove_book(title)

        elif choice == "4":

            title = input("Enter Book Title: ")
            quantity = int(get_number("Enter New Quantity: ", True))

            bookstore.update_inventory(title, quantity)

        elif choice == "5":

            title = input("Enter Book Title: ")
            quantity = int(get_number("Enter Quantity: "))

            bookstore.record_sale(title, quantity)

        elif choice == "6":
            bookstore.generate_report()

        elif choice == "7":
            bookstore.show_charts()

        elif choice == "8":
            print("Thank you!")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()