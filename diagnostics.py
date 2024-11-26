import pandas as pd
import statsmodels.api as sm

# Load the dataset
file_path = './calibration_data/calibration_data.csv'  # Adjust to your actual file path
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: File not found at {file_path}. Please check the file path.")
    exit()

def list_version_numbers():
    """Lists all unique version numbers in the dataset."""
    print("\nAvailable version numbers:")
    unique_versions = data['version_number'].unique()
    print(unique_versions)
    return unique_versions

def analyze_version(version_number):
    """Filters data by version_number and performs regression analysis."""
    # Ensure version_number matches data type in the dataset
    filtered_data = data[data['version_number'] == version_number]

    if filtered_data.empty:
        print(f"\nNo data found for version number '{version_number}'.")
        return

    # Regression: forecasted_result as predictor, actual_result as dependent variable
    try:
        X = filtered_data['forecasted_result']
        y = filtered_data['actual_result']
    except KeyError as e:
        print(f"Error: Missing required column in dataset: {e}")
        return

    # Add a constant for the intercept
    X = sm.add_constant(X)

    # Fit the OLS regression model
    model = sm.OLS(y, X).fit()

    # Display the regression summary
    print("\nRegression Analysis Table:")
    print(model.summary())

def main():
    """Main program for user interaction."""
    while True:
        print("\nDo you want to:")
        print("1. Analyze a specific version number")
        print("2. List all version numbers")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice == '1':
            version_number = input("Enter the version number to analyze: ").strip()
            try:
                # Attempt to convert the input to match the version_number column type
                if data['version_number'].dtype in ['float64', 'int64']:
                    version_number = float(version_number)
                analyze_version(version_number)
            except ValueError:
                print("Invalid version number format. Please try again.")
        elif choice == '2':
            list_version_numbers()
        elif choice == '3':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
