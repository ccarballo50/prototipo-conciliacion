import streamlit as st

st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# Reglas STOPP - Ejemplo simplificado
def analizar_medicacion(meds, edad, fc):
    alertas = []
    if edad >= 65:
        if any("digoxina" in m and ("250" in m or "0.25" in m) for m in meds):
            alertas.append("Evitar digoxina >125 µg/día como tratamiento crónico en mayores.")
        if any("bisoprolol" in m or "atenolol" in m for m in meds) and fc < 50:
            alertas.append("Evitar betabloqueantes si FC < 50 lpm (riesgo de bradicardia).")
    return alertas

st.title("Conciliación de Medicación en Urgencias (Prototipo)")

edad = st.number_input("Edad del paciente", min_value=0, step=1)
fc = st.number_input("Frecuencia cardiaca (lpm)", min_value=0, step=1)
med_input = st.text_area("Introducir medicación (una por línea):")

if st.button("Analizar"):
    meds = [m.strip().lower() for m in med_input.splitlines() if m.strip()]
    alertas = analizar_medicacion(meds, edad, fc)
    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.write("- " + alerta)
    else:
        st.success("No se han detectado alertas con los datos introducidos.")
