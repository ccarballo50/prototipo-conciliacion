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

def detectar_alertas(edad, sexo, diagnosticos_detectados, medicamentos_detectados, reglas):
    alertas = []
    for regla in reglas:
        # Comprobación de edad
        if "edad_min" in regla and "edad_max" in regla:
            if not (regla["edad_min"] <= edad <= regla["edad_max"]):
                continue


        # Comprobación de sexo si aplica
        if regla["sexo"] != "cualquiera" and regla["sexo"].lower() != sexo.lower():
            continue

        # Comprobación de diagnóstico (match exacto o por prefijo contenido)
        if regla["diagnosticos"]:
            if not any(
                diag_regla.lower() in diag_detectado.lower()
                for diag_regla in regla["diagnosticos"]
                for diag_detectado in diagnosticos_detectados
            ):
                continue

        # Comprobación de medicamentos (match por inclusión)
        if regla["medicamentos"]:
            if not any(
                med_regla.lower() in med_detectado.lower()
                for med_regla in regla["medicamentos"]
                for med_detectado in medicamentos_detectados
            ):
                continue

        # Si pasa todas las condiciones
        alertas.append(regla["alerta"])

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
