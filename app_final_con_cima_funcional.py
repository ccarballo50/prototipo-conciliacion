
import streamlit as st
import json
import re
import requests

# Cargar reglas STOPP
with open("reglas_stopp.json", "r", encoding="utf-8") as f:
    reglas_stopp = json.load(f)

# Cargar diccionarios auxiliares
with open("diccionario_diagnosticos.json", "r", encoding="utf-8") as f:
    diccionario_diagnosticos = json.load(f)

with open("diccionario_diagnosticos_cie10_completo.json", "r", encoding="utf-8") as f:
    diccionario_cie10 = json.load(f)

# -------------------------------
def detectar_patrones(texto, diccionario):
    encontrados = []
    texto = texto.lower()
    for categoria, sinonimos in diccionario.items():
        for patron in sinonimos:
            if re.search(rf"\\b{re.escape(patron.lower())}\\b", texto):
                encontrados.append(categoria.lower())
                break
    return list(set(encontrados))

# -------------------------------
def normalizar_lista(texto):
    return [x.strip().lower() for x in texto.splitlines() if x.strip()]

# ---------- INTERFAZ PRINCIPAL CON TABS ----------
tabs = st.tabs(["Conciliación STOPP", "Consulta CIMA-AEMPS"])

with tabs[0]:
    st.title("Conciliación de Medicación - Reglas STOPP")

    edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=75)
    antecedentes = st.text_area("Antecedentes personales / Historia clínica")
    tratamiento = st.text_area("Tratamiento actual (una línea por fármaco):")

    if st.button("Analizar"):
        diagnosticos_detectados = detectar_patrones(antecedentes, diccionario_diagnosticos)
        medicamentos_detectados = detectar_patrones(tratamiento, diccionario_diagnosticos)

        st.subheader("Diagnósticos detectados:")
        if diagnosticos_detectados:
            for d in sorted(diagnosticos_detectados):
                st.markdown(f"- {d}")
        else:
            st.write("No se han detectado diagnósticos reconocidos.")

        st.subheader("Medicamentos detectados:")
        if medicamentos_detectados:
            for m in sorted(medicamentos_detectados):
                st.markdown(f"- {m}")
        else:
            st.write("No se han detectado medicamentos reconocidos.")

        st.subheader("Alertas STOPP detectadas:")
        alertas = []
        for regla in reglas_stopp:
            if any(d in diagnosticos_detectados for d in regla.get("diagnosticos", [])) and                any(m in medicamentos_detectados for m in regla.get("medicamentos", [])):
                alertas.append(f"[{regla['id']}] {regla['descripcion']}")
        if alertas:
            for a in alertas:
                st.warning(a)
        else:
            st.success("No se han detectado alertas con los datos introducidos.")

with tabs[1]:
    st.title("Consulta de medicamentos - Ficha oficial AEMPS")
    medicamento = st.text_input("Introduce el nombre del medicamento para consultar (ej: ibuprofeno)")

    if st.button("Buscar medicamento en CIMA"):
        if medicamento.strip() == "":
            st.warning("Introduce un nombre válido.")
        else:
            url = f"https://cima.aemps.es/cima/rest/medicamentos?nombre={medicamento.strip()}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    med = data[0]
                    st.subheader(f"🧾 {med['nombre']}")
                    st.markdown(f"**Nº Registro:** {med['nregistro']}")
                    st.markdown(f"**Principios activos:** {med['pactivos']}")
                    st.markdown(f"**Vía de administración:** {med['via']}")
                    st.markdown(f"**Forma farmacéutica:** {med['formafarmaceutica']}")
                    st.markdown("---")
                    st.subheader("Ficha técnica (PDF):")
                    st.markdown(f"[📄 Descargar ficha técnica]({med['docs'][0]['url']})", unsafe_allow_html=True)
                else:
                    st.error("No se encontró información para este medicamento.")
            else:
                st.error("Error al conectar con la API de CIMA-AEMPS.")
