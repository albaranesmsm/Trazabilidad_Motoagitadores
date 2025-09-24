import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from PIL import Image
import numpy as np
import cv2
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
# =======================
# Función para obtener hoja
# =======================
def get_worksheet(title):
   try:
       return spreadsheet.worksheet(title)
   except gspread.exceptions.WorksheetNotFound:
       return spreadsheet.add_worksheet(title=title, rows="1000", cols="3")
worksheet = get_worksheet(tipo)
# =======================
# Lector de QR múltiple con OpenCV
# =======================
st.subheader("📷 Escanea los QR de los equipos")
if "serie_leidas" not in st.session_state:
   st.session_state.serie_leidas = []
uploaded_file = st.camera_input("Abre la cámara para escanear QR:")
if uploaded_file is not None:
   image = Image.open(uploaded_file)
   image_np = np.array(image)
   # Crear detector de QR con OpenCV
   detector = cv2.QRCodeDetector()
   data, bbox, _ = detector.detectAndDecode(image_np)
   if data:
       numero_serie = data.strip()
       if numero_serie not in st.session_state.serie_leidas:
           # Registrar en Google Sheets
           fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           worksheet.append_row([numero_serie, taller, fecha])
           st.session_state.serie_leidas.append(numero_serie)
           st.success(f"✅ Registrado número de serie: {numero_serie}")
       else:
           st.info(f"🔁 El número de serie {numero_serie} ya ha sido registrado")
   else:
       st.warning("No se pudo leer ningún QR. Intenta de nuevo.")
# Mostrar los números de serie registrados en esta sesión
if st.session_state.serie_leidas:
   st.subheader("Números de serie registrados en esta sesión:")
   for i, s in enumerate(st.session_state.serie_leidas, 1):
       st.text(f"{i}. {s}")
