import requests
import json
import time 
import pandas as pd
from datetime import datetime
from django.utils import timezone
from ResumenCommentsAPI.Logica.ResourcesFilesTransformerSpanish.Summarization import SummarizationPredict
from ResumenCommentsAPI.ClavesPrivadas.firebaseAdminConfig import CLOUD_DATABASE
import dateutil.parser as dateparser

def obtenerTipoComentario(comentario):
    url = "https://multilingual-sentiment-analysis2.p.rapidapi.com/sentiment/multilingual/1.0/classify"
    headers = {
            'content-type': 'application/json',
            'X-RapidAPI-Key': str('2376c0d36cmsha5bbc926e003defp162c2djsn5f53c06cce2c'),
            'X-RapidAPI-Host': 'multilingual-sentiment-analysis2.p.rapidapi.com',
          }
    data= {'text': comentario}
    output = requests.post(url, data=json.dumps(data), headers=headers).json()
    return output['label']

def guardarComentarioFirebase(comentario, correo, fecha, idPost):
    
    docs = CLOUD_DATABASE.collection(u'Comentario').where(u'idPost', u'==', idPost).stream()
    verificacion = next(docs, None)

    if(verificacion == None):
        tipoComentario = obtenerTipoComentario(comentario)
        ##Llamada directa metodos almacenamiento API
        resumen_Comentario = SummarizationPredict().predictSummarization(comentario)
        #Almacenamiento en la base de datos en la nube
        data = {"correo_comentario":correo,"comentario_completo": comentario, 
                "tipo_comentario":tipoComentario, "resumen_comentario":resumen_Comentario, 
                "fecha_comentario": dateparser.parse(fecha),
                "idPost": idPost,
                "RedSocial":"Facebook"
                }
        CLOUD_DATABASE.collection("Comentario").document(idPost).set(data)
        ##Esto debido a que la api de clasificacion realiza 3 consultas por minuto, en el plan sin costo 
        time.sleep(25)
        print("Archivo Guardado :) ")
    else:
        print("Comenatarios ya alamacenado: ", idPost)

def obtenerCometarios(df):
    for i in df.index:
        print("Guardando Archivo...")
        guardarComentarioFirebase(df['comentario_completo'][i], 'user@Facebook.com', df['fecha_comentario'][i], df['id_pagina_post'][i])
    return "Proceso Terminado...."
    
def main():
    df = pd.read_csv('ResumenCommentsAPI/Logica/DatasetComentarios/datasetPostFacebook.csv', sep=';')
    obtenerCometarios(df)
    return 'ok'