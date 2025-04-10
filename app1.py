import streamlit as st
import json
import datetime
from fpdf import FPDF
from io import BytesIO

# ---------------- CONFIGURACION ----------------
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ---------------- CARGA DE ARCHIVOS ----------------
@st.cache_data
def cargar_reglas_stopp():
    with open("reglas_stopp.json", "r", encoding="utf-8") as file:
        return json.load(file)

@st.cache_data
def cargar_diccionario_cie10():
    with open("diccionario_diagnosticos_cie10_completo.json", "r", encoding="utf-8") as f:
        return json.load(f)

reglas_stopp = cargar_reglas_stopp()
diccionario_cie10 = cargar_diccionario_cie10()

# ---------------- INTERFAZ PRINCIPAL ----------------
st.title("Conciliación de Medicación en Urgencias (Prototipo)")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=85)
fc = st.number_input("Frecuencia cardiaca (lpm)", min_value=30, max_value=200, value=100)
crea = st.text_input("Creatinina (mg/dL)", value="1.2")
ant = st.text_area("Antecedentes personales / Historia clínica")
input_meds = st.text_area("Tratamiento actual (una línea por fármaco):")

if st.button("Analizar"):
    meds = [line.strip() for line in input_meds.split("\n") if line.strip()]
    cie10_detectados = []
    for clave, codigos in diccionario_cie10.items():
        if clave.lower() in ant.lower():
            cie10_detectados.extend(codigos)
    cie10_detectados = sorted(set(cie10_detectados))

    alertas = []
    for regla in reglas_stopp:
        if "palabras" not in regla or "mensaje" not in regla:
            continue
        palabras = regla["palabras"]
        cie10 = regla.get("cie10", [])
        if any(p.lower() in input_meds.lower() for p in palabras):
            if not cie10 or any(c in cie10_detectados for c in cie10):
                alertas.append(regla["mensaje"])

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    st.info("Diagnósticos detectados: " + ", ".join(cie10_detectados))

