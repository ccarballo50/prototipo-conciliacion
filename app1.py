import streamlit as st
import json
import re
import datetime
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Conciliación de Medicación", layout="centered")

# ------------------ CARGA DE ARCHIVOS ------------------
@st.cache_data
def cargar_reglas_stopp():
    with open("reglas_stopp.json", "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def cargar_diccionario_etiquetas():
    with open("diccionario_diagnosticos.json", "r", encoding="utf-8") as f:
        return json.load(f)

reglas_stopp = cargar_reglas_stopp()
diccionario_etiquetas = cargar_diccionario_etiquetas()

# ------------------ FUNCIONES AUXILIARES ------------------
def detectar_etiquetas(texto, diccionario):
    etiquetas = set()
    for etiqueta, sinonimos in diccionario.items():
        for s in sinonimos:
            if re.search(rf"\b{s.lower()}\b", texto.lower()):
                etiquetas.add(etiqueta)
                break
    return list(etiquetas)

def normalizar_medicamentos(lista):
    return [re.sub(r"[^a-zA-Z0-9]", "", med.lower()) for med in lista]

def generar_pdf(edad, sexo, crea, meds, alertas, etiquetas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Informe de Conciliación de Medicación", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(200, 10, txt=f"Edad: {edad} años", ln=True)
    pdf.cell(200, 10, txt=f"Sexo: {sexo}", ln=True)
    pdf.cell(200, 10, txt=f"Creatinina: {crea}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Tratamiento introducido:", ln=True)
    pdf.set_font("Arial", size=12)
    for med in meds:
        pdf.cell(200, 8, txt=f"- {med}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Alertas detectadas:", ln=True)
    pdf.set_font("Arial", size=12)
    if alertas:
        for alerta in alertas:
            pdf.multi_cell(0, 8, txt=f"- {alerta}")
    else:
        pdf.cell(200, 8, txt="No se detectaron alertas.", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Etiquetas clínicas detectadas:", ln=True)
    pdf.set_font("Arial", size=12)
    if etiquetas:
        pdf.multi_cell(0, 8, txt=", ".join(etiquetas))
    else:
        pdf.cell(200, 8, txt="Ninguna", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# ------------------ INTERFAZ STREAMLIT ------------------
st.title("Conciliación de Medicación (Demo STOPP)")

edad = st.number_input("Edad del paciente", min_value=0, max_value=120, value=80)
sexo = st.selectbox("Sexo del paciente", ["masculino", "femenino"])
crea = st.text_input("Creatinina (mg/dL)", value="1.2")
antecedentes = st.text_area("Antecedentes personales")
medicacion_input = st.text_area("Tratamiento actual (una línea por fármaco)")

if st.button("Analizar"):
    medicamentos = [m.strip() for m in medicacion_input.splitlines() if m.strip()]
    meds_normalizados = normalizar_medicamentos(medicamentos)
    etiquetas_detectadas = detectar_etiquetas(antecedentes, diccionario_etiquetas)

    alertas = []
    for regla in reglas_stopp:
        condiciones = regla.get("condiciones", {})
        medicamentos_regla = condiciones.get("medicamentos", [])
        diagnosticos_regla = condiciones.get("diagnosticos", [])
        edad_min = condiciones.get("edad_min", 0)
        edad_max = condiciones.get("edad_max", 200)
        sexo_regla = condiciones.get("sexo", "ambos")

        if edad < edad_min or edad > edad_max:
            continue
        if sexo_regla != "ambos" and sexo != sexo_regla:
            continue
        if diagnosticos_regla and not any(d in etiquetas_detectadas for d in diagnosticos_regla):
            continue
        if medicamentos_regla and not any(m in meds_normalizados for m in medicamentos_regla):
            continue

        alertas.append(regla.get("descripcion"))

    if alertas:
        st.warning("Se han detectado las siguientes alertas:")
        for alerta in alertas:
            st.markdown(f"- {alerta}")
    else:
        st.success("No se han detectado alertas con los datos introducidos.")

    st.info("Etiquetas detectadas: " + ", ".join(etiquetas_detectadas))

    pdf_bytes = generar_pdf(edad, sexo, crea, medicamentos, alertas, etiquetas_detectadas)
    st.download_button("Descargar informe PDF", data=pdf_bytes, file_name="informe_conciliacion.pdf")

