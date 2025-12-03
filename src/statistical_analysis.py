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
PN,a38032e7
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





#print number of participants having accuracy_P > accuracy_N
num_better_P = (results['accuracy_P'] > results['accuracy_N']).sum()
print(f"Number of participants with better accuracy in Personalized (P) than Non-personalized (N): {num_better_P}")

num_better_N = (results['accuracy_N'] > results['accuracy_P']).sum()
print(f"Number of participants with better accuracy in Non-personalized (N) than Personalized (P): {num_better_N}")

num_equal = (results['accuracy_N'] == results['accuracy_P']).sum()
print(f"Number of participants with equal accuracy in both conditions: {num_equal}")

#print number of participants having accuracy in first test > second test
first_test = []
second_test = []
for _, row in results.iterrows():
    if row['Condition'] == 'PN':
        first_test.append(row['accuracy_P'])
        second_test.append(row['accuracy_N'])
    else:
        first_test.append(row['accuracy_N'])
        second_test.append(row['accuracy_P'])
num_better_first = sum(1 for ft, st in zip(first_test, second_test) if ft > st)
print(f"Number of participants with better accuracy in First Test than Second Test: {num_better_first}")
num_better_second = sum(1 for ft, st in zip(first_test, second_test) if st > ft)
print(f"Number of participants with better accuracy in Second Test than First Test: {num_better_second}")
num_equal_tests = sum(1 for ft, st in zip(first_test, second_test) if ft == st)
print(f"Number of participants with equal accuracy in both tests: {num_equal_tests}")   


###-------------Youtube usage filtering---------------------------###
# filter for youtube usage more than 45 min, count number of participants
filtered_results = results[results['youtube_usage'] == "More than 45 minutes"]
num_participants = filtered_results.shape[0]
print(f"Number of participants with YouTube usage > 45 min: {num_participants}")

filtered_results = results[results['youtube_usage'] == "16-45 minutes"]
num_participants = filtered_results.shape[0]
print(f"Number of participants with YouTube usage 16-45 min: {num_participants}")

filtered_results = results[results['youtube_usage'] == "0-15 minutes"]
num_participants = filtered_results.shape[0]
print(f"Number of participants with YouTube usage 0-15 min: {num_participants}")


filtered_results_youtubeUsage_long = results[results['youtube_usage'] != "0-15 minutes"]
num_participants = filtered_results_youtubeUsage_long.shape[0]
print(f"Number of participants with YouTube usage > 15 min: {num_participants}")

#print number of participants having accuracy_P > accuracy_N in filtered results_youtubeUsage
num_better_P_filtered = (filtered_results_youtubeUsage_long['accuracy_P'] > filtered_results_youtubeUsage_long['accuracy_N']).sum()
print(f"Number of participants with better accuracy in Personalized (P) than Non-personalized (N) (YouTube usage > 15 min): {num_better_P_filtered}")   

#print number of participants having accuracy_N > accuracy_P in filtered results_youtubeUsage
num_better_N_filtered = (filtered_results_youtubeUsage_long['accuracy_N'] > filtered_results_youtubeUsage_long['accuracy_P']).sum()
print(f"Number of participants with better accuracy in Non-personalized (N) than Personalized (P) (YouTube usage > 15 min): {num_better_N_filtered}")
num_equal_filtered = (filtered_results_youtubeUsage_long['accuracy_N'] == filtered_results_youtubeUsage_long['accuracy_P']).sum()
print(f"Number of participants with equal accuracy in both conditions (YouTube usage > 15 min): {num_equal_filtered}")  

#print number of participants having accuracy in first test > second test in filtered results_youtubeUsage
first_test_filtered = []    
second_test_filtered = []
for _, row in filtered_results_youtubeUsage_long.iterrows():
    if row['Condition'] == 'PN':
        first_test_filtered.append(row['accuracy_P'])
        second_test_filtered.append(row['accuracy_N'])
    else:
        first_test_filtered.append(row['accuracy_N'])
        second_test_filtered.append(row['accuracy_P'])
num_better_first_filtered = sum(1 for ft, st in zip(first_test_filtered, second_test_filtered) if ft > st)
print(f"Number of participants with better accuracy in First Test than Second Test (YouTube usage > 15 min): {num_better_first_filtered}")
num_better_second_filtered = sum(1 for ft, st in zip(first_test_filtered, second_test_filtered) if st > ft)
print(f"Number of participants with better accuracy in Second Test than First Test (YouTube usage > 15 min): {num_better_second_filtered}")
num_equal_tests_filtered = sum(1 for ft, st in zip(first_test_filtered, second_test_filtered) if ft == st)
print(f"Number of participants with equal accuracy in both tests (YouTube usage > 15 min): {num_equal_tests_filtered}") 


filtered_results_youtubeUsage_short = results[results['youtube_usage'] == "0-15 minutes"]

###### PLOTS ######


#plot histogram with interpolation for accuracy distributions
#in two panels for each condition
#with seaborn
import seaborn as sns   


fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
sns.histplot(results['accuracy_N'], bins=10, binrange=(0, 1), kde=True, ax=axs[0], color='tab:blue')
axs[0].set_xlim(0, 1)
axs[0].set_title('Accuracy Distribution: Non-personalized (N)') 
axs[0].set_xlabel('Accuracy')
axs[0].set_ylabel('Frequency')

sns.histplot(results['accuracy_P'], bins=10, binrange=(0, 1), kde=True, ax=axs[1], color='tab:orange')
axs[1].set_xlim(0, 1)
axs[1].set_title('Accuracy Distribution: Personalized (P)')
axs[1].set_xlabel('Accuracy')

plt.tight_layout()
plt.show()


# fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
# sns.histplot(filtered_results_youtubeUsage_long['accuracy_N'], bins=10, kde=True, ax=axs[0], color='tab:blue')
# axs[0].set_title('Accuracy Distribution: Non-personalized (N) in participants with YouTube usage > 15 min') 
# axs[0].set_xlabel('Accuracy')
# axs[0].set_ylabel('Frequency')
# sns.histplot(filtered_results_youtubeUsage_long['accuracy_P'], bins=10, kde=True, ax=axs[1], color='tab:orange')
# axs[1].set_title('Accuracy Distribution: Personalized (P) in participants with YouTube usage > 15 min')
# axs[1].set_xlabel('Accuracy')
# plt.tight_layout()
# plt.show()




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
plt.ylim(0, 1)

plt.tight_layout()
plt.show()


# # box plot for accuracy distribution by condition
# data = [results['accuracy_N'], results['accuracy_P']]

# plt.figure(figsize=(6, 6))

# plt.boxplot(data, 
#             labels=['Non-personalized (N)', 'Personalized (P)'], patch_artist=True,
#             boxprops=dict(facecolor='none', color='black', linewidth=1.2),
#             medianprops=dict(color='red', linewidth=2),
#             whiskerprops=dict(color='black'),
#             capprops=dict(color='black'),)

# # --- Overlay individual datapoints (jittered) ---
# for i, acc in enumerate(data, start=1):
#     x_jitter = np.random.normal(loc=i, scale=0.05, size=len(acc))  # small horizontal spread
#     plt.scatter(x_jitter, 
#                 acc, 
#                 alpha=0.6, 
#                 edgecolors='black', 
#                 linewidth=0.5,
#                 s=50,)

# plt.title('Accuracy Comparison: Personalized vs Non-personalized')
# plt.ylabel('Accuracy')
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.tight_layout()
# #plt.show()


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
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
#plt.show()








#plot box plot for first and second test (getting out of Condition)
# when condition = PN, first test = accuracy_P, second_test = accuracy_N
# when condition = NP, first test = accuracy_N, second_test = accuracy_P
#color points based on condition

