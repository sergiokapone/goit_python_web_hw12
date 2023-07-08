from pathlib import Path
import pathlib

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from environs import Env

from services.auth import auth_service

file_env = pathlib.Path(__file__).parent.parent.parent.joinpath(".env")
env = Env()
env.read_env(file_env)

MAIL_USERNAME = env.str("MAIL_USERNAME")
MAIL_PASSWORD = env.str("MAIL_PASSWORD")
MAIL_SERVER = env.str("MAIL_SERVER")
MAIL_FROM_NAME = env.str("MAIL_FROM_NAME")

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=EmailStr(MAIL_USERNAME),
    MAIL_PORT=465,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, 
                           "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
