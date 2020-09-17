# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage


# Create a text/plain message
msg = EmailMessage()
msg.set_content("este é um email de teste...")

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = f'Testando...'
msg['From'] = 'moniquebm@tcu.gov.br'
msg['To'] = 'moniquelouise@gmail.com'

# Send the message via our own SMTP server.
s = smtplib.SMTP('smtp.tcu.gov.br')
s.send_message(msg)
s.quit()