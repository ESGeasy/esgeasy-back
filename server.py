from flask import Flask
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

df_predict_scores = pd.read_csv("data/Amostra_das_empresas.csv", sep=";")
df_companies = pd.read_csv("data/companies_all.csv")
df_esg = pd.read_csv("data/esg_scores_history_rated.csv")
df_esg["assessment_year"] = pd.to_datetime(df_esg["assessment_year"],format="%Y")
df_esg.fillna(0,inplace=True)
dims = ['Environmental Dimension', 'Governance & Economic Dimension',
       'S&P Global ESG Score', 'Social Dimension']

SECTORS = ['Oil, Gas and Consumable Fuels', 'Metals and Mining',
           'Road and Rail', 'Textiles, Apparel and Luxury Goods']
@app.route("/futureRanking/<string:sector>/<string:score>")
def getScores(sector,score):
    sectors = [sector]
    if score == None:
        score = "S&P Global ESG Score"
    if sector == "All":  
        sectors = SECTORS
        
    mask = df_predict_scores["industry"].isin(sectors)
    data = mask[["company_id", "company_name", score]].sort_values(
    return data.T.to_json()

@app.route("/ranking/<string:sector>/<string:score>")
def getCurrentScores(sector,score):
    sector = sector.replace("%20"," ")
    score = score.replace("%20"," ")
    sectors = [sector]
    if score == None:
        score = "S&P Global ESG Score"
    if sector == "All":  
        sectors = SECTORS

    mask = df_predict_scores[df_predict_scores["industry"].isin(sectors)]
    data = mask[["company_id", "company_name", score]].sort_values(
        by=[score], ascending=[False])
    return data.T.to_json()

## FUNCAO QUE DADO UM DATAFRAME FAZ A MEDIA PONDERADA
def singleSum(df):
    total = 0
    denom = 0
    for i,row in df.iterrows():
        w = row["score_weight"]
        if row["score_value"] != np.nan:
            total += row["score_value"]*w
        denom += w
    return total/denom

## FUNCAO QUE RETORNA UMA IMAGEM CODIFICADA EM BASE64, CONTENDO A EVOLUCAO DAS MÉTRICAS AO LONGO DO TEMPO 
def getHistory(id):
    series = []
    fig, ax = plt.subplots()
    for dim in dims:
        if dim == 'S&P Global ESG Score':
            type_ = "aspect"
        else:
            type_ = "parent_aspect"
        mask = (df_esg["company_id"] == id) & (df_esg[type_] == dim)
        s = df_esg[mask].groupby("assessment_year").apply(singleSum)
        s.plot(legend=True,ax=ax)
        # series.append({dim:s})
    ax.legend(dims)
    plt.title("ESG Scores")
    plt.ylabel("Score")
    plt.xlabel("Ano")
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read())
    return str(my_base64_jpgData)

@app.route("/companies/<int:id>")
def filterById(id):
    mask = df_companies["company_id"] == id
    data = df_companies[mask].T.to_json()
    history = getHistory(id)
    data_and_image = {}
    data_and_image["data"] = data
    data_and_image["image"] = history
    return data_and_image
