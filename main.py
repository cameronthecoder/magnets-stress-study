import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

df = pd.read_excel("study_responses.ods", engine="odf")

# ['Timestamp', 'Which task were you assigned first?', 'SUDS Baseline\n\nRate your stress/anxiety level on a scale from 0-100.\n\n0: Totally relaxed, peaceful.\n\n10-20: Minimal distress, alert.\n\n30-40: Mild anxiety, no interference with performance.\n\n50: Moderate discomfort, but can continue to perform.\n\n70: Discomfort dominates thoughts, interfering with performance.\n\n80-90: Very anxious, panicky.\n\n100: Highest distress/fear ever felt', 'Rate your stress level on a scale of 1 to 10 (Baseline)', 'SUDS Post Task 1 (1)\n\nRate your stress/anxiety level on a scale from 0-100.\n\n0: Totally relaxed, peaceful.\n\n10-20: Minimal distress, alert.\n\n30-40: Mild anxiety, no interference with performance.\n\n50: Moderate discomfort, but can continue to perform.\n\n70: Discomfort dominates thoughts, interfering with performance.\n\n80-90: Very anxious, panicky.\n\n100: Highest distress/fear ever felt', 'Rate your stress level on a scale of 1 to 10 (1)', 'SUDS  2\n\nRate your stress/anxiety level on a scale from 0-100.\n\n0: Totally relaxed, peaceful.\n\n10-20: Minimal distress, alert.\n\n30-40: Mild anxiety, no interference with performance.\n\n50: Moderate discomfort, but can continue to perform.\n\n70: Discomfort dominates thoughts, interfering with performance.\n\n80-90: Very anxious, panicky.\n\n100: Highest distress/fear ever felt', 'Rate your stress level on a scale of 1 to 10 (2)', 'Which condition felt more calming?', 'Why did that condition feel more calming?']

def to_number(x):
    x = str(x).strip().replace("–", "-")   # handles both dash types
    if "-" in x:
        low, high = x.split("-")
        return (float(low) + float(high)) / 2
    return float(x)


df = df.rename(columns={
    'Timestamp': 'timestamp',
    'Which task were you assigned first?': 'task_assigned_first',
    'SUDS Baseline\n\nRate your stress/anxiety level on a scale from 0-100.\n\n0: Totally relaxed, peaceful.\n\n10-20: Minimal distress, alert.\n\n30-40: Mild anxiety, no interference with performance.\n\n50: Moderate discomfort, but can continue to perform.\n\n70: Discomfort dominates thoughts, interfering with performance.\n\n80-90: Very anxious, panicky.\n\n100: Highest distress/fear ever felt': 'suds_baseline',
    'Rate your stress level on a scale of 1 to 10 (Baseline)': 'stress_level_baseline',
    'SUDS Post Task 1 (1)\n\nRate your stress/anxiety level on a scale from 0-100.\n\n0: Totally relaxed, peaceful.\n\n10-20: Minimal distress, alert.\n\n30-40: Mild anxiety, no interference with performance.\n\n50: Moderate discomfort, but can continue to perform.\n\n70: Discomfort dominates thoughts, interfering with performance.\n\n80-90: Very anxious, panicky.\n\n100: Highest distress/fear ever felt': 'suds_post_task_1',
    'Rate your stress level on a scale of 1 to 10 (1)': 'stress_level_post_task_1',
    'SUDS  2\n\nRate your stress/anxiety level on a scale from 0-100.\n\n0: Totally relaxed, peaceful.\n\n10-20: Minimal distress, alert.\n\n30-40: Mild anxiety, no interference with performance.\n\n50: Moderate discomfort, but can continue to perform.\n\n70: Discomfort dominates thoughts, interfering with performance.\n\n80-90: Very anxious, panicky.\n\n100: Highest distress/fear ever felt': 'suds_post_task_2',
    'Rate your stress level on a scale of 1 to 10 (2)': 'stress_level_post_task_2',
    'Which condition felt more calming?': 'condition_more_calming',
    'Why did that condition feel more calming?': 'reason_condition_more_calming'
})

print(df["task_assigned_first"].unique())

score_cols = ["suds_baseline", "stress_level_baseline", "suds_post_task_1", "stress_level_post_task_1", "suds_post_task_2", "stress_level_post_task_2"]

for col in score_cols:
    df[col] = df[col].apply(to_number)

magnets_first = df["task_assigned_first"] == "Magnets"

df["suds_magnets"] = df["suds_post_task_1"].where(magnets_first, df["suds_post_task_2"])
df["suds_rest"] = df["suds_post_task_2"].where(magnets_first, df["suds_post_task_1"])

df["stress_magnets"] = df["stress_level_post_task_1"].where(magnets_first, df["stress_level_post_task_2"])
df["stress_rest"] = df["stress_level_post_task_2"].where(magnets_first, df["stress_level_post_task_1"])

print(magnets_first.sum())

# Averages

suds_cols = ["suds_baseline", "suds_rest", "suds_magnets"]
stress_cols = ["stress_level_baseline", "stress_rest", "stress_magnets"]

for cols in [suds_cols, stress_cols]:
    print(df[cols].count())
    print(df[cols].mean().round(2))
    print(df[cols].median())
    print(df[cols].std().round(2))
    print("------")

# T-tests

# did rest lower stress?
print("Rest vs. baseline")
print(stats.ttest_rel(df["suds_rest"], df["suds_baseline"]))

# did magnets lower stress?
print("Magnets vs. baseline")
print(stats.ttest_rel(df["suds_magnets"], df["suds_baseline"]))

# did magnets beat rest?
print("Magnets vs. rest")
print(stats.ttest_rel(df["suds_magnets"], df["suds_rest"]))

diff = df["suds_magnets"] - df["suds_rest"]
d = diff.mean() / diff.std()
print(round(d, 2))

# who preferred what
print("Who preferred what")
print(df["condition_more_calming"].value_counts())

# did prefernces match the scores?
print("Prefences matching scores")
df["suds_diff"] = df["suds_magnets"] - df["suds_rest"]
print(df.groupby("condition_more_calming")["suds_diff"].mean().round(2))

# order check
# did the second task lower regarddless of what it was
print("Did the second task lower regarddless of what the first task was?")
print(df[["suds_post_task_1", "suds_post_task_2"]].mean().round(2))

# did order change the manget advantage
print("Did order change the magnet advantage?")
print(df.groupby("task_assigned_first")["suds_diff"].mean().round(2))

print("Preference binomial test")
print(stats.binomtest(13, 18))

print("1-10: rest vs baseline")
print(stats.ttest_rel(df["stress_rest"], df["stress_level_baseline"]))


print("1-10: magnets vs. baseline")
print(stats.ttest_rel(df["stress_magnets"], df["stress_level_baseline"]))

print("1-10: magnets vs. rest")
print(stats.ttest_rel(df["stress_magnets"], df["stress_rest"]))

stress_diff = df["stress_magnets"] - df["stress_rest"]
print("1-10 d:", round(stress_diff.mean() / stress_diff.std(), 2))

# figure 1
conditions = ["Baseline", "Rest", "Magnets"]
cols = ["suds_baseline", "suds_rest", "suds_magnets"]

fig, ax = plt.subplots(figsize=(6, 4))
for _, row in df.iterrows():
    ax.plot(conditions, row[cols], color="lightgray", marker="o", linewidth=1)

ax.plot(conditions, df[cols].mean(), color="black", marker="o", linewidth=3, label="Mean")

ax.set_ylabel("SUDS rating (0–100)")
ax.set_ylim(0, 100)
ax.legend()

plt.tight_layout()
plt.savefig("figure1.pdf")


# figure 2
order_means = df.groupby("task_assigned_first")["suds_diff"].mean()
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(["Magnets first\n(n = 10)", "Rest first\n(n = 8)"],
       [order_means["Magnets"], order_means["Rest"]],
       color=["gray", "black"], width=0.5)

ax.axhline(0, color="black", linewidth=0.8)   # the zero line
ax.set_ylabel("SUDS difference (magnets - rest)")

plt.tight_layout()
plt.savefig("figure2.pdf")
plt.show()


# tehemes for which condition was more calming

for pref in ["Magnets", "Rest"]:
    print(f"--- Preferred {pref} ---")
    for reason in df[df["condition_more_calming"] == pref]["reason_condition_more_calming"]:
        print("-", reason)