import streamlit as st
from fpdf import FPDF
import datetime
import re
import json
from io import BytesIO

# Configuración de la página (debe ir primero)
st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ----------- CARGA DE DICCIONARIO CIE-10 -------------------
@st.cache_data
def cargar_diccionario_cie10(ruta_json="diccionario_diagnosticos_cie10_completo.json"):
    with open(ruta_json, "r", encoding="utf-8") as f:
        return json.load(f)

def detectar_diagnosticos(texto, diccionario):
    texto = texto.lower()
    encontrados = set()
    for codigo, patrones in diccionario.items():
        for patron in patrones:
            if re.search(rf"\b{re.escape(patron)}\b", texto):
                encontrados.add(codigo)
                break
    return list(encontrados)

# ------------- CARGA DE REGLAS STOPP ----------------------
@st.cache_data
def cargar_reglas_stopp():
    with open("reglas_stopp.json", "r", encoding="utf-8") as file:
        reglas = json.load(file)
    return reglas

reglas_stopp = cargar_reglas_stopp()

# ------------- ANALIZADOR DE MEDICACIÓN -------------------
def analizar_medicacion(meds, edad, fc, crea, cie10_detectados):
    alertas = []
    for regla in reglas_stopp:
        condiciones = regla.get("condiciones", {})
        aplica = True

        if "edad_min" in condiciones and edad < condiciones["edad_min"]:
            aplica = False
        if "edad_max" in condiciones and edad > condiciones["edad_max"]:
            aplica = False
        if "creatinina_max" in condiciones and crea is not None and crea <= condiciones["creatinina_max"]:
            aplica = False
        if "creatinina_min" in condiciones and crea is not None and crea >= condiciones["creatinina_min"]:
            aplica = False

        # Coincidencia parcial con códigos CIE10 (ej. H40 -> H401)
        if "requiere_diagnostico_cie10" in condiciones:
            if not any(
                any(detectado.startswith(cod) for detectado in cie10_detectados)
                for cod in condiciones["requiere_diagnostico_cie10"]
            ):
                aplica = False

        if aplica and any(palabra in m for m in meds for palabra in regla["palabras_clave"]):
            alertas.append(regla["mensaje"])

    return alertas

# ------------- GENERADOR DE PDF ---------------------------
def generar_pdf(edad, fc, crea, meds, alertas, cie10_detectados):
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

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Diagnósticos detectados (CIE-10):", ln=True)
    pdf.set_font("Arial", size=12)
    if cie10_detectados:
        for cod in cie10_detectados:
            pdf.cell(200, 8, txt="- " + cod, ln=True)
    else:
        pdf.cell(200, 8, txt="Ninguno", ln=True)

    pdf.ln(5)
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

    # ✅ Generación segura de PDF como bytes
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

# ------------------ INTERFAZ DE USUARIO ------------------
st.title("Conciliación de Medicación en Urgencias")

edad = st.number_input("Edad del paciente", min_value=0, step=1)
fc = st.number_input("Frecuencia cardiaca (lpm)", min_value=0, step=1)
crea = st.number_input("Creatinina (mg/dL)", min_value=0.0, step=0.1)
historia_clinica_texto = st.text_area("Antecedentes personales / Historia clínica")
med_input = st.text_area("Tratamiento actual (una línea por fármaco):")
meds = [m.strip().lower() for m in med_input.splitlines() if m.strip()]

if st.button("Analizar"):
    diccionario_cie10 = cargar_diccionario_cie10("diccionario_diagnosticos_cie10_completo.json")
    cie10_detectados = detectar_diagnosticos(historia_clinica_texto, diccionario_cie10)

    st.info(f"Diagnósticos detectados: {', '.join(cie10_detectados) if cie10_detectados else 'ninguno'}")

    alertas = analizar_medicacion(meds, edad, fc, crea, cie10_detectados)

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.write("• " + alerta)
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    # PDF
    pdf_bytes = generar_pdf(edad, fc, crea, meds, alertas, cie10_detectados)
    st.download_button(
        label="📄 Descargar informe en PDF",
        data=pdf_bytes,
        file_name="informe_conciliacion.pdf",
        mime="application/pdf"
    )
