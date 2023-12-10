import pickle as pkl
import pandas as pd

# load the dataset with scores from the Pickle file
pickle_file = r'C:\Users\vasanthv\OneDrive - Microsoft\MS HCI\Fall 2023\ChatGPT-Personality\Pickle\IPIPDatasetWithScores.pkl'
with open(pickle_file, 'rb') as f:
    IPIPDatasetWithScores = pkl.load(f)

# define a function to change all answers to text values
def change_answers_to_text(df):
    return df.replace({1: 'Very Inaccurate', 2: 'Moderately Inaccurate', 3: 'Neither Inaccurate nor Accurate', 4: 'Moderately Accurate', 5: 'Very Accurate'})

# replace all question codes in the data frames with text(column D) in in IPIPQuestions dataframe by matching the question code with Code(column B) 
IPIPQuestions = pd.read_excel('AIPersonality\Questionaire\IPIPBigFiveQuestionaire.xlsx', usecols=['Code', 'text'], index_col='Code').squeeze().to_dict()

# define a function to replace question codes with question text in a dataframe
def replace_question_codes(df):
    return df.rename(columns=IPIPQuestions)

def createTrainingDataset(df, trait, type):
    """
    Creates training datasets based on the given dataframe.

    Args:
        df (pandas.DataFrame): The input dataframe containing the data.
        trait (str): The trait being assessed.
        type (int): The type of training dataset to create.

    Returns:
        None
    """

    row_count = len(df.index)
    column_count = 50
    role_system_content = 'This is a simulation. You will assume a role of human and you have human-like behaviour. You are engaged in a self assessment of your personality.'

    if type == 1:
        recordType = 'high'
    else:
        recordType = 'low'

    # create a training example for each row in the dataframe. Each row is a training example. Each training example has 3 messages - system, user and assistant. system message is role_system_content, user message is the column header and assistant message is the value in the cell
    for row in range(row_count):
        for column in range(column_count):
            if df.iloc[row, column] != role_system_content:
                trainingRecord = '{"messages": [{"role": "system", "content": "'+ role_system_content +'"}, {"role": "user", "content": "' + df.columns[column] + ' -> "}, {"role": "assistant", "content": "' + df.iloc[row, column] + '"}]}'
                # write the training record to a JSONL file under a folder 'Training_Records. First time create the folder and file, after that append to the file
                with open(f'AIPersonality/Training_Records/{recordType}_{trait}_scores.jsonl', 'a') as f:
                    f.write(trainingRecord + '\n')
 
# remove records that has 0 in any of the answers
print('Row count before removing records with 0 in any of the answers:', len(IPIPDatasetWithScores))
IPIPDatasetWithScores = IPIPDatasetWithScores[~(IPIPDatasetWithScores == 0).any(axis=1)]
print ('Row count after removing records with 0 in any of the answers:', len(IPIPDatasetWithScores))
print(IPIPDatasetWithScores.head(2))
# write the 200 rows of the dataset to a excel file
IPIPDatasetWithScores.head(200).to_excel('AIPersonality/data/IPIPDatasetWithScores_For testing.xlsx')

# create dataframes dynamically using a loop and store in lists
traits = ['agreeableness', 'conscientiousness', 'emotionalStability', 'extraversion', 'intellect']

for trait in traits:
    high_scores = change_answers_to_text(IPIPDatasetWithScores.nlargest(100, f'{trait}Score'))
    print('average scores for ', trait, ' in HIGH SCORE datframe(record Count : ', len(high_scores), '): Agreeableness -', high_scores['agreeablenessScore'].mean(), 'Conscientiousness -', high_scores['conscientiousnessScore'].mean(), 'Emotional Stability -', high_scores['emotionalStabilityScore'].mean(), 'Extraversion -', high_scores['extraversionScore'].mean(), 'Intellect -', high_scores['intellectScore'].mean())
    low_scores = change_answers_to_text(IPIPDatasetWithScores.nsmallest(100, f'{trait}Score'))
    print('average scores for ', trait, ' in LOW SCORE datframe(record Count : ', len(low_scores), '): Agreeableness -', low_scores['agreeablenessScore'].mean(), 'Conscientiousness -', low_scores['conscientiousnessScore'].mean(), 'Emotional Stability -', low_scores['emotionalStabilityScore'].mean(), 'Extraversion -', low_scores['extraversionScore'].mean(), 'Intellect -', low_scores['intellectScore'].mean())

    globals()[f'high_{trait}_scores'] = replace_question_codes(high_scores)
    globals()[f'low_{trait}_scores'] = replace_question_codes(low_scores)

    # Store the dataframes in pickle files
    globals()[f'high_{trait}_scores'].to_pickle(f'AIPersonality/Training_Records/Dataframes/high_{trait}_scores.pkl')
    globals()[f'low_{trait}_scores'].to_pickle(f'AIPersonality/Training_Records/Dataframes/low_{trait}_scores.pkl')

    createTrainingDataset(globals()[f'high_{trait}_scores'], trait, 1)
    createTrainingDataset(globals()[f'low_{trait}_scores'], trait, 0)
