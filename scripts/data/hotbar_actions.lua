return {
    categories = {
        {
            key = "weapon_techniques",
            label = "Weapon Techniques",
            provider = "weapon_techniques",
            sort_order = 10,
        },
        {
            key = "combat_maneuvers",
            label = "Combat Maneuvers",
            provider = "combat_maneuvers",
            sort_order = 20,
        },
        {
            key = "magic",
            label = "Magic",
            provider = "magic",
            sort_order = 30,
        },
    },

    combat_maneuvers = {
        {
            key = "feint",
            label = "Feint",
            command_template = "feint",
            targeting = "current_target_optional",
            sort_order = 10,
            description = "Throw a foe off balance and lower its defenses for your next attack.",
        },
        {
            key = "sweep",
            label = "Sweep",
            command_template = "sweep {target}",
            targeting = "current_target_required",
            sort_order = 20,
            description = "Knock a target off its feet with your Rogue Guild sweep training.",
        },
        {
            key = "subdue",
            label = "Subdue",
            command_template = "subdue {target}",
            targeting = "current_target_required",
            sort_order = 30,
            description = "Spring from hiding and disable a target with Rogue Guild subdue training.",
        },
        {
            key = "cheapshot",
            label = "Cheapshot",
            command_template = "cheapshot {target}",
            targeting = "current_target_required",
            sort_order = 40,
            description = "Use your default cheapshot against the current target.",
        },
        {
            key = "rgambit_divert",
            label = "Divert",
            command_template = "rgambit divert {target}",
            targeting = "current_target_required",
            sort_order = 50,
            description = "Use Rogue Gambits to divert a target and open space.",
        },
    },
}
