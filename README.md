
# Predictioneer's Game Simulation

Welcome to the **Predictioneer's Game Simulation**, a recreation of the strategic prediction framework described in Bruce Bueno de Mesquita's *The Predictioneer's Game*. This project uses game theory, Bayesian updating, and data-driven modeling to simulate negotiations and predict outcomes in multi-agent interactions.

## Features

- **Dynamic Game Tree Simulation**: Build and simulate extensive-form games using the `pygambit` library.
- **Bayesian Belief Updating**: Track and adjust players' beliefs about each other over time.
- **Strategic Position Updates**: Model shifts in player positions based on credible proposals and utility optimization.
- **Jittered Simulations**: Add stochastic variation to player attributes for robustness testing.
- **Data Visualization**: Generate plots showing changes in positions and utilities over simulation rounds.
- **Customizable Scenarios**: Import player data from CSV files or create new datasets interactively.

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python libraries:
  - `pygambit`
  - `numpy`
  - `pandas`
  - `matplotlib`

Install dependencies with:
```bash
pip install -r requirements.txt
```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/havenawilliams/predictioneers_game.git
   cd predictioneers-game
   ```

2. Set up the project directory structure:
   ```bash
   mkdir data output
   ```

3. Add your CSV datasets to the `data` directory.

### Running the Simulation

Use the main script to run simulations:
```bash
python main.py --auto --jitter data/example_dataset.csv
```

#### Arguments

- `--auto`: Automates all inputs for batch processing.
- `--jitter`: Adds stochastic variation to player salience during simulations.
- `<csv_file>`: Path to the input dataset in CSV format.

### Outputs

Simulation results are saved in the `output` directory, including:
- CSV files detailing final player positions and belief matrices.
- Plots visualizing the evolution of player positions and status quo.

## How It Works

### Key Modules

- **`main.py`**: The entry point for running simulations. Handles file I/O, dataset management, and simulation orchestration.

More documentation on other modules to follow.

### Theoretical Basis

This project models negotiation as a game of imperfect information, where players:
1. Propose actions based on their utility functions (e.g., Cobb-Douglas).
2. Adjust beliefs about opponents based on observed outcomes.
3. Update positions iteratively until equilibrium is achieved.

## Contributing

Contributions are welcome! Please:
1. Fork this repository.
2. Create a feature branch.
3. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## References

- Bruce Bueno de Mesquita, *The Predictioneer's Game: Using the Logic of Brazen Self-Interest to See and Shape the Future*, Random House Trade Paperbacks, 2010.

## Contact

For questions or suggestions, open an issue or contact [havenawilliams](https://github.com/havenawilliams).
