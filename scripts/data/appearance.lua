---------------------------------------------------
-- data/appearance.lua
-- Character creation appearance options, stat metadata,
-- suggested stat builds, cultures, and age ranges.
--
-- Sources:
--   gswiki.play.net/Culture
--   gswiki.play.net/AGE_(verb)
--   gswiki.play.net/Statistic
---------------------------------------------------

local Appearance = {}

-- ── HAIR COLORS ───────────────────────────────────────────────────────────────
Appearance.hair_colors = {
    "black", "dark brown", "auburn", "brown", "light brown",
    "blonde", "golden blonde", "platinum blonde", "red", "copper",
    "silver", "white", "blue-black", "strawberry blonde",
}

-- ── HAIR STYLES ───────────────────────────────────────────────────────────────
Appearance.hair_styles = {
    "short", "long", "shoulder-length", "waist-length",
    "cropped", "braided", "tied back", "loose", "curly",
    "straight", "wavy", "wild", "neatly combed", "shaved",
}

-- ── EYE COLORS ────────────────────────────────────────────────────────────────
Appearance.eye_colors = {
    "blue", "green", "brown", "hazel", "grey",
    "amber", "violet", "dark", "emerald", "sapphire",
    "golden", "silver", "black", "sea green", "stormy grey",
}

-- ── SKIN TONES ────────────────────────────────────────────────────────────────
Appearance.skin_tones = {
    "fair", "pale", "tanned", "olive", "dark",
    "dusky", "bronze", "ivory", "sun-kissed", "alabaster",
}

-- ── STAT NAMES, ABBREVIATIONS, KEYS ──────────────────────────────────────────
-- Index order: STR CON DEX AGI DIS AUR LOG INT WIS INF (0-based in Python, 1-based in Lua)
Appearance.stat_names = {
    "Strength", "Constitution", "Dexterity", "Agility", "Discipline",
    "Aura", "Logic", "Intuition", "Wisdom", "Influence",
}

Appearance.stat_abbrevs = {
    "STR", "CON", "DEX", "AGI", "DIS",
    "AUR", "LOG", "INT", "WIS", "INF",
}

Appearance.stat_keys = {
    "strength", "constitution", "dexterity", "agility", "discipline",
    "aura", "logic", "intuition", "wisdom", "influence",
}

-- ── STAT DESCRIPTIONS (shown during character creation) ───────────────────────
-- Index 1=STR ... 10=INF
Appearance.stat_descriptions = {
    [1]  = "Physical power. Affects melee AS, carrying capacity before encumbrance.",
    [2]  = "Durability. Determines max HP, disease resistance, critical hit defense.",
    [3]  = "Hand-eye coordination. Lockpicking, pickpocketing, ranged aiming, dual wield.",
    [4]  = "Grace and nimbleness. Directly affects DS, dodge, balance, initiative.",
    [5]  = "Force of will. Experience absorption before rest, mental attack resistance.",
    [6]  = "Spiritual/elemental connection. Spirit points, elemental TD/CS, mana (casters).",
    [7]  = "Reasoning ability. Experience absorption, magic item activation, arcane TD/CS.",
    [8]  = "Instinctive awareness. Trap detection, perception, stalking, ambush.",
    [9]  = "Pragmatism and spiritual insight. Spiritual TD/CS, mana for semis.",
    [10] = "Charisma and persuasion. Trading, mind-affecting magic, social skills.",
}

-- ── SUGGESTED STAT BUILDS ─────────────────────────────────────────────────────
-- [STR, CON, DEX, AGI, DIS, AUR, LOG, INT, WIS, INF]
-- All builds total exactly 660 points (640 base + 20 prime bonus).
-- Prof IDs: 1=Warrior 2=Rogue 3=Wizard 4=Cleric 5=Empath
--           6=Sorcerer 7=Ranger 8=Bard 9=Paladin 10=Monk
Appearance.suggested_stats = {
    [1]  = { 90, 85, 65, 65, 70, 40, 40, 55, 40, 70 },  -- Warrior
    [2]  = { 60, 50, 92, 90, 68, 45, 50, 80, 40, 45 },  -- Rogue
    [3]  = { 40, 50, 50, 60, 70, 95, 90, 55, 55, 55 },  -- Wizard
    [4]  = { 50, 60, 50, 55, 60, 55, 55, 80, 92, 63 },  -- Cleric
    [5]  = { 40, 60, 50, 55, 65, 55, 50, 60, 90, 95 },  -- Empath
    [6]  = { 40, 50, 50, 55, 65, 95, 90, 55, 80, 40 },  -- Sorcerer
    [7]  = { 65, 55, 90, 65, 65, 50, 45, 85, 55, 40 },  -- Ranger
    [8]  = { 50, 50, 60, 60, 55, 70, 50, 60, 50, 95 },  -- Bard
    [9]  = { 90, 80, 55, 60, 65, 50, 40, 50, 90, 40 },  -- Paladin
    [10] = { 80, 65, 60, 90, 85, 50, 55, 60, 40, 35 },  -- Monk
}

-- ── CULTURES BY RACE ─────────────────────────────────────────────────────────
-- Source: gswiki.play.net/Culture
-- race_id matches races.lua
-- culture_key is the internal identifier (lowercase, underscored)
-- name is the display name
-- desc is a brief description for the selection menu
Appearance.cultures = {

    -- Human (race_id=1)
    [1] = {
        label = "Human Cultures",
        options = {
            { key="aelendyl",   name="Aelendyl",      desc="Maritime culture of the western coastlands, skilled sailors and traders." },
            { key="aradenai",   name="Aradenai",       desc="Highland culture known for fierce independence and warrior tradition." },
            { key="bourth",     name="Bourth",         desc="Central plains farmers and craftsmen who value community above all." },
            { key="cynarith",   name="Cynarith",       desc="River delta culture of merchants and diplomats." },
            { key="dhe_nar",    name="Dhe'nar-aligned", desc="Humans who live among or share the culture of the Dhe'nar dark elves." },
            { key="estild",     name="Estild",         desc="Northern forest hunters and trappers, self-sufficient and pragmatic." },
            { key="khanshael",  name="Khanshael-aligned", desc="Humans deeply intertwined with dwarven Khanshael culture." },
            { key="murkwood",   name="Murkwood",       desc="Swamp-dwelling humans known for herbalism and survival skills." },
            { key="tehir",      name="Tehir",          desc="Desert nomads of the Tehir sands, proud and fierce warriors." },
            { key="seareach",   name="Seareach",       desc="Island seafarers known for exploration and trade." },
            { key="none",       name="No Culture",     desc="Your character has no specific cultural affiliation. May be selected later with TITLE SET CULTURE." },
        },
    },

    -- Elf (race_id=2)
    [2] = {
        label = "Elf Cultures",
        options = {
            { key="ardenai",    name="Ardenai",        desc="The forest elves, deeply connected to nature and ancient magic." },
            { key="illistim",   name="Illistim",       desc="Scholars and mages of House Illistim, seekers of arcane knowledge." },
            { key="loenthra",   name="Loenthra",       desc="Artists and bards of House Loenthra, celebrating beauty and expression." },
            { key="nalfein",    name="Nalfein",        desc="Merchants and spymasters of House Nalfein, masters of subtlety." },
            { key="vaalor",     name="Vaalor",         desc="Warriors of House Vaalor, disciplined defenders of elven civilization." },
            { key="ornathian",  name="Ornathian",      desc="Elves from the Isle of Ornath, touched by the old powers." },
            { key="none",       name="No Culture",     desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Dark Elf (race_id=3)
    [3] = {
        label = "Dark Elf Cultures",
        options = {
            { key="dhenar",     name="Dhe'nar",        desc="The shadow-walkers, followers of Luukos. Cunning, ruthless, proud." },
            { key="evashir",    name="Evashir",        desc="Dark elves of the eastern reaches, pragmatic and independent." },
            { key="faendryl",   name="Faendryl",       desc="Exiled sorcerers of House Faendryl, masters of forbidden magic." },
            { key="ornathian",  name="Ornathian",      desc="Dark elves from the Isle of Ornath, touched by ancient powers." },
            { key="none",       name="No Culture",     desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Half-Elf (race_id=4)
    [4] = {
        label = "Half-Elf Cultures",
        options = {
            { key="ardenai",    name="Ardenai-raised",  desc="Raised among the Ardenai forest elves, embracing their nature." },
            { key="vaalor",     name="Vaalor-raised",   desc="Raised in the martial culture of Vaalor elves." },
            { key="human",      name="Human-raised",    desc="Raised among humans, more comfortable in human society." },
            { key="tehir",      name="Tehir-raised",    desc="Raised among the Tehir desert nomads." },
            { key="none",       name="No Culture",      desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Dwarf (race_id=5)
    [5] = {
        label = "Dwarf Clans",
        options = {
            { key="borthuum",   name="Borthuum Clan",   desc="Iron miners of the deep stone, stocky and stubborn." },
            { key="egrentek",   name="Egrentek Clan",   desc="Weapon-crafters renowned across Elanthia." },
            { key="gotronek",   name="Gotronek Clan",   desc="Stone-shapers and architects of great underground halls." },
            { key="greetok",    name="Greetok Clan",    desc="Traders and travelers, more worldly than most dwarves." },
            { key="grevnek",    name="Grevnek Clan",    desc="Fierce warriors known for their berserker traditions." },
            { key="gulroten",   name="Gulroten Clan",   desc="Gem-cutters with an unmatched eye for precious stones." },
            { key="kazunel",    name="Kazunel Clan",    desc="Scholars of dwarven history and runic lore." },
            { key="khanshael",  name="Khanshael",       desc="Outcast dwarves who speak the Dhe'nar language and share their ways." },
            { key="kikthuum",   name="Kikthuum Clan",   desc="Mountain scouts and rangers of the high peaks." },
            { key="krenlumtrek",name="Krenlumtrek Clan", desc="Seafaring dwarves of the coastal holds, unusual among their kin." },
            { key="mithrenek",  name="Mithrenek Clan",  desc="Mithril-smiths who produce legendary arms and armor." },
            { key="none",       name="No Culture",      desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Halfling (race_id=6)
    [6] = {
        label = "Halfling Cultures",
        options = {
            { key="shire",      name="Shire Halfling",  desc="Homebodies of the fertile lowlands, fond of comfort and good food." },
            { key="wanderer",   name="Wandering Halfling", desc="Footloose halflings who travel constantly, acquiring skills and stories." },
            { key="burrow",     name="Burrow Halfling",  desc="Tunnel-dwellers who share traditions with dwarven culture." },
            { key="none",       name="No Culture",      desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Giantman (race_id=7)
    [7] = {
        label = "Giantman Clans",
        options = {
            { key="aradenai",   name="Aradenai Clan",   desc="Highland giantmen, the most common clan in the western lands." },
            { key="blood",      name="Blood Clan",      desc="Fierce warrior giantmen with a tradition of ritual combat." },
            { key="dobrek",     name="Dobrek Clan",     desc="Northern giantmen adapted to harsh arctic conditions." },
            { key="kalerk",     name="Kalerk Clan",     desc="Coastal giantmen skilled in fishing and seafaring." },
            { key="none",       name="No Culture",      desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Forest Gnome (race_id=8)
    [8] = {
        label = "Forest Gnome Bloodlines",
        options = {
            { key="greel",      name="Greel Bloodline",  desc="Gnomes with an affinity for animals and the deep forest." },
            { key="loaber",     name="Loaber Bloodline", desc="Gnomes known for invention and tinkering with the natural world." },
            { key="mhoragian",  name="Mhoragian Bloodline", desc="Gnomes of the northern woods, hardy and resourceful." },
            { key="none",       name="No Culture",       desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Burghal Gnome (race_id=9)
    [9] = {
        label = "Burghal Gnome Bloodlines",
        options = {
            { key="aledotter",  name="Aledotter Bloodline",  desc="Urban gnomes known for their breweries and social connections." },
            { key="neimhean",   name="Neimhean Bloodline",   desc="Gnomes with a gift for illusion magic and misdirection." },
            { key="nylem",      name="Nylem Bloodline",      desc="Clockwork artificers who push the boundaries of gnomish invention." },
            { key="vylem",      name="Vylem Bloodline",      desc="Merchants and financiers, moving silver through hidden channels." },
            { key="winedotter", name="Winedotter Bloodline", desc="Vintners and sommeliers with a refined palate and sharp eye." },
            { key="withycombe", name="Withycombe Bloodline", desc="Gnomes of the country estates, genteel and well-mannered." },
            { key="none",       name="No Culture",           desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Sylvankind (race_id=10)
    [10] = {
        label = "Sylvankind D'ahranals",
        options = {
            { key="forest",     name="Forest D'ahranalin", desc="Sylvans of the deep wood, communing with ancient trees." },
            { key="glade",      name="Glade D'ahranalin",  desc="Sylvans of the open glades, light-touched and fleet of foot." },
            { key="river",      name="River D'ahranalin",  desc="Sylvans of the river valleys, adaptable and flowing like water." },
            { key="none",       name="No Culture",         desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Aelotoi (race_id=11)
    [11] = {
        label = "Aelotoi Clans",
        options = {
            { key="cyrtaeni",   name="Cyrtae'ni Clan",  desc="Aelotoi survivors known for their adaptability and quick thinking." },
            { key="gaehdeh",    name="Gaeh'deh Clan",   desc="Warriors among the Aelotoi, bearing the scars of their escape." },
            { key="mraeni",     name="Mrae'ni Clan",    desc="Healers and empaths, tending wounds of body and spirit." },
            { key="vaersah",    name="Vaer'sah Clan",   desc="Scholars preserving what remains of Aelotoi culture and history." },
            { key="none",       name="No Culture",      desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Erithian (race_id=12)
    [12] = {
        label = "Erithian Dai",
        options = {
            { key="eloth",      name="Eloth Dai",   desc="Scholars of the Eloth order, pursuing arcane and philosophical knowledge." },
            { key="nathala",    name="Nathala Dai", desc="Martial artists of the Nathala order, disciplined warrior-monks." },
            { key="surath",     name="Surath Dai",  desc="Merchants of the Surath order, building wealth and influence across Elanthia." },
            { key="tichan",     name="Tichan Dai",  desc="Healers of the Tichan order, practitioners of both herb-craft and empath arts." },
            { key="valaka",     name="Valaka Dai",  desc="Spies and intelligence-gatherers of the Valaka order." },
            { key="volnath",    name="Volnath Dai", desc="Warriors of the Volnath order, sworn blades in service of Erithia." },
            { key="yachan",     name="Yachan Dai",  desc="Spirit-speakers of the Yachan order, communing with ancestors." },
            { key="none",       name="No Culture",  desc="Your character has no specific cultural affiliation." },
        },
    },

    -- Half-Krolvin (race_id=13)
    [13] = {
        label = "Half-Krolvin Klinasts",
        options = {
            { key="froskar",    name="Froskar Klinast",  desc="Half-Krolvin raised among the Krolvin sea raiders, fierce and proud." },
            { key="sharath",    name="Sharath Klinast",  desc="Half-Krolvin raised on land, straddling both human and Krolvin worlds." },
            { key="none",       name="No Culture",       desc="Your character has no specific cultural affiliation." },
        },
    },
}

-- ── AGE RANGES BY RACE ────────────────────────────────────────────────────────
-- Source: gswiki.play.net/AGE_(verb) - Age Ranges table
-- Columns: new_adult, young_adult, adult, approaching_middle, middle_aged,
--          leaving_middle, mature, retiring, old, very_old, extremely_old
-- Each value is { min, max } for that age stage.
-- Races sharing the same table are grouped.
Appearance.age_ranges = {
    -- Human (1), Aelotoi (11) share the same age table
    [1]  = { {20,25}, {26,31}, {32,37}, {38,43}, {44,49}, {50,55}, {56,61}, {62,67}, {68,73}, {74,79}, {80,999} },
    [11] = { {20,25}, {26,31}, {32,37}, {38,43}, {44,49}, {50,55}, {56,61}, {62,67}, {68,73}, {74,79}, {80,999} },

    -- Half-Krolvin (13)
    [13] = { {16,23}, {24,31}, {32,39}, {40,47}, {48,55}, {56,63}, {64,71}, {72,79}, {80,87}, {88,95}, {96,999} },

    -- Giantman (7)
    [7]  = { {20,27}, {28,35}, {36,43}, {44,51}, {52,59}, {60,67}, {68,75}, {76,83}, {84,91}, {92,99}, {100,999} },

    -- Halfling (6)
    [6]  = { {20,27}, {28,35}, {36,43}, {44,51}, {52,59}, {60,67}, {68,75}, {76,83}, {84,91}, {92,99}, {100,999} },

    -- Burghal Gnome (9)
    [9]  = { {20,35}, {36,51}, {52,67}, {68,83}, {84,99}, {100,115}, {116,131}, {132,147}, {148,163}, {164,179}, {180,999} },

    -- Dwarf (5)
    [5]  = { {30,44}, {45,59}, {60,74}, {75,89}, {90,104}, {105,119}, {120,134}, {135,149}, {150,165}, {166,181}, {182,999} },

    -- Forest Gnome (8)
    [8]  = { {20,37}, {38,55}, {56,73}, {74,91}, {92,109}, {110,127}, {128,145}, {146,163}, {164,181}, {182,199}, {200,999} },

    -- Half-Elf (4)
    [4]  = { {25,61}, {62,98}, {99,135}, {136,172}, {173,209}, {210,246}, {247,283}, {284,320}, {321,357}, {358,394}, {395,999} },

    -- Erithian (12)
    [12] = { {15,55}, {56,96}, {97,137}, {138,178}, {179,219}, {220,260}, {261,301}, {302,342}, {343,383}, {384,424}, {425,999} },

    -- Elf (2), Dark Elf (3), Sylvankind (10) share the same table
    [2]  = { {30,176}, {177,323}, {324,470}, {471,617}, {618,764}, {765,911}, {912,1058}, {1059,1205}, {1206,1352}, {1353,1499}, {1500,9999} },
    [3]  = { {30,176}, {177,323}, {324,470}, {471,617}, {618,764}, {765,911}, {912,1058}, {1059,1205}, {1206,1352}, {1353,1499}, {1500,9999} },
    [10] = { {30,176}, {177,323}, {324,470}, {471,617}, {618,764}, {765,911}, {912,1058}, {1059,1205}, {1206,1352}, {1353,1499}, {1500,9999} },
}

-- Age stage labels (same for all races)
Appearance.age_stage_names = {
    "New Adult", "Young Adult", "Adult", "Approaching Middle Age",
    "Middle Aged", "Leaving Middle Aged", "Mature", "Retiring",
    "Old", "Very Old", "Extremely Old",
}

return Appearance
