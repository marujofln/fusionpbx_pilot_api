from pydantic import BaseModel


class SIPProvisioning(BaseModel):
    """
    Schema for SIP provisioning data.
    """

    display_name: str
    user: str
    password: str
    domain: str
    uri: str


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
