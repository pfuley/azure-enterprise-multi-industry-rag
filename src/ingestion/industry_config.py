from dataclasses import dataclass, field


@dataclass
class IndustryConfig:
    industry: str
    department: str
    document_type: str
    classification: str = "internal"

    allowed_groups: list[str] = field(
        default_factory=list
    )

    allowed_roles: list[str] = field(
        default_factory=list
    )