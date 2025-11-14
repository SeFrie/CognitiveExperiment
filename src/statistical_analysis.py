import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from io import StringIO

# --- 1. Load all CSV files ---
csv_files = glob.glob(os.path.join("data", "*.csv"))
df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

# -- mapping order of conditions
# --- 1. Define mapping between experiment ID and order (PN/NP) ---
mapping_data = """
Condition,ExperimentID
PN,8dc44e9e
PN,07c0d72f
NP,8eeeea92
NP,876f1414
NP,c4965dd4
PN,59ff9f63
PN,84a19300
NP,0b4961e6
PN,9a0372dc
NP,ddd75cbe
PN,dfc79e19
NP,829376dd
PN,57acf7c0
PN,55c8ef4e
NP,4c530066
NP,3fe7c21f
PN,47e8e079
PN,8f19053c
NP,4694ef8b
NP,112da591
PN,ae9e001e
PN,ea3152e9
NP,75b3bb64
NP,d2f7f91e
NP,15c05f54
PN,81a463c0
NP,aa6f473f
PN,1c4deccf
NP,e628612d
PN,6521b425
PN,c7fdcf89
PN,2eac1f8f
NP,38471d30
NP,d6d3b091
NP,ced624c2
"""

mapping_df = pd.read_csv(StringIO(mapping_data))



# --- 3. Compute accuracy per row ---
df['correct'] = (df['answer'].str.strip().str.lower() == df['eng'].str.strip().str.lower()).astype(int)

# --- 4. Merge mapping onto main data using `id` <-> `ExperimentID` ---
df = df.merge(mapping_df, left_on='id', right_on='ExperimentID', how='left')


# Compute grouped stats
summary = (
    df.groupby(['id', 'Condition', 'condition'])
      .agg(
          correct_count=('correct', 'sum'),
          total=('correct', 'count'),
          accuracy=('correct', 'mean')
      )
      .reset_index()
)

# --- 6. Pivot to get separate columns for N and P ---
results = summary.pivot_table(
    index=['id', 'Condition'],
    columns='condition',
    values=['correct_count', 'accuracy'],
    fill_value=0
)







# Flatten MultiIndex columns
results.columns = [f"{metric}_{cond}" for metric, cond in results.columns]
results = results.reset_index()

# --- 6b. Add youtube_usage column ---
youtube_usage = df[['id', 'youtube_usage']].drop_duplicates(subset='id')
results = results.merge(youtube_usage, on='id', how='left')

# --- 7. View results ---
print(results.head())






###### PLOTS ######


#plot histogram with interpolation for accuracy distributions
#in two panels for each condition
#with seaborn
import seaborn as sns   


fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
sns.histplot(results['accuracy_N'], bins=10, kde=True, ax=axs[0], color='tab:blue')
axs[0].set_title('Accuracy Distribution: Non-personalized (N)') 
axs[0].set_xlabel('Accuracy')
axs[0].set_ylabel('Frequency')
sns.histplot(results['accuracy_P'], bins=10, kde=True, ax=axs[1], color='tab:orange')
axs[1].set_title('Accuracy Distribution: Personalized (P)')
axs[1].set_xlabel('Accuracy')
plt.tight_layout()
plt.show()


# bar plot for accuracy by condition for each experiment

fig, ax = plt.subplots(figsize=(10, 6))
width = 0.35  # width of the bars
x = np.arange(len(results))
bars_N = ax.bar(x - width/2, results['accuracy_N'], width, label='Non-personalized')
bars_P = ax.bar(x + width/2, results['accuracy_P'], width, label='Personalized')

ax.bar_label(bars_N, labels=[f"{v*100:.1f}%" for v in results['accuracy_N']], padding=3, fontsize=7)
ax.bar_label(bars_P, labels=[f"{v*100:.1f}%" for v in results['accuracy_P']], padding=3, fontsize=7)
#add average lines
avg_N = results['accuracy_N'].mean()
avg_P = results['accuracy_P'].mean()
ax.axhline(avg_N, color='blue', linestyle='--', linewidth=1, label=f'Mean Non-personalized {avg_N*100:.1f}%')
ax.axhline(avg_P, color='orange', linestyle='--', linewidth=1, label=f'Mean Personalized {avg_P*100:.1f}%')

ax.set_xlabel('Experiment ID')
ax.set_ylabel('Accuracy')
ax.set_title('Accuracy by Condition')
ax.set_xticks(x)
ax.set_xticklabels(results['id'], rotation=45, ha='right')
ax.legend()

