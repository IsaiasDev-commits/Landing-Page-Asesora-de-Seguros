from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Permitir CORS manualmente
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def enviar_correo_confirmacion(destinatario, nombre, email, telefono, plan_interes, mensaje_cliente):
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    
    if not remitente or not password:
        app.logger.error("Credenciales de email no configuradas")
        return False
    
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = f"📋 Nueva cotización de seguros - {nombre}"
    
    cuerpo = f"""
    📋 NUEVA SOLICITUD DE COTIZACIÓN - SEGUROS CONFIANZA
    
    👤 **Nombre:** {nombre}
    📧 **Email:** {email}
    📞 **Teléfono:** {telefono}
    🏦 **Plan de interés:** {plan_interes if plan_interes else 'No especificado'}
    
    💬 **Mensaje del cliente:**
    {mensaje_cliente}
    
    ---
    📅 **Enviado el:** {datetime.now().strftime("%d/%m/%Y %H:%M")}
    🔔 **Contactar al cliente lo antes posible**
    """
    
    mensaje.attach(MIMEText(cuerpo, 'plain'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(remitente, password)
            server.send_message(mensaje)
        app.logger.info(f"✅ Correo enviado a {destinatario}")
        return True
    except Exception as e:
        app.logger.error(f"❌ Error enviando correo: {e}")
        return False

@app.route("/enviar-cotizacion", methods=["POST", "OPTIONS"])
def enviar_cotizacion():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})
    
    try:
        data = request.get_json()
        app.logger.info(f"Datos recibidos: {data}")
        
        if not data:
            return jsonify({"error": "Datos incompletos"}), 400
            
        # Obtener datos del formulario
        nombre = data.get("name", "").strip()
        email = data.get("email", "").strip()
        telefono = data.get("phone", "").strip()
        plan_interes = data.get("plan_type", "").strip()
        mensaje = data.get("message", "").strip()
        
        # Validaciones básicas
        if not nombre or not email or not telefono:
            return jsonify({"error": "Por favor completa todos los campos requeridos"}), 400
        
        # Enviar correo
        if enviar_correo_confirmacion(
            os.getenv("ASESORA_SEGUROS_EMAIL"),
            nombre,
            email,
            telefono,
            plan_interes,
            mensaje
        ):
            app.logger.info(f"✅ Cotización enviada: {nombre} - {email}")
            return jsonify({
                "status": "success", 
                "message": "¡Gracias! Nuestra asesora te contactará en menos de 24 horas."
            })
        else:
            app.logger.error("❌ Error al enviar correo de cotización")
            return jsonify({"error": "Error al enviar la solicitud. Por favor intenta nuevamente."}), 500
            
    except Exception as e:
        app.logger.error(f"❌ Error en enviar-cotizacion: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Ruta principal que sirve tu landing page
@app.route('/')
def landing_page():
    # Aquí pega TODO el código HTML que te di anteriormente
    # (el de la landing page completo)
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    return html_content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.logger.info("🚀 Iniciando servidor de Seguros Confianza...")
    app.run(host='0.0.0.0', port=port, debug=True)