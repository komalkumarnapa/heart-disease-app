# -*- coding: utf-8 -*-
"""Untitled19.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16gwHL4JQ7-gdLjf3u6pgKwm0usYZID0C
"""

pip install streamlit

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import KNNImputer
import shap

# Load and preprocess dataset
def load_data():
    data = pd.read_csv('processed.cleveland.data', header=None, na_values='?')
    data.columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
        "exang", "oldpeak", "slope", "ca", "thal", "num"
    ]
    data['target'] = data['num'].apply(lambda x: 1 if x > 0 else 0)
    data.drop(columns='num', inplace=True)
    imputer = KNNImputer(n_neighbors=5)
    data_imputed = pd.DataFrame(imputer.fit_transform(data), columns=data.columns)
    return data_imputed

# Train model
def train_model(data):
    X = data.drop('target', axis=1)
    y = data['target']
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    return model

# SHAP explainer
def shap_explainer(model, X):
    explainer = shap.TreeExplainer(model)
    return explainer.shap_values(X)

# Streamlit GUI
st.title("Heart Disease Prediction with Explainable AI")

data = load_data()
model = train_model(data)

# User input form
st.sidebar.header('Enter Patient Details:')
user_input = {}
for column in data.drop('target', axis=1).columns:
    user_input[column] = st.sidebar.number_input(f"{column}", float(data[column].min()), float(data[column].max()), float(data[column].mean()))

# Predict button
if st.sidebar.button("Predict"):
    input_df = pd.DataFrame([user_input])
    prediction = model.predict(input_df)[0]
    prediction_proba = model.predict_proba(input_df)[0, 1]

    # SHAP explanation
    shap_values = shap_explainer(model, data.drop('target', axis=1))
    shap.initjs()
    st.subheader('Prediction Result')
    if prediction == 1:
        st.error(f"High risk of heart disease (Probability: {prediction_proba:.2f})")
    else:
        st.success(f"Low risk of heart disease (Probability: {prediction_proba:.2f})")

    st.subheader('Feature Influence')
    shap.force_plot(
        shap.TreeExplainer(model).expected_value[1],
        shap.TreeExplainer(model).shap_values(input_df)[1],
        input_df, matplotlib=True, show=False
    )
    st.pyplot(bbox_inches='tight')