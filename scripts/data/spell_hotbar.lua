local SpellHotbar = {}

SpellHotbar.by_spell = {
    ["1101"] = {
        submenu_label = "Harm/Heal",
        command_preview = "PREPARE 1101, then choose Harm or Heal",
        actions = {
            {
                key = "harm",
                label = "Harm",
                description = "Attack a hostile target with empathic harm.",
                verb = "cast",
                targeting = "current_target_optional",
                command_preview = "CAST <hostile>",
            },
            {
                key = "heal_self",
                label = "Heal Self",
                description = "Channel empathic healing into yourself to restore health.",
                verb = "channel",
                targeting = "self_only",
                command_preview = "CHANNEL SELF",
            },
            {
                key = "heal_other",
                label = "Heal Player",
                description = "Channel empathic healing into a visible player in the room.",
                verb = "channel",
                targeting = "room_player_only",
                command_preview = "CHANNEL <player>",
            },
        },
    },
}

return SpellHotbar
