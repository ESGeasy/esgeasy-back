"""
Backend do projeto que retorna um json com os dados requisitados
conforme a rota selecionada e parâmetros passados
"""

import io
import base64
from flask import Flask
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
def get_scores(sector,score):
    """
    Funcao que retorna um json no formato {"company_id":, "company_name":, "score":}
    contendo o id da empresa, nome e score com base na previsão das métricas ESG
    --------------------------------------------------------------------------------
    Parameters:
    sector: O setor da indústria que se deseja obter o rankeamento
    score: O tipo de métrica que se deseja analisar. Pode ser um dos componentes do ESG
    ou um agregado das 3
    """
    sectors = [sector]
    if score is None:
        score = "S&P Global ESG Score"
    if sector == "All":
        sectors = SECTORS
    mask = df_predict_scores[df_predict_scores["industry"].isin(sectors)]
    data = mask[["company_id", "company_name", score]]\
                .sort_values(by=[score], ascending=[False])\
                .rename(columns={score:'score'})
    return data.T.to_json()

@app.route("/ranking/<string:sector>/<string:score>")
def get_current_scores(sector,score):
    """
    Funcao que retorna um json no formato {"company_id":, "company_name":, "score":}
    contendo o id da empresa, nome e score com base no último resultado das métricas ESG
    --------------------------------------------------------------------------------
    Parameters:
    sector: O setor da indústria que se deseja obter o rankeamento
    score: O tipo de métrica que se deseja analisar. Pode ser um dos componentes do ESG
    ou um agregado das 3
    """
    sector = sector.replace("%20"," ")
    score = score.replace("%20"," ")
    sectors = [sector]
    if score is None:
        score = "S&P Global ESG Score"
    if sector == "All":
        sectors = SECTORS
    type_ = ""
    if score == 'S&P Global ESG Score':
        type_ = "aspect"
    else:
        type_ = "parent_aspect"

    mask = df_predict_scores[df_predict_scores["industry"].isin(sectors)]
    ids = mask["company_id"].unique()
    last_year = df_esg["assessment_year"].max()
    esg_mask = (df_esg["company_id"].isin(ids)) & \
                (df_esg["assessment_year"] == last_year) & \
                (df_esg[type_] == score)
    s = df_esg[esg_mask].groupby("company_id").apply(single_sum)
    data = mask[["company_id", "company_name"]]\
                .merge(s.to_frame(name=score),left_on="company_id",right_index=True)\
                .sort_values(by=[score], ascending=[False])\
                .rename(columns={score:'score'})
    return data.T.to_json()

def single_sum(df):
    """
    Funcao que dado um dataframe retorna a media ponderada de uma métrica ESG
    -------------------------------------------------------------------------
    Parameters:
    df: dataframe a ser computado a media, contendo apenas os score_values de um
    dos aspectos do ESG
    """
    total = 0
    denom = 0
    for _,row in df.iterrows():
        w = row["score_weight"]
        if row["score_value"] != np.nan:
            total += row["score_value"]*w
        denom += w
    return total/denom

def get_history(company_id):
    """
    Funcao que retorna uma imagem em base64 contendo o histórico das métricas ESG
    ao longo dos anos
    -------------------------------------------------------------------
    Parameter:
    company_id: id da compania que deseja o histórico
    """
    _, ax = plt.subplots()
    for dim in dims:
        if dim == 'S&P Global ESG Score':
            type_ = "aspect"
        else:
            type_ = "parent_aspect"
        mask = (df_esg["company_id"] == company_id) & (df_esg[type_] == dim)
        s = df_esg[mask].groupby("assessment_year").apply(single_sum)
        s.plot(legend=True,ax=ax)
    ax.legend(dims)
    plt.title("ESG Scores")
    plt.ylabel("Score")
    plt.xlabel("Ano")
    my_string_IO_bytes = io.BytesIO()
    plt.savefig(my_string_IO_bytes, format='jpg')
    my_string_IO_bytes.seek(0)
    my_base64_jpg_data = base64.b64encode(my_string_IO_bytes.read())
    return str(my_base64_jpg_data)

@app.route("/companies/<int:company_id>")
def filter_by_id(company_id):
    """
    Funcao que retorna uma gráfico com a evolução das métricas ESG
    da empresa e dados relacionados a ela, como o nome, região, país etc.
    ----------------------------------------------------------------------
    Parameter:
    company_id: id da compania que deseja o histórico
    """
    mask = df_companies["company_id"] == company_id
    data = df_companies[mask].T.to_json()
    history = get_history(company_id)
    data_and_image = {}
    data_and_image["data"] = data
    data_and_image["image"] = history
    return data_and_image

if __name__ == '__main__':
    app.run(host='0.0.0.0')