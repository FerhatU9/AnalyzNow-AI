
import json
from pathlib import Path

# Load the historical predictions.
path = Path("outputs/epl_2024_25_evaluation.json")
report = json.loads(path.read_text(encoding="utf-8"))

matches = report["individual_forecasts"]

outcomes = {
    "home_win": "H",
    "draw": "D",
    "away_win": "A",
}

print("\nANALYZNOW AI — OUTCOME EVALUATION")
print("--------------------------------")
print(f"Matches evaluated: {len(matches)}")

for outcome, code in outcomes.items():
    total_probability = 0
    actual_count = 0

    # Examine this outcome across every match.
    for match in matches:
        probability = match["forecast"][outcome]
        total_probability += probability

        if match["actual"] == code:
            actual_count += 1

    average_prediction = total_probability / len(matches)
    actual_frequency = actual_count / len(matches)

    difference = actual_frequency - average_prediction

    print(f"\nOutcome: {outcome}")
    print(f"Average predicted: {average_prediction:.1%}")
    print(f"Actual frequency:  {actual_frequency:.1%}")
    print(f"Difference:        {difference:+.1%}")
    print(f"Actual matches:    {actual_count}")


print("\nDETAILED PROBABILITY CALIBRATION")
print("--------------------------------")

for outcome, code in outcomes.items():
    print(f"\n{outcome.upper()}")
    print("Range    Matches   Predicted   Actual")

    # Create ten probability groups.
    groups = {i: [] for i in range(10)}

    for match in matches:
        probability = match["forecast"][outcome]
        actual = int(match["actual"] == code)

        group = min(int(probability * 10), 9)
        groups[group].append((probability, actual))

    for group, values in groups.items():
        if not values:
            continue

        count = len(values)

        predicted = sum(p for p, a in values) / count
        actual_rate = sum(a for p, a in values) / count

        lower = group * 10
        upper = lower + 9

        print(
            f"{lower:02d}-{upper:02d}%"
            f"   {count:5d}"
            f"      {predicted:6.1%}"
            f"     {actual_rate:6.1%}"
        )

        if count < 20:
            print("         Small sample — interpret cautiously")
