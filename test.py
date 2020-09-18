import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Download the helper library from https://www.twilio.com/docs/python/install
# from twilio.rest import Client


# # Your Account Sid and Auth Token from twilio.com/console
# # DANGER! This is insecure. See http://twil.io/secure
# account_sid = 'AC99c11c35fb5623c437c7d549f684069e'
# auth_token = '0784814e5484fe69909c65e0657785f7'
# client = Client(account_sid, auth_token)

# call = client.calls.create(
#                         url='http://demo.twilio.com/docs/voice.xml',
#                         to='+14252832729',
#                         from_='+15086904064'
#                     )

# print(call.sid)
# import the smtplib module. It should be included in Python by default
import smtplib
# set up the SMTP server
s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
s.starttls()
s.login(MY_ADDRESS, PASSWORD)
msg = MIMEMultipart() 
msg['From']=MY_ADDRESS
msg['To']='lucasdmoyer@gmail.com'
msg['Subject']="This is TEST"
message="hello"
# add in the message body
msg.attach(MIMEText(message, 'plain'))

# send the message via the server set up earlier.
s.send_message(msg)
del msg