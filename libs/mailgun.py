import os
from typing import List
from requests import Response, post

from libs.strings import gettext


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", None)
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", None)
    FROM_EMAIL = " mailgun@sandbox32da1783382f4f179450826de0756764.mailgun.org"
    FROM_TITLE = "Jos Montes Inc."

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(gettext("mailgun_api_key_error"))
        if cls.MAILGUN_DOMAIN is None:
            raise MailgunException(gettext("mailgun_domain_error"))

        print(email)

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            },
        )

        if response.status_code != 200:
            print(response.status_code)
            print(response.__dict__)
            raise MailgunException(gettext("mailgun_email_error"))

        return response
