from dataclasses import dataclass, field


@dataclass
class PromptShieldResult:
    user_prompt_attack: bool
    document_attack: bool

    @property
    def attack_detected(self) -> bool:
        return (
            self.user_prompt_attack
            or self.document_attack
        )


@dataclass
class ContentSafetyResult:
    hate: int
    self_harm: int
    sexual: int
    violence: int

    blocklist_matches: list[str] = field(
        default_factory=list
    )

    @property
    def max_severity(self) -> int:
        return max(
            self.hate,
            self.self_harm,
            self.sexual,
            self.violence,
        )

    @property
    def blocklist_match_detected(self) -> bool:
        return bool(
            self.blocklist_matches
        )

    def exceeds_threshold(
        self,
        threshold: int,
    ) -> bool:
        return (
            self.max_severity >= threshold
        )