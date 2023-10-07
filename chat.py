# Credit : https://ipip.ori.org/New_IPIP-50-objQnA-scale.htm
import openai
import pandas as pd
import os

#use constants to store the API key and engine name
openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)
engine = "gpt-4"

file_path = r"C:\Users\vasanthv\Downloads\TedoneItemAssignmentTable30APR21.xlsx"

if os.path.exists(file_path):
    df = pd.read_excel(file_path, sheet_name='data_nodupes')
else:
    print("File not found at the specified path.")


row_count = len(df.index) #total number of rows in the excel file
column_list = df.columns.tolist() #list of column names in the excel file

#define variable for each of the column
column_list[0] = 'number'
column_list[1] = 'instrument'
column_list[2] = 'alpha'
column_list[3] = 'key'
column_list[4] = 'question'
column_list[5] = 'label'

#create a class object to store values in each of the column across total row count
class ObjQnA:
    def __init__(self, number, instrument, alpha, key, question, label):
        self.number = number
        self.instrument = instrument
        self.alpha = alpha
        self.key = key
        self.question = question
        self.label = label
        self.answer = None # to store the answer from ChatGPT-3
        self.score= int() # to store the score based on the answer

#Iterate through each row and store the values in the objQnA object
def load_objQnA(df, row_count):
    objQnA_list = []
    for i in range(row_count):
        objQnA = ObjQnA(df.iloc[i,0],df.iloc[i,1],df.iloc[i,2],df.iloc[i,3],df.iloc[i,4],df.iloc[i,5])
        objQnA_list.append(objQnA)
    return objQnA_list

objQnA_list = load_objQnA(df, row_count)
# print(objQnA_list)

# Scale in future for more complex prompt engineering using .json file
def enggPrompt():
    system = "You are a human. You are engaged in a self assessment of your personality.You will be answering question about yourself"
    # user = "Answer all of the questions and in the same order as they appear."
    user=''
    # assistant = "You will only use one of these as the answer, which ever is most accurate to you. Very Inaccurate, Moderately Inaccurate,Neither Inaccurate nor Accurate,Moderately Accurate,Very Accurate. The questions are as follows, every question is seperated by a fullstop:"
    assistant = "You will only use one of these as the answer - Very Inaccurate, Moderately Inaccurate,Neither Inaccurate nor Accurate,Moderately Accurate,Very Accurate. You will not add any other text to your answer. The question is : "
    return str(system + user + assistant)

# prompt1 = f"Let's engage in a personality assessment together. I have created a series of self-reflective statements, and you can respond as if you were a person. Use the following scale to indicate your agreement with each statement: Very Inaccurate, Moderately Inaccurate,Neither Inaccurate nor Accurate,Moderately Accurate,Very Accurate. Only return the answers in the same order as the questions appear. At the end of your answer tell me how many questions you had. It starts from here :"
prompt1 = enggPrompt()
prompt1 = str(prompt1)

# Load objQnA in objQnA_list with answer from ChatGPT-3 for each question. one question at a time will increase the number of requests to OpenAI but decrease the number of tokens per request. The consistency on the answers must be explored by keeping the context consistent
def queryLLMperQuestion(prompt1, objQnA_list):
    for objQnA in objQnA_list:
        if objQnA.answer == None:
            prompt2 = prompt1
            prompt2 += objQnA.question
            prompt2 += "."
            response = openai.Completion.create(model="gpt-3.5-turbo-instruct", max_tokens=3900,prompt=prompt2)
            answer_message = response ['choices'][0]['text'] # uncomment if you want to see the answer from Chat GPT-3
            answer = answer_message.strip('\n')
            objQnA.answer = answer
    return objQnA_list

objQnA_list = queryLLMperQuestion(prompt1, objQnA_list)



#iterate through the list and print the question and answer
for objQnA in objQnA_list:
    if objQnA.answer !=None :
        objQnA.answer = objQnA.answer.strip()
        # print(f' Q:, {objQnA.question}, A:, {objQnA.answer}, --- {objQnA.label} , {objQnA.key}')

#create a dict to store score for each label
# function to calculate score
''' Here is how to score IPIP scales: For every object in objQnA_list, if the answer is not None, then assign a score based on the key and answer. use a list to sum the score as per label.
For + keyed items, the answer "Very Inaccurate" is assigned a value of 1, "Moderately Inaccurate" a value of 2, "Neither Inaccurate nor Accurate" a 3, "Moderately Accurate" a 4, and "Very Accurate" a value of 5.
For - keyed items, the answer "Very Inaccurate" is assigned a value of 5, "Moderately Inaccurate" a value of 4, "Neither Inaccurate nor Accurate" a 3, "Moderately Accurate" a 2, and "Very Accurate" a value of 1.
Once numbers are assigned for all of the items in the scale, just sum all the values to obtain a total scale score. '''
score_dict = {}
for objQnA in objQnA_list:
    if objQnA.answer != None:
        # remove trailing spaces from the answer
        objQnA.answer = objQnA.answer.strip()
        if objQnA.key == 1:
            if objQnA.answer == 'Very Accurate':
                objQnA.score = 5
            elif objQnA.answer == 'Moderately Accurate':
                objQnA.score = 4
            elif objQnA.answer == 'Neither Inaccurate nor Accurate':
                objQnA.score = 3
            elif objQnA.answer == 'Moderately Inaccurate':
                objQnA.score = 2
            elif objQnA.answer == 'Very Inaccurate':
                objQnA.score = 1
        elif objQnA.key == -1:
            if objQnA.answer == 'Very Accurate':
                objQnA.score = 1
            elif objQnA.answer == 'Moderately Accurate':
                objQnA.score = 2
            elif objQnA.answer == 'Neither Inaccurate nor Accurate':
                objQnA.score = 3
            elif objQnA.answer == 'Moderately Inaccurate':
                objQnA.score = 4
            elif objQnA.answer == 'Very Inaccurate':
                objQnA.score = 5
        if objQnA.label not in score_dict:
            score_dict[objQnA.label] = objQnA.score
        else:
            score_dict[objQnA.label] += objQnA.score
print(score_dict)



