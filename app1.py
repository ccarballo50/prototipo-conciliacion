import streamlit as st
import json

# Cargar reglas STOPP desde el archivo JSON
with open("reglas_stopp.json", "r", encoding="utf-8") as f:
    reglas_stopp = json.load(f)

st.title("Asistente de Conciliación Farmacológica - Reglas STOPP")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, step=1)
antecedentes = st.text_area("Antecedentes personales / Historia clínica")
medicacion = st.text_area("Tratamiento actual (una línea por fármaco)")

if st.button("Analizar"):
    alertas = []
    diagnosticos_detectados = set()
    medicamentos_detectados = set()

    antecedentes_texto = antecedentes.lower()
    medicacion_texto = medicacion.lower()

    # Evaluar cada regla
    for regla in reglas_stopp:
        sexo_req = regla.get("sexo", "ambos")
        if sexo_req not in ["ambos", "no especificado"]:
            continue  # Por ahora ignoramos la variable sexo si no está definida correctamente

        diagnosticos = regla.get("diagnosticos", [])
        medicamentos = regla.get("medicamentos", [])

        match_diag = any(diag.lower() in antecedentes_texto for diag in diagnosticos)
        match_meds = any(med.lower() in medicacion_texto for med in medicamentos)

        if match_diag:
            for diag in diagnosticos:
                if diag.lower() in antecedentes_texto:
                    diagnosticos_detectados.add(diag)

        if match_meds:
            for med in medicamentos:
                if med.lower() in medicacion_texto:
                    medicamentos_detectados.add(med)

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

    # Mostrar medicamentos detectados (opcional)
    st.markdown("#### Medicamentos detectados:")
    if medicamentos_detectados:
        for med in sorted(medicamentos_detectados):
            st.write(f"- {med}")
    else:
        st.write("No se han detectado medicamentos reconocidos.")

