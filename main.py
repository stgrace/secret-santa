from config import settings
from loguru import logger
import yaml
import sys
import copy
from random import shuffle
import smtplib
from email.message import EmailMessage
from time import sleep
import logging
from email.mime.text import MIMEText

email_content = """
Gegroet {name}!

Dit jaar voor secret santa heb jij {target}

Succes dermee
"""
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0)

logger.remove()
logger.add(sys.stdout, level=settings.log_level)

class Person:
    def __init__(self, name, partner, email):
        self.name = name
        self.partner = partner
        self.email = email
        self.target = None
    def __str__(self):
        return f"{self.name} -> {self.target}"
    def __repr__(self) -> str:
        return self.__str__()

def verify_target(p):
    if p.target != p.name and p.target != p.partner:
        return True
    return False

def match_target(bowl, targets):
    shuffle(targets)
    shuffle(bowl)
    for i, p in enumerate(bowl):
        p.target = targets[i].name
        if not verify_target(p):
            match_target(bowl, targets)

def send_email(bowl):
    for p in bowl:
        msg = EmailMessage()
        msg = MIMEText(email_content.format(name = p.name, target = p.target))
        msg['Subject'] = 'Secret santa'
        msg['From'] = settings.email_user
        msg['To'] = p.email
        with smtplib.SMTP(settings.email_server, 587) as s:
            s.ehlo('mylowercasehost')
            s.starttls()
            s.ehlo('mylowercasehost')
            logger.info("Logging in to mail server")
            logger.debug(f"Email: {settings.email_account}")
            logger.debug(f"Email password: {settings.email_password}")
            s.login(settings.email_account, settings.email_password)
            logger.info(f"Sending email to {p.email}")
            s.sendmail(settings.email_account, [p.email], msg.as_string())
        sleep(5)
        
        
def main():
    with open(settings.santa_file) as w:
        persons = yaml.load(w.read(), Loader=yaml.SafeLoader)
        logger.debug(f"YAML load: {persons}")
        bowl = []
        for person in persons:
            p = Person(person['name'], person['partner'], person['email'])
            bowl.append(p)
            logger.debug(f"Added {p} to the bowl")
        logger.debug(f"The bowl {bowl}")
    targets = copy.deepcopy(bowl)
    match_target(bowl, targets)
    logger.info("Matched target with everybody")
    logger.debug(f"The bowl with targets: {bowl}")
    send_email(bowl)

if __name__ == "__main__":
    main()