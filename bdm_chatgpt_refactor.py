from dataclasses import dataclass
from typing import List, Optional
import csv


@dataclass
class Actor:
    """Represents a political actor."""
    name: str
    position: float  # Policy position
    capabilities: float  # Capability score (0 to 1)
    salience: float  # Importance of issue (0 to 1)
    risk_aversion: float = 1.0  # Risk aversion (0.5 to 2.0)

    def utility(self, target_position: float, position_range: float) -> float:
        """Calculates utility of a given position based on distance and salience."""
        # Ensure position_range is non-zero
        position_range = position_range if position_range > 0 else 1e-6
        distance = abs(self.position - target_position) / position_range

        # Handle the case where distance is 0 explicitly
        if distance == 0:
            return self.capabilities * self.salience

        return self.capabilities * self.salience * (1 - distance ** self.risk_aversion)


@dataclass
class Offer:
    """Represents an offer between two actors."""
    actor: Actor
    target: Actor
    position: float
    offer_type: str


def calculate_position_range(actors: List[Actor]) -> float:
    """Calculates the range of positions in the model."""
    positions = [actor.position for actor in actors]
    range_value = max(positions) - min(positions)
    return range_value if range_value > 0 else 1e-6  # Use a small non-zero value


def calculate_probabilities(
    x_i: float, x_j: float, actors: List[Actor], position_range: float
) -> float:
    """Calculates the probability of one actor succeeding against another."""
    if x_i == x_j:
        return 0.0

    total_comparisons = sum(
        actor.utility(x_i, position_range) - actor.utility(x_j, position_range)
        for actor in actors
    )
    return max(0, total_comparisons)


def calculate_danger_level(actor: Actor, actors: List[Actor], position_range: float) -> float:
    """Calculates the danger level for an actor's position."""
    return sum(
        calculate_probabilities(actor.position, other.position, actors, position_range)
        for other in actors if other != actor
    )


def update_risk_aversions(actors: List[Actor], position_range: float):
    """Update risk aversions for all actors based on current positions."""
    for actor in actors:
        danger_levels = [
            calculate_danger_level(other, actors, position_range)
            for other in actors if other != actor
        ]
        max_danger = max(danger_levels, default=1)
        min_danger = min(danger_levels, default=0)
        current_danger = calculate_danger_level(actor, actors, position_range)
        actor.risk_aversion = (1 - (current_danger - min_danger) / (max_danger - min_danger)) / (
            1 + (current_danger - min_danger) / (max_danger - min_danger)
        )


def get_best_offer(actor: Actor, actors: List[Actor], position_range: float) -> Optional[Offer]:
    """Find the best offer for an actor based on expected utility."""
    offers = []
    for other_actor in actors:
        if actor == other_actor:
            continue
        # Generate potential offers
        position = (actor.position + other_actor.position) / 2
        offer_type = "compromise"  # Simplified for now
        offers.append(Offer(actor, other_actor, position, offer_type))
    return min(offers, key=lambda o: abs(o.position - actor.position), default=None)


def update_positions(actors: List[Actor], position_range: float):
    """Update actors' positions based on best offers."""
    for actor in actors:
        best_offer = get_best_offer(actor, actors, position_range)
        if best_offer:
            print(f"{actor.name} accepts {best_offer.offer_type} at {best_offer.position}")
            actor.position = best_offer.position


def calculate_mean_position(actors: List[Actor]) -> float:
    """Calculate the mean position of actors, weighted by capabilities and salience."""
    total_weight = sum(actor.capabilities * actor.salience for actor in actors)
    weighted_sum_positions = sum(
        actor.capabilities * actor.salience * actor.position for actor in actors
    )
    return weighted_sum_positions / total_weight if total_weight > 0 else 0


def run_model(actors: List[Actor], num_rounds: int):
    """Run the simulation for a specified number of rounds."""
    position_range = calculate_position_range(actors)

    for round_num in range(1, num_rounds + 1):
        print(f"--- Round {round_num} ---")

        # Update risk aversions
        update_risk_aversions(actors, position_range)

        # Update positions based on best offers
        update_positions(actors, position_range)

        # Print positions after each round
        print("\nCurrent positions:")
        for actor in actors:
            print(f"{actor.name}: {actor.position}")

        # Calculate and print the mean position
        mean_pos = calculate_mean_position(actors)
        print(f"Mean position: {mean_pos:.2f}")


def load_actors_from_csv(file_path: str) -> List[Actor]:
    """Load actors from a CSV file."""
    actors = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            actors.append(
                Actor(
                    name=row['Actor'],
                    position=float(row['Position']),
                    capabilities=float(row['Capability']),
                    salience=float(row['Salience']),
                )
            )
    return actors


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the BDM Expected Utility Model.")
    parser.add_argument("csv_path", help="Path to the CSV file containing actor data.")
    parser.add_argument("num_rounds", type=int, help="Number of rounds to simulate.")
    args = parser.parse_args()

    # Load actors from the CSV file
    actors = load_actors_from_csv(args.csv_path)

    # Run the model
    run_model(actors, args.num_rounds)
