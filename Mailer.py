import os
import re
import socket
import smtplib
from ntpath import basename

from ntlm.ntlm import create_NTLM_NEGOTIATE_MESSAGE, parse_NTLM_CHALLENGE_MESSAGE, create_NTLM_AUTHENTICATE_MESSAGE
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# noinspection PyUnresolvedReferences
from pprint import pprint as pp

# Regular expression for email address validation
eregex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class Mailer:
    # Response codes
    SMTP_EHLO_OKAY      = 250
    SMTP_AUTH_CHALLENGE = 334
    SMTP_AUTH_OKAY      = 235
    SMTP_AUTH_ERROR     = 530

    # Mandatory settings
    auth: str
    host: str
    port: int

    # Optional setings
    username: str = None
    password: str = None

    # Properties set via dedicated methods
    mailcc: str
    mailto: list
    mailfrom: str

    def __init__(self, **kwargs):
        """ Possible arguments to start with

        * **str** `auth`       - SMTP auth type [login, ntlm]
        * **str** `host`       - SMTP hostname or IP-address
        * **int** `port`       - SMTP port number
        * **str** `username`   - SMTP username
        * **str** `password`   - SMTP password

        :raises AttributeError if mandatory attribute is missing or attributes mutually exclude/mismatch
        :raises ValueError if one of given attributes fails during validation
        :raises ConnectionRefusedError authentication error
        :raises ConnectionError server can not be reached or connection is filtered/firewalled
        """
        self.__setattribues(kwargs)
        self.text        = ''
        self.subject     = ''
        self.attachments = []
        self.__message   = MIMEMultipart()
        self.__server    = None

    # noinspection PyBroadException
    def __del__(self):
        try:
            self.__server.close()
        except:
            pass

    def __setattribues(self, attrs) -> None:
        """ Validating and setting attributes for Mailer class

        :param attrs: dictionary of kwargs from Mailer.__init__
        :type attrs: dict
        """
        # Run dynamic validation
        for key, value in attrs.items():
            if hasattr(MailerValidator, key) and callable(getattr(MailerValidator, key)):
                if getattr(MailerValidator, key)(value):
                    setattr(self, key, value)
        # Check for mandatory attributes
        for a in ["auth", "host", "port"]:
            if not hasattr(self, a):
                raise AttributeError(f"Mandatory attribute '{a}' has not been set")
        # If password set, username must exist and vice versa
        if "password" in attrs.keys() and "username" not in attrs.keys():
            raise AttributeError(f"If you are giving password, ensure username also presents")
        if "username" in attrs.keys() and "password" not in attrs.keys():
            raise AttributeError(f"If you are giving username, ensure password also presents")
        # If you auth ntlm is used, then username must contain domain
        if self.auth == "ntlm" and (not self.username or "\\" not in self.username):
            raise AttributeError("AUTH NTLM: username does not contain domain name")

    def __presend_validation(self) -> None:
        """ Validating attributes within send() before actual sending an e-mail. Useful in case
        if somehow attributes were overwritten or set directly instead of setters
        """
        attrs = list(self.__dict__.keys())
        if not all(e in attrs for e in ['auth', 'host', 'port', 'mailfrom', 'mailto']):
            raise AttributeError("One of mandatory attributes is missing")
        for attr in attrs:
            value = getattr(self, attr)
            if hasattr(MailerValidator, attr) and callable(getattr(MailerValidator, attr)):
                getattr(MailerValidator, attr)(value)
            elif hasattr(MessageValidator, attr) and callable(getattr(MessageValidator, attr)):
                getattr(MessageValidator, attr)(value)

    def add_to(self, val):
        """ Set mail recipient(-s)

        :param val: single email address, string of comma or semicolon delimeted addresses or a list of addresses
        :type val: Union[str, list]

        :return: self
        """
        MessageValidator.mailto(val)
        if isinstance(val, str):
            val = val.replace(';', ',')
            val = val.split(",")
        self.mailto = [x.strip() for x in val]
        return self

    def add_cc(self, val):
        """ Set mail carbon copy recipient(-s)

        :param val: single email address, string of comma or semicolon delimeted addresses or a list of addresses
        :type val: Union[str, list]

        :return: self
        """
        MessageValidator.mailto(val)
        if isinstance(val, list):
            val = list(dict.fromkeys(val))
            val = ", ".join(val)
        val = val.replace(';', ',')
        self.mailcc = val
        return self

    def add_from(self, val):
        """ Set mail sender address. If server needs an authentication, make sure sender address matches the account
        credentials you are using.

        :param val: single email address
        :type val: str

        :return: self
        """
        MessageValidator.mailfrom(val)
        self.mailfrom = val
        return self

    def add_subject(self, val):
        """ Set mail subject

        :param val: subject text
        :type val: str

        :return: self
        """
        MessageValidator.subject(val)
        self.subject = val if val is not None else ''
        return self

    def add_attachment(self, val):
        """ Set mail attachment

        :param val: path to a file that should be attached
        :type val: str

        :return: self
        """
        MessageValidator.attachment(val, self.attachments)
        self.attachments.append(val)
        return self

    def add_text(self, val):
        """ Set mail body text

        :param val: message body text
        :type val: str

        :return: self
        """
        MessageValidator.text(val)
        self.text = val if val is not None else ''
        return self

    def login(self):
        """ AUTH LOGIN handler
        """
        self.__server.login(self.username, self.password)

    def ntlm(self):
        """ AUTH NTLM handler
        """
        args      = "NTLM " + create_NTLM_NEGOTIATE_MESSAGE(self.username).decode("utf-8")
        code, res = self.__server.docmd("AUTH", args)

        if code != self.SMTP_AUTH_CHALLENGE:
            raise ConnectionAbortedError("Server did not respond as expected to NTLM negotiate message")

        chlng, flags = parse_NTLM_CHALLENGE_MESSAGE(res)
        user_parts   = self.username.split("\\", 1)
        args         = create_NTLM_AUTHENTICATE_MESSAGE(chlng, user_parts[1], user_parts[0], self.password, flags)
        args         = args.decode("utf-8")
        code, res    = self.__server.docmd("", args)

        if code != self.SMTP_AUTH_OKAY:
            raise ConnectionRefusedError(res)

    def send(self) -> dict:
        """ Send e-mail.
        Method incapsulates validation and message building.

        :return: dict
        """
        self.__presend_validation()
        self.__build_message()

        try:
            self.__server = smtplib.SMTP(
                host=self.host,
                port=self.port,
            )

            ehlo_code, ehlo_message = self.__server.ehlo()
            if ehlo_code != self.SMTP_EHLO_OKAY:
                self.__server.close()
                raise ConnectionError("Server did not respond 250 OK to the EHLO greeting")

            ehlo_message = ehlo_message.decode("ansi")
            if self.auth is not None and not re.search(rf"AUTH.+{self.auth}\n", ehlo_message, re.IGNORECASE):
                self.__server.close()
                raise ConnectionAbortedError("Server did not respond with supported authentication type")

            if self.username and self.password:
                getattr(self, str(self.auth))()

            result = self.__server.sendmail(
                from_addr=self.mailfrom,
                to_addrs=self.mailto,
                msg=self.__message.as_string()
            )
            self.__server.close()
            self.reset()
            return result
        except (smtplib.SMTPSenderRefused, smtplib.SMTPAuthenticationError) as e:
            raise ConnectionRefusedError(str(e.smtp_error)) from e
        except (socket.gaierror, OSError) as e:
            raise ConnectionError("Unable to connect to SMTP server") from e

    def reset(self):
        """ Clear message data if there're multiple mails being sent one after another.
            This method is necessary to clear attributes, leaving server connection
            properties intact.
        """
        self.__message   = MIMEMultipart()
        self.__server    = None
        self.text        = ''
        self.subject     = ''
        self.attachments = []
        self.mailcc      = ''
        self.mailto      = []
        self.mailfrom    = ''

    def get_message(self) -> str:
        """ For debugging purposes only - don't use in live scripts.
        Get current message text representation.

        :return: current message text representation
        :rtype: str
        """
        self.__message = MIMEMultipart()
        self.__build_message()
        return self.__message.as_string()

    def __build_message(self) -> None:
        """ Build message from previously set attributes
        """
        self.__message["From"]    = self.mailfrom
        self.__message["To"]      = ", ".join(self.mailto)
        self.__message["Subject"] = self.subject
        if hasattr(self, 'mailcc') and self.mailcc:
            self.__message["Cc"]  = self.mailcc
        self.__message.attach(MIMEText(self.text, "plain"))

        if self.attachments:
            for attach in self.attachments:
                with open(attach, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={basename(attach)}",
                )
                self.__message.attach(part)


