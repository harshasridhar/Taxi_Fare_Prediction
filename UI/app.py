import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import explained_variance_score,max_error,mean_absolute_error,mean_squared_error,mean_squared_log_error,median_absolute_error,mean_poisson_deviance,mean_gamma_deviance
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from pandas.plotting import autocorrelation_plot
from statsmodels.graphics.tsaplots import plot_acf
from sklearn.neural_network import MLPRegressor
from flask import Flask, flash, redirect, request, jsonify, make_response, Response
import json
import requests
import urllib.parse
from datetime import datetime
from flask_cors import CORS, cross_origin
import pickle
model=pickle.load(open('models/ensemble.model','rb'))
dt=pickle.load(open('models/dt_regressor.model','rb'))
from enum import IntEnum
from dotenv import dotenv_values
config = dotenv_values(".env")
class HttpStatus(IntEnum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    OK = 200
from flask import Blueprint
history=pd.DataFrame(columns=['trip_duration','trip_distance','hour_of_day','day_of_week','fare_amount','timestamp','request_timestamp'])
api_key=config['API_KEY']
app=Flask(__name__)
app.config['SECRET_KEY'] = config['SECRET_KEY']
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# model=pickle.load(open('~/Downloads/ensemble.model','rb'))
@app.route("/info", methods=['GET'])
def server_info():
    return jsonify({'name': 'Test APIs', 'title': 'Mock APIs', 'description': 'description of your API', 'termsOfService': '', 'contact': None, 'license': None, 'version': 'v1'}), int(HttpStatus.OK)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

@app.route("/geocode",methods=["GET","OPTIONS"])
def geocode():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response
    reverse = request.args.get('reverse')
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    url = 'https://graphhopper.com/api/1/geocode?key={}&reverse=true&point={},{}'.format(api_key, lat,lng)
    response_data = requests.get(url=url)
    response_data=response_data.json()
    return jsonify(response_data['hits'][-1])

@app.route("/compute",methods=["POST","OPTIONS"])
def compute_price():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    actualBody = json.loads(request.data)
    print(actualBody)
    url='https://graphhopper.com/api/1/route?locale=en&point='+actualBody['from'].replace(' ','')+'&point='+actualBody['to'].replace(' ','') \
     + '&vehicle=car&cal_points=false&key='+api_key
    response_data = requests.get(url=url).json()
    details = response_data['paths'][0]
    date_time_obj = datetime.strptime(actualBody['time'], '%Y/%m/%d %H:%M')
    print(date_time_obj)
    print(date_time_obj.hour)
    print("Trip Distance : ",details['distance'])
    print("Trip Time     :",details['time'])
    print("Day of Week   :",date_time_obj.weekday())
    print('Hour of Day   :',date_time_obj.hour)
    print
    history.loc[len(history.index)] = {'trip_distance':float(details['distance'])*0.0006213712,'trip_duration':float(details['time'])/60000.0, 'hour_of_day':date_time_obj.hour, 'day_of_week':date_time_obj.weekday(),'request_timestamp':datetime.now(),'timestamp':date_time_obj}
    last_record=history.tail(1)
    print(last_record[['trip_duration','trip_distance','hour_of_day','day_of_week']])
    Y_pred = model.predict(history.tail(1)[['trip_duration','trip_distance','hour_of_day','day_of_week']])
    print(Y_pred)
    history.at[len(history.index)-1, 'fare_amount']=Y_pred[0]
    print(Y_pred)
    return jsonify({'prediction':Y_pred[0]})
    # return jsonify({'distance': route_json['paths'][0]['distance'], 'time':float(route_json['paths'][0]['time']/ (1.0*60000))})

@app.route("/geojson",methods=['GET','OPTIONS'])
def get_geojson():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    text_data = open('zones.geojson').read()
    return Response(text_data, mimetype="application/json")

@app.route("/density",methods=["GET","OPTIONS"])
def get_density():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    pred_data=pd.DataFrame(columns=['PULocationID','day_of_week','hour_of_day','Count'])
    pred_data['PULocationID'] = list(range(1,266))
    pred_data['day_of_week']=list([5]*len(pred_data.index))
    pred_data['hour_of_day']=list([19]*len(pred_data.index))
    pred_data['Count']=dt.predict(pred_data[['PULocationID','day_of_week','hour_of_day']])
    pred_data.dropna()
    pred_data.set_index('PULocationID',inplace=True)
    return make_response(pred_data['Count'].to_json())

@app.route("/history",methods=['GET'])
def get_history():
    return jsonify(history.to_dict('dict'))

if __name__ == '__main__':
    app.run(host="localhost", port=int("8081"),debug=True)