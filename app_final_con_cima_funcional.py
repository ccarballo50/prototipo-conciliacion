import streamlit as st
import json
import re
import requests

# ---------------------- CONFIGURACIÓN ----------------------
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")
st.title("Conciliación de Medicación - Herramienta Integral")

# ---------------------- CARGA DE DATOS ----------------------
@st.cache_data

def cargar_diccionario(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

reglas_stopp = cargar_diccionario("reglas_stopp.json")
diccionario_diagnosticos = cargar_diccionario("diccionario_diagnosticos.json")
diccionario_medicamentos = cargar_diccionario("diccionario_medicamentos.json")

# ---------------------- FUNCIONES ----------------------
def limpiar_texto(texto):
    return re.sub(r"[\W_]+", " ", texto.lower()).strip()

def detectar_patrones(texto, diccionario):
    encontrados = []
    texto_limpio = limpiar_texto(texto)
    for categoria, sinonimos in diccionario.items():
        for patron in sinonimos:
            if patron.lower() in texto_limpio:
                encontrados.append(categoria.lower())
                break
    return list(set(encontrados))

def limpiar_nombre_medicamento(nombre):
    return re.sub(r"\s\d+.*", "", nombre).strip().lower()

def buscar_medicamento_cima(nombre):
    url = f"https://cima.aemps.es/cima/rest/medicamentos?nombre={nombre}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and data.get("resultados"):
            return data["resultados"]
    return []

# ---------------------- INTERFAZ ----------------------
modo = st.radio("Selecciona una funcionalidad:", ["Análisis STOPP", "Consulta en CIMA"])

# ---------------------- ANÁLISIS STOPP ----------------------
if modo == "Análisis STOPP":
    edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=75)
    antecedentes = st.text_area("Antecedentes personales / Historia clínica")
    tratamiento = st.text_area("Tratamiento actual (una línea por fármaco):")

    if st.button("Analizar"):
        diagnosticos_detectados = detectar_patrones(antecedentes, diccionario_diagnosticos)
        medicamentos_detectados = detectar_patrones(tratamiento, diccionario_medicamentos)

        alertas = []
        for regla in reglas_stopp:
            if any(d.lower() in diagnosticos_detectados for d in regla["diagnosticos"]) and \
               any(m.lower() in medicamentos_detectados for m in regla["medicamentos"]):
                alertas.append(regla["descripcion"])

        st.subheader("Alertas STOPP detectadas:")
        if alertas:
            for alerta in alertas:
                st.warning(f"- {alerta}")
        else:
            st.success("No se han detectado alertas con los datos introducidos.")

        st.subheader("Diagnósticos detectados:")
        if diagnosticos_detectados:
            for d in sorted(set(diagnosticos_detectados)):
                st.markdown(f"- {d}")
        else:
            st.write("No se han detectado diagnósticos reconocidos.")

        st.subheader("Medicamentos detectados:")
        if medicamentos_detectados:
            for m in sorted(set(medicamentos_detectados)):
                st.markdown(f"- {m}")
        else:
            st.write("No se han detectado medicamentos reconocidos.")

# ---------------------- CONSULTA EN CIMA ----------------------
if modo == "Consulta en CIMA":
    med_input = st.text_input("Introduce el nombre del medicamento para consultar (ej: ibuprofeno)", "")
    if st.button("Buscar medicamento en CIMA"):
        med_limpio = limpiar_nombre_medicamento(med_input)
        resultados = buscar_medicamento_cima(med_limpio)

        if resultados:
            st.success(f"Se han encontrado {len(resultados)} resultados para '{med_limpio}':")
            for med in resultados:
                nombre = med.get("nombre")
                codigo = med.get("nregistro")
                url = f"https://cima.aemps.es/cima/pdfs/{codigo}/prospecto.pdf"
                st.markdown(f"- [{nombre}]({url})")
        else:
            st.warning("No se ha encontrado el medicamento en CIMA.")
