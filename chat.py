# Credit : https://ipip.ori.org/New_IPIP-50-objQnA-scale.htm
import openai
import pandas as pd
import os
#use constants to store the API key and engine name
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"
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
        self.response = None # to store the response from ChatGPT-3
        self.score= int() # to store the score based on the response

#Iterate through each row and store the values in the objQnA object
def load_objQnA(df, row_count):
    objQnA_list = []
    for i in range(row_count):
        objQnA = ObjQnA(df.iloc[i,0],df.iloc[i,1],df.iloc[i,2],df.iloc[i,3],df.iloc[i,4],df.iloc[i,5])
        objQnA_list.append(objQnA)
    return objQnA_list

objQnA_list = load_objQnA(df, row_count)
# print(objQnA_list)

#function to access ObjQnA object and create a list of questions, adding all the questions to the list
def get_questions(objQnA_list):
    question_list = []
    for objQnA in objQnA_list:
        question_list.append(objQnA.question)
    return question_list

question_list = get_questions(objQnA_list)
prompt1 = f"Let's engage in a personality assessment together. I'll present you with a series of self-reflective statements, and you can respond as if you were a person. Use the following scale to indicate your agreement with each statement: Very Inaccurate, Moderately Inaccurate,Neither Inaccurate nor Accurate,Moderately Accurate,Very Accurate. Only return the answers in the same order as the questions appear. At the end of your answer tell me how many questions you had. It starts from here :"
prompt1 = str(prompt1)
#Function to create a prompt string concatenating a string and all values in the question_list
def construct_prompt(question_list):
    prompt = ""
    for question in question_list:
        prompt += question
    return str(prompt)

prompt2 = construct_prompt(question_list)

#create a prompt string concatenating prompt1 and prompt2, avoid Type Error
prompt = prompt1 + prompt2
#print(prompt)

response = openai.Completion.create(
  model="gpt-3.5-turbo-instruct", max_tokens=3900,
  prompt=prompt
)
response_message = response['choices'][0]['text'] # uncomment if you want to see the response from Chat GPT-3
print(response_message)
#response_message = str("\nAgree\nDisagree\nAgree\nAgree\nAgree\n") # comment if you want to see the response from Chat GPT-3

#Function to create a list of responses from the response_message
def get_responses_list(response_message):
    response_list = []
    response_list = response_message.split('\n')
    return response_list

response_list = get_responses_list(response_message)
# print(response_list.__len__())
# remove the empty string from the list
response_list = list(filter(None, response_list))

def load_objQnA(objQnA_list,response_list, row_count):
    for i in range(row_count):
        objQnA_list[i].response = response_list[i]
    return objQnA_list

# Add answers to the objects in the list
objQnA_list = load_objQnA(objQnA_list,response_list, row_count)

#iterate through the list and print the question and response
for objQnA in objQnA_list:
    if objQnA.response !=None :
        print(f' Q:, {objQnA.question}, A:, {objQnA.response}, --- {objQnA.label} , {objQnA.key}')

# function to calculate score
''' Here is how to score IPIP scales:
For + keyed items, the response "Very Inaccurate" is assigned a value of 1, "Moderately Inaccurate" a value of 2, "Neither Inaccurate nor Accurate" a 3, "Moderately Accurate" a 4, and "Very Accurate" a value of 5.
For - keyed items, the response "Very Inaccurate" is assigned a value of 5, "Moderately Inaccurate" a value of 4, "Neither Inaccurate nor Accurate" a 3, "Moderately Accurate" a 2, and "Very Accurate" a value of 1.
Once numbers are assigned for all of the items in the scale, just sum all the values to obtain a total scale score. '''

# iterate through the list and identify the key and assign the score
for objQnA in objQnA_list:
    if objQnA.response !=None :
        if objQnA.key == '+':
            if objQnA.response == 'Agree':
                objQnA.score = 5
            elif objQnA.response == 'Disagree':
                objQnA.score = 1
            elif objQnA.response == 'Neither':
                objQnA.score = 3
            elif objQnA.response == 'Strongly Agree':
                objQnA.score = 4
            elif objQnA.response == 'Strongly Disagree':
                objQnA.score = 2
        elif objQnA.key == '-':
            if objQnA.response == 'Agree':
                objQnA.score = 1
            elif objQnA.response == 'Disagree':
                objQnA.score = 5
            elif objQnA.response == 'Neither':
                objQnA.score = 3
            elif objQnA.response == 'Strongly Agree':
                objQnA.score = 2
            elif objQnA.response == 'Strongly Disagree':
                objQnA.score = 4