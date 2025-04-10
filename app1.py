import streamlit as st
import json
import re
from fpdf import FPDF
from io import BytesIO

# ------------------ CONFIGURACIÓN DE PÁGINA ------------------
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ------------------ CARGA DE DATOS ------------------
@st.cache_data
def cargar_reglas_stopp(ruta_json="reglas_stopp.json"):
    with open(ruta_json, "r", encoding="utf-8") as file:
        return json.load(file)

@st.cache_data
def cargar_diccionario_cie10(ruta_json="diccionario_diagnosticos_cie10_completo.json"):
    with open(ruta_json, "r", encoding="utf-8") as f:
        return json.load(f)

reglas_stopp = cargar_reglas_stopp()
diccionario_cie10 = cargar_diccionario_cie10()

# ------------------ FUNCIONES ------------------

def detectar_diagnosticos(texto, diccionario_cie10):
    encontrados = set()
    for patron, codigos in diccionario_cie10.items():
        # Escapamos el patrón para evitar errores por paréntesis, etc.
        patron_escapado = re.escape(patron.lower())
        if re.search(rf"\b{patron_escapado}\b", texto.lower()):
            encontrados.update(codigos)
    return list(encontrados)


def normalizar_medicamentos(lista):
    return [re.sub(r"[^a-zA-Z0-9]", "", med.lower()) for med in lista]

def generar_pdf(edad, fc, crea, meds, alertas, cie10_detectados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Informe de Conciliación de Medicación", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Edad: {edad} años", ln=True)
    pdf.cell(200, 10, txt=f"Frecuencia Cardíaca: {fc} lpm", ln=True)
    pdf.cell(200, 10, txt=f"Creatinina: {crea}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Medicación introducida:", ln=True)
    pdf.set_font("Arial", size=12)
    for med in meds:
        pdf.cell(200, 10, txt=f"- {med}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Alertas detectadas:", ln=True)
    pdf.set_font("Arial", size=12)
    if alertas:
        for alerta in alertas:
            pdf.multi_cell(0, 10, txt=f"- {alerta}")
    else:
        pdf.cell(200, 10, txt="No se han detectado alertas.", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Diagnósticos CIE10 detectados:", ln=True)
    pdf.set_font("Arial", size=12)
    if cie10_detectados:
        pdf.multi_cell(0, 10, txt=", ".join(cie10_detectados))
    else:
        pdf.cell(200, 10, txt="Ninguno", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# ------------------ INTERFAZ STREAMLIT ------------------
st.title("Conciliación de Medicación en Urgencias (Prototipo)")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=75)
fc = st.number_input("Frecuencia cardiaca (lpm)", min_value=0, max_value=300, value=80)
crea = st.text_input("Creatinina (mg/dL)", value="1.2")
ant = st.text_area("Antecedentes personales / Historia clínica")
medicacion_input = st.text_area("Tratamiento actual (una línea por fármaco):")

if st.button("Analizar"):
    medicamentos = [m.strip() for m in medicacion_input.splitlines() if m.strip()]
    medicamentos_normalizados = normalizar_medicamentos(medicamentos)
    antecedentes = ant.lower()

    cie10_detectados = detectar_diagnosticos(antecedentes, diccionario_cie10)
    alertas = []

    for regla in reglas_stopp:
        palabras = regla["palabras"]
        cie_excluyentes = regla.get("cie_excluyentes", [])
        mensaje = regla["mensaje"]

        if any(palabra in medicamentos_normalizados for palabra in palabras):
            if any(cie in cie10_detectados for cie in cie_excluyentes):
                alertas.append(mensaje)

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    st.info("**Diagnósticos detectados:** " + ", ".join(cie10_detectados))

    pdf_bytes = generar_pdf(edad, fc, crea, medicamentos, alertas, cie10_detectados)
    st.download_button("Descargar informe en PDF", data=pdf_bytes, file_name="informe_conciliacion.pdf")
