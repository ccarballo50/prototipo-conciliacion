import streamlit as st
import json
import re

# ------------- CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ------------- CARGA DE REGLAS ----------------
@st.cache_data
def cargar_reglas_stopp(path="reglas_stopp.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

try:
    reglas_stopp = cargar_reglas_stopp()
except Exception as e:
    st.error(f"Error cargando reglas STOPP: {e}")
    reglas_stopp = []

# ------------- INTERFAZ ----------------
st.title("Conciliación de Medicación")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=75)
antecedentes = st.text_area("Antecedentes personales / Historia clínica")
medicacion = st.text_area("Tratamiento actual (una línea por fármaco)")

if st.button("Analizar"):
    alertas = []

    for regla in reglas_stopp:
        palabras = regla.get("palabras_clave", [])
        condiciones = regla.get("condiciones", {})
        mensaje = regla.get("mensaje", "")

        if condiciones.get("edad_min") and edad < condiciones["edad_min"]:
            continue
        if any(p.lower() in medicacion.lower() for p in palabras):
            alertas.append(mensaje)

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

