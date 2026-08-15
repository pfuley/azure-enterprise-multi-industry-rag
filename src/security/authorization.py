from dataclasses import dataclass, field


@dataclass
class AuthorizationContext:
    user_id: str

    roles: list[str] = field(
        default_factory=list
    )

    groups: list[str] = field(
        default_factory=list
    )

    allowed_industries: list[str] = field(
        default_factory=list
    )

    allowed_departments: list[str] = field(
        default_factory=list
    )

    max_classification: str = "public"