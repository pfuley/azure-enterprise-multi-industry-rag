from dataclasses import dataclass


@dataclass
class IndustryConfig:
    industry: str
    department: str
    document_type: str
    classification: str = "internal"