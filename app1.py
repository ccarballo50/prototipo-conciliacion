import streamlit as st
import json
import re

# Cargar reglas STOPP desde el archivo JSON
with open("reglas_stopp.json", "r", encoding="utf-8") as f:
    reglas_stopp = json.load(f)

# Cargar diccionario de diagnósticos normalizados
with open("diccionario_diagnosticos.json", "r", encoding="utf-8") as f:
    diccionario_diagnosticos = json.load(f)

def detectar_diagnosticos(texto, diccionario):
    etiquetas = set()
    texto = texto.lower()
    for etiqueta, sinonimos in diccionario.items():
        for termino in sinonimos:
            if re.search(rf"\\b{re.escape(termino.lower())}\\b", texto):
                etiquetas.add(etiqueta)
                break
    return etiquetas

def detectar_medicamentos(texto, lista_meds):
    encontrados = set()
    texto = texto.lower()
    for med in lista_meds:
        if med.lower() in texto:
            encontrados.add(med)
    return encontrados

st.title("Asistente de Conciliación Farmacológica - Reglas STOPP")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, step=1)
antecedentes = st.text_area("Antecedentes personales / Historia clínica")
medicacion = st.text_area("Tratamiento actual (una línea por fármaco)")

if st.button("Analizar"):
    alertas = []
    texto_antecedentes = antecedentes.lower()
    texto_meds = medicacion.lower()

    diagnosticos_detectados = detectar_diagnosticos(texto_antecedentes, diccionario_diagnosticos)
    medicamentos_detectados = set()

    for regla in reglas_stopp:
        sexo_req = regla.get("sexo", "ambos")
        if sexo_req not in ["ambos", "no especificado"]:
            continue  # Por ahora ignoramos la variable sexo si no está definida correctamente

        diagnosticos_regla = set(regla.get("diagnosticos", []))
        medicamentos_regla = set(regla.get("medicamentos", []))

        match_diag = bool(diagnosticos_regla & diagnosticos_detectados)
        match_meds = bool(detectar_medicamentos(texto_meds, medicamentos_regla))

        if match_diag:
            medicamentos_detectados |= detectar_medicamentos(texto_meds, medicamentos_regla)

        if match_diag and match_meds:
            alertas.append(regla["descripcion"])

    # Mostrar alertas
    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    # Mostrar diagnósticos detectados
    st.markdown("#### Diagnósticos detectados en texto libre:")
    if diagnosticos_detectados:
        for diag in sorted(diagnosticos_detectados):
            st.write(f"- {diag}")
    else:
        st.write("No se han detectado diagnósticos reconocidos.")

    # Mostrar medicamentos detectados (sin duplicados)
    st.markdown("#### Medicamentos detectados:")
    if medicamentos_detectados:
        for med in sorted(medicamentos_detectados):
            st.write(f"- {med}")
    else:
        st.write("No se han detectado medicamentos reconocidos.")

