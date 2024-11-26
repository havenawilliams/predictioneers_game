import os
import pandas as pd

def generate_sheet():

    # Define player names and column names for the dataset
    players = ["player_a", "player_b", "player_c", "player_d"]
    columns = ["name", "position", "capabilities", "salience", "resolve"]

    # Initialize the dataset with zeros for the relevant columns
    data = {
        "name": players,
        "position": [0] * len(players),
        "capabilities": [0] * len(players),
        "salience": [0] * len(players),
        "resolve": [0] * len(players),
    }

    # Ask for a name for the dataset
    sheet_name = input("Write a name for the dataset: ")

    # Create the DataFrame
    bruce_sheet = pd.DataFrame(data)

    # Ensure the directory exists
    save_dir = "./data"  # Relative path for the "data" folder
    os.makedirs(save_dir, exist_ok=True)

    # Save the dataset to the "data" directory
    csv_path = os.path.join(save_dir, f"{sheet_name}.csv")
    bruce_sheet.to_csv(csv_path, index=False)

    print(f"Fill out the sheet called {sheet_name}.csv saved in the data folder with the relevant information. Good luck.")
