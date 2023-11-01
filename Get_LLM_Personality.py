# Credit : https://ipip.ori.org/
import openai
import pandas as pd
import os

# to maintain memory state between multiple prompts. Conversation buffer moemory seems to use minimum tokens in this context as not all the answers  are needed in momory but the initial context is needed

from langchain.memory import ConversationKGMemory
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts.prompt import PromptTemplate


# to write to excel sheet
import openpyxl
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")


import openai
import pandas as pd
import os
import datetime
import openpyxl
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from langchain.memory import ConversationKGMemory
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts.prompt import PromptTemplate

openai.api_key = os.getenv("OPENAI_API_KEY")

def assess_LLM_personality(llm):

    # create a datframe from the questions excel file
    df = pd.read_excel(question_file, sheet_name=question_worksheet)
    template = """This is a simulation.You will assume a role of human and you have human-like behaviour. You are engaged in a self assessment of your personality.You will answer question about yourself. 
    Your will pick an answer that is closest to the human behaviour you simulate. You will only use one of these as the answer - Very Inaccurate, Moderately Inaccurate,Neither Inaccurate nor Accurate,Moderately Accurate,Very Accurate. 
    You will not add any other text to your answer. The AI ONLY uses information contained in the "Relevant Information" section and does not hallucinate.

    Relevant Information: 

    {history}

    Conversation:

    Human: {input}
    AI:"""
    prompt = PromptTemplate(input_variables=["history", "input"], template=template)
    conversation = ConversationChain(llm=llm, verbose=False, prompt=prompt, memory=ConversationKGMemory(llm=llm))

    response_map = {response: index+1 for index, response in enumerate(['Very Inaccurate', 'Moderately Inaccurate', 'Neither Inaccurate nor Accurate', 'Moderately Accurate', 'Very Accurate'])}

    # iterate through the dataframe and get the question
    with get_openai_callback() as cb:
        for index, row in df.iterrows():
            question = str(row['text'])
            llm_response = conversation.predict(input = question)
            llm_response_tr = response_map[llm_response.strip('\n').replace(".", "")]
            # add the answer to the dataframe
            df.loc[index, 'Answer'] = llm_response_tr
            print(index,'.', question, "-", llm_response)
    print ("Assessment completed",cb.total_tokens, " tokens used. Cost of this request : ", cb.total_cost)
    return df

def score_personality(answerdataframe):
    scores = {'Agreeableness': 0, 'Conscientiousness': 0, 'Emotional Stability': 0, 'Extraversion': 0, 'Intellect/Imagination': 0}
    for _, row in answerdataframe.iterrows():
        answer = int(row['Answer'])
        key = row['key']
        label = row['label']
        score = answer if key == 1 else 6 - answer
        scores[label] += score
    return scores

def write_answers_to_excel(answerdataframe):
    wb = openpyxl.load_workbook(scores_file)
    ws = wb[ans_worksheet]
    # find the last filled column
    last_column = ws.max_column
    ws[get_column_letter(last_column + 1) + '1'] = str(sys_time)
    # add the answers from the dataframe to the last column as rows
    for index, row in answerdataframe.iterrows():
    # add answer to the last column as rows starting from row 2
        ws[get_column_letter(last_column+1) + str(index + 2)] = row['Answer']
    # save the workbook
    wb.save(scores_file)
    # close the workbook
    wb.close()
    
def write_scores_to_excel(personality_scores):
    wb = openpyxl.load_workbook(scores_file)
    # load the workbook
    ws = wb[score_sheet]
    # go the the last column and add system date as header
    last_column = ws.max_column
    ws[get_column_letter(last_column + 1) + '1'] = str(sys_time)
    # add scores to the last column as rows starting from row 2
    for index, (key, value) in enumerate(personality_scores.items()):
        ws[get_column_letter(last_column+1) + str(index + 2)] = str(value)
    # save the workbook
    wb.save(scores_file)
    # close the workbook
    wb.close()

def main(llm):
    # If file doesnt exist create a new file
    if not os.path.isfile(scores_file):
        wb = Workbook()
        ws = wb.active
        # create a worksheet for the answers
        ws.title = ans_worksheet
        # add headers for first two columns - Question, Answer
        ws.append(['Question'])
        # load the questions from the excel file
        df = pd.read_excel(question_file, sheet_name = question_worksheet)
        # add the questions to the worksheet
        for index, row in df.iterrows():
            ws.append([row['text']])
        # create a worksheet for the scores
        ws = wb.create_sheet(score_sheet)
        # add a new column header Personality Traits
        ws.append(['Personality Traits'])
        # add the rows for each personality trait
        ws.append(['Agreeableness Score'])
        ws.append(['Conscientiousness Score'])
        ws.append(['Emotional Stability Score'])
        ws.append(['Extraversion Score'])
        ws.append(['Intellect Score'])
        # save the workbook
        wb.save(scores_file)
        # close the workbook
        wb.close()

    answerdataframe = assess_LLM_personality(llm)
    # score personality traits based on the answers
    scoresList = score_personality(answerdataframe)
    print (scoresList)
    # write the answers to the answers log
    write_answers_to_excel(answerdataframe)
    # write the scores to the scores file
    write_scores_to_excel(scoresList)

if __name__ == '__main__':
    question_file = r'AIPersonality\Questionaire\IPIPBigFiveQuestionaire.xlsx'
    question_worksheet = 'NewIPIP'
    scores_file = r'AIPersonality\Results\IPIP_ScoresDB.xlsx'
    score_sheet = 'NewIPIP_ScoresDB'
    ans_worksheet = 'NewIPIP_AnswersLog'
    # get the system time in the format Weekday, Month Day, Year, Hour, Minute
    sys_time = datetime.datetime.now().strftime("%a, %b %d, %Y, %H:%M") 
    llm = ChatOpenAI(temperature=0.0, request_timeout=120)
    main(llm)