first_test = []
second_test = []
for _, row in results.iterrows():
    if row['Condition'] == 'PN':
        first_test.append(row['accuracy_P'])
        second_test.append(row['accuracy_N'])
    else:
        first_test.append(row['accuracy_N'])
        second_test.append(row['accuracy_P'])

data = [first_test, second_test]
plt.figure(figsize=(6, 6))
plt.boxplot(data, 
            labels=['First Test', 'Second Test'], patch_artist=True,
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
for ft, st in zip(first_test, second_test):
    plt.plot([1, 2], [ft, st], color='gray', alpha=0.6, linewidth=1)
plt.title('Paired Accuracy Comparison: First Test vs Second Test')
plt.ylabel('Accuracy')
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


first_test = []
second_test = []
first_colors = []
second_colors = []

for _, row in results.iterrows():
    if row['Condition'] == 'PN':
        # First = P, Second = N
        first_test.append(row['accuracy_P'])
        second_test.append(row['accuracy_N'])
        first_colors.append('tab:orange')   # P
        second_colors.append('tab:blue')    # N
    else:
        # First = N, Second = P
        first_test.append(row['accuracy_N'])
        second_test.append(row['accuracy_P'])
        first_colors.append('tab:blue')     # N
        second_colors.append('tab:orange')  # P

data = [ , second_test]
colors = [first_colors, second_colors]

plt.figure(figsize=(6, 6))
plt.boxplot(
    data,
    labels=['First Test', 'Second Test'], 
    patch_artist=True,
    boxprops=dict(facecolor='none', color='black', linewidth=1.2),
    medianprops=dict(color='red', linewidth=2),
    whiskerprops=dict(color='black'),
    capprops=dict(color='black')
)

# --- Overlay individual datapoints (jittered) ---
for i, (acc, col) in enumerate(zip(data, colors), start=1):
    x_jitter = np.random.normal(loc=i, scale=0.05, size=len(acc))
    plt.scatter(
        x_jitter,
        acc,
        c=col,                 # <-- color per-condition
        alpha=0.7,
        edgecolors='black',
        linewidth=0.5,
        s=50,
    )

# --- Connect paired samples ---
for ft, st in zip(first_test, second_test):
    plt.plot([1, 2], [ft, st], color='gray', alpha=0.6, linewidth=1)

import matplotlib.patches as mpatches
patch_P = mpatches.Patch(color='tab:orange', label='P')
patch_N = mpatches.Patch(color='tab:blue', label='N')
plt.legend(handles=[patch_P, patch_N], loc='upper right')


plt.title('Paired Accuracy Comparison: First Test vs Second Test')
plt.ylabel('Accuracy')
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()



## -filtered results for YouTube usage --##

# box plot for accuracy distribution by condition with lines connecting paired samples
data_combined = [filtered_results_youtubeUsage_short['accuracy_N'], filtered_results_youtubeUsage_short['accuracy_P'], filtered_results_youtubeUsage_long['accuracy_N'], filtered_results_youtubeUsage_long['accuracy_P']]

labels = ['Non-personalized', 'Personalized', 'Non-personalized', 'Personalized']
plt.figure(figsize=(8, 6))

plt.boxplot(data_combined, 
            labels=labels, patch_artist=True,
            boxprops=dict(facecolor='none', color='black', linewidth=1.2),
            medianprops=dict(color='red', linewidth=2),
            whiskerprops=dict(color='black'),
            capprops=dict(color='black'),
            widths=0.25,)

# --- Overlay individual datapoints (jittered) ---
colors = ['tab:blue', 'tab:orange', 'tab:blue', 'tab:orange']
for i, acc in enumerate(data_combined, start=1):
    x_jitter = np.random.normal(loc=i, scale=0.05, size=len(acc))  # small horizontal spread
    plt.scatter(x_jitter, 
                acc, 
                alpha=0.6, 
                edgecolors='black', 
                linewidth=0.5,
                s=50,
                c=colors[i-1],)
    # --- Connect paired samples with lines ---
for n, p in zip(filtered_results_youtubeUsage_short['accuracy_N'], filtered_results_youtubeUsage_short['accuracy_P']):
    plt.plot([1, 2], [n, p], color='gray', alpha=0.6, linewidth=1)

for n, p in zip(filtered_results_youtubeUsage_long['accuracy_N'], filtered_results_youtubeUsage_long['accuracy_P']):
    plt.plot([3, 4], [n, p], color='gray', alpha=0.6, linewidth=1)

plt.axvline(2.5, color='black', linestyle='--', linewidth=1)
plt.text(1.5, plt.ylim()[0] - 0.15, 'Short (0-15 min)', ha='center', va='center', fontsize=11)
plt.text(3.5, plt.ylim()[0] - 0.15, 'Long (>15 min)', ha='center', va='center', fontsize=11)
plt.title('Accuracy comparison by YouTube Shorts usage')
plt.ylabel('Accuracy')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.ylim(0, 1)
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

# effect size of Wilcoxon test
n = len(results)
z = (stat - (n*(n+1))/4) / np.sqrt((n*(n+1)*(2*n+1))/24)
r = z / np.sqrt(n)
print(f"Effect size r: {r:.4f}")

## Wilcoxon signed-rank test for filtered YouTube usage > 15 min
stat_long, p_long = wilcoxon(filtered_results_youtubeUsage_long['accuracy_N'], filtered_results_youtubeUsage_long['accuracy_P'])
print(f"Wilcoxon signed-rank test (YouTube usage > 15 min): stat={stat_long:.4f}, p={p_long:.4f}") 

if p < 0.05:
    print("Reject H0: Significant difference between conditions. The data provides sufficient evidence to conclude that there is a difference in accuracy between Personalized and Non-personalized conditions.")
else:
    print("Fail to reject H0: No significant difference between conditions. The data does not provide sufficient evidence to conclude that there is a difference in accuracy between Personalized and Non-personalized conditions.")


## Wilcoxon signed-rank test for filtered YouTube usage 0-15 min
stat_short, p_short = wilcoxon(filtered_results_youtubeUsage_short['accuracy_N'], filtered_results_youtubeUsage_short['accuracy_P'])
print(f"Wilcoxon signed-rank test (YouTube usage 0-15 min): stat={stat_short:.4f}, p={p_short:.4f}")

if p < 0.05:
    print("Reject H0: Significant difference between conditions. The data provides sufficient evidence to conclude that there is a difference in accuracy between Personalized and Non-personalized conditions.")
else:
    print("Fail to reject H0: No significant difference between conditions. The data does not provide sufficient evidence to conclude that there is a difference in accuracy between Personalized and Non-personalized conditions.")

## Compute Wilcoxon rank-sum test for short vs long usage based on accuracy differences between conditions
from scipy.stats import ranksums
accuracy_diff_short = filtered_results_youtubeUsage_short['accuracy_P'] - filtered_results_youtubeUsage_short['accuracy_N']
accuracy_diff_long = filtered_results_youtubeUsage_long['accuracy_P'] - filtered_results_youtubeUsage_long['accuracy_N']

stat_rs, p_rs = ranksums(accuracy_diff_short, accuracy_diff_long)
print(f"Wilcoxon rank-sum test (Short vs Long YouTube usage): stat={stat_rs:.4f}, p={p_rs:.4f}")

if p_rs < 0.05:
    print("Reject H0: Significant difference between short and long YouTube usage groups in accuracy differences between conditions.")
else:
    print("Fail to reject H0: No significant difference between short and long YouTube usage groups in accuracy differences between conditions.")


#compute variability (standard deviation) for each condition
std_N = results['accuracy_N'].std()
std_P = results['accuracy_P'].std()
print(f"Standard Deviation Non-personalized (N): {std_N:.4f}")
print(f"Standard Deviation Personalized (P): {std_P:.4f}")
