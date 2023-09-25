# Credit : https://ipip.ori.org/New_IPIP-50-objQnA-scale.htm
import openai
import pandas as pd
#use constants to store the API key and engine name
openai.api_key = os.getenv("OPENAI_API_KEY")
engine = "gpt-4"


import os
import pandas as pd

file_path = r"C:\Users\vasanthv\Downloads\TedoneItemAssignmentTable30APR21.xlsx"

if os.path.exists(file_path):
    df = pd.read_excel(file_path, sheet_name='data_nodupes')
else:
    print("File not found at the specified path.")

column_list=[]
row_count = len(df.index)
column_list = df.columns.tolist()

#define variable for each of the column
column_list[0] = 'number'
column_list[1] = 'objQnA'
column_list[2] = 'alpha'
column_list[3] = 'key'
column_list[4] = 'question'
column_list[5] = 'label'

#create a class object to store values in each of the column across total row count
class ObjQnA:
    def __init__(self, number, objQnA, alpha, key, question, label):
        self.number = number
        self.objQnA = objQnA
        self.alpha = alpha
        self.key = key
        self.question = question
        self.label = label

#Iterate through each row and store the values in the objQnA object
def load_objQnA(df, row_count):
    objQnA_list = []
    for i in range(10):
        objQnA = ObjQnA(df.iloc[i,0],df.iloc[i,1],df.iloc[i,2],df.iloc[i,3],df.iloc[i,4],df.iloc[i,5])
        objQnA_list.append(objQnA)
    return objQnA_list

objQnA_list = load_objQnA(df, row_count)
#print(objQnA_list)

#function to access ObjQnA object and create a list of questions, adding all the questions to the list
def get_questions(objQnA_list):
    question_list = []
    for objQnA in objQnA_list:
        question_list.append(objQnA.question)
    return question_list

question_list = get_questions(objQnA_list)
prompt1 = f"I will ask you,questions.Answer with either agree or disagree for each of them."
prompt1 = str(prompt1)
#Function to create a prompt string concatenating a string and all values in the question_list
def create_prompt(question_list):
    prompt = "This is a list of questions.Answer them in the same order as they appear."
    for question in question_list:
        prompt += question
    return str(prompt)

prompt2 = create_prompt(question_list)

#create a prompt string concatenating prompt1 and prompt2, avoid Type Error
prompt = prompt1 + prompt2
print(prompt)

response = openai.Completion.create(
  model="gpt-3.5-turbo-instruct",
  prompt=prompt
)
response_message = response['choices'][0]['text']
print(response_message)