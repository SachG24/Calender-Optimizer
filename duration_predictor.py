import glob
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
 
from parser import parse_calendar
 
 
def load_all_todos(pattern="generated/todos/*.ical"):
    # Parse every generated calendar file and collect all Todo objects
    all_todos = []
    for filepath in sorted(glob.glob(pattern)):
        _, todos = parse_calendar(filepath)
        all_todos.extend(todos)
    return all_todos
 
 
def todos_to_dataframe(todos):
    # Convert list of Todo dataclasses into a feature-ready DataFrame.
    rows = []
    for t in todos:
        due = t.due
        rows.append({
            "priority": t.priority,
            "status": t.status,
            "due_dayofweek": due.weekday() if due else -1,
            "due_hour": due.hour if due else -1,
            "due_month": due.month if due else -1,
            "duration": t.duration,  # target
        })
    return pd.DataFrame(rows)
 
 
def build_pipeline(model):
    #Wraps a regressor with categorical encoding for 'status'.
    preprocessor = ColumnTransformer(
        transformers=[
            ("status_ohe", OneHotEncoder(handle_unknown="ignore"), ["status"]),
        ],
        remainder="passthrough",  # priority, due_dayofweek, due_hour, due_month pass through as-is
    )
    return Pipeline(steps=[
        ("preprocess", preprocessor),
        ("model", model),
    ])
 
 
def evaluate(name, model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"{name:22s}  MAE={mae:6.2f} min   RMSE={rmse:6.2f} min")
    return mae, rmse
 
 
def main():
    print("Loading todos from generated calendars...")
    todos = load_all_todos()
    print(f"Loaded {len(todos)} todo items.\n")
 
    df = todos_to_dataframe(todos)
    print("Feature preview:")
    print(df.head(), "\n")
 
    X = df.drop(columns=["duration"])
    y = df["duration"]
 
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
 
    print(f"Train size: {len(X_train)}   Test size: {len(X_test)}\n")
    print("Model performance (lower is better):")
    print("-" * 60)
 
    # Baseline: always predict the mean training duration
    dummy = build_pipeline(DummyRegressor(strategy="mean"))
    evaluate("Baseline (mean)", dummy, X_train, X_test, y_train, y_test)
 
    # Linear regression
    lin = build_pipeline(LinearRegression())
    evaluate("Linear Regression", lin, X_train, X_test, y_train, y_test)
 
    # Random forest
    rf = build_pipeline(RandomForestRegressor(n_estimators=200, random_state=42))
    evaluate("Random Forest", rf, X_train, X_test, y_train, y_test)
 
    print("-" * 60)
    print(f"\nTrue duration range in data: {y.min()}-{y.max()} min, "
          f"mean={y.mean():.1f}, std={y.std():.1f}")
 
 
if __name__ == "__main__":
    main()