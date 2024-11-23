import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
import joblib

def create_supervised(df, lag=1):
    columns = [df.shift(i) for i in range(1, lag + 1)]
    columns.append(df)
    df_supervised = pd.concat(columns, axis=1)
    df_supervised.fillna(0, inplace=True)
    return df_supervised

# Load the training dataset
train_data = pd.read_csv('sales_data2.csv')


train_data['date'] = pd.to_datetime(train_data['date'], format='mixed')
train_data['month'] = train_data['date'].dt.month
train_data['year_diff'] = train_data['date'].dt.year - 2014

# One-hot encoding for categorical variables
encoder = OneHotEncoder(sparse_output=False, drop='first')
encoded_cats = encoder.fit_transform(train_data[['state', 'item category', 'festival']])

# Create a DataFrame for the encoded categorical variables
encoded_cats_df = pd.DataFrame(encoded_cats, columns=encoder.get_feature_names_out(['state', 'item category', 'festival']))
train_data = pd.concat([train_data, encoded_cats_df], axis=1)


train_data['sales_diff'] = train_data['sales'].diff()
train_data.dropna(inplace=True)  
relevant_columns = ['sales_diff','month','year_diff'] + list(encoded_cats_df.columns)
supervised_data = create_supervised(train_data[relevant_columns], 12)

# Splitting data into features and target
X_train = supervised_data.iloc[:, 1:]
y_train = supervised_data.iloc[:, 0].values.reshape(-1, 1)

# Scaling features
scaler_X = MinMaxScaler(feature_range=(-1, 1))
scaler_y = MinMaxScaler(feature_range=(-1, 1))

# Check if the model and scalers are already saved
model_path = 'linear_regression_model.pkl'
scaler_X_path = 'scaler_X.pkl'
scaler_y_path = 'scaler_y.pkl'
encoder_path = 'encoder.pkl'

if os.path.exists(model_path) and os.path.exists(scaler_X_path) and os.path.exists(scaler_y_path) and os.path.exists(encoder_path):
    lr_model = joblib.load(model_path)
    scaler_X = joblib.load(scaler_X_path)
    scaler_y = joblib.load(scaler_y_path)
    
else:
    scaler_X.fit(X_train)
    scaler_y.fit(y_train)

    X_train_scaled = scaler_X.transform(X_train)
    y_train_scaled = scaler_y.transform(y_train)

    
    lr_model = LinearRegression()
    lr_model.fit(X_train_scaled, y_train_scaled)

    # Save the trained model and scalers
    joblib.dump(lr_model, model_path)
    joblib.dump(scaler_X, scaler_X_path)
    joblib.dump(scaler_y, scaler_y_path)
    joblib.dump(encoder, 'encoder_path')




