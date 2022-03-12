import pydantic

from typing import Optional


class Base(pydantic.BaseModel):
    pass


class ConnectionParameters(Base):
    pass


class RDPConnectionParameters(ConnectionParameters):
    class Config:
        alias_generator = lambda x: x.replace("_", "-")
        allow_population_by_field_name = True

    create_drive_path: str = ""
    dest_port: str = ""
    domain: str = ""
    drive_name: str = ""
    drive_path: str = ""
    enable_drive: str = ""
    gateway_domain: str = ""
    gateway_hostname: str = ""
    gateway_password: str = ""
    gateway_port: str = ""
    gateway_username: str = ""
    hostname: str = ""
    ignore_cert: str = "true"
    password: str = ""
    port: str = ""
    username: str = ""


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


class ConnectionAttributes(Base):
    max_connections: str | None = ""
    max_connections_per_user: str | None = ""
    weight: str | None = ""
    failover_only: str | None = ""
    guacd_port: str | None = ""
    guacd_encryption: str | None = ""


class Connection(Base):
    id: str | None
    parentIdentifier: str = "ROOT"
    name: str
    protocol: str
    parameters: ConnectionParameters = pydantic.Field(
        default_factory=ConnectionParameters
    )
    attributes: ConnectionAttributes = pydantic.Field(
        default_factory=ConnectionAttributes
    )


class UserAttributes(Base):
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


class User(Base):
    username: str = ""
    password: str = ""
    attributes: UserAttributes = pydantic.Field(default_factory=UserAttributes)


class GroupAttributes(Base):
    disabled: str | None = ""


class GroupPermissions(Base):
    connectionPermissions: dict[str, list[str]]
    connectionGroupPermissions: dict[str, str]
    sharingProfilePermissions: dict[str, str]
    activeConnectionPermissions: dict[str, str]
    userPermissions: dict[str, str]
    userGroupPermissions: dict[str, str]
    systemPermissions: list[str]


class Group(Base):
    identifier: str = ""
    attributes: GroupAttributes = pydantic.Field(default_factory=GroupAttributes)
    permissions: GroupPermissions | None
