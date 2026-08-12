import streamlit as st
import imaplib
import email
import datetime
import io
import zipfile

st.set_page_config(page_title="Extractor de JSON Gmail", page_icon="📥")

st.title("Extractor de JSON desde Gmail")
st.write("Ingresa tus datos de acceso para conectar con tu cuenta de correo y descargar todos los archivos en un solo ZIP.")

# Campos en la barra lateral
with st.sidebar:
    st.header("Configuración")
    EMAIL = st.text_input("Correo de Gmail")
    PASSWORD = st.text_input("Contraseña de Aplicación", type="password")
    st.info("Usa una contraseña de aplicación de 16 caracteres de Google.")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Fecha Inicio", datetime.date.today() - datetime.timedelta(days=30))
with col2:
    end_date = st.date_input("Fecha Fin", datetime.date.today())

def conectar_y_buscar(email_user, email_pass, fecha_inicio, fecha_fin):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_user, email_pass.strip())
    mail.select("inbox")

    f_ini = fecha_inicio.strftime("%d-%b-%Y")
    f_fin = fecha_fin.strftime("%d-%b-%Y")
    
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
                        content = part.get_payload(decode=True)
                        archivos.append((filename, content))
    mail.logout()
    return archivos

if st.button("Buscar y Descargar Todos en ZIP"):
    if not EMAIL or not PASSWORD:
        st.error("Por favor, ingresa tu correo y tu contraseña de aplicación en la barra lateral.")
    else:
        try:
            with st.spinner("Conectando con Gmail, buscando y empaquetando archivos..."):
                resultados = conectar_y_buscar(EMAIL, PASSWORD, start_date, end_date)
            
            if resultados:
                # Crear un archivo ZIP en memoria RAM
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for nombre, contenido in resultados:
                        zip_file.writestr(nombre, contenido)
                
                zip_buffer.seek(0)
                
                st.success(f"¡Se empaquetaron {len(resultados)} archivos JSON exitosamente!")
                
                # Botón único para descargar el ZIP completo
                st.download_button(
                    label="📦 Descargar Todos los JSON (ZIP)",
                    data=zip_buffer,
                    file_name=f"documentos_json_{datetime.date.today()}.zip",
                    mime="application/zip"
                )
            else:
                st.warning("No se encontraron archivos JSON adjuntos en ese rango de fechas.")
        except Exception as e:
            st.error(f"Error de autenticación o conexión: {e}. Asegúrate de usar una Contraseña de Aplicación válida.")
