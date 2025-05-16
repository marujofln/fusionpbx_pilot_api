from pydantic import BaseModel


class SIPProvisioning(BaseModel):
    """
    Schema for SIP provisioning data.
    """

    user: str
    password: str
    domain: str


class DetailMessage(BaseModel):
    """
    Schema for detail message.
    """

    message: str


class Extension(BaseModel):
    """
    Schema for extension data.
    """

    name: str
    uuid: str
    password: str
    voicemail_mail_to: str
    voicemail_enabled: bool


class Domain(BaseModel):
    """
    Schema for domain data.
    """

    name: str
