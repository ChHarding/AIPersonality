# Credit : https://ipip.ori.org/New_IPIP-50-item-scale.htm
import openai
openai.api_key = "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"
model_engine = "text-davinci-003"  
prompt="Egypt?"
completion = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=1024,n=1,stop=None, temperature=0.5)
response = completion.choices[0].text
print(response)



