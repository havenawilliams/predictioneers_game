import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

def plot_calibration_data(version_number):
    """
    Generates a Q-Plot for the specified version number.
    """
    # File and folder setup
    folder = "calibration_data"
    file_path = os.path.join(folder, "calibration_data.csv")

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist. Ensure the 'calibration_data.csv' is in the '{folder}' folder.")
        return

    # Load the CSV file
    data = pd.read_csv(file_path)

    # Check if required columns exist
    required_columns = ["data_set_name", "forecasted_result", "actual_result", "version_number"]
    if not all(col in data.columns for col in required_columns):
        print(f"The CSV file must contain the columns: {', '.join(required_columns)}")
        return

    # Filter data by version number (as a string)
    filtered_data = data[data["version_number"].astype(str) == str(version_number)]
    if filtered_data.empty:
        print(f"No data found for version number '{version_number}'.")
        return

    # Extract data for plotting
    forecasted = filtered_data["forecasted_result"]
    actual = filtered_data["actual_result"]
    labels = filtered_data["data_set_name"]

    # Create the Q-plot
    plt.figure(figsize=(8, 8))
    plt.scatter(forecasted, actual, alpha=0.7, label="Data Points")
    plt.plot([0, 1], [0, 1], color="red", linestyle="--", label="Perfect Calibration")

    # Add labels to points
    for i, label in enumerate(labels):
        plt.text(
            forecasted.iloc[i], actual.iloc[i], label,
            fontsize=8, rotation=4,
            ha='left', va='bottom'
        )

    # Add title, labels, and legend
    plt.title(f"Q-Plot: Forecasted vs Actual Results (Version {version_number})", fontsize=14)
    plt.xlabel("Forecasted Result", fontsize=12)
    plt.ylabel("Actual Result", fontsize=12)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(fontsize=10)

    # Save and show the plot
    plot_path = os.path.join(folder, f"q_plot_v{version_number}.png")
    plt.savefig(plot_path, bbox_inches="tight")
    plt.show()
    print(f"Q-Plot saved to {plot_path}")

if __name__ == "__main__":
    # Check for a version number in command-line arguments
    if len(sys.argv) > 1:
        version = sys.argv[1]  # Accept the version as a string
    else:
        # Prompt the user for a version number
        while True:
            user_input = input("Enter the version number to filter by (or type 'exit' to quit): ").strip().lower()
            if user_input == "exit":
                print("Exiting without generating a plot.")
                sys.exit(0)
            # Treat input as a string directly
            version = user_input
            break

    # Generate the plot for the specified version number
    plot_calibration_data(version)
