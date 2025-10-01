import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import os
# =======================
# CONFIGURAR GOOGLE SHEETS
# =======================
creds_json = {
   "type": st.secrets["GCP_TYPE"],
   "project_id": st.secrets["GCP_PROJECT_ID"],
   "private_key_id": st.secrets["GCP_PRIVATE_KEY_ID"],
   "private_key": st.secrets["GCP_PRIVATE_KEY"].replace("\\n", "\n"),
   "client_email": st.secrets["GCP_CLIENT_EMAIL"],
   "client_id": st.secrets["GCP_CLIENT_ID"],
   "auth_uri": st.secrets["GCP_AUTH_URI"],
   "token_uri": st.secrets["GCP_TOKEN_URI"],
   "auth_provider_x509_cert_url": st.secrets["GCP_AUTH_PROVIDER_X509_CERT_URL"],
   "client_x509_cert_url": st.secrets["GCP_CLIENT_X509_CERT_URL"],
   "universe_domain": st.secrets["GCP_UNIVERSE_DOMAIN"]
}
creds = Credentials.from_service_account_info(
   creds_json,
   scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
SHEET_ID = "1st-BhcBfkLmvnxJZVHQOtOSfH9aa-Ke0ZHX85kH77x4"
spreadsheet = client.open_by_key(SHEET_ID)
# =======================
# CARGAR DATOS DE TALLERES/BO DESDE EXCEL
# =======================
@st.cache_data
def load_talleres(path="data/talleres.xlsx"):
   """Carga el Excel de talleres y normaliza los datos"""
   if not os.path.exists(path):
       st.error(f"No se encuentra el archivo requerido: {path}")
       return pd.DataFrame(columns=["Codigo", "Nombre", "Tipo"])
   try:
       df = pd.read_excel(path, dtype=str)  # Forzar todo a string
       df["Codigo"] = df["Codigo"].str.strip()  # Quitar espacios
       df["Nombre"] = df["Nombre"].str.strip()
       df["Tipo"] = df["Tipo"].str.strip()
       return df
   except Exception as e:
       st.error(f"No se pudo cargar el Excel de talleres: {e}")
       return pd.DataFrame(columns=["Codigo", "Nombre", "Tipo"])
talleres_df = load_talleres()
# =======================
# FUNCIÓN PARA OBTENER HOJA
# =======================
def get_worksheet(title):
   try:
       return spreadsheet.worksheet(title)
   except gspread.exceptions.WorksheetNotFound:
       return spreadsheet.add_worksheet(title=title, rows="1000", cols="3")
# =======================
# PANTALLA 1: SELECCIÓN DE ALMACÉN
# =======================
if "pantalla" not in st.session_state:
   st.session_state.pantalla = "inicio"
if "tipo" not in st.session_state:
   st.session_state.tipo = None
if "taller_nombre" not in st.session_state:
   st.session_state.taller_nombre = None
if st.session_state.pantalla == "inicio":
   st.title("🔑 Validación de Almacén")
   codigo_input = st.text_input("Introduce el código de almacén:")
   if codigo_input:
       codigo_input = str(codigo_input).strip()  # Convertir a string y quitar espacios
       row = talleres_df.loc[talleres_df["Codigo"] == codigo_input]
       if not row.empty:
           nombre = row.iloc[0]["Nombre"]
           tipo_almacen = row.iloc[0]["Tipo"]
           st.success(f"✔ Código válido: **{codigo_input} - {nombre} ({tipo_almacen})**")
           if tipo_almacen == "BO":
               tipo = st.radio("Selecciona el tipo de registro:", ["Instalación", "Incidencia"])
           else:  # TALLER
               tipo = "Reparación"
               st.info("🔧 Tipo de registro asignado automáticamente: Reparación")
           if st.button("Continuar ➡️"):
               st.session_state.tipo = tipo
               st.session_state.taller_nombre = nombre
               st.session_state.codigo = codigo_input
               st.session_state.pantalla = "registro"
               st.rerun()
       else:
           st.error("❌ Código no encontrado en el Excel de talleres/BO.")
# =======================
# PANTALLA 2: REGISTRO DE NÚMEROS DE SERIE
# =======================
if st.session_state.pantalla == "registro":
   st.title("📋 Registro de Números de Serie")
   st.markdown(f"""
   **Almacén:** {st.session_state.taller_nombre}  
   **Código:** {st.session_state.codigo}  
   **Tipo de registro:** {st.session_state.tipo}
   """)
   worksheet = get_worksheet(st.session_state.tipo)
   if "serie_leidas" not in st.session_state:
       st.session_state.serie_leidas = []
   numero_serie = st.text_input("Número de serie (enter para registrar)")
   if st.button("Registrar número de serie") and numero_serie:
       numero_serie = numero_serie.strip()
       if numero_serie not in st.session_state.serie_leidas:
           tz = pytz.timezone("Europe/Madrid")
           fecha = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
           worksheet.append_row([numero_serie, st.session_state.taller_nombre, fecha])
           st.session_state.serie_leidas.append(numero_serie)
           st.success(f"✅ Registrado número de serie: {numero_serie}")
       else:
           st.info(f"🔁 El número de serie {numero_serie} ya ha sido registrado en esta sesión.")
   if st.session_state.serie_leidas:
       st.subheader("Números de serie registrados en esta sesión:")
       for i, s in enumerate(st.session_state.serie_leidas, 1):
           st.text(f"{i}. {s}")
