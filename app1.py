import json
import re
import streamlit as st

# ------------------ CONFIGURACIÓN PÁGINA ------------------
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ------------------ CARGA DE REGLAS STOPP ------------------
@st.cache_data
def cargar_reglas_stopp(path="reglas_stopp.json"):
    with open(path, encoding="utf-8") as file:
        return json.load(file)

reglas_stopp = cargar_reglas_stopp()

# ------------------ CARGA DE DICCIONARIO CIE10 ------------------
@st.cache_data
def cargar_diccionario_cie10(ruta_json="diccionario_diagnosticos_cie10_completo.json"):
    with open(ruta_json, "r", encoding="utf-8") as f:
        return json.load(f)

diccionario_cie10 = cargar_diccionario_cie10()

# ------------------ DETECTOR DE DIAGNÓSTICOS ------------------
def detectar_diagnosticos(texto, diccionario):
    codigos_detectados = []
    for patron, codigo in diccionario.items():
        try:
            if re.search(rf"\b{patron.lower()}\b", texto.lower()):
                codigos_detectados.append(codigo)
        except:
            continue
    return list(set(codigos_detectados))

# ------------------ DETECTOR DE ALERTAS ------------------
def detectar_alertas(edad, cie10_detectados, tratamiento, reglas):
    alertas = []
    for regla in reglas:
        palabras = regla.get("palabras_clave", [])
        condiciones = regla.get("condiciones", {})
        mensaje = regla["mensaje"]

        if condiciones.get("edad_min") and edad < condiciones["edad_min"]:
            continue
        if condiciones.get("requiere_diagnostico_cie10"):
            if not any(d in cie10_detectados for d in condiciones["requiere_diagnostico_cie10"]):
                continue
        if any(palabra in tratamiento.lower() for palabra in palabras):
            alertas.append(mensaje)

    return alertas
