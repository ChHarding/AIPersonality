
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)

# upload the training data to OpenAI

datasets=['high_agreeableness_scores.json', 'high_conscientiousness_scores.json', 'high_emotionalStability_scores.json', 'high_extraversion_scores.json', 'high_intellect_scores.json', 'low_agreeableness_scores.json', 'low_conscientiousness_scores.json', 'low_emotionalStability_scores.json', 'low_extraversion_scores.json', 'low_intellect_scores.json']
Personality_models = {'High_AGR', 'High_CSN', 'High_EST', 'High_EXT', 'High_OPN', 'Low_AGR', 'Low_CSN', 'Low_EST', 'Low_EXT', 'Low_OPN'}
for dataset in datasets:
    with open (f'AIPersonality/Training_Records/{dataset}', 'rb') as f:
        response = openai.File.create(file=f, purpose='fine-tune')
        fileId = response['id']
        print('File id for ', dataset, ' is ', fileId)
    # create a fine tuning job for each dataset and name the model as per the dataset name
    model_name = dataset.replace('.json', '')
    # remove the word _scores
    model_name = model_name.replace('_scores', '')
    if(model_name.startswith('high')):
        model_name = model_name.replace('high_', 'High')
    else:
        model_name = model_name.replace('low_', 'Low')
    # replace agreeableness with AGR, conscientiousness with CSN, emotionalStability with EST, extraversion with EXT, intellect with OPN
    model_name = model_name.replace('agreeableness', 'AGR')
    model_name = model_name.replace('conscientiousness', 'CSN')
    model_name = model_name.replace('emotionalStability', 'EST')
    model_name = model_name.replace('extraversion', 'EXT')
    model_name = model_name.replace('intellect', 'OPN')
    model_name = model_name + 'v1'
    # remove trailing spaces
    model_name = model_name.strip()
    # replace any invalid characters with underscores
    model_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in model_name)
    print(model_name)
    response = openai.FineTuningJob.create(training_file=fileId, model='gpt-3.5-turbo', model_name=model_name)
    jobId = response['id']
    print(jobId)
    print('Training started for ', model_name)


