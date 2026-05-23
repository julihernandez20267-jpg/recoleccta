import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings

def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Sends an email to the user with the 6-character alphanumeric OTP verification code
    using the system configured SMTP mail settings.
    """
    try:
        # Create SMTP MIME message
        msg = MIMEMultipart()
        msg['From'] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        msg['To'] = to_email
        msg['Subject'] = f"Código de recuperación de contraseña: {otp_code}"
        
        # HTML formatted template for the email body
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f6f9f6; padding: 20px; color: #182018;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; border: 1px solid #dce4d8; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h2 style="color: #0d631b; margin: 0;">Recoleccta</h2>
                        <p style="font-size: 14px; color: #5c635a; margin: 5px 0 0 0;">Impacto positivo para el planeta</p>
                    </div>
                    <hr style="border: 0; border-top: 1px solid #e7ece4; margin-bottom: 24px;">
                    <p style="font-size: 16px; line-height: 24px;">Hola,</p>
                    <p style="font-size: 16px; line-height: 24px;">Hemos recibido una solicitud para restablecer la contraseña de tu cuenta. Tu código de verificación OTP (One-Time Password) es:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #0d631b; background-color: #edf2ec; padding: 12px 30px; border-radius: 8px; border: 1px solid #c8d3c4; display: inline-block;">{otp_code}</span>
                    </div>
                    <p style="font-size: 14px; color: #5c635a; line-height: 20px;">Este código es de un solo uso y expirará en 10 minutos. Si no has solicitado este cambio, por favor ignora este correo.</p>
                    <hr style="border: 0; border-top: 1px solid #e7ece4; margin-top: 30px; margin-bottom: 16px;">
                    <p style="font-size: 12px; color: #8e958d; text-align: center; margin: 0;">Trabajando por un mundo más limpio · © 2026 Recoleccta</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect to SMTP server and initialize security headers
        if settings.MAIL_SSL_TLS:
            server = smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT)
        else:
            server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
            if settings.MAIL_STARTTLS:
                server.starttls()
                
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())
        server.quit()
        print(f"OTP code {otp_code} successfully sent via SMTP to {to_email}")
        return True
    except Exception as e:
        print(f"SMTP Error encountered while sending email: {e}")
        return False
