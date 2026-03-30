"""Shared player-facing outcome summaries for maneuvers and techniques."""

from __future__ import annotations


_CANONICAL_EFFECTS = {
    "blind": "blinded",
    "blinded": "blinded",
    "confused": "confused",
    "crippled": "crippled",
    "dazed": "dazed",
    "demoralized": "demoralized",
    "disoriented": "disoriented",
    "pinned": "pinned",
    "prone": "prone",
    "rooted": "rooted",
    "silenced": "silenced",
    "slowed": "slowed",
    "staggered": "staggered",
    "stunned": "stunned",
    "vulnerable": "vulnerable",
    "weakened_armament": "weakened_armament",
    "major_bleed": "major_bleed",
    "frenzy": "frenzy",
    "evasiveness": "evasiveness",
    "forceful_blows": "forceful_blows",
    "fortified_stance": "fortified_stance",
    "slashing_strikes": "slashing_strikes",
    "parry_bonus": "parry_bonus",
    "evade_bonus": "evade_bonus",
    "ds_bonus": "ds_bonus",
    "avoid_engagement_bonus": "avoid_engagement_bonus",
    "enhance_dexterity": "enhance_dexterity",
}


def canonical_effect(effect_id: str) -> str:
    raw = str(effect_id or "").strip().lower()
    return _CANONICAL_EFFECTS.get(raw, raw)


def entity_name(entity, fallback: str = "the target") -> str:
    return str(
        getattr(entity, "full_name", None)
        or getattr(entity, "name", None)
        or getattr(entity, "character_name", None)
        or fallback
    ).strip()


def effect_label(server, effect_id: str) -> str:
    effect = canonical_effect(effect_id)
    status = getattr(server, "status", None)
    if status and hasattr(status, "get_def"):
        try:
            row = status.get_def(effect) or {}
            label = str(row.get("name") or "").strip()
            if label:
                return label
        except Exception:
            pass
    return effect.replace("_", " ").title()


def effect_feedback_line(server, effect_id: str, *, entity=None, target_label: str = "defender") -> str:
    effect = canonical_effect(effect_id)
    if target_label in {"self", "self_and_party"}:
        if effect == "frenzy":
            return "You surge into a killing frenzy."
        if effect == "evasiveness":
            return "You become markedly harder to pin down."
        if effect == "forceful_blows":
            return "Your strikes carry extra force."
        if effect == "fortified_stance":
            return "You settle into a fortified stance."
        if effect == "slashing_strikes":
            return "Your edge-work sharpens into a relentless rhythm."
        if effect == "parry_bonus":
            return "Your parrying edge improves."
        if effect == "evade_bonus":
            return "Your evasive footwork sharpens."
        if effect == "ds_bonus":
            return "Your defenses rise."
        if effect == "avoid_engagement_bonus":
            return "You become harder to pin into melee."
        if effect == "enhance_dexterity":
            return "Your hands quicken noticeably."
        return f"You gain {effect_label(server, effect).lower()}."

    target = entity_name(entity)
    lead = target.capitalize()
    if effect == "prone":
        return f"{lead} is knocked to the ground."
    if effect == "vulnerable":
        return f"{lead} is left vulnerable."
    if effect == "staggered":
        return f"{lead} reels from the blow."
    if effect == "stunned":
        return f"{lead} is stunned."
    if effect == "blinded":
        return f"{lead} is blinded."
    if effect == "silenced":
        return f"{lead} is silenced."
    if effect == "demoralized":
        return f"{lead} looks shaken."
    if effect == "confused":
        return f"{lead} looks confused."
    if effect == "dazed":
        return f"{lead} looks dazed."
    if effect == "crippled":
        return f"{lead} is left badly hobbled."
    if effect == "slowed":
        return f"{lead} slows noticeably."
    if effect == "rooted":
        return f"{lead} is rooted in place."
    if effect == "pinned":
        return f"{lead} is pinned down."
    if effect == "disoriented":
        return f"{lead} looks badly disoriented."
    if effect == "weakened_armament":
        return f"{lead}'s weapon control falters."
    if effect == "major_bleed":
        return f"{lead} starts bleeding heavily."
    return f"{lead} is afflicted with {effect_label(server, effect).lower()}."


def summarize_applied_effects(server, applied_rows: list[dict]) -> list[str]:
    lines: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for row in applied_rows or []:
        if not isinstance(row, dict):
            continue
        effect = canonical_effect(str(row.get("effect") or ""))
        if not effect:
            continue
        entity = row.get("entity")
        target_label = str(row.get("target_label") or "defender").strip().lower()
        target_name = entity_name(entity, target_label)
        marker = (effect, target_label, target_name.lower())
        if marker in seen:
            continue
        seen.add(marker)
        lines.append(effect_feedback_line(server, effect, entity=entity, target_label=target_label))
    return lines
