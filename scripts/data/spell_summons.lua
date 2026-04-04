------------------------------------------------------------------------
-- scripts/data/spell_summons.lua
-- Data-driven runtime definitions for spell-created summoned entities.
------------------------------------------------------------------------

return {
    by_spell = {
        ["511"] = {
            summon_key = "floating_disk",
            entity_kind = "disk",
            template_short_name = "floating disk",
            slot = "floating_disk",
            default_capacity = 8,
            max_weight = 500,
            empty_verb = "turn",
            dismiss_verb = true,
            show_in_room = true,
            room_line = "You also see a shimmering floating disk hovering near %s.",
            look_lines = {
                "A circular platform of elemental force hangs in the air without effort.",
                "It drifts after its owner and exists to carry burdens that would otherwise drag them down.",
            },
        },
        ["218"] = {
            summon_key = "spirit_servant",
            entity_kind = "servant",
            template_short_name = "spirit servant",
            slot = "spirit_servant",
            hand_capacity = 2,
            show_in_room = true,
            room_line = "You also see a translucent spirit servant lingering near %s.",
            away_room_line = "You also see a translucent spirit servant hovering here, watchful and awaiting instruction.",
            look_lines = {
                "A pale servant-spirit hovers just above the ground, its form wavering like moonlight on disturbed water.",
                "Its attention is fixed on simple tasks: carrying, fetching, scouting, and preserving what its master cannot keep in hand.",
            },
            commands = {
                get = true,
                give = true,
                drop = true,
                go = true,
                report = true,
                return_home = true,
                dismiss = true,
                recover = true,
            },
        },
    },
}
