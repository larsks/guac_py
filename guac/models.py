import pydantic

from typing import Optional


class ConnectionParameters(pydantic.BaseModel):
    pass


class RDPConnectionParameters(ConnectionParameters):
    class Config:
        alias_generator = lambda x: x.replace("_", "-")
        allow_population_by_field_name = True

    port: str = ""
    dest_port: str = ""
    ignore_cert: str = "true"
    gateway_port: str = ""
    hostname: str = ""
    username: str = ""
    password: str = ""
    domain: str = ""
    gateway_hostname: str = ""
    gateway_username: str = ""
    gateway_password: str = ""
    gateway_domain: str = ""


class SSHConnectionParameters(ConnectionParameters):
    class Config:
        alias_generator = lambda x: x.replace("_", "-")
        allow_population_by_field_name = True

    port: str = ""
    dest_port: str = ""
    backspace: str = ""
    terminal_type: str = "xterm-256color"
    hostname: str = ""
    host_key: str = ""
    private_key: str = ""
    username: str = ""
    password: str = ""
    passphrase: str = ""
    command: str = ""


class ConnectionAttributes(pydantic.BaseModel):
    max_connections: str = ""
    max_connections_per_user: str = ""
    weight: str = ""
    failover_only: str = ""
    guacd_port: str = ""
    guacd_encryption: str = ""


class Connection(pydantic.BaseModel):
    parentIdentifier: str = "ROOT"
    name: str
    protocol: str
    parameters: ConnectionParameters = pydantic.Field(
        default_factory=ConnectionParameters
    )
    attributes: ConnectionAttributes = pydantic.Field(
        default_factory=ConnectionAttributes
    )


class UserAttributes(pydantic.BaseModel):
    disabled: str = ""
    expired: str = ""
    access_window_start: str = ""
    access_window_end: str = ""
    valid_from: str = ""
    valid_until: str = ""
    timezone: Optional[str] = None
    guac_full_name: str = ""
    guac_organization: str = ""
    guac_organizational_role: str = ""


class User(pydantic.BaseModel):
    username: str = ""
    password: str = ""
    attributes: UserAttributes = pydantic.Field(default_factory=UserAttributes)
