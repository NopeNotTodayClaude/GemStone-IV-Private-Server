---------------------------------------------------
-- data/starter_spells.lua
-- Starter spell research per profession for new characters.
-- Loader-driven so profession spellbooks can scale cleanly later.
--
-- ranks:
--   [circle_id] = known spell count in that circle
-- A value of 1 grants the first castable spell in that circle.
---------------------------------------------------

local StarterSpells = {}

StarterSpells.kits = {
    [3] = {
        description = "Wizard Starter Spellbook",
        ranks = {
            [8] = 1, -- Wizard Base: 901 Minor Shock
        },
    },
    [4] = {
        description = "Cleric Starter Spellbook",
        ranks = {
            [3] = 1, -- Cleric Base: 301 Prayer of Holding
        },
    },
    [5] = {
        description = "Empath Starter Spellbook",
        ranks = {
            [10] = 1, -- Empath Base: 1101 Harm/Heal
        },
    },
    [6] = {
        description = "Sorcerer Starter Spellbook",
        ranks = {
            [7] = 1, -- Sorcerer Base: 701 Blood Burst
        },
    },
    [7] = {
        description = "Ranger Starter Spellbook",
        ranks = {
            [6] = 1, -- Ranger Base: 601 Natural Colors
        },
    },
    [8] = {
        description = "Bard Starter Spellbook",
        ranks = {
            [9] = 1, -- Bard Base: 1001 Holding Song
        },
    },
    [9] = {
        description = "Paladin Starter Spellbook",
        ranks = {
            [11] = 1, -- Paladin Base: 1601 Mantle of Faith
        },
    },
    [10] = {
        description = "Monk Starter Spellbook",
        ranks = {
            [12] = 1, -- Minor Mental: 1201 Soothing Word
        },
    },
}

return StarterSpells
