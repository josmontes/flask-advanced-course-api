import os
from typing import List
from requests import Response, post

API_KEY_ERROR = "Failed to load Mailgun API key."
DOMAIN_ERROR = "Failed to load Mailgun Domain."


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")  # can be None
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")  # can be None
    FROM_EMAIL = " mailgun@sandbox32da1783382f4f179450826de0756764.mailgun.org"
    FROM_TITLE = "Jos Montes, Inc."

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(API_KEY_ERROR)
        if cls.MAILGUN_DOMAIN is None:
            raise MailgunException(DOMAIN_ERROR)

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
            raise MailgunException("Error in sending email.")

        return response
