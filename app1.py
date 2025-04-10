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
    encontrados = []
    for clave, sinonimos in diccionario.items():
        for patron in sinonimos:
            if re.search(rf"\\b{patron.lower()}\\b", texto.lower()):
                encontrados.append(clave)
                break
    return list(set(encontrados))

def cumple_diagnostico_por_prefijo(diagnosticos_detectados, diagnosticos_regla):
    return any(d.lower().startswith(r.lower()) for d in diagnosticos_detectados for r in diagnosticos_regla)

def detectar_alertas(edad, sexo, diagnosticos_detectados, medicacion, reglas):
    alertas = []
    for regla in reglas:
        if regla.get("sexo") and sexo.lower() != regla["sexo"].lower():
            continue
        if "diagnosticos" in regla:
            if not cumple_diagnostico_por_prefijo(diagnosticos_detectados, regla["diagnosticos"]):
                continue
        if "palabras" in regla:
            if not any(re.search(rf"\\b{p}\b", medicacion.lower()) for p in regla["palabras"]):
                continue
        alertas.append(regla["mensaje"])
    return alertas

# ------------------ INTERFAZ ------------------
st.title("Conciliación de Medicación - STOPP/START")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, step=1)
sexo = st.radio("Sexo del paciente", ["masculino", "femenino"])
antecedentes = st.text_area("Antecedentes personales / Historia clínica")
medicacion = st.text_area("Tratamiento actual (una línea por fármaco)")

if st.button("Analizar"):
    diagnosticos_detectados = detectar_diagnosticos(antecedentes, diccionario_diagnosticos)

    st.info("Diagnósticos detectados en antecedentes:")
    for d in diagnosticos_detectados:
        st.markdown(f"- **{d}**")

    alertas = detectar_alertas(edad, sexo, diagnosticos_detectados, medicacion, reglas_stopp)

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")
