import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
import joblib
import math

def create_supervised(df, lag=1):
    columns = [df.shift(i) for i in range(1, lag + 1)]
    columns.append(df)
    df_supervised = pd.concat(columns, axis=1)
    df_supervised.fillna(0, inplace=True)
    return df_supervised

# model_path = r'E:\ALGROWBIZ\AlgrowBiz\linear_regression_model.pkl'
model_path = 'linear_regression_model.pkl'
# scaler_X_path = r'E:\ALGROWBIZ\AlgrowBiz\scaler_X.pkl'
scaler_X_path = 'scaler_X.pkl'
# scaler_y_path = r'E:\ALGROWBIZ\AlgrowBiz\scaler_y.pkl'
scaler_y_path = 'scaler_y.pkl'

lr_model = joblib.load(model_path)
scaler_X = joblib.load(scaler_X_path)
scaler_y = joblib.load(scaler_y_path)
# encoder = joblib.load(r'E:\ALGROWBIZ\AlgrowBiz\encoder.pkl')
encoder = joblib.load('encoder.pkl')

# train_data = pd.read_csv(r'E:\ALGROWBIZ\AlgrowBiz\test_data2.csv')
train_data = pd.read_csv('test_data2.csv')

# Convert 'date' column to datetime format specifying the correct format
train_data['date'] = pd.to_datetime(train_data['date'], format='mixed')

# One-hot encoding for categorical variables
encoded_cats = encoder.fit_transform(train_data[['state', 'item category', 'festival']])
encoded_cats_df = pd.DataFrame(encoded_cats, columns=encoder.get_feature_names_out(['state', 'item category', 'festival']))
train_data = pd.concat([train_data, encoded_cats_df], axis=1)

# Feature Engineering: Creating a supervised learning problem
train_data['sales_diff'] = train_data['sales'].diff()
train_data.dropna(inplace=True)  

train_data['month'] = train_data['date'].dt.month
train_data['year_diff'] = train_data['date'].dt.year - 2014
relevant_columns = ['sales_diff', 'month','year_diff'] + list(encoded_cats_df.columns)
supervised_data = create_supervised(train_data[relevant_columns], 12)

# Function to predict cumulative sales
def predict_sales(state, item_category, subcategory, num_months):
    if not (1 <= num_months <= 6):
        raise ValueError("Number of months must be between 1 and 6.")
    
    input_data = pd.DataFrame({
        'state': [state] * num_months,
        'item category': [item_category] * num_months,
        'subcategory': [subcategory] * num_months,
        'festival': ['No Festival'] * num_months,
        'date': pd.date_range(start=pd.to_datetime('today'), periods=num_months, freq='ME')    
        })
    
    encoded_input = encoder.transform(input_data[['state', 'item category', 'festival']])
    encoded_input_df = pd.DataFrame(encoded_input, columns=encoder.get_feature_names_out(['state', 'item category', 'festival']))
    input_data = pd.concat([input_data, encoded_input_df], axis=1)

    input_data['month'] = input_data['date'].dt.month
    input_data['year_diff'] = input_data['date'].dt.year - 2014
    
    input_data['sales_diff'] = 0
    input_supervised = create_supervised(input_data[relevant_columns], lag=12)

    
    X_input = input_supervised.iloc[:, 1:]
    X_input_scaled = scaler_X.transform(X_input)
    predictions_scaled = lr_model.predict(X_input_scaled)
    predictions = scaler_y.inverse_transform(predictions_scaled)

    cumulative_sales = predictions.sum()  

    return cumulative_sales  

# Function to predict cumulative sales
def prev_sales_predict(state, item_category, subcategory, num_months):
   
    start_date = pd.to_datetime('today') - pd.DateOffset(months=num_months)

    prev_data = pd.DataFrame({
        'state': [state] * num_months,
        'item category': [item_category] * num_months,
        'subcategory': [subcategory] * num_months,
        'festival': ['No Festival'] * num_months,
        'date': pd.date_range(
            end=pd.to_datetime('today'), periods=num_months, freq='MS'
        )  
    })

    encoded_input = encoder.transform(prev_data[['state', 'item category', 'festival']])
    encoded_input_df = pd.DataFrame(encoded_input, columns=encoder.get_feature_names_out(['state', 'item category', 'festival']))

    prev_data = pd.concat([prev_data, encoded_input_df], axis=1)
    prev_data['month'] = prev_data['date'].dt.month
    prev_data['year_diff'] = prev_data['date'].dt.year - 2014
    prev_data['sales_diff'] = 0  
    input_supervised = create_supervised(prev_data[relevant_columns], lag=12)
    
    X_input = input_supervised.iloc[:, 1:]
    X_input_scaled = scaler_X.transform(X_input)
    
    predictions_scaled = lr_model.predict(X_input_scaled)
    
    predictions = scaler_y.inverse_transform(predictions_scaled)
    cumulative_sales = predictions.sum()  

    return cumulative_sales  


def sales_prediction(state, item_category, subcategory, months,user_prev_sale):
    pred_sales = predict_sales(state, item_category, subcategory, months)
    prev_sales = prev_sales_predict(state, item_category, subcategory, months)

    mean_value = train_data.loc[(train_data['item category'] == item_category) & (train_data['state'] == state), 'sales'].mean()

    if not isinstance(mean_value, (int, float)) or math.isnan(mean_value):
        mean_value=45
    
    sales_diff=pred_sales-prev_sales
    
    change_percent=sales_diff/mean_value

    predicted=math.floor(user_prev_sale*(1+change_percent))

    return predicted


