import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from dotenv import load_dotenv
import os

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_welcome_email(to_email: str, username: str):
    """Envoie un email de bienvenue personnalisé pour KAUZA'CV."""

    subject = "Bienvenue sur KAUZA’CV – Votre compte a été créé avec succès !"

    html_template = Template("""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <h2>Bonjour {{ username }} 👋</h2>

            <p>
                Félicitations ! Votre compte a été créé avec succès sur <strong>KAUZA’CV</strong>.  
                Nous sommes ravis de vous accueillir parmi nous !
            </p>

            <p>Grâce à votre compte, vous pouvez désormais :</p>

            <ul>
                <li>Créer des CV professionnels optimisés pour les systèmes ATS</li>
                <li>Accéder à votre tableau de bord personnalisé</li>
                <li>Générer automatiquement des CV avec l’intelligence artificielle</li>
                <li>Importer et analyser un CV depuis un fichier</li>
            </ul>

            <p>
                Si vous avez la moindre question, notre équipe reste disponible pour vous accompagner à tout moment.
            </p>

            <p style="margin-top: 30px;">
                Encore une fois, bienvenue dans la communauté <strong>KAUZA’CV</strong> 🌟<br>
                <strong>L’équipe KAUZA’CV</strong>
            </p>
        </body>
        </html>
    """)

    html_content = html_template.render(username=username)

    # Construire l'email
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    # Envoi SMTP
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())

        print(f"Email envoyé à {to_email}")
        return True

    except Exception as e:
        print("EMAIL ERROR:", e)
        return False
