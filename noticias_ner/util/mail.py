import configparser
import os
import smtplib
import ssl
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Adiciona diretorio raiz ao PATH. Devido a ausência de setup.py, isto garante que as importações sempre funcionarão
diretorio_raiz = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)
sys.path.append(diretorio_raiz)

from noticias_ner import config


def enviar_email(arquivos, assunto, text, html):
    """
    Envia um e-mail para o destinatário especificado no arquivo noticias_ner.cfg.
    :param arquivos: Caminhos para os arquivos a serem enviado como anexos.
    :param assunto: Assunto da mensagem.
    :param text: Conteúdo da mensagem em formato texto.
    :param html: Conteúdo da mensagem em formato HTML.
    :return:
    """
    credencial, porta, receiver_email, sender_email, servidor_smtp = __get_configuracoes()
    message = __criar_mensagem(arquivos, assunto, html, receiver_email, sender_email, text)
    text = message.as_string()

    try:
        server = smtplib.SMTP(servidor_smtp, porta)
        server.sendmail(sender_email, receiver_email.split(','), text)
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()
        print('Executou server.quit()')


def __criar_mensagem(arquivos, assunto, html, receiver_email, sender_email, text):
    # Cria uma mensagem multipart e define os cabeçalhos
    message = MIMEMultipart('alternative')
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    # Adiciona partes HTML/texto à mensagem
    # O cliente de e-mail tenará renderizar primeiramente a última parte
    message.attach(part1)
    message.attach(part2)
    message["From"] = sender_email
    message["To"] = sender_email
    message["Subject"] = assunto
    message["Bcc"] = receiver_email  # Recommended for mass emails
    __anexar_arquivos(arquivos, message)
    return message


def __anexar_arquivos(arquivos, message):
    for arquivo, nome_arquivo in arquivos:
        # Abre o arquivo a ser anexado em modo binário
        with open(arquivo, "rb") as attachment:
            # Adiciona o arquivo como application/octet-stream
            # Clientes de e-mail normalmente conseguem baixar o arquivo automaticamente como anexo.
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Codifica o arquivo em caracteres ASCII para envia-lo por e-mail
        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {nome_arquivo}",
        )

        # Adiciona o anexo à mensagem e converte a mensagem em string
        message.attach(part)


def __get_configuracoes():
    cfg = configparser.ConfigParser()
    cfg.read_file(open(config.arquivo_config))
    sender_email = cfg.get('mail', 'sender_email')
    receiver_email = cfg.get('mail', 'receiver_email')
    servidor_smtp = cfg.get('mail', 'smtp')
    porta = cfg.get('mail', 'port')
    credencial = cfg.get('mail', 'sender_pwd')
    return credencial, porta, receiver_email, sender_email, servidor_smtp
