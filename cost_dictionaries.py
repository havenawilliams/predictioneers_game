# cost_dictionaries.py

# Default cost values (current script values)
default_costs = {
    'alpha_hawk': 0.01,  # Lower cost for hawks
    'alpha_not_hawk': 0.02,  # Higher cost for non-hawks
    'gamma_retaliatory': 0.02,  # Higher cost when opponent is retaliatory
    'gamma_not_retaliatory': 0.01,  # Lower cost when opponent is not retaliatory
    'tau_retaliatory': 0.02,  # Higher cost when opponent is retaliatory
    'tau_not_retaliatory': 0.01,  # Lower cost when opponent is not retaliatory
    'phi_hawk': 0.01,  # Lower cost for hawks
    'phi_not_hawk': 0.02,  # Higher cost for non-hawks
}

# Alternative 1: Higher costs across the board
high_costs = {
    'alpha_hawk': 0.015,
    'alpha_not_hawk': 0.03,
    'gamma_retaliatory': 0.03,
    'gamma_not_retaliatory': 0.015,
    'tau_retaliatory': 0.03,
    'tau_not_retaliatory': 0.015,
    'phi_hawk': 0.015,
    'phi_not_hawk': 0.03,
}

# Alternative 2: Lower costs across the board
low_costs = {
    'alpha_hawk': 0.005,
    'alpha_not_hawk': 0.01,
    'gamma_retaliatory': 0.01,
    'gamma_not_retaliatory': 0.005,
    'tau_retaliatory': 0.01,
    'tau_not_retaliatory': 0.005,
    'phi_hawk': 0.005,
    'phi_not_hawk': 0.01,
}

# Alternative 2: Lower costs across the board
lowest_costs = {
    'alpha_hawk': 0.0005,
    'alpha_not_hawk': 0.001,
    'gamma_retaliatory': 0.001,
    'gamma_not_retaliatory': 0.0005,
    'tau_retaliatory': 0.001,
    'tau_not_retaliatory': 0.0005,
    'phi_hawk': 0.0005,
    'phi_not_hawk': 0.001,
}

# Add more variations here as needed...

cost_dictionary = lowest_costs
