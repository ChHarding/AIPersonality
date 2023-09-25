# Credit : https://ipip.ori.org/New_IPIP-50-item-scale.htm
import openai
import pandas as pd
openai.api_key = "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"
#openai.api_key = "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"
model_engine = "text-davinci-003"  



# read excel in to a dataframe
import pandas as pd

df = pd.read_excel(r'C:\Users\vasanthv\Downloads\TedoneItemAssignmentTable30APR21.xlsx', sheet_name='data_nodupes')
prompt_list = []

def retrieve_row_data(df, index):
    qNo = df.loc[index, 'Number'] # get the title from the data frame
    instrument = df.loc[index, 'instrument'] # get the year from the data frame
    alpha = df.loc[index, 'alpha'] # get the author from the data frame
    key = df.loc[index, 'key'] # get the summary from the data frame
    question = df.loc[index, 'text'] # get the summary from the data frame
    label = df.loc[index, 'label'] # get the summary from the data frame
    list = [qNo, instrument, alpha, key, question, label]
    return list

#Store column names in a list
column_names = df.columns.tolist()
#row_count = len(df.index)
row_count = 5
# iterate through the rows of the dataframe and print values in column question
for i in range(row_count):
    row_data = retrieve_row_data(df, i)
    prompt_list = prompt_list + [row_data[4]]
#print(prompt_list)

def constructPrompt (df) : 
    prompt = f"I will say {row_count} things about you and you must sys_ans_text agree or disagree for all of them Sort your sys_ans_text in the same order as the question Here are the questions I am a person who\n"
    for i in range(row_count):
        row_data = retrieve_row_data(df, i)
        prompt = prompt + str(row_data[4]) + "\n"
    return prompt
prompt = constructPrompt(df)
print(prompt)
#completion = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=1024,n=1,stop=None, listerature=0.5)
#response = completion.choices[0].text
#response_list = response.split("\n")
# find the number of sentences in a text
list_ans = []
sys_ans_text = "Disagree, Agree, Disagree, Disagree, Disagree"
def count_sentences(text):
    count = 0
    list_ans = []
    for i in range(len(text)):
        if text[i] == ',':
            count += 1
            list_ans = list_ans + [text[i]]
    return count+1, list_ans

sys_ans_texts_count, list_ans = count_sentences(sys_ans_text)

for i in range(sys_ans_texts_count):
    print(f"Question {prompt_list[i]} sys_ans_text : {list_ans[i]}")
