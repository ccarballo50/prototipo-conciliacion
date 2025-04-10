import streamlit as st
import json
import re

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
    for categoria, sinonimos in diccionario.items():
        for patron in sinonimos:
            if re.search(rf"\\b{re.escape(patron.lower())}\\b", texto.lower()):
                encontrados.append(categoria.lower())
                break
    return list(set(encontrados))

# -------------------------------
st.title("Conciliación de Medicación - Reglas STOPP")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=75)
antecedentes = st.text_area("Antecedentes personales / Historia clínica")
tratamiento = st.text_area("Tratamiento actual (una línea por fármaco):")

if st.button("Analizar"):
    # Detectar diagnósticos y medicamentos
    diagnosticos_detectados = detectar_patrones(antecedentes, diccionario_diagnosticos)
    medicamentos_detectados = detectar_patrones(tratamiento, diccionario_diagnosticos)

    # Evaluar reglas
    alertas = []
    for regla in reglas_stopp:
        sexo = regla.get("sexo", "ambos")
        condiciones = regla.get("condiciones", {})

        # Reglas de edad (futuro)

        # Comprobación de diagnósticos y medicamentos
        if any(d.lower() in diagnosticos_detectados for d in regla["diagnosticos"]) and \
           any(m.lower() in medicamentos_detectados for m in regla["medicamentos"]):
            alertas.append(regla["descripcion"])

    # Mostrar resultados
    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    st.subheader("Diagnósticos detectados en texto libre:")
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

