import pandas as pd
import os

# File paths
inventory_file = "inventory.csv"
database_file = "dealership.csv"

def load_inventory():
    """Load inventory from CSV file or create empty DataFrame if file doesn't exist"""
    try:
        df = pd.read_csv(inventory_file)
        # if the file is empty return a base/empty data frame with respect to tehir columns
        if df.empty:
            return pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity"])
        # Ensure ID column exists
        if "ID" not in df.columns:
            df["ID"] = range(1, len(df) + 1)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # exception to return an empty data frame when the file doesnt exist or runs into an error.
        return pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity"])

def save_inventory(df):
    """Save inventory DataFrame to CSV file"""
    # Ensure IDs are sequential
    df["ID"] = range(1, len(df) + 1) # reset each ID to maintain consistency after saving so that we dont have issues with another save
    df.to_csv(inventory_file, index=False) # Save it to CSV, while also maintaining the proper column as to not mess things up

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear') # Windows uses cls and others use clear

def view_inventory():
    """Display current inventory"""
    #loads our inventory to check for later
    df = load_inventory()
    # if empty return inventory empty, else you show the inventory
    if df.empty:
        print("\nInventory is empty.")
    else:
        print("\nCurrent Inventory:")
        print(df.to_string(index=False))

#allows the user to add cars manually whenever needed.
def add_manually():
    
    """Add car to inventory manually"""
    df = load_inventory()

    #initialization of variables ie company and model of cars
    print("\nAdding New Car Manually")
    company = input("Enter company: ").strip().title()
    model = input("Enter model: ").strip().title()
    
    # Validate year input for formatting
    while True:
        year = input("Enter year: ").strip()
        if year.isdigit() and len(year) == 4:
            break
        print("Invalid year format. Please enter a 4-digit year.")
    
    colour = input("Enter colour: ").strip().title()
    
    # Validate quantity input to make sure it stays positive 
    while True:
        try:
            quantity = int(input("Enter quantity: ").strip())
            if quantity > 0:
                break
            print("Quantity must be greater than 0.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Check if identical car already exists in inventory - case insensitive comparison
    mask = (df["Company"].str.lower() == company.lower()) & \
           (df["Model"].str.lower() == model.lower()) & \
           (df["Year"] == year) & \
           (df["Colour"].str.lower() == colour.lower())
    
    if any(mask):
        # Car exists, increment quantity 
        idx = df.loc[mask].index[0]
        current_qty = df.loc[idx, "Quantity"]
        df.loc[idx, "Quantity"] = current_qty + quantity
        car_id = df.loc[idx, "ID"]
        print(f"\nAdded {quantity} to existing inventory (ID: {car_id})")
        print(f"Total quantity now: {df.loc[idx, 'Quantity']}")
    else:
        # Add new car
        new_row = pd.DataFrame([{
            "ID": len(df) + 1,
            "Company": company,
            "Model": model,
            "Year": year,
            "Colour": colour,
            "Quantity": quantity
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        print(f"\nAdded new car to inventory (ID: {len(df)})")
    
    save_inventory(df) # save inventory after all this to keep it up to date

def add_from_database():
    """Add car to inventory by selecting from dealership database"""
    #check to see if database is accessible/valid 
    try:
        db = pd.read_csv(database_file)
        #if not throw an exception for an error when the database isnt found or empty
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print("\nDealership database not found or empty.")
        return
    # message to show the user that the ading is working
    print("\nAdding Car from Dealership Database")
    
    # List available companies
    companies = sorted(db["Company"].unique())
    print("\nAvailable companies:")
    for i, company in enumerate(companies, 1):
        print(f"{i}. {company}")
    
    # Select company
    while True:
        # asks the user for which company the car belongs to
        try:
            company_idx = int(input("\nSelect company number (0 to cancel): ").strip())
            if company_idx == 0:
                return
            if 1 <= company_idx <= len(companies):
                selected_company = companies[company_idx - 1]
                break
            print(f"Please enter a number between 1 and {len(companies)}")
            #exception for an error when a proper number isnt entered.
        except ValueError:
            print("Please enter a valid number.")
    
    # Filter models by selected company
    filtered_db = db[db["Company"].str.lower() == selected_company.lower()]
    models = sorted(filtered_db["Model"].unique())
    
    # List available models
    print(f"\nAvailable {selected_company} models:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    
    # Select model
    while True:
        # asks the user for the model of the car they want to add.
        try:
            model_idx = int(input("\nSelect model number (0 to cancel): ").strip())
            if model_idx == 0:
                return
            if 1 <= model_idx <= len(models):
                selected_model = models[model_idx - 1]
                break
            print(f"Please enter a number between 1 and {len(models)}")
            #another exception for when they enter something incorrect
        except ValueError:
            print("Please enter a valid number.")
    
    # Get remaining details such as the year of the car
    while True:
        year = input("Enter year: ").strip()
        if year.isdigit() and len(year) == 4:
            break
        print("Invalid year format. Please enter a 4-digit year.")
    
    colour = input("Enter colour: ").strip().title()

    #asks the user for the quantity of the car they would like to add
    while True:
        try:
            quantity = int(input("Enter quantity: ").strip())
            #if the quantity is proper we break out an move to the next step, if not we throw an error exception when invalid and a print statement which reloops when the number is less than 09
            if quantity > 0:
                break
            print("Quantity must be greater than 0.")

        #value error if the user doesnt enter a number
        except ValueError:
            print("Please enter a valid number.")
    
    # Add to inventory - case insensitive comparison
    df = load_inventory()
    mask = (df["Company"].str.lower() == selected_company.lower()) & \
           (df["Model"].str.lower() == selected_model.lower()) & \
           (df["Year"] == year) & \
           (df["Colour"].str.lower() == colour.lower())
    
    if any(mask):
        # Car exists, increment quantity
        idx = df.loc[mask].index[0]
        current_qty = df.loc[idx, "Quantity"]
        df.loc[idx, "Quantity"] = current_qty + quantity
        car_id = df.loc[idx, "ID"]
        print(f"\nAdded {quantity} to existing inventory (ID: {car_id})")
        print(f"Total quantity now: {df.loc[idx, 'Quantity']}")
    else:
        # Add new car
        new_row = pd.DataFrame([{
            "ID": len(df) + 1,
            "Company": selected_company,
            "Model": selected_model,
            "Year": year,
            "Colour": colour,
            "Quantity": quantity
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        print(f"\nAdded new car to inventory (ID: {len(df)})")

    #save the inventory right after adding to make sure it stays up to date 
    save_inventory(df)

def remove_inventory():
    """Remove cars from inventory by ID"""
    df = load_inventory()
    # if inventory is empty display the message to the user
    if df.empty:
        print("\nInventory is empty.")
        return
    #else just show what the database looks like currently and ask the user to select which one to remove
    print("\nRemove Car from Inventory")
    view_inventory()
    
    # Get car ID to remove
    while True:
        # try except to ask the user what numbered car they want to remove, if they dont enter a valid number throw and error, and if they pick 0 cancel them out of the remove.
        try:
            car_id = input("\nEnter car ID to remove (0 to cancel): ").strip()
            if car_id == "0":
                return
            car_id = int(car_id)
            if car_id in df["ID"].values:
                break
            print("ID not found in inventory. Please enter a valid ID.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Find the car
    mask = df["ID"] == car_id
    car_idx = df.loc[mask].index[0]
    car_info = df.loc[car_idx]
    current_quantity = car_info["Quantity"]

    # print out the selected car and its quantity to the user
    print(f"\nSelected car: {car_info['Company']} {car_info['Model']} ({car_info['Year']}, {car_info['Colour']})")
    print(f"Current quantity: {current_quantity}")
    
    # Get quantity to remove
    while True:
        try:
            quantity_to_remove = int(input(f"Enter quantity to remove (1-{current_quantity}): ").strip())
            if 1 <= quantity_to_remove <= current_quantity:
                break
            print(f"Please enter a number between 1 and {current_quantity}")
        except ValueError:
            print("Please enter a valid number.")
    
    # Remove cars
    # if the quantity is greater than the quanityt of the stock, remove all of that specific stock.
    if quantity_to_remove >= current_quantity:
        df = df[~mask]
        print(f"\nRemoved all {car_info['Company']} {car_info['Model']} (ID: {car_id}) from inventory")

    #otherwise remove specified amount
    else:
        df.loc[car_idx, "Quantity"] -= quantity_to_remove
        print(f"\nRemoved {quantity_to_remove} {car_info['Company']} {car_info['Model']} from inventory")
        print(f"Remaining quantity: {df.loc[car_idx, 'Quantity']}")
    
    save_inventory(df)

#Search function which functions like an inventory viewer through different prompts.
def search_inventory():
    """Search inventory by various criteria"""
    df = load_inventory()
    if df.empty:
        print("\nInventory is empty.")
        return

    #initial prints to help the user follow where to go
    print("\nSearch Inventory")
    print("1. Search by Company")
    print("2. Search by Model")
    print("3. Search by Year")
    print("4. Search by Colour")

    #if statements to check what was pressed and give a follow up messgae to continue moving through the program (ie. if 1, ask for company name)
    choice = input("\nEnter search option (0 to cancel): ").strip()
    if choice == "0":
        return
    if choice == "1":
        search_term = input("Enter company name: ").strip().lower()
        results = df[df["Company"].str.lower().str.contains(search_term)]
    elif choice == "2":
        search_term = input("Enter model name: ").strip().lower()
        results = df[df["Model"].str.lower().str.contains(search_term)]
    elif choice == "3":
        search_term = input("Enter year: ").strip()
        results = df[df["Year"].astype(str) == search_term]
    elif choice == "4":
        search_term = input("Enter colour: ").strip().lower()
        results = df[df["Colour"].str.lower().str.contains(search_term)]
    else:
        print("Invalid option.")
        return

    #if else for when the user enters an incorrect term in searching
    if results.empty:
        print("\nNo matching cars found.")
    else:
        print("\nSearch Results:")
        print(results.to_string(index=False))

def main():
    """Main program loop"""
    #main function to actually run the program. has all the options to move through the program efficiently.
    while True:
        print("\nCar Inventory Management System")
        print("=" * 40)
        print("1. * View Inventory *")
        print("2. * Add Inventory *")
        print("3. * Remove Inventory *")
        print("4. * Search Inventory *")
        print("5. * Exit *")
        print("=" * 40)
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            view_inventory()
        elif choice == "2":
            print("\nAdd Inventory")
            print("1. Add Manually")
            print("2. Add from Dealership Database")
            add_choice = input("\nEnter your choice (0 to cancel): ").strip()
            if add_choice == "1":
                add_manually()
            elif add_choice == "2":
                add_from_database()
        elif choice == "3":
            remove_inventory()
        elif choice == "4":
            search_inventory()
        elif choice == "5":
            print("\nThank you for using Car Inventory Management System. Goodbye!")
            break
        else:
            print("\nInvalid choice, please try again.")
        input("\nPress Enter to continue...")
        clear_screen()

if __name__ == "__main__":
    main()
