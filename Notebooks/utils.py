#!/usr/bin/env python3

"""  This file contains utility functions for data preprocessing and evaluation. """

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.metrics import ( r2_score,
                             explained_variance_score,
                             max_error,
                             mean_absolute_error,
                             mean_squared_error,
                             mean_squared_log_error,
                             median_absolute_error,
                             mean_poisson_deviance,
                             mean_gamma_deviance )


def show_heat_map(data):
  correlation_matrix = data.corr()
  #To mask out the upper triangle
  plt.figure(figsize=(20,10))
  mask = np.zeros_like(correlation_matrix, dtype=np.bool)
  mask[np.triu_indices_from(mask)] = True
  sns.heatmap(data.corr(), mask=mask, annot=True)

def clean_data(data):
  data.drop(['mta_tax','trip_type','improvement_surcharge'], axis=1, inplace=True)
  data['lpep_pickup_datetime'] = pd.to_datetime(data['lpep_pickup_datetime'])
  data['lpep_dropoff_datetime'] = pd.to_datetime(data['lpep_dropoff_datetime'])
  data['trip_duration'] = (data['lpep_dropoff_datetime'] - data['lpep_pickup_datetime']).dt.total_seconds().div(60)

  data = data[(data['trip_duration']>0) & (data['trip_duration']<(24*60))]
  data = data[(data['lpep_pickup_datetime'].dt.year >=2017) & (data['lpep_pickup_datetime'].dt.year <=2018)]
  return data

def create_features(data):
  data['hour_of_day'] = data['lpep_pickup_datetime'].dt.hour
  data['day_of_week'] = data['lpep_pickup_datetime'].dt.dayofweek
  data['month_of_year'] = data['lpep_pickup_datetime'].dt.month
  return data

def get_model_train_stats(Y_pred, Y_test, model_name, stats_df):
  stats_map = {}
  stats_str='\033[94m'+'-------------------------------------------------\n'
  stats_str+='       REPORT for '+model_name+'\n'
  stats_str+='-------------------------------------------------\n'
  metric_function_map={
      'Explained Variance':explained_variance_score,
      'Maximum Error':max_error,
      'Mean Absolute Error':mean_absolute_error,
      'Mean Squared Error':mean_squared_error,
      'Mean Squared Log Error':mean_squared_log_error,
      'Meadian Absolute Error':median_absolute_error,
      'R2 Value':r2_score,
      'Mean Poisson Deviance':mean_poisson_deviance,
      'Mean Gamma Deviance':mean_gamma_deviance
  }
  for metric_name in metric_function_map.keys():
    try:
      stats_map[metric_name] = metric_function_map[metric_name](Y_test,Y_pred)
      stats_str+=metric_name+" : "+str(metric_function_map[metric_name](Y_test,Y_pred))+"\n"
    except Exception:
      stats_map[metric_name] = 'N/A'
  stats_str+='-------------------------------------------------\n'
  stats_df.loc[model_name]=stats_map
  return stats_str, stats_df


def get_train_test_split(split_ratio):
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split_ratio, random_state=42)
