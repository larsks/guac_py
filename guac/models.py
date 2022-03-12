import enum
import pydantic

from typing import Optional


class SystemPermissionsEnum(str, enum.Enum):
    ADMINISTER = "ADMINISTER"
    CREATE_CONNECTION = "CREATE_CONNECTION"
    CREATE_CONNECTION_GROUP = "CREATE_CONNECTION_GROUP"
    CREATE_SHARING_PROFILE = "CREATE_SHARING_PROFILE"
    CREATE_USER = "CREATE_USER"
    CREATE_USER_GROUP = "CREATE_USER_GROUP"


class PermissionsEnum(str, enum.Enum):
    READ = "READ"


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
    disabled: str | None = ""
    expired: str | None = ""
    access_window_start: str | None = ""
    access_window_end: str | None = ""
    valid_from: str | None = ""
    valid_until: str | None = ""
    timezone: str | None = None
    guac_full_name: str | None = ""
    guac_organization: str | None = ""
    guac_organizational_role: str | None = ""


class GroupPermissions(Base):
    connectionPermissions: dict[str, list[PermissionsEnum]]
    connectionGroupPermissions: dict[str, str]
    sharingProfilePermissions: dict[str, str]
    activeConnectionPermissions: dict[str, str]
    userPermissions: dict[str, list[PermissionsEnum]]
    userGroupPermissions: dict[str, str]
    systemPermissions: list[SystemPermissionsEnum]


class UserPermissions(GroupPermissions):
    pass


class User(Base):
    username: str = ""
    password: str = ""
    attributes: UserAttributes = pydantic.Field(default_factory=UserAttributes)
    permissions: UserPermissions | None


class GroupAttributes(Base):
    disabled: str | None = ""


class Group(Base):
    identifier: str = ""
    attributes: GroupAttributes = pydantic.Field(default_factory=GroupAttributes)
    permissions: GroupPermissions | None
