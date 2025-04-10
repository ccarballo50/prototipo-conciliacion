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
    encontrados = set()
    texto = texto.lower()
    for clave, sinonimos in diccionario.items():
        for s in sinonimos:
            if re.search(rf"\b{s.lower()}\b", texto):
                encontrados.add(clave)
                break
    return list(encontrados)

    st.success("No se han detectado alertas con los datos introducidos.")
    for diag in detectados:
        for req in requeridos:
            if diag.startswith(req):
                return True
    return False

def detectar_alertas(edad, sexo_paciente, diagnosticos_detectados, tratamiento, reglas, creatinina, fc):
    alertas = []
    for regla in reglas:
        condiciones = regla.get("condiciones", {})
        medicamentos = condiciones.get("medicamentos", [])
        diagnosticos_regla = condiciones.get("requiere_diagnostico_cie10", [])
        edad_min = condiciones.get("edad_minima")
        edad_max = condiciones.get("edad_maxima")
        sexo = condiciones.get("sexo", "ambos")
        crea_min = condiciones.get("creatinina_minima")
        crea_max = condiciones.get("creatinina_maxima")
        fc_min = condiciones.get("fc_minima")
        fc_max = condiciones.get("fc_maxima")

        if edad_min and edad < edad_min:
            continue
        if edad_max and edad > edad_max:
            continue
        if sexo != "ambos" and sexo != sexo_paciente:
            continue
        if diagnosticos_regla and not cumple_diagnostico_por_prefijo(diagnosticos_detectados, diagnosticos_regla):
            continue
        if crea_min and creatinina < crea_min:
            continue
        if crea_max and creatinina > crea_max:
            continue
        if fc_min and fc < fc_min:
            continue
        if fc_max and fc > fc_max:
            continue
        if not any(med.lower() in tratamiento.lower() for med in medicamentos):
            continue

        alertas.append(regla["descripcion"])
    return alertas

# ------------------ INTERFAZ STREAMLIT ------------------
st.title("Conciliación de Medicación en Urgencias (Prototipo)")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=75)
sexo = st.selectbox("Sexo del paciente", options=["masculino", "femenino"])
creatinina = st.number_input("Creatinina (mg/dL)", min_value=0.0, max_value=20.0, value=1.0, step=0.1)
fc = st.number_input("Frecuencia cardíaca (lpm)", min_value=20, max_value=200, value=70)
antecedentes = st.text_area("Antecedentes personales / Historia clínica")
medicacion = st.text_area("Tratamiento actual (una línea por fármaco)")

if st.button("Analizar"):
    # Detectar diagnósticos
    diagnosticos_detectados = detectar_diagnosticos(antecedentes, diccionario_diagnosticos)

    if diagnosticos_detectados:
        st.info("🩺 Diagnósticos detectados en antecedentes:")
        for diag in diagnosticos_detectados:
            st.markdown(f"- **{diag}**")
    else:
        st.warning("⚠️ No se detectaron diagnósticos clínicos relevantes en los antecedentes.")

    # Detectar alertas STOPP
    alertas = detectar_alertas(edad, sexo, diagnosticos_detectados, medicacion, reglas_stopp, creatinina, fc)

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")