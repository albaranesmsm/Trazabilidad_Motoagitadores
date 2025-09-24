import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
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
# Abrir Google Sheet
SHEET_ID = "1st-BhcBfkLmvnxJZVHQOtOSfH9aa-Ke0ZHX85kH77x4"
spreadsheet = client.open_by_key(SHEET_ID)
# =======================
# STREAMLIT UI
# =======================
st.title("📋 Registro de Números de Serie")
# Pregunta 1
tipo = st.radio(
   "Selecciona el tipo de registro:",
   ["Instalación", "Reparación", "Incidencia"]
)
# Pregunta 2
taller = st.selectbox(
   "Selecciona el Taller/BO:",
   ["ECESA", "Jocertec", "Tecbecar", "Cervetecnica"]
)
# Pregunta 3
numero_serie = st.text_input(
   "Introduce o escanea el número de serie:"
)
# Botón enviar
if st.button("Registrar"):
   if not numero_serie:
       st.error("⚠️ Debes introducir un número de serie.")
   else:
       # Seleccionar hoja según la pregunta 1
       if tipo == "Instalación":
           worksheet = spreadsheet.worksheet("Instalacion")
       elif tipo == "Reparación":
           worksheet = spreadsheet.worksheet("Reparacion")
       else:
           worksheet = spreadsheet.worksheet("Incidencia")
       # Registrar datos
       fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       worksheet.append_row([numero_serie, taller, fecha])
       st.success(f"✅ Número de serie **{numero_serie}** registrado en hoja **{tipo}**")