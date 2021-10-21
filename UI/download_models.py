import gdown

base_url = 'https://drive.google.com/uc?id='
models={'dt':'1-juMcTNWlFSU5YcH5b8zMdaZZC4HwEmE','ensemble':'1-iv9S-nHz9GeTX1w1gIHlpwiEh2AhSPX','knn':'1-b6NxIHkRq84pTcRsOUi9n615bAgFrQJ','demand_pred_dt':'1AYMqfGTZKZaXAwOT7rCHIjgwja3Yr9TW'}
for model in models.keys():
    gdown.download(base_url+models[model],'models/'+model+'.model',quiet=False)