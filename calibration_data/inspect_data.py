import pandas as pd
import os
os.getcwd()
os.chdir("C:\\Users\\haw27\\Documents\\Haven_Code_Projects\\predictioneers_game\\predictioneers_game_alpha_00\\calibration_data")

data = pd.read_csv('calibration_data.csv')

# Check the first few rows
print(data.head())

import statsmodels.api as sm

# Define the predictor (independent variable) and the response (dependent variable)
X = data['forecasted_result']  # Predictor
y = data['actual_result']      # Response

# Add a constant to the predictor for the intercept in the regression model
X = sm.add_constant(X)

# Fit the Ordinary Least Squares (OLS) regression model
model = sm.OLS(y, X).fit()

# Display the regression results summary
print(model.summary())
