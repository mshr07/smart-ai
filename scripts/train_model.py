"""Python AI script: train, evaluate on held-out examples, save model."""

from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from scripts.check_dataset import read_dataset

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "ticket_model.joblib"


def build_pipeline():
    return Pipeline(
        [
            ("text_features", TfidfVectorizer(ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )


def main():
    rows, _ = read_dataset()
    texts = [row["text"] for row in rows]
    labels = [row["category"] for row in rows]

    train_x, test_x, train_y, test_y = train_test_split(
        texts, labels, test_size=0.25, stratify=labels, random_state=42
    )

    candidate = build_pipeline()
    candidate.fit(train_x, train_y)
    predictions = candidate.predict(test_x)
    print(f"Held-out accuracy: {accuracy_score(test_y, predictions):.3f}")
    print(classification_report(test_y, predictions, zero_division=0))
    print("Educational demo: tiny synthetic data is NOT a production quality check.")

    final_model = build_pipeline()
    final_model.fit(texts, labels)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)
    print(f"Saved trained model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
