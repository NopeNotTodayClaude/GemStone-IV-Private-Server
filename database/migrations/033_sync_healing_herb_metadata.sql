-- Sync core healing-herb metadata with the canonical Lua wound system.
-- Keeps existing shop stock intact; only corrects herb classification/details.

UPDATE items
SET
    herb_heal_type = 'blood',
    herb_heal_amount = 10,
    herb_heal_severity = 'minor',
    description = 'Blood Loss | Restores a small amount of health and helps slow bleeding.'
WHERE id = 601;

UPDATE items
SET
    herb_heal_type = 'wound',
    herb_heal_amount = 0,
    herb_heal_severity = 'minor',
    description = 'Minor Nerve Wound | Eases light nerve trauma and twitching.'
WHERE id = 602;

UPDATE items
SET
    herb_heal_type = 'scar',
    herb_heal_amount = 0,
    herb_heal_severity = 'scar_minor',
    description = 'Minor Nerve Scar | Reduces lingering minor nerve scarring once the wound is gone.'
WHERE id = 603;

UPDATE items
SET
    herb_heal_type = 'scar',
    herb_heal_amount = 0,
    herb_heal_severity = 'scar_major',
    description = 'Major Nerve Scar | Reduces deep, lingering nerve scarring once the wound is gone.'
WHERE id = 604;

UPDATE items
SET
    herb_heal_type = 'wound',
    herb_heal_amount = 0,
    herb_heal_severity = 'minor',
    description = 'Minor Organ Wound | Helps close lighter torso and eye injuries.'
WHERE id = 605;

UPDATE items
SET
    herb_heal_type = 'wound',
    herb_heal_amount = 0,
    herb_heal_severity = 'minor',
    description = 'Minor Limb Wound | Helps close lighter arm, hand, and leg injuries.'
WHERE id = 606;

UPDATE items
SET
    herb_heal_type = 'scar',
    herb_heal_amount = 0,
    herb_heal_severity = 'scar_minor',
    description = 'Minor Head Scar | Softens lighter scars on the head and neck once the wound is gone.'
WHERE id = 607;

UPDATE items
SET
    herb_heal_type = 'scar',
    herb_heal_amount = 0,
    herb_heal_severity = 'scar_minor',
    description = 'Minor Limb Scar | Softens lighter scars on the arms, hands, and legs once the wound is gone.'
WHERE id = 608;

UPDATE items
SET
    herb_heal_type = 'wound',
    herb_heal_amount = 0,
    herb_heal_severity = 'major',
    description = 'Major Head Wound | Helps close serious head and neck injuries.'
WHERE id = 609;

UPDATE items
SET
    herb_heal_type = 'wound',
    herb_heal_amount = 0,
    herb_heal_severity = 'major',
    description = 'Major Organ Wound | Helps close serious torso and eye injuries.'
WHERE id = 610;

UPDATE items
SET
    herb_heal_type = 'wound',
    herb_heal_amount = 0,
    herb_heal_severity = 'major',
    description = 'Major Limb Wound | Helps close serious arm, hand, and leg injuries.'
WHERE id = 611;

UPDATE items
SET
    herb_heal_type = 'scar',
    herb_heal_amount = 0,
    herb_heal_severity = 'scar_major',
    description = 'Major Limb Scar | Softens deep scars on the arms, hands, and legs once the wound is gone.'
WHERE id = 612;

UPDATE items
SET
    herb_heal_type = 'limb_regen',
    herb_heal_amount = 0,
    herb_heal_severity = 'missing',
    description = 'Severed Limb | Restores a missing or severed limb.'
WHERE id = 613;

UPDATE items
SET
    herb_heal_type = 'blood',
    herb_heal_amount = 15,
    herb_heal_severity = 'minor',
    description = 'Blood Loss | Restores a moderate amount of health and helps slow bleeding.'
WHERE id = 614;

UPDATE items
SET
    herb_heal_type = 'blood',
    herb_heal_amount = 50,
    herb_heal_severity = 'major',
    description = 'Blood Loss | Restores a large amount of health and helps slow bleeding.'
WHERE id = 615;

UPDATE items
SET
    herb_heal_type = 'wound',
    herb_heal_amount = 0,
    herb_heal_severity = 'major',
    description = 'Major Nerve Wound | Eases serious nerve trauma and paralysis.'
WHERE id = 616;

UPDATE items
SET
    herb_heal_type = 'wound',
    herb_heal_amount = 0,
    herb_heal_severity = 'minor',
    description = 'Minor Head Wound | Helps close lighter head and neck injuries.'
WHERE id = 617;

UPDATE items
SET
    herb_heal_type = 'scar',
    herb_heal_amount = 0,
    herb_heal_severity = 'scar_major',
    description = 'Major Head Scar | Softens deep scars on the head and neck once the wound is gone.'
WHERE id = 618;

UPDATE items
SET
    herb_heal_type = 'scar',
    herb_heal_amount = 0,
    herb_heal_severity = 'scar_minor',
    description = 'Minor Organ Scar | Softens lighter scars on the chest, abdomen, back, and eyes once the wound is gone.'
WHERE id = 619;

UPDATE items
SET
    herb_heal_type = 'scar',
    herb_heal_amount = 0,
    herb_heal_severity = 'scar_major',
    description = 'Major Organ Scar | Softens deep scars on the chest, abdomen, back, and eyes once the wound is gone.'
WHERE id = 620;

UPDATE items
SET
    herb_heal_type = 'eye_regen',
    herb_heal_amount = 0,
    herb_heal_severity = 'missing',
    description = 'Missing Eye | Restores a destroyed or missing eye.'
WHERE id = 621;
