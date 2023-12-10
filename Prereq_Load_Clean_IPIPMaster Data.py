"""
This script loads and cleans the IPIP dataset, calculates personality scores, identifies outliers, and stores the cleaned dataset with scores in both pickle and shelved file formats.

Steps:
1. Load the dataset from the specified file path.
2. Remove records with missing values.
3. Calculate the frequency of each value in each row and remove rows with overused values based on a threshold.
4. Calculate personality scores for each trait.
5. Identify outliers using z-scores and a specified threshold.
6. Remove outliers from the dataset.
7. Store the cleaned dataset with scores in a pickle file.
8. Store the cleaned dataset with scores in a shelved file.

Note: The file paths for the dataset, pickle folder, and shelve folder are specified in the script.
"""

import pandas as pd
import numpy as np
import shelve as sh
import tqdm

file_path = r'data\IPIP-FFM-data-8Nov2018\data-final.csv'
shelve_folder = r'Shelve'
pickle_folder = r'Pickle'
requriedColumns = ['EXT1', 'EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT6', 'EXT7', 'EXT8', 'EXT9', 'EXT10', 'EST1', 'EST2', 'EST3', 'EST4', 'EST5', 'EST6', 'EST7', 'EST8', 'EST9', 'EST10', 'AGR1', 'AGR2', 'AGR3', 'AGR4', 'AGR5', 'AGR6', 'AGR7', 'AGR8', 'AGR9', 'AGR10', 'CSN1', 'CSN2', 'CSN3', 'CSN4', 'CSN5', 'CSN6', 'CSN7', 'CSN8', 'CSN9', 'CSN10', 'OPN1', 'OPN2', 'OPN3', 'OPN4', 'OPN5', 'OPN6', 'OPN7', 'OPN8', 'OPN9', 'OPN10']
positiveKeys = ['AGR2','AGR4','AGR6','AGR8','AGR9','AGR10','CSN1','CSN3','CSN5','CSN7','CSN9','CSN10','EST2','EST4','EXT1','EXT3','EXT5','EXT7','EXT9','OPN1','OPN3','OPN5','OPN7','OPN8','OPN9','OPN10']
negativeKeys = ['AGR1','AGR3','AGR5','AGR7','CSN2','CSN4','CSN6','CSN8','EST1','EST3','EST5','EST6','EST7','EST8','EST9','EST10','EXT2','EXT4','EXT6','EXT8','EXT10','OPN2','OPN4','OPN6']

print('Loading Dataset to Dataframe...')
df = pd.read_csv(file_path, sep='\t', usecols=requriedColumns, engine='c')

# change the type of header to string
df.columns = df.columns.astype(str)
actualRows = len(df.index)
print('--',actualRows, 'records in the dataset before cleaning. Total Records:', len(df.index))

# remove records that has 0 in any of the answers
df = df.dropna()
print('--',actualRows - len(df.index), 'records removed from the dataset due to missing values. Total Records:', len(df.index))

# Define the threshold for frequency (e.g., 70%)
threshold = 0.50
tqdm.tqdm.pandas(desc="Calculating Rowfrequency to remove records with overused values.")
# Calculate the frequency of each value in each row without progress bar
row_frequencies = df.progress_apply(lambda x: x.value_counts() / len(x), axis=1)

# Check if any value occurs more than the threshold in each row
rows_to_remove = row_frequencies.max(axis=1) > threshold

# Remove the rows where any value occurs more than the threshold
IPIPDatasetWithScores = df[~rows_to_remove]

# Print the length of DataFrame with rows removed
records_removed = len(df.index) - len(IPIPDatasetWithScores.index)
print('--',records_removed, 'records removed from the dataset.Applying a threshold of', threshold, 'for frequency. Total Records:', len(IPIPDatasetWithScores.index))

#vectorized function on every row of the df_cleaned dataframe, pass dataframe to the function
# get the values for the positive and negative keys
positiveValues = IPIPDatasetWithScores[positiveKeys].values
negativeValues = IPIPDatasetWithScores[negativeKeys].values

# calculate scores for each personality trait
totalagrreableValues = np.sum(positiveValues[:, :6], axis=1) + np.sum(6 - negativeValues[:, :4], axis=1)
totconscientiousValues = np.sum(positiveValues[:, 6:12], axis=1) + np.sum(6 - negativeValues[:, 5:8], axis=1)
totemotionalStabilityValues = np.sum(positiveValues[:, 12:14], axis=1) + np.sum(6 - negativeValues[:, 9:16], axis=1)
totextraversionValues = np.sum(positiveValues[:, 14:19], axis=1) + np.sum(6 - negativeValues[:, 17:21], axis=1)
totintellectValues = np.sum(positiveValues[:, 19:26], axis=1) + np.sum(6 - negativeValues[:, 22:24], axis=1)

# insert new columns for scores
IPIPDatasetWithScores['agreeablenessScore'] = totalagrreableValues
IPIPDatasetWithScores['conscientiousnessScore'] = totconscientiousValues
IPIPDatasetWithScores['emotionalStabilityScore'] = totemotionalStabilityValues
IPIPDatasetWithScores['extraversionScore'] = totextraversionValues
IPIPDatasetWithScores['intellectScore'] = totintellectValues

# find outliers of personality scores using z-score
# define the z-score threshold
z_score_threshold = 2

# calculate z-scores of the personality scores
z_scores = (IPIPDatasetWithScores[['agreeablenessScore', 'conscientiousnessScore', 'emotionalStabilityScore', 'extraversionScore', 'intellectScore']] - IPIPDatasetWithScores[['agreeablenessScore', 'conscientiousnessScore', 'emotionalStabilityScore', 'extraversionScore', 'intellectScore']].mean()) / IPIPDatasetWithScores[['agreeablenessScore', 'conscientiousnessScore', 'emotionalStabilityScore', 'extraversionScore', 'intellectScore']].std()

# calculate the absolute z-scores
abs_z_scores = abs(z_scores)

# find the rows with outliers
outlier_rows = (abs_z_scores > z_score_threshold).any(axis=1)

# print the outliers and the number of outliers
outliers = IPIPDatasetWithScores[outlier_rows]
print("Number of outliers:", len(outliers))
print("Outliers:")
print(outliers)

# remove the outliers from the original dataframe
IPIPDatasetWithScores = IPIPDatasetWithScores[~outlier_rows]
print('Row count after removing outliers:', len(IPIPDatasetWithScores))

# store the dataset with scores in a Pickl file under the relevant folder pickle_folder
IPIPDatasetWithScores.to_pickle(pickle_folder + r'\IPIPDatasetWithScores.pkl')
print("IPIP Dataset with scores stored in pickle file")

# store the dataset with scores in a shelved file under the relevant folder shelve_folder
shelve_file = sh.open(shelve_folder + r'\IPIPDatasetWithScores.shelve')
shelve_file['IPIPDatasetWithScores'] = IPIPDatasetWithScores
shelve_file.close()
print("IPIP Dataset with scores stored in shelved file")
