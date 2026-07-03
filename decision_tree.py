from datetime import date, datetime, time
from pathlib import Path
import sys
from typing import List
from sklearn.tree import DecisionTreeClassifier, export_text
from parser import Todo, parse_calendar


FEATURE_NAMES = [
    "priority",
    "hours_until_due",
    "duration_minutes",
    "slack_hours",
]

LABEL_NAMES = {
    0: "Schedule later",
    1: "Schedule soon",
    2: "Schedule first",
}


def normalize_priority(priority: int) -> int:
    """
    iCalendar priorities use:
    1 = highest priority
    9 = lowest priority
    0 = undefined
    """
    if priority == 0:
        return 5

    return max(1, min(priority, 9))


def convert_due_to_datetime(due: date | datetime) -> datetime:
    """Convert a date-only deadline into a deadline at the end of that day."""
    if isinstance(due, datetime):
        return due

    return datetime.combine(due, time(hour=23, minute=59))


def hours_until_due(todo: Todo, now: datetime) -> float:
    """Return the number of hours remaining before a task is due."""
    if todo.due is None:
        return 10_000.0

    due = convert_due_to_datetime(todo.due)
    comparable_now = now

    # Prevent errors when one datetime has a timezone and the other does not.
    if due.tzinfo is not None and comparable_now.tzinfo is None:
        comparable_now = comparable_now.replace(tzinfo=due.tzinfo)
    elif due.tzinfo is None and comparable_now.tzinfo is not None:
        comparable_now = comparable_now.replace(tzinfo=None)

    hours_left = (due - comparable_now).total_seconds() / 3600
    return max(0.0, hours_left)


def extract_features(todo: Todo, now: datetime) -> List[float]:
    """Convert a Todo object into the four inputs used by the tree."""
    hours_left = hours_until_due(todo, now)
    duration_minutes = max(0, todo.duration)
    duration_hours = duration_minutes / 60
    slack_hours = hours_left - duration_hours

    return [
        float(normalize_priority(todo.priority)),
        hours_left,
        float(duration_minutes),
        slack_hours,
    ]


def build_training_data() -> tuple[List[List[float]], List[int]]:
    """Create synthetic examples for the Milestone 1 decision tree."""
    training_features: List[List[float]] = []
    training_labels: List[int] = []

    for priority in range(1, 10):
        for hours_left in [6, 12, 24, 48, 72, 120, 168, 336]:
            for duration_minutes in [30, 60, 120, 240]:
                duration_hours = duration_minutes / 60
                slack_hours = hours_left - duration_hours

                # Class 2: schedule first
                if (
                    hours_left <= 12
                    or slack_hours <= 1
                    or (priority <= 2 and hours_left <= 48)
                ):
                    label = 2

                # Class 1: schedule soon
                elif (
                    hours_left <= 72
                    or priority <= 3
                    or slack_hours <= 6
                ):
                    label = 1

                # Class 0: schedule later
                else:
                    label = 0

                training_features.append(
                    [
                        float(priority),
                        float(hours_left),
                        float(duration_minutes),
                        float(slack_hours),
                    ]
                )

                training_labels.append(label)

    return training_features, training_labels


def train_tree() -> DecisionTreeClassifier:
    """Train and return the decision-tree classifier."""
    features, labels = build_training_data()

    model = DecisionTreeClassifier(
        max_depth=4,
        random_state=42,
    )

    model.fit(features, labels)

    return model


def classify_todo(
    model: DecisionTreeClassifier,
    todo: Todo,
    now: datetime,
) -> int:
    """Classify one task as first, soon, or later."""
    task_features = extract_features(todo, now)
    prediction = model.predict([task_features])[0]

    return int(prediction)


def main() -> None:
    """Classify the real Todo objects produced by parser.py."""
    now = datetime.now()
    model = train_tree()

    # You can optionally provide another calendar path in the terminal.
    # Example: python3 decision_tree.py generated/example1.ical
    calendar_file = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path("generated/example0.ical")
    )

    if not calendar_file.exists():
        print(f"Calendar file not found: {calendar_file}")
        print("Run these commands first:")
        print("  mkdir -p generated")
        print("  python3 ical_generator.py")
        return

    _, todos = parse_calendar(str(calendar_file))

    # Ignore completed or cancelled tasks.
    active_todos = [
        todo
        for todo in todos
        if todo.status.upper() not in {"COMPLETED", "CANCELLED"}
    ]

    print("LEARNED DECISION TREE:\n")

    print(
        export_text(
            model,
            feature_names=FEATURE_NAMES,
        )
    )

    if not active_todos:
        print(f"No active tasks were found in {calendar_file}.")
        return

    ranked_todos = []

    for todo in active_todos:
        prediction = classify_todo(model, todo, now)
        ranked_todos.append((prediction, todo))

    # Schedule-first tasks appear first.
    # Within each class, higher priority and earlier deadlines appear first.
    ranked_todos.sort(
        key=lambda item: (
            -item[0],
            normalize_priority(item[1].priority),
            hours_until_due(item[1], now),
        )
    )

    print(f"\nTASK PREDICTIONS FROM {calendar_file}:\n")

    for prediction, todo in ranked_todos:
        if todo.due is None:
            due_text = "No deadline"
        else:
            due_datetime = convert_due_to_datetime(todo.due)
            due_text = due_datetime.strftime("%Y-%m-%d %H:%M")

        print(
            f"{LABEL_NAMES[prediction]}: {todo.summary} | "
            f"due {due_text} | priority {todo.priority} | "
            f"duration {todo.duration} minutes"
        )


if __name__ == "__main__":
    main()