-- scripts/globals/seals.lua
-- Global seal-award configuration driven from Lua.

local Seals = {
    enabled = true,

    defaults = {
        drop_chance = 0.30,
        quantity = 1,
        stack_cap = 999,
        allowed_sources = { "*" },
        auto_mark = true,
        announce = true,
    },

    seal_types = {
        beastmen = {
            key = "beastmen",
            item_short_name = "beastmen seal",
            display_name = "Beastmen Seal",
            drop_chance = 0.30,
            quantity = 1,
            stack_cap = 999,
            allowed_sources = { "*" },
            auto_mark = true,
            announce = true,
            message = "  You receive a Beastmen Seal.",
        },
    },
}

return Seals
