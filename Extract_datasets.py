import pickle as pkl
import pandas as pd

# load the dataset with scores from the Pickle file
pickle_file = r'C:\Users\vasanthv\OneDrive - Microsoft\MS HCI\Fall 2023\ChatGPT-Personality\Pickle\IPIPDatasetWithScores.pkl'
with open(pickle_file, 'rb') as f:
    IPIPDatasetWithScores = pkl.load(f)

# define a function to change all answers to text values
def change_answers_to_text(df):
    return df.replace({1: 'Disagree Strongly', 2: 'Disagree Moderately', 3: 'Neither Agree nor Disagree', 4: 'Agree Moderately', 5: 'Agree Strongly'})

# replace all question codes in the data frames with Question(column D) in in IPIPQuestions dataframe by matching the question code with Code(column B) 
IPIPQuestions = pd.read_excel('data/IPIP-FFM-data-8Nov2018/IPIPQuestionaire.xlsx', usecols=['Code', 'Question'], index_col='Code').squeeze().to_dict()

# define a function to replace question codes with question text in a dataframe
def replace_question_codes(df):
    return df.rename(columns=IPIPQuestions)

def createTrainingDataset(df,trait,type):
    row_count = len(df.index)
    column_count = 50
    role_system_content = 'xx'
    if type == 1:
        recordType='high'
    else:
        recordType='low'
    # create a training example for each row in the dataframe. Each row is a training example. Each training example has 3 messages - system, user and assistant. system message is role_system_content, user message is the column header and assistant message is the value in the cell
    for row in range(row_count):
        for column in range(column_count):
            if df.iloc[row, column] != role_system_content:
                trainingRecord = '{"messages": [{"role": "system", "content":'+ role_system_content +'}, {"role": "user", "content": "' + df.columns[column] + '"}, {"role": "assistant", "content": "' + df.iloc[row, column] + '"}]}'
                # write the training record to a text file under a folder 'Training_Records. First time create the folder and file, after that append to the file
                with open(f'Training_Records/{recordType}_{trait}_scores.txt', 'a') as f:
                    f.write(trainingRecord + '\n')
    print(f'Training records created for {trait} trait with {recordType} scores')

        
# create dataframes dynamically using a loop and store in lists
traits = ['agreeableness', 'conscientiousness', 'emotionalStability', 'extraversion', 'intellect']
# remove records that has 0 in any of the answers
print('Row count before removing records with 0 in any of the answers:', len(IPIPDatasetWithScores))

IPIPDatasetWithScores = IPIPDatasetWithScores[~(IPIPDatasetWithScores == 0).any(axis=1)]
print ('Row count after removing records with 0 in any of the answers:', len(IPIPDatasetWithScores))


for trait in traits:
    high_scores = change_answers_to_text(IPIPDatasetWithScores.nlargest(100, f'{trait}Score'))
    low_scores = change_answers_to_text(IPIPDatasetWithScores.nsmallest(100, f'{trait}Score'))

    globals()[f'high_{trait}_scores'] = replace_question_codes(high_scores)
    print('Dataframe for high scores:', globals()[f'high_{trait}_scores'].describe())

    globals()[f'low_{trait}_scores'] = replace_question_codes(low_scores)
    print('Dataframe for low scores:', globals()[f'low_{trait}_scores'].describe())
    
    createTrainingDataset(globals()[f'high_{trait}_scores'],trait,1)
    createTrainingDataset(globals()[f'low_{trait}_scores'],trait,0)
