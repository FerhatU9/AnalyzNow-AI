
import json
from collections import defaultdict
from pathlib import Path

# Read the historical evaluation results.
path = Path("outputs/epl_2024_25_evaluation.json")
report = json.loads(path.read_text(encoding="utf-8"))

matches = report["individual_forecasts"]

outcomes = {
    "H": "home_win",
    "D": "draw",
    "A": "away_win",
}

groups = defaultdict(list)
correct_predictions = 0

for match in matches:
    probabilities = match["forecast"]

    # Find the outcome with the highest probability.
    prediction = max(probabilities, key=probabilities.get)
    confidence = probabilities[prediction]

    # Compare the prediction with the actual result.
    actual = outcomes[match["actual"]]
    correct = int(prediction == actual)

    correct_predictions += correct

    # Group forecasts into confidence ranges.
    band = min(int(confidence * 10) * 10, 90)
    groups[band].append((confidence, correct))

print("\nANALYZNOW AI — MODEL CALIBRATION")
print("--------------------------------")

total = len(matches)
print(f"Evaluated matches: {total}")
print(f"Correct outcome predictions: {correct_predictions}")
print(f"Outcome accuracy: {correct_predictions / total:.1%}")

print("\nConfidence calibration:")
print("Range    Matches   Average confidence   Actual accuracy")

for band in sorted(groups):
    values = groups[band]
    count = len(values)

    average_confidence = sum(p for p, _ in values) / count
    accuracy = sum(correct for _, correct in values) / count

    print(
        f"{band:02d}-{band+9:02d}%"
        f"   {count:5d}"
        f"       {average_confidence:6.1%}"
        f"               {accuracy:6.1%}"
    )

    if count < 20:
        print("         Caution: small sample.")