import streamlit as st
import imaplib
import email
import datetime

st.set_page_config(page_title="Extractor de JSON Gmail", page_icon="📥")

st.title("Extractor de JSON desde Gmail")
st.write("Ingresa tus datos de acceso para conectar con tu cuenta de correo.")

# Campos en la interfaz para que pongas tus datos de forma segura
with st.sidebar:
    st.header("Configuración")
    EMAIL = st.text_input("reynaestela.escobar.m@gmail.com")
    PASSWORD = st.text_input("Contraseña de Aplicación", type="xhpyyabsdygialf")
    st.info("Usa una contraseña de aplicación de 16 caracteres de Google, no tu clave normal.")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Fecha Inicio", datetime.date.today() - datetime.timedelta(days=30))
with col2:
    end_date = st.date_input("Fecha Fin", datetime.date.today())

def conectar_y_buscar(email_user, email_pass, fecha_inicio, fecha_fin):
    # Conexión al servidor IMAP de Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    
    # Codificar la contraseña en utf-8 para evitar errores de caracteres especiales
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

if st.button("Buscar y Descargar JSON"):
    if not EMAIL or not PASSWORD:
        st.error("Por favor, ingresa tu correo y tu contraseña de aplicación en la barra lateral.")
    else:
        try:
            with st.spinner("Conectando con Gmail y buscando archivos..."):
                resultados = conectar_y_buscar(EMAIL, PASSWORD, start_date, end_date)
            
            if resultados:
                st.success(f"¡Se encontraron {len(resultados)} archivos JSON!")
                for nombre, contenido in resultados:
                    st.download_button(
                        label=f"📥 Descargar {nombre}",
                        data=contenido,
                        file_name=nombre,
                        mime="application/json"
                    )
            else:
                st.warning("No se encontraron archivos JSON adjuntos en ese rango de fechas.")
        except Exception as e:
            st.error(f"Error de autenticación o conexión: {e}. Asegúrate de usar una Contraseña de Aplicación válida.")