plt.tight_layout()
plt.show()


# box plot for accuracy distribution by condition
data = [results['accuracy_N'], results['accuracy_P']]

plt.figure(figsize=(6, 6))

plt.boxplot(data, 
            labels=['Non-personalized (N)', 'Personalized (P)'], patch_artist=True,
            boxprops=dict(facecolor='none', color='black', linewidth=1.2),
            medianprops=dict(color='red', linewidth=2),
            whiskerprops=dict(color='black'),
            capprops=dict(color='black'),)

# --- Overlay individual datapoints (jittered) ---
for i, acc in enumerate(data, start=1):
    x_jitter = np.random.normal(loc=i, scale=0.05, size=len(acc))  # small horizontal spread
    plt.scatter(x_jitter, 
                acc, 
                alpha=0.6, 
                edgecolors='black', 
                linewidth=0.5,
                s=50,)

plt.title('Accuracy Comparison: Personalized vs Non-personalized')
plt.ylabel('Accuracy')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


# box plot for accuracy distribution by condition with lines connecting paired samples
data = [results['accuracy_N'], results['accuracy_P']]

plt.figure(figsize=(6, 6))

plt.boxplot(data, 
            labels=['Non-personalized (N)', 'Personalized (P)'], patch_artist=True,
            boxprops=dict(facecolor='none', color='black', linewidth=1.2),
            medianprops=dict(color='red', linewidth=2),
            whiskerprops=dict(color='black'),
            capprops=dict(color='black'),)

# --- Overlay individual datapoints (jittered) ---
for i, acc in enumerate(data, start=1):
    x_jitter = np.random.normal(loc=i, scale=0.05, size=len(acc))  # small horizontal spread
    plt.scatter(x_jitter, 
                acc, 
                alpha=0.6, 
                edgecolors='black', 
                linewidth=0.5,
                s=50,)
    # --- Connect paired samples with lines ---
for n, p in zip(results['accuracy_N'], results['accuracy_P']):
    plt.plot([1, 2], [n, p], color='gray', alpha=0.6, linewidth=1)

plt.title('Paired Accuracy Comparison: Personalized vs Non-personalized')
plt.ylabel('Accuracy')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()








##### Statistical Tests #####

#Hypotheses:
# H0: There is no difference in accuracy between Personalized and Non-personalized conditions.
# H1: There is a significant difference in accuracy between Personalized and Non-personalized conditions

## Shapiro Wilk test for normality
# gives a p-value > 0.05 indicates normality
from scipy.stats import shapiro, ttest_rel, wilcoxon


#stat_N and stat_P are the test statistics for Non-personalized and Personalized conditions respectively, #p_N and p_P are the corresponding p-values.
# stat_i measures the size of the difference relative to the variability in your sample.
stat_N, p_N = shapiro(results['accuracy_N'])
stat_P, p_P = shapiro(results['accuracy_P'])
print(f"Shapiro-Wilk Test for Non-personalized (N): stat={stat_N:.4f}, p={p_N:.4f}")
print(f"Shapiro-Wilk Test for Personalized (P): stat={stat_P:.4f}, p={p_P:.4f}")


if p_N > 0.05 and p_P > 0.05:
    print("Both groups look normally distributed — you can proceed with a t-test.")
else:
    print("At least one group is not normal — consider a non-parametric test (Wilcoxon).")


### Non parametric test: Wilcoxon signed-rank test###
# paired samples (same participants in both conditions)
# differences are not normally distributed, t-test is not appropriate

# Wilcoxon does:
# test whether the median difference between pairs of observations is zero
# H0: median difference = 0 (no effect)
# H1: median difference ≠ 0 (there is an effect)

#stat: sum of ranks of differences between pairs
#p: probability of observing the data if H0 is true
#p < 0.05 indicates significant difference between conditions

stat, p = wilcoxon(results['accuracy_N'], results['accuracy_P'])
print(f"Wilcoxon signed-rank test: stat={stat:.4f}, p={p:.4f}") 

if p < 0.05:
    print("Reject H0: Significant difference between conditions. The data provides sufficient evidence to conclude that there is a difference in accuracy between Personalized and Non-personalized conditions.")
else:
    print("Fail to reject H0: No significant difference between conditions. The data does not provide sufficient evidence to conclude that there is a difference in accuracy between Personalized and Non-personalized conditions.")
