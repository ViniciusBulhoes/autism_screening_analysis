import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Exemplo 1: Elementos Básicos do Streamlit", page_icon=":computer:")

st.title('Teste de triagem de autismo em adultos')

@st.cache_data
def carregar_dados():
    df = pd.read_csv('https://raw.githubusercontent.com/ViniciusBulhoes/autism_screening_analysis/refs/heads/main/data_set/autism_screening.csv')
    df = df.dropna()
    df.drop(['age_desc', 'used_app_before', 'relation'], axis=1, inplace=True)
    df.rename(columns={'jundice': 'jaundice', 'austim': 'autism'}, inplace=True)
    df['autism'].replace('no', 'doesnt have ASD', inplace=True)
    df['autism'].replace('yes', 'has ASD', inplace=True)
    df['gender'].replace('m', 'male', inplace=True)
    df['gender'].replace('f', 'female', inplace=True)
    df['jaundice'].replace('no', 'negative jaundice', inplace=True)
    df['jaundice'].replace('yes', 'positive jaundice', inplace=True)

    age = df[df["age"]==383].index
    df.drop(age, inplace=True)

    return df

df_autism = carregar_dados()

st.sidebar.header("Filtros para o gráfico das questões")

q_cols = st.sidebar.multiselect("Quais questões mostrar:", ['A1_Score', 'A2_Score', 'A3_Score', 'A4_Score', 'A5_Score', 'A6_Score', 'A7_Score', 'A8_Score', 'A9_Score', 'A10_Score'], default = ['A1_Score', 'A2_Score', 'A3_Score', 'A4_Score', 'A5_Score', 'A6_Score', 'A7_Score', 'A8_Score', 'A9_Score', 'A10_Score'])

st.header("Composição de indivíduos por gênero, diagnóstico de autismo e histórico de icterícia")

fig_sunb = px.sunburst(df_autism, path=['autism', 'jaundice', 'gender'])

st.plotly_chart(fig_sunb, use_container_width=True)

st.header("Distribuição das pontuações de cada questão")

sex_but = st.sidebar.toggle("Sexo")
if sex_but:
    st.sidebar.write("Males")
    sex = "male"
else:
    st.sidebar.write("Female")
    sex = "female"

aut_but = st.sidebar.toggle("Autism")
if aut_but:
    st.sidebar.write("Diagnosed")
    aut = "has ASD"
else:
    st.sidebar.write("Not diagnosed")
    aut = "doesnt have ASD"

jaun_but = st.sidebar.toggle("Jaundice")
if jaun_but:
    st.sidebar.write("Positive")
    jaun = "positive jaundice"
else:
    st.sidebar.write("Negative")
    jaun = "negative jaundice"

df_hist_s = df_autism[df_autism["gender"] == sex].copy()
df_hist_a = df_hist_s[df_hist_s["autism"] == aut].copy()
df_hist = df_hist_a[df_hist_a["jaundice"] == jaun].copy()

todos_but = st.sidebar.toggle("Sem filtros")

if todos_but:
    q_count_hist = (df_autism[q_cols]).sum()
else:
    q_count_hist = (df_hist[q_cols]).sum()

question_stats_ndiag = q_count_hist.reset_index()
question_stats_ndiag.columns = ['Questão', 'Respostas positivas']

fig_hist = px.bar(question_stats_ndiag, x="Questão", y="Respostas positivas")

st.plotly_chart(fig_hist, use_container_width=True)

opt = st.selectbox("Selecione o critério de filtragem", ("Idade", "Etnia"))

if opt == "Idade":
    age_sel = st.select_slider("Selecione a idade mínima", options = list(range(df_autism["age"].min().astype(int), df_autism['age'].max().astype(int)+1)))

    df_age = df_autism.copy()

    df_age = df_age[df_age["age"] >= age_sel]

    df_age["autism"].replace("has ASD", 1, inplace=True)
    df_age["autism"].replace("doesnt have ASD", 0, inplace=True)
    df_age["Class/ASD"].replace("YES", 1, inplace=True)
    df_age["Class/ASD"].replace("NO", 0, inplace=True)

    count_diag_pos = df_age["autism"].sum()
    count_diag_neg = (df_age["autism"] == 0).sum()
    count_class_pos = df_age["Class/ASD"].sum()
    count_class_neg = (df_age["Class/ASD"] == 0).sum()

    count_data = {"Categoria": ["Com diagnóstico", "Sem diagnóstico", "Classificação provável", "Classificação não provável"],
                  "Contagem": [count_diag_pos, count_class_neg, count_class_pos, count_class_neg]}
    count_age_df = pd.DataFrame(count_data)

    age_fig = px.bar(count_age_df, x="Categoria", y="Contagem")
    st.plotly_chart(age_fig, use_container_width=True)

else:
    df_et = df_autism.copy()

    df_et["autism"].replace("has ASD", 1, inplace=True)
    df_et["autism"].replace("doesnt have ASD", 0, inplace=True)
    df_et["Class/ASD"].replace("YES", 1, inplace=True)
    df_et["Class/ASD"].replace("NO", 0, inplace=True)

    count_rows = []
    for etnia, group in df_et.groupby("ethnicity"):
        count_rows.append({"etnia": etnia, "Categoria": "Com diagnóstico", "Contagem": group["autism"].sum()})
        count_rows.append({"etnia": etnia, "Categoria": "Sem diagnóstico", "Contagem": (group["autism"] == 0).sum()})
        count_rows.append({"etnia": etnia, "Categoria": "Classificação provável", "Contagem": group["Class/ASD"].sum()})
        count_rows.append({"etnia": etnia, "Categoria": "Classificação não provável", "Contagem": (group["Class/ASD"] == 0).sum()})

    count_et_df = pd.DataFrame(count_rows)

    et_fig = px.bar(count_et_df, x="Categoria", y="Contagem", color="etnia", barmode="group")
    st.plotly_chart(et_fig, use_container_widtg=True)