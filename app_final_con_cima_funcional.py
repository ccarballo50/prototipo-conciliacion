import streamlit as st
import json
import re
import requests

# ------------------- Cargar reglas y diccionarios -------------------
with open("reglas_stopp.json", "r", encoding="utf-8") as f:
    reglas_stopp = json.load(f)

with open("diccionario_diagnosticos.json", "r", encoding="utf-8") as f:
    diccionario_diagnosticos = json.load(f)

with open("diccionario_medicamentos.json", "r", encoding="utf-8") as f:
    diccionario_medicamentos = json.load(f)

# ------------------- Funciones auxiliares -------------------
def detectar_patrones(texto, diccionario):
    encontrados = []
    for categoria, sinonimos in diccionario.items():
        for patron in sinonimos:
            if re.search(rf"\\b{re.escape(patron.lower())}\\b", texto.lower()):
                encontrados.append(categoria.lower())
                break
    return list(set(encontrados))

# ------------------- Interfaz -------------------
st.title("Conciliación de Medicación - Herramienta Integral")

pestaña = st.sidebar.radio("Selecciona una funcionalidad:", ["Análisis STOPP", "Consulta en CIMA"])

# ------------------- Pestaña 1: Análisis STOPP -------------------
if pestaña == "Análisis STOPP":
    edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=75)
    antecedentes = st.text_area("Antecedentes personales / Historia clínica")
    tratamiento = st.text_area("Tratamiento actual (una línea por fármaco):")

    if st.button("Analizar"):
        diagnosticos_detectados = detectar_patrones(antecedentes, diccionario_diagnosticos)
        medicamentos_detectados = detectar_patrones(tratamiento, diccionario_medicamentos)

        alertas = []
        for regla in reglas_stopp:
            if any(d.lower() in diagnosticos_detectados for d in regla.get("diagnosticos", [])) and \
               any(m.lower() in medicamentos_detectados for m in regla.get("medicamentos", [])):
                alertas.append(regla["descripcion"])

        st.subheader("Alertas STOPP detectadas:")
        if alertas:
            st.warning("Se han detectado las siguientes alertas:")
            for alerta in alertas:
                st.markdown(f"- {alerta}")
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

# ------------------- Pestaña 2: Consulta en CIMA -------------------
elige = st.session_state.get("med") if "med" in st.session_state else ""

if pestaña == "Consulta en CIMA":
    medicamento = st.text_input("Introduce el nombre del medicamento para consultar (ej: ibuprofeno)", value=elige)
    if st.button("Buscar medicamento en CIMA"):
        url = f"https://cima.aemps.es/cima/rest/medicamentos?nombre={medicamento}"
        try:
            response = requests.get(url)
            data = response.json().get("resultados", [])
            if data:
                med = data[0]
                st.session_state.med = medicamento
                st.markdown(f"**Nombre comercial:** {med.get('nombre', 'No disponible')}")
                st.markdown(f"**Laboratorio:** {med.get('labtitular', 'No disponible')}")
                st.markdown(f"**Principio activo:** {med.get('composicion', 'No disponible')}")
            else:
                st.warning("No se ha encontrado el medicamento en CIMA.")
        except Exception as e:
            st.error(f"Error al consultar la API de CIMA: {e}")
