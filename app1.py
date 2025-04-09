import streamlit as st
from fpdf import FPDF
import datetime
import json

st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ---- CARGA DE REGLAS ----
@st.cache_data
def cargar_reglas_stopp():
    with open("reglas_stopp.json", "r", encoding="utf-8") as file:
        reglas = json.load(file)
    return reglas

reglas_stopp = cargar_reglas_stopp()

# ---- FUNCIONES CLÍNICAS ----
def analizar_medicacion(meds, edad, fc, crea):
    alertas = []
    for regla in reglas_stopp:
        condiciones = regla.get("condiciones", {})
        aplica = True

        # Verificar condiciones de edad
        if "edad_min" in condiciones and edad < condiciones["edad_min"]:
            aplica = False
        if "edad_max" in condiciones and edad > condiciones["edad_max"]:
            aplica = False

        # Verificar condiciones de creatinina
        if "creatinina_max" in condiciones and crea is not None and crea <= condiciones["creatinina_max"]:
            aplica = False
        if "creatinina_min" in condiciones and crea is not None and crea >= condiciones["creatinina_min"]:
            aplica = False

        # Verificar palabras clave en la medicación
        if aplica and any(palabra in m for m in meds for palabra in regla["palabras_clave"]):
            alertas.append(regla["mensaje"])

    return alertas

# ---- GENERADOR DE INFORME PDF ----
def generar_pdf(edad, fc, crea, meds, alertas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Informe de Conciliación de Medicación", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Edad: {edad} años", ln=True)
    pdf.cell(200, 10, txt=f"Frecuencia cardiaca: {fc} lpm", ln=True)
    pdf.cell(200, 10, txt=f"Creatinina: {crea} mg/dL", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Tratamiento introducido:", ln=True)
    pdf.set_font("Arial", size=12)
    for med in meds:
        pdf.cell(200, 8, txt="- " + med, ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Alertas detectadas:", ln=True)
    pdf.set_font("Arial", size=12)
    if alertas:
        for alerta in alertas:
            pdf.multi_cell(0, 8, txt="• " + alerta)
    else:
        pdf.cell(200, 8, txt="No se detectaron alertas.", ln=True)

    return pdf.output(dest='S').encode('latin1')


# ---- INTERFAZ STREAMLIT ----
st.title("Conciliación de Medicación en Urgencias (Prototipo)")

edad = st.number_input("Edad del paciente", min_value=0, step=1)
fc = st.number_input("Frecuencia cardiaca (lpm)", min_value=0, step=1)
crea = st.number_input("Creatinina (mg/dL)", min_value=0.0, step=0.1)

med_input = st.text_area("Introducir medicación (una por línea):")
meds = [m.strip().lower() for m in med_input.splitlines() if m.strip()]

if st.button("Analizar"):
    alertas = analizar_medicacion(meds, edad, fc, crea)
    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.write("• " + alerta)
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    # ---- PDF EXPORT ----
    pdf_bytes = generar_pdf(edad, fc, crea, meds, alertas)
    st.download_button(
        label="📄 Descargar informe en PDF",
        data=pdf_bytes,
        file_name="informe_conciliacion.pdf",
        mime="application/pdf"
    )
