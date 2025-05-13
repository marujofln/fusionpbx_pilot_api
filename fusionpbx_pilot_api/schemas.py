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
