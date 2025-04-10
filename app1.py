import streamlit as st
import json
import datetime
from fpdf import FPDF
from io import BytesIO

# ---------------- CONFIGURACION ----------------
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ---------------- CARGA DE ARCHIVOS ----------------
@st.cache_data
def cargar_reglas_stopp():
    with open("reglas_stopp.json", "r", encoding="utf-8") as file:
        return json.load(file)

@st.cache_data
def cargar_diccionario_cie10():
    with open("diccionario_diagnosticos_cie10_completo.json", "r", encoding="utf-8") as f:
        return json.load(f)

reglas_stopp = cargar_reglas_stopp()
diccionario_cie10 = cargar_diccionario_cie10()

# ---------------- FUNCION PARA PDF ----------------
def generar_pdf(edad, fc, crea, meds, alertas, cie10_detectados):
    pdf = FPDF()
    pdf.add_page()

    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.cell(200, 10, txt="Informe de Conciliación de Medicación", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Edad: {edad} años", ln=True)
    pdf.cell(200, 10, txt=f"Frecuencia cardiaca: {fc} lpm", ln=True)
    pdf.cell(200, 10, txt=f"Creatinina: {crea} mg/dL", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Diagnósticos detectados (CIE-10):", ln=True)
    if cie10_detectados:
        for cod in cie10_detectados:
            pdf.cell(200, 8, txt="- " + cod, ln=True)
    else:
        pdf.cell(200, 8, txt="Ninguno", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Tratamiento introducido:", ln=True)
    for med in meds:
        pdf.cell(200, 8, txt="- " + med, ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Alertas detectadas:", ln=True)
    if alertas:
        for alerta in alertas:
            pdf.multi_cell(0, 8, txt="• " + alerta)
    else:
        pdf.cell(200, 8, txt="No se detectaron alertas.", ln=True)

    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode('latin1'))
    buffer.seek(0)
    return buffer

# ---------------- INTERFAZ PRINCIPAL ----------------
st.title("Conciliación de Medicación en Urgencias (Prototipo)")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=85)
fc = st.number_input("Frecuencia cardiaca (lpm)", min_value=30, max_value=200, value=100)
crea = st.text_input("Creatinina (mg/dL)", value="1.2")
ant = st.text_area("Antecedentes personales / Historia clínica")
input_meds = st.text_area("Tratamiento actual (una línea por fármaco):")

if st.button("Analizar"):
    meds = [line.strip() for line in input_meds.split("\n") if line.strip()]
    cie10_detectados = []
    for clave, codigos in diccionario_cie10.items():
        if clave.lower() in ant.lower():
            cie10_detectados.extend(codigos)
    cie10_detectados = sorted(set(cie10_detectados))

    alertas = []
    for regla in reglas_stopp:
        palabras = regla.get("palabras", [])
        cie10 = regla.get("cie10", [])
        if any(p.lower() in input_meds.lower() for p in palabras):
            if not cie10 or any(c in cie10_detectados for c in cie10):
                alertas.append(regla["mensaje"])

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    st.info("Diagnósticos detectados: " + ", ".join(cie10_detectados))

    # Generar PDF
    pdf_bytes = generar_pdf(edad, fc, crea, meds, alertas, cie10_detectados)
    st.download_button(
        label="📄 Descargar informe en PDF",
        data=pdf_bytes,
        file_name="informe_conciliacion.pdf",
        mime="application/pdf"
    )

