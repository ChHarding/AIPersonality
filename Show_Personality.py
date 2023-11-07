# Show the personality scores from AIPersonality\Results\IPIP_ScoresDB.xlsx
import pandas as pd
import matplotlib.pyplot as plt

import pickle as pkl
import pandas as pd

# Load the excel file with the scores
scores_file = r'AIPersonality\Results\IPIP_ScoresDB.xlsx'
score_sheet = 'NewIPIP_ScoresDB'
# load the sheet to dataframe
df = pd.read_excel(scores_file, sheet_name = score_sheet)
# create a dictionary with the each personality trait and its average score
avg_personality_scores = {}
for index, row in df.iterrows():
    # skip the first column which is the personality trait
    avg_personality_scores[row['Personality Traits']] = int(row[1:].mean())
# print the average personality scores
print('Average Personality Scores:')
print(avg_personality_scores)
# plot the average personality scores as sliders for each personality trait
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
plt.xlabel('Personality Traits')
plt.ylabel('Average Score')
plt.title('Personality Scores')
plt.xticks(rotation=90)
plt.yticks(range(0, 50, 5))
plt.grid(True)
plt.subplots_adjust(bottom=0.25)
plt.bar(avg_personality_scores.keys(), avg_personality_scores.values())
plt.show()









