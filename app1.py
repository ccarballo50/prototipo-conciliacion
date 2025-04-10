import streamlit as st
import json
import re

# Cargar reglas STOPP
with open("reglas_stopp.json", "r", encoding="utf-8") as f:
    reglas_stopp = json.load(f)

# Cargar diccionario CIE10
with open("diccionario_diagnosticos_cie10_completo.json", "r", encoding="utf-8") as f:
    diccionario_cie10 = json.load(f)

# Funciones auxiliares para análisis
def normalizar(texto):
    return texto.lower().strip()

def detectar_diagnosticos(texto_libre, diccionario):
    diagnosticos_detectados = set()
    for cie, sinonimos in diccionario.items():
        for palabra in sinonimos:
            patron = r"\\b" + re.escape(palabra.lower()) + r"\\b"
            if re.search(patron, texto_libre.lower()):
                diagnosticos_detectados.add(cie)
                break
    return list(diagnosticos_detectados)

def evaluar_reglas(diagnosticos, medicamentos, sexo):
    alertas = []
    for regla in reglas_stopp:
        if regla.get("sexo", "ambos") not in ["ambos", sexo.lower()]:
            continue

        diag_regla = [normalizar(d) for d in regla.get("diagnosticos", [])]
        meds_regla = [normalizar(m) for m in regla.get("medicamentos", [])]
        condiciones = regla.get("condiciones", {})

        match_diag = any(d in texto_antecedentes for d in diag_regla)
        match_meds = any(m in texto_meds for m in meds_regla)

        if match_diag and match_meds:
            alertas.append(regla["descripcion"])
    return alertas

# Interfaz Streamlit
st.title("Conciliación de Medicación - Criterios STOPP")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=75)
sexo = st.radio("Sexo del paciente", ["hombre", "mujer"], index=0)
texto_antecedentes = st.text_area("Antecedentes personales / Historia clínica")
texto_meds = st.text_area("Tratamiento actual (una línea por fármaco)")

if st.button("Analizar"):
    cie10_detectados = detectar_diagnosticos(texto_antecedentes, diccionario_cie10)
    medicamentos_normalizados = [normalizar(l) for l in texto_meds.splitlines() if l.strip() != ""]
    
    alertas = evaluar_reglas(cie10_detectados, medicamentos_normalizados, sexo)

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    st.info("Diagnósticos detectados:")
    st.write(cie10_detectados)

