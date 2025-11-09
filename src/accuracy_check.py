import pandas as pd

# --- 1. Load a single CSV file ---
file = "data\experiment_07c0d72f_20251029_200243.csv"  # change to your filename
df = pd.read_csv(file)

# compute 'is_correct' column
df["is_correct"] = (
    df["eng"].astype(str).str.strip().str.lower()
    == df["answer"].astype(str).str.strip().str.lower()
)   

# compute accuracy by condition
acc_by_cond = df.groupby("condition")["is_correct"].mean()

#print accuracy results
print("Accuracy by Condition:")
for cond, acc in acc_by_cond.items():
    print(f"Condition {cond}: {acc:.2f}")


    
