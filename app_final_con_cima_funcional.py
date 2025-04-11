import streamlit as st
import json
import re

# ---------------------- CONFIGURACIÓN ----------------------
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")
st.title("Conciliación de Medicación - Reglas STOPP")

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
diccionario_clases = cargar_diccionario("diccionario_clases_farmacos.json")

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

def obtener_clases(medicamentos, diccionario_clases):
    clases = []
    for m in medicamentos:
        if m in diccionario_clases:
            clases.extend(diccionario_clases[m])
    return list(set(clases))

# ---------------------- INTERFAZ ----------------------
st.subheader("Datos del paciente")
edad = st.number_input("Edad", min_value=0, max_value=120, value=75)
frecuencia_cardiaca = st.number_input("Frecuencia cardiaca (lpm)", min_value=20, max_value=200, value=70)
filtrado_glomerular = st.number_input("Filtrado glomerular estimado (ml/min)", min_value=0, max_value=200, value=80)
creatinina = st.number_input("Creatinina (mg/dL)", min_value=0.0, max_value=10.0, value=0.9, step=0.1)

st.subheader("Información clínica")
antecedentes = st.text_area("Antecedentes personales / Historia clínica")
tratamiento = st.text_area("Tratamiento actual (una línea por fármaco):")

if st.button("Analizar"):
    diagnosticos_detectados = detectar_patrones(antecedentes, diccionario_diagnosticos)
    medicamentos_detectados = detectar_patrones(tratamiento, diccionario_medicamentos)
    clases_detectadas = obtener_clases(medicamentos_detectados, diccionario_clases)

    alertas = []
    for regla in reglas_stopp:
        condiciones = regla.get("condiciones", {})
        # Aplicar condiciones clínicas aquí si fuese necesario

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

    st.subheader("Clases terapéuticas detectadas:")
    if clases_detectadas:
        for c in sorted(set(clases_detectadas)):
            st.markdown(f"- {c}")
    else:
        st.write("No se han detectado clases de medicamentos reconocidas.")

