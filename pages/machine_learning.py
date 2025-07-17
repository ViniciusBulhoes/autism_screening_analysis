import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

st.title("Aplicação do modelo Random Forest")

dt = pd.read_csv("https://raw.githubusercontent.com/ViniciusBulhoes/autism_screening_analysis/refs/heads/main/data_set/autism_screening.csv")
dt = dt.dropna()
dt.drop(['age_desc', 'used_app_before', 'relation', "contry_of_res", "ethnicity"], axis=1, inplace=True)
dt.rename(columns={'jundice': 'jaundice', 'austim': 'autism'}, inplace=True)
age = dt[dt["age"]==383].index
dt.drop(age, inplace=True)

dt.reset_index(inplace=True)
dt.replace('no', 0, inplace=True)
dt.replace('yes', 1, inplace=True)
dt.replace('NO', 0, inplace=True)
dt.replace('YES', 1, inplace=True)

dt.rename(columns={'gender':'sexo_M'})
dt.replace('m', 1, inplace=True)
dt.replace('f', 0, inplace=True)

X = dt.drop("autism", axis=1)
X = X.drop(columns=['index', 'result'])
y = dt["autism"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=500, class_weight='balanced', random_state=64)
model.fit(X_train, y_train)

probs = model.predict_proba(X_test)[:, 1]
threshold = 0.3
y_pred = (probs >= threshold).astype(int)

st.text(classification_report(y_test, y_pred))

st.title("Importância de cada parâmetro")
importances = pd.Series(model.feature_importances_, index=X.columns)

fig_param, ax_param = plt.subplots(figsize=(8,6))
importances.nlargest(16).plot(kind='barh', ax=ax_param)
ax_param.set_title("Importância das variáveis no Random Forest")

st.pyplot(fig_param)

st.title("Matriz de confusão")

cm = confusion_matrix(y_test, y_pred)  # usa o y_pred com threshold 0.3
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap=plt.cm.Blues)
plt.title("Matriz de Confusão com threshold 0.3")
st.pyplot(plt.gcf())