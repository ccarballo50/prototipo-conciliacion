import streamlit as st
import json
import re

# ------------------ CONFIGURACIÓN PÁGINA ------------------
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ------------------ CARGA DE ARCHIVOS ------------------
@st.cache_data
def cargar_reglas_stopp(path="reglas_stopp.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def cargar_diccionario_diagnosticos(path="diccionario_diagnosticos.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

reglas_stopp = cargar_reglas_stopp()
diccionario_diagnosticos = cargar_diccionario_diagnosticos()

# ------------------ FUNCIONES ------------------
def detectar_diagnosticos(texto, diccionario):
    encontrados = set()
    texto = texto.lower()
    for clave, sinonimos in diccionario.items():
        for s in sinonimos:
            if re.search(rf"\b{s.lower()}\b", texto):
                encontrados.add(clave)
                break
    return list(encontrados)

    st.success("No se han detectado alertas con los datos introducidos.")
