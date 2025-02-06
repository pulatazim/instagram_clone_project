import re
import threading
import phonenumbers
from decouple import config
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from twilio.rest import Client

email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
phone_regex = re.compile(r'(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+')
username_regex = re.compile(r'^[A-Za-z0-9.-_]+$')


def check_email_or_phone(email_or_phone):
    # print(email_or_phone)
    # phone_number = phonenumbers.parse(email_or_phone)

    if re.fullmatch(email_regex, email_or_phone):
        email_or_phone = 'email'

    elif re.fullmatch(phone_regex, email_or_phone):
        email_or_phone = 'phone'

    # elif phonenumbers.is_valid_number(phone_number):
    #     email_or_phone = 'phone'

    else:
        data = {
            "success": False,
            "message": "Email yoki telefonraqamingiz noto'gri"
        }
        raise ValidationError(data)
    return email_or_phone


def check_user_type(user_input):
    if re.fullmatch(email_regex, user_input):
        user_input = 'email'
    elif re.fullmatch(phone_regex, user_input):
        user_input = 'phone'
    elif re.fullmatch(username_regex, user_input):
        user_input = 'username'
    else:
        data = {
            "success": False,
            "message": "Username, Email yoki telefonraqamingiz noto'gri"
        }
        raise ValidationError(data)
    return user_input


class EmailThread(threading.Thread):
    """ Thread class to send emails """

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']],
        )
        if data.get('content_type') == "html":
            email.content_subtype = 'html'
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {'code': code}
    )
    Email.send_email(
        {
            "subject": "Ro'yhatdan o'tish",
            "to_email": email,
            "body": html_content,
            "content_type": "html"
        }
    )
    print(f"Bu kodni hech kimga bermang!-{code}")



def send_phone_code(phone, code):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Salom do'stim. Sizning tasdiqlash kodingiz: {code}\n",
        from_="+998993451588",
        to=f"{phone}",
    )
