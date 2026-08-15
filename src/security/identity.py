from dataclasses import dataclass, field


@dataclass
class UserIdentity:
    user_id: str

    display_name: str | None = None

    email: str | None = None

    roles: list[str] = field(
        default_factory=list
    )

    groups: list[str] = field(
        default_factory=list
    )

    authenticated: bool = False