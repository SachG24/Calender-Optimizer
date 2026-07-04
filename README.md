# Calendar Optimizer — CMPT 310

This project is an AI-based schedule optimizer that reads calendar events and tasks from iCalendar files and helps determine which tasks should be completed first.

## Current Features

- Generates sample `.ical` calendar files
- Parses fixed events and tasks
- Reads task deadlines, priorities, durations, and statuses
- Uses a scikit-learn decision tree to classify tasks as:
  - Schedule first
  - Schedule soon
  - Schedule later
- Sorts active tasks based on urgency and priority

## Decision Tree

The decision tree uses four features:

- Task priority
- Hours remaining until the deadline
- Estimated task duration
- Slack time before the deadline

The tree determines the order in which tasks should be considered by the scheduling system. It does not currently choose exact time slots or resolve calendar conflicts.

## Requirements

- Python 3
- `icalendar`
- `scikit-learn`

Install the required packages with:

python3 -m pip install -r requirements.txt

## Running the Project

First, create the folder for generated calendar files:

mkdir -p generated

Generate the sample calendar files:

python3 ical_generator.py

Run the decision tree:

python3 decision_tree.py