import streamlit as st
import imaplib
import email
from email.header import decode_header
import datetime

# Título y configuración
st.title("Extractor de JSON desde Gmail")

# Configuración de credenciales (considera usar st.secrets para mayor seguridad)
EMAIL = "tu_correo@gmail.com"
PASSWORD = "tu_contraseña_de_aplicacion" # Mantén esto seguro

def conectar_y_buscar(fecha_inicio, fecha_fin):
    # Conexión al servidor IMAP
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    # Formateo de fechas para el criterio IMAP (DD-Mon-YYYY)
    f_ini = fecha_inicio.strftime("%d-%b-%Y")
    f_fin = fecha_fin.strftime("%d-%b-%Y")
    
    # Criterio de búsqueda
    criterio = f'(SINCE {f_ini} BEFORE {f_fin})'
    _, data = mail.search(None, criterio)
    
    archivos = []
    for num in data[0].split():
        _, msg_data = mail.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart': continue
                    if part.get('Content-Disposition') is None: continue
                    filename = part.get_filename()
                    if filename and filename.endswith('.json'):
                        # Guardar o procesar el archivo
                        content = part.get_payload(decode=True)
                        archivos.append((filename, content))
    mail.logout()
    return archivos

# Interfaz en Streamlit
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Fecha Inicio", datetime.date.today() - datetime.timedelta(days=30))
with col2:
    end_date = st.date_input("Fecha Fin", datetime.date.today())

if st.button("Buscar y Descargar JSON"):
    try:
        resultados = conectar_y_buscar(start_date, end_date)
        if resultados:
            for nombre, contenido in resultados:
                st.download_button(f"Descargar {nombre}", contenido, nombre, "application/json")
        else:
            st.warning("No se encontraron archivos JSON en ese rango.")
    except Exception as e:
        st.error(f"Error: {e}. Verifica tu contraseña de aplicación.")