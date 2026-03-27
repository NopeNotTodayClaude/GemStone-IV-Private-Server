---------------------------------------------------
-- data/crafting.lua
-- Shared Artisan Guild / crafting definitions.
-- Retail-aligned foundation:
--   ARTISAN verb
--   Artisan skill list / rank bands / unlearn preferences
--   Starter station + recipe metadata for later crafting loops
---------------------------------------------------

local Crafting = {}

Crafting.total_rank_limit = 1200

Crafting.rank_bands = {
    { key = "novice",          label = "Novice",         min = 0,   max = 99  },
    { key = "apprentice",      label = "Apprentice",     min = 100, max = 199 },
    { key = "journeyman",      label = "Journeyman",     min = 200, max = 299 },
    { key = "skilled",         label = "Skilled",        min = 300, max = 399 },
    { key = "highly_skilled",  label = "Highly-Skilled", min = 400, max = 499 },
    { key = "master",          label = "Master",         min = 500, max = 9999 },
}

Crafting.skill_order = {
    "cobbling",
    "fletching",
    "forging_brawling",
    "forging_crafting",
    "forging_ohe",
    "forging_ohb",
    "forging_pa",
    "forging_thw",
    "mining",
    "smelting",
}

Crafting.skills = {
    cobbling = {
        key = "cobbling",
        label = "Cobbling",
        command_token = "COBBLING",
        family = "artisan",
        retail_group = "artisan",
    },
    fletching = {
        key = "fletching",
        label = "Fletching",
        command_token = "FLETCHING",
        family = "artisan",
        retail_group = "artisan",
    },
    forging_brawling = {
        key = "forging_brawling",
        label = "Forging - Brawling",
        command_token = "FORGING-BRAWLING",
        family = "forging",
        retail_group = "forging",
        weapon_group = "brawling",
    },
    forging_crafting = {
        key = "forging_crafting",
        label = "Forging - Crafting",
        command_token = "FORGING-CRAFTING",
        family = "forging",
        retail_group = "forging",
        weapon_group = "crafting",
    },
    forging_ohe = {
        key = "forging_ohe",
        label = "Forging - One-Handed Edged",
        command_token = "FORGING-OHE",
        family = "forging",
        retail_group = "forging",
        weapon_group = "ohe",
    },
    forging_ohb = {
        key = "forging_ohb",
        label = "Forging - One-Handed Blunt",
        command_token = "FORGING-OHB",
        family = "forging",
        retail_group = "forging",
        weapon_group = "ohb",
    },
    forging_pa = {
        key = "forging_pa",
        label = "Forging - Polearms",
        command_token = "FORGING-PA",
        family = "forging",
        retail_group = "forging",
        weapon_group = "polearm",
    },
    forging_thw = {
        key = "forging_thw",
        label = "Forging - Two-Handed Weapons",
        command_token = "FORGING-THW",
        family = "forging",
        retail_group = "forging",
        weapon_group = "thw",
    },
    mining = {
        key = "mining",
        label = "Mining",
        command_token = "MINING",
        family = "artisan",
        retail_group = "artisan",
    },
    smelting = {
        key = "smelting",
        label = "Smelting",
        command_token = "SMELTING",
        family = "artisan",
        retail_group = "artisan",
    },
}

Crafting.stations = {
    fletching_bench = {
        key = "fletching_bench",
        label = "Fletching Bench",
        skills = { "fletching" },
        room_tags = { "fletching", "fletcher", "bowyer", "archery_workshop", "archery" },
    },
    cobbling_bench = {
        key = "cobbling_bench",
        label = "Cobbling Bench",
        skills = { "cobbling" },
        room_tags = { "cobbling", "cobbler", "cordwainer", "leather_workshop", "footwear" },
    },
    forge = {
        key = "forge",
        label = "Forge",
        skills = { "smelting", "forging_crafting", "forging_brawling", "forging_ohe", "forging_ohb", "forging_pa", "forging_thw" },
        room_tags = { "forge", "smithy", "anvil" },
    },
    mine = {
        key = "mine",
        label = "Mine",
        skills = { "mining" },
        room_tags = { "mine", "shaft", "quarry" },
    },
    smelter = {
        key = "smelter",
        label = "Smelter",
        skills = { "smelting" },
        room_tags = { "smelter", "foundry", "forge" },
    },
}

Crafting.recipes = {
    fletching_hunting_arrow = {
        key = "fletching_hunting_arrow",
        label = "Hunting Arrow",
        skill = "fletching",
        station = "fletching_bench",
        output_noun = "arrow",
        difficulty = "basic",
        output_item_short_name = "fletched hunting arrow",
        rank_projects = 3,
        rough_yield_min = 3,
        rough_yield_max = 3,
        item_keys = {
            wood_source = "smooth branch",
            shaft = "arrow shaft",
            glue = "bottle of fletching glue",
            fletchings = "bundle of goose fletchings",
            output = "fletched hunting arrow",
        },
        tools = {
            { key = "handaxe", label = "handaxe" },
            { key = "dagger",  label = "dagger" },
            { key = "bow",     label = "bow" },
        },
        materials = {
            { key = "wood_source", count = 1, label = "a smooth branch", consume = true },
            { key = "glue", count = 1, label = "a bottle of fletching glue", consume = false },
            { key = "fletchings", count = 1, label = "a bundle of goose fletchings", consume = true },
        },
        stages = {
            { key = "rough",   label = "Cut rough shafts",             command = "CUT ARROWS FROM MY BRANCH WITH MY HANDAXE" },
            { key = "pared",   label = "Pare the shaft",               command = "CUT MY SHAFT WITH MY DAGGER" },
            { key = "nocked",  label = "Cut nocks",                    command = "CUT NOCKS IN MY SHAFT WITH MY DAGGER" },
            { key = "measured",label = "Measure the shaft",            command = "MEASURE MY SHAFT WITH MY BOW" },
            { key = "trimmed", label = "Trim the shaft to length",     command = "CUT MY SHAFT WITH MY DAGGER" },
            { key = "glued",   label = "Apply glue",                   command = "PUT MY GLUE ON MY SHAFT" },
            { key = "fletched",label = "Attach fletchings",            command = "PUT MY FLETCHING ON MY SHAFT" },
            { key = "finished",label = "Whittle the point and finish", command = "CUT MY SHAFT WITH MY DAGGER" },
        },
    },
    cobbling_leather_slippers = {
        key = "cobbling_leather_slippers",
        label = "Leather Slippers",
        skill = "cobbling",
        station = "cobbling_bench",
        output_noun = "slippers",
        difficulty = "basic",
        output_item_short_name = "leather slippers",
        rank_projects = 3,
        item_keys = {
            upper = "leather upper",
            sole = "leather sole",
            chalk = "tailor's chalk",
            cord = "measuring cord",
            output = "leather slippers",
        },
        tools = {
            { key = "chalk",  label = "tailor's chalk" },
            { key = "dagger", label = "dagger" },
            { key = "cord",   label = "measuring cord" },
        },
        materials = {
            { key = "upper", count = 1, label = "a leather upper", consume = true },
            { key = "sole", count = 1, label = "a leather sole", consume = true },
            { key = "chalk", count = 1, label = "a piece of tailor's chalk", consume = false },
            { key = "cord", count = 1, label = "a measuring cord", consume = false },
        },
        stages = {
            { key = "started", label = "Join upper and sole",      command = "COBBLING START SLIPPERS" },
            { key = "chalked", label = "Mark the slippers",        command = "COBBLING CHALK MY SLIPPERS" },
            { key = "cut",     label = "Trim the edges",           command = "COBBLING CUT MY SLIPPERS" },
            { key = "fit",     label = "Measure the fit",          command = "COBBLING FIT MY SLIPPERS" },
            { key = "finished",label = "Finish the slippers",      command = "COBBLING FINISH MY SLIPPERS" },
        },
    },
    forging_iron_short_sword = {
        key = "forging_iron_short_sword",
        label = "Iron Short Sword",
        skill = "forging_ohe",
        station = "forge",
        output_noun = "short sword",
        difficulty = "basic",
        materials = {
            { key = "iron_ingot", count = 1 },
            { key = "forging_fuel", count = 1 },
        },
    },
}

return Crafting
