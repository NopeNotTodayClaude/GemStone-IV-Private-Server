---------------------------------------------------
-- data/starter_gear.lua
-- Starting equipment per profession for new characters.
-- Sourced from gswiki.play.net new player documentation.
--
-- Item IDs match the gemstone_items_seed.sql seeding order.
-- Containers MUST be listed before items placed inside them.
--
-- slot values (worn locations):
--   "back"           backpack worn on back
--   "belt"           belt pouch/scabbard
--   "shoulders"      cloak or mantle
--   "torso"          armor
--   "shoulder_slung" shield worn on shoulder/back
--   "right_hand"     item held in right hand
--   "left_hand"      item held in left hand
--
-- container values (noun of container to put item inside):
--   "backpack"       into the back-worn backpack
--   "pouch"          into the belt pouch
--   "scabbard"       into a belt scabbard
--
-- hand: "right" or "left"  (places item directly in that hand)
---------------------------------------------------

local StarterGear = {}

-- ── Starting silver per profession ────────────────────────────────────────────
StarterGear.starting_silver = {
    [1]  = 5000,  -- Warrior
    [2]  = 5000,  -- Rogue
    [3]  = 5000,  -- Wizard
    [4]  = 5000,  -- Cleric
    [5]  = 5000,  -- Empath
    [6]  = 5000,  -- Sorcerer
    [7]  = 5000,  -- Ranger
    [8]  = 5000,  -- Bard
    [9]  = 5000,  -- Paladin
    [10] = 5000,  -- Monk
}

-- ── Starter item kits per profession ─────────────────────────────────────────
-- Containers must appear before items that go inside them.
StarterGear.kits = {

    -- ── [1] WARRIOR ────────────────────────────────────────────────────────────
    [1] = {
        description = "Warrior Starter Kit",
        items = {
            -- Containers first
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=238, name="a belt pouch",              slot="belt"           },
            { item_id=241, name="an adventurer's cloak",     slot="shoulders"      },
            -- Armor (reinforced leather - warriors start with 2 armor ranks)
            { item_id=75,  name="some reinforced leather armor", slot="torso"      },
            -- Shield slung on back; warrior starts with shield use
            { item_id=94,  name="a steel target shield",     slot="shoulder_slung" },
            -- Primary weapon: longsword in right hand
            { item_id=9,   name="a steel longsword",         hand="right"          },
            -- Backup dagger in backpack
            { item_id=2,   name="a steel dagger",            container="backpack"  },
            -- Small healing supply in backpack
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
        },
    },

    -- ── [2] ROGUE ──────────────────────────────────────────────────────────────
    [2] = {
        description = "Rogue Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=238, name="a belt pouch",              slot="belt"           },
            { item_id=241, name="an adventurer's cloak",     slot="shoulders"      },
            { item_id=73,  name="some light leather armor",  slot="torso"          },
            { item_id=93,  name="a steel buckler",           slot="shoulder_slung" },
            { item_id=7,   name="a steel short sword",       hand="right"          },
            { item_id=2,   name="a steel dagger",            container="backpack"  },
            -- Lockpicks in belt pouch
            { item_id=205, name="a crude lockpick",          container="pouch"     },
            { item_id=205, name="a crude lockpick",          container="pouch"     },
            { item_id=206, name="a simple lockpick",         container="pouch"     },
            { item_id=206, name="a simple lockpick",         container="pouch"     },
            { item_id=207, name="a standard lockpick",       container="pouch"     },
        },
    },

    -- ── [3] WIZARD ─────────────────────────────────────────────────────────────
    [3] = {
        description = "Wizard Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=239, name="a herb pouch",              slot="belt"           },
            { item_id=242, name="a flowing silk cloak",      slot="shoulders"      },
            -- Robes (ASG 2) - wizards cannot wear heavy armor
            { item_id=352, name="some flowing robes",        slot="torso"          },
            -- Runestaff in right hand
            { item_id=101, name="a wooden runestaff",        hand="right"          },
            -- Arcane symbol component in backpack
            { item_id=750, name="a copper symbol",           container="backpack"  },
            -- Mana herb supply
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
        },
    },

    -- ── [4] CLERIC ─────────────────────────────────────────────────────────────
    [4] = {
        description = "Cleric Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=238, name="a belt pouch",              slot="belt"           },
            { item_id=243, name="a white linen cloak",       slot="shoulders"      },
            -- Double leather armor (clerics train moderate armor)
            { item_id=76,  name="some double leather armor", slot="torso"          },
            -- Target shield (clerics use shields)
            { item_id=94,  name="a steel target shield",     slot="shoulder_slung" },
            -- Mace in right hand
            { item_id=52,  name="a steel mace",              hand="right"          },
            -- Holy symbol in pouch
            { item_id=751, name="a holy symbol",             container="pouch"     },
            -- Healing herbs
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=602, name="some wolifrew lichen",      container="backpack"  },
            { item_id=603, name="some torban leaf",          container="backpack"  },
        },
    },

    -- ── [5] EMPATH ─────────────────────────────────────────────────────────────
    [5] = {
        description = "Empath Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=239, name="a herb pouch",              slot="belt"           },
            { item_id=244, name="a pale green cloak",        slot="shoulders"      },
            -- Robes (empaths typically wear robes or light leather)
            { item_id=352, name="some flowing robes",        slot="torso"          },
            -- Runestaff (empaths use runestaves for DS)
            { item_id=101, name="a wooden runestaff",        hand="right"          },
            -- Full herb kit in herb pouch - empaths are healers
            { item_id=601, name="some acantha leaf",         container="pouch"     },
            { item_id=601, name="some acantha leaf",         container="pouch"     },
            { item_id=602, name="some wolifrew lichen",      container="pouch"     },
            { item_id=603, name="some torban leaf",          container="pouch"     },
            { item_id=604, name="some woth flower",          container="pouch"     },
            { item_id=605, name="some basal moss",           container="pouch"     },
            { item_id=606, name="some ambrominas leaf",      container="pouch"     },
            { item_id=607, name="some haphip root",          container="backpack"  },
            { item_id=608, name="some cactacae spine",       container="backpack"  },
            { item_id=609, name="some aloeas stem",          container="backpack"  },
        },
    },

    -- ── [6] SORCERER ───────────────────────────────────────────────────────────
    [6] = {
        description = "Sorcerer Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=239, name="a herb pouch",              slot="belt"           },
            { item_id=245, name="a dark silk cloak",         slot="shoulders"      },
            -- Robes (sorcerers avoid heavy armor)
            { item_id=352, name="some flowing robes",        slot="torso"          },
            -- Runestaff
            { item_id=101, name="a wooden runestaff",        hand="right"          },
            -- Arcane components
            { item_id=750, name="a copper symbol",           container="backpack"  },
            { item_id=752, name="a vaalin stylus",           container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
        },
    },

    -- ── [7] RANGER ─────────────────────────────────────────────────────────────
    [7] = {
        description = "Ranger Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=238, name="a belt pouch",              slot="belt"           },
            { item_id=246, name="a forest green cloak",      slot="shoulders"      },
            -- Light leather armor (rangers avoid heavy armor)
            { item_id=73,  name="some light leather armor",  slot="torso"          },
            -- Short sword as primary (rangers favor edged or ranged)
            { item_id=7,   name="a steel short sword",       hand="right"          },
            -- Short bow in backpack (rangers train ranged)
            { item_id=201, name="a short bow",               container="backpack"  },
            -- Arrows in backpack
            { item_id=211, name="a bundle of arrows",        container="backpack"  },
            { item_id=211, name="a bundle of arrows",        container="backpack"  },
            -- Survival herbs
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=602, name="some wolifrew lichen",      container="pouch"     },
        },
    },

    -- ── [8] BARD ───────────────────────────────────────────────────────────────
    [8] = {
        description = "Bard Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=238, name="a belt pouch",              slot="belt"           },
            { item_id=247, name="a colorful traveling cloak",slot="shoulders"      },
            -- Full leather (bards are semi, moderate armor)
            { item_id=74,  name="some full leather armor",   slot="torso"          },
            -- Short sword (bards fight with weapons)
            { item_id=7,   name="a steel short sword",       hand="right"          },
            -- Lute (instrument) in backpack - bards use songs
            { item_id=760, name="a simple wooden lute",      container="backpack"  },
            { item_id=2,   name="a steel dagger",            container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
        },
    },

    -- ── [9] PALADIN ────────────────────────────────────────────────────────────
    [9] = {
        description = "Paladin Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=238, name="a belt pouch",              slot="belt"           },
            { item_id=248, name="a white tabard cloak",      slot="shoulders"      },
            -- Reinforced leather (paladins train armor well)
            { item_id=75,  name="some reinforced leather armor", slot="torso"      },
            -- Target shield (paladins are shield users)
            { item_id=94,  name="a steel target shield",     slot="shoulder_slung" },
            -- Broadsword
            { item_id=12,  name="a steel broadsword",        hand="right"          },
            -- Holy symbol in pouch
            { item_id=751, name="a holy symbol",             container="pouch"     },
            -- Healing herbs
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=602, name="some wolifrew lichen",      container="backpack"  },
        },
    },

    -- ── [10] MONK ──────────────────────────────────────────────────────────────
    [10] = {
        description = "Monk Starter Kit",
        items = {
            { item_id=236, name="a leather backpack",        slot="back"           },
            { item_id=238, name="a belt pouch",              slot="belt"           },
            { item_id=249, name="a rough-spun monk's cloak", slot="shoulders"      },
            -- Padded armor or light leather (monks prefer low encumbrance)
            { item_id=353, name="some padded armor",         slot="torso"          },
            -- Cestus as brawling weapon
            { item_id=302, name="a steel cestus",            hand="right"          },
            -- Monks carry minimal gear
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
            { item_id=601, name="some acantha leaf",         container="backpack"  },
        },
    },
}

return StarterGear