# Validation rules for Mailer class __init__ kwargs/atributes
class MailerValidator:

    @staticmethod
    def auth(val):
        if val is None:
            return True
        if not isinstance(val, str) or val.lower() not in ["login", "ntlm"]:
            raise ValueError("Wrong attribute for 'auth'")
        return True

    @staticmethod
    def host(val):
        if isinstance(val, str) and re.match(r"\d+\.\d+\.\d+\.\d", val):
            try:
                socket.inet_aton(val)
            except socket.error:
                raise ValueError("Incorrect host IP-adress")
        if not isinstance(val, str) or len(val) < 1:
            raise ValueError("Incorrect hostname")
        return True

    @staticmethod
    def port(val):
        if not isinstance(val, int) or val > 65535 or val < 1:
            raise ValueError("Wrong port number")
        return True

    @staticmethod
    def username(val):
        if not isinstance(val, str) or len(val) < 1:
            raise ValueError("Incorrect username")
        return True

    @staticmethod
    def password(val):
        if not isinstance(val, str) or len(val) < 1:
            raise ValueError("Incorrect password")
        return True


# Validation rules for message attributes
class MessageValidator:

    @staticmethod
    def attachment(val, attachments):
        if val is None:
            return True
        if not isinstance(val, str):
            raise ValueError("Attachment must be either None or string")
        if not os.path.isfile(val):
            raise FileNotFoundError("Attachment file does not exist")
        if val in attachments:
            raise ValueError("Atachments must be unique files, unable to attach the same file twice")
        return True

    @staticmethod
    def subject(val):
        if val is not None and not isinstance(val, str):
            raise ValueError("Subject must be either None or string")
        return True

    @staticmethod
    def mailfrom(val):
        if not isinstance(val, str) or not re.search(eregex, val):
            raise ValueError("Invalid 'From' e-mail address")
        return True

    @staticmethod
    def mailto(val):
        if not isinstance(val, str) and not isinstance(val, list):
            raise ValueError("Fields 'To' and 'CC' must be either string or list")
        if isinstance(val, str):
            val = val.replace(';', ',')
            val = [x.strip() for x in val.split(",")]
        if isinstance(val, list):
            for addr in val:
                if not re.search(eregex, addr):
                    raise ValueError("Invalid entry in 'To' or 'CC' list")
        return True

    @staticmethod
    def text(val):
        if val is not None and not isinstance(val, str):
            raise ValueError("Message text must be either None or string")
        return True
