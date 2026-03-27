---------------------------------------------------
-- scripts/data/items/materials.lua
-- All materials for GemStone IV private server.
--
-- Fields:
--   display         printable name
--   rarity          common / uncommon / rare / very_rare / extremely_rare
--   level_req       minimum character level to wield/wear
--   enchant_bonus   inherent magical bonus (contributes to AS/DS via _calc_effective_enchant)
--   attack_mod      flat AS modifier for weapons of this material
--   defense_mod     flat DS modifier for armor/shields of this material
--   cost_mult       price multiplier over base item cost
--   apply_to        array: which item types this material applies to
--   weight_modifier multiplier on base item weight (0.7 = 30% lighter)
--   hardness        durability tier 1-10
--   magical         can this material strike magical/incorporeal creatures?
--   rare            is this material hard to obtain / shop-restricted?
--   flare_type      elemental flare type or nil.  Consumed by flare_system.lua.
--                   Valid values: "cold", "fire", "lightning", "vibration"
--                   nil means no elemental flare.
--   crit_weight     phantom damage added to raw_damage BEFORE crit divisor.
--                   Used by crit_resolver.lua.  0 for all standard materials.
--                   razern = 2 (raises effective crit floor, per GS4 wiki CEP mechanic)
--   description     flavour text shown on INSPECT
---------------------------------------------------

local Materials = {}

Materials.list = {

    -- ── Common metals ─────────────────────────────────────────────────────────
    iron = {
        display        = "iron",
        rarity         = "common",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 1.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.0,
        hardness       = 4,
        magical        = false,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Ordinary iron.  No enchantment bonus.",
    },

    steel = {
        display        = "steel",
        rarity         = "common",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 1.2,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.0,
        hardness       = 5,
        magical        = false,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Quality steel.  Reliable and well-balanced.",
    },

    bronze = {
        display        = "bronze",
        rarity         = "common",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 1.0,
        apply_to       = { "weapon", "armor", "shield", "jewelry" },
        weight_modifier = 1.0,
        hardness       = 4,
        magical        = false,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Common bronze alloy.",
    },

    copper = {
        display        = "copper",
        rarity         = "common",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 0.9,
        apply_to       = { "weapon", "jewelry" },
        weight_modifier = 1.0,
        hardness       = 3,
        magical        = false,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Common copper.  Soft but workable.",
    },

    silver = {
        display        = "silver",
        rarity         = "uncommon",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 2.0,
        apply_to       = { "weapon", "jewelry" },
        weight_modifier = 1.0,
        hardness       = 3,
        magical        = true,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Pure silver.  Effective against certain undead.",
    },

    gold = {
        display        = "gold",
        rarity         = "uncommon",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 3.0,
        apply_to       = { "jewelry" },
        weight_modifier = 1.1,
        hardness       = 2,
        magical        = false,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Lustrous gold, popular for jewelry.",
    },

    -- ── Low enchant (level 5-10) ──────────────────────────────────────────────
    mithril = {
        display        = "mithril",
        rarity         = "uncommon",
        level_req      = 5,
        enchant_bonus  = 10,
        attack_mod     = 5,
        defense_mod    = 5,
        cost_mult      = 2.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.9,
        hardness       = 7,
        magical        = true,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A light, silvery metal with minor enchantment.",
    },

    ora = {
        display        = "ora",
        rarity         = "uncommon",
        level_req      = 8,
        enchant_bonus  = 15,
        attack_mod     = 7,
        defense_mod    = 7,
        cost_mult      = 2.5,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.9,
        hardness       = 7,
        magical        = true,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A pale golden metal resonant with elemental force.",
    },

    invar = {
        display        = "invar",
        rarity         = "uncommon",
        level_req      = 8,
        enchant_bonus  = 15,
        attack_mod     = 7,
        defense_mod    = 7,
        cost_mult      = 2.5,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.0,
        hardness       = 8,
        magical        = true,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Dense dark alloy that holds enchantment exceptionally well.",
    },

    -- ── Elemental / special low-to-mid materials ──────────────────────────────
    --
    -- gornar  : vibration (impact) flares  — effective on earth-type creatures
    -- rhimar  : cold flares                — effective on fire-type creatures
    -- zorchar : lightning flares           — broad effectiveness
    -- drakar  : fire flares                — effective vs undead and trolls
    --
    -- crit_weight = 0 on all flare materials; the flare is their special mechanic.
    -- razern gets crit_weight = 2 instead of a flare type.

    gornar = {
        display        = "gornar",
        rarity         = "rare",
        level_req      = 3,
        enchant_bonus  = 5,
        attack_mod     = 5,
        defense_mod    = 5,
        cost_mult      = 5.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.1,
        hardness       = 8,
        magical        = true,
        rare           = true,
        flare_type     = "vibration",
        crit_weight    = 0,
        description    = "A dark, heavy metal that resonates with the force of the earth.  Causes vibration flares, effective against earth creatures.",
    },

    rhimar = {
        display        = "rhimar",
        rarity         = "rare",
        level_req      = 3,
        enchant_bonus  = 5,
        attack_mod     = 5,
        defense_mod    = 5,
        cost_mult      = 5.5,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.95,
        hardness       = 7,
        magical        = true,
        rare           = true,
        flare_type     = "cold",
        crit_weight    = 0,
        description    = "A blue-tinged ice-cold metal prized by northern hunters.  Causes cold flares, highly effective against fire creatures.",
    },

    zorchar = {
        display        = "zorchar",
        rarity         = "rare",
        level_req      = 3,
        enchant_bonus  = 5,
        attack_mod     = 5,
        defense_mod    = 5,
        cost_mult      = 5.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.0,
        hardness       = 7,
        magical        = true,
        rare           = true,
        flare_type     = "lightning",
        crit_weight    = 0,
        description    = "A storm-grey metal crackling with latent static energy.  Causes lightning flares, broadly effective against most creatures.",
    },

    drakar = {
        display        = "drakar",
        rarity         = "rare",
        level_req      = 3,
        enchant_bonus  = 5,
        attack_mod     = 5,
        defense_mod    = 5,
        cost_mult      = 5.0,
        apply_to       = { "weapon" },
        weight_modifier = 1.0,
        hardness       = 8,
        magical        = true,
        rare           = true,
        flare_type     = "fire",
        crit_weight    = 0,
        description    = "A dark metal forged in volcanic heat.  Causes fire flares, dealing double damage to trolls and bonus damage to undead.",
    },

    -- ── Critical-weighted material ────────────────────────────────────────────
    --
    -- razern: no elemental flare.  Instead, crit_weight = 2 adds 2 phantom
    -- damage points to raw_damage BEFORE the crit divisor is applied, raising
    -- the effective crit floor.  This is the GS4 CEP (crit enhancement points)
    -- mechanic.  See crit_resolver.lua and the wiki: gswiki.play.net/Weighting

    razern = {
        display        = "razern",
        rarity         = "rare",
        level_req      = 5,
        enchant_bonus  = 10,
        attack_mod     = 10,
        defense_mod    = 10,
        cost_mult      = 9.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.0,
        hardness       = 9,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 2,
        description    = "An extremely keen metal whose razor edge drives criticals deeper.  No elemental flare, but criticals land harder.",
    },

    -- ── Mid enchant (level 10+) ───────────────────────────────────────────────
    vultite = {
        display        = "vultite",
        rarity         = "rare",
        level_req      = 10,
        enchant_bonus  = 20,
        attack_mod     = 10,
        defense_mod    = 10,
        cost_mult      = 3.5,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.8,
        hardness       = 9,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A brilliant blue-green metal crackling with magical energy.",
    },

    kelyn = {
        display        = "kelyn",
        rarity         = "rare",
        level_req      = 10,
        enchant_bonus  = 20,
        attack_mod     = 10,
        defense_mod    = 10,
        cost_mult      = 3.5,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.7,
        hardness       = 8,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "An incredibly light yet strong metal from the Elemental Planes.",
    },

    laje = {
        display        = "laje",
        rarity         = "rare",
        level_req      = 10,
        enchant_bonus  = 20,
        attack_mod     = 10,
        defense_mod    = 10,
        cost_mult      = 3.5,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.1,
        hardness       = 9,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A dense black metal of unusual spiritual properties.",
    },

    -- ── High enchant (level 13+) ──────────────────────────────────────────────
    rolaren = {
        display        = "rolaren",
        rarity         = "very_rare",
        level_req      = 13,
        enchant_bonus  = 25,
        attack_mod     = 12,
        defense_mod    = 12,
        cost_mult      = 5.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.8,
        hardness       = 10,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A silvery metal infused with pure magical essence.",
    },

    faenor = {
        display        = "faenor",
        rarity         = "very_rare",
        level_req      = 13,
        enchant_bonus  = 25,
        attack_mod     = 12,
        defense_mod    = 12,
        cost_mult      = 5.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.7,
        hardness       = 9,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A pale elven metal of exquisite refinement.",
    },

    eahnor = {
        display        = "eahnor",
        rarity         = "very_rare",
        level_req      = 13,
        enchant_bonus  = 25,
        attack_mod     = 12,
        defense_mod    = 12,
        cost_mult      = 5.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.0,
        hardness       = 10,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A dark reddish metal with powerful spiritual ties.",
    },

    mithglin = {
        display        = "mithglin",
        rarity         = "rare",
        level_req      = 8,
        enchant_bonus  = 15,
        attack_mod     = 15,
        defense_mod    = 15,
        cost_mult      = 11.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 1.05,
        hardness       = 9,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A dark, heavy dwarven metal.  Extremely durable.",
    },

    -- ── Very high enchant (level 15+) ─────────────────────────────────────────
    imflass = {
        display        = "imflass",
        rarity         = "extremely_rare",
        level_req      = 15,
        enchant_bonus  = 30,
        attack_mod     = 15,
        defense_mod    = 15,
        cost_mult      = 7.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.6,
        hardness       = 10,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A translucent golden metal of extraordinary lightness and power.",
    },

    vaalorn = {
        display        = "vaalorn",
        rarity         = "extremely_rare",
        level_req      = 15,
        enchant_bonus  = 30,
        attack_mod     = 15,
        defense_mod    = 15,
        cost_mult      = 7.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.8,
        hardness       = 10,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A deep red metal sacred to the Vaalor elves.",
    },

    -- ── Legendary (level 18+) ─────────────────────────────────────────────────
    golvern = {
        display        = "golvern",
        rarity         = "extremely_rare",
        level_req      = 18,
        enchant_bonus  = 35,
        attack_mod     = 18,
        defense_mod    = 18,
        cost_mult      = 9.0,
        apply_to       = { "weapon", "armor", "shield" },
        weight_modifier = 0.5,
        hardness       = 10,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "A shimmering, almost living metal of legendary potency.",
    },

    -- ── Non-metal materials ───────────────────────────────────────────────────
    leather = {
        display        = "leather",
        rarity         = "common",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 1.0,
        apply_to       = { "armor" },
        weight_modifier = 1.0,
        hardness       = 3,
        magical        = false,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Treated animal hide.",
    },

    wood = {
        display        = "wood",
        rarity         = "common",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 0.5,
        apply_to       = { "weapon" },
        weight_modifier = 0.8,
        hardness       = 3,
        magical        = false,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Carved hardwood.",
    },

    bone = {
        display        = "bone",
        rarity         = "uncommon",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 0.8,
        apply_to       = { "weapon", "jewelry" },
        weight_modifier = 0.7,
        hardness       = 3,
        magical        = false,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Carved bone or horn.",
    },

    crystal = {
        display        = "crystal",
        rarity         = "uncommon",
        level_req      = 5,
        enchant_bonus  = 5,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 1.5,
        apply_to       = { "weapon", "jewelry" },
        weight_modifier = 1.0,
        hardness       = 5,
        magical        = true,
        rare           = false,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Magically resonant crystal.",
    },

    glaes = {
        display        = "glaes",
        rarity         = "rare",
        level_req      = 0,
        enchant_bonus  = 0,
        attack_mod     = 0,
        defense_mod    = 0,
        cost_mult      = 2.0,
        apply_to       = { "weapon" },
        weight_modifier = 0.5,
        hardness       = 6,
        magical        = true,
        rare           = true,
        flare_type     = nil,
        crit_weight    = 0,
        description    = "Volcanic glass prized by locksmiths.  Exceptionally sharp.",
    },
}

-- ── Lookup helpers ─────────────────────────────────────────────────────────────

--- Get a material entry by name.  Returns nil if unknown.
function Materials.get(name)
    if not name then return nil end
    return Materials.list[name:lower()]
end

--- Get a single field from a material, with a default fallback.
function Materials.field(name, field, default)
    local mat = Materials.get(name)
    if not mat then return default end
    local v = mat[field]
    if v == nil then return default end
    return v
end

--- Returns the flare_type string for a material, or nil.
function Materials.flareType(name)
    return Materials.field(name, "flare_type", nil)
end

--- Returns the crit_weight integer for a material (0 if none / unknown).
function Materials.critWeight(name)
    return Materials.field(name, "crit_weight", 0)
end

--- Returns the weight_modifier for a material (1.0 if none / unknown).
function Materials.weightModifier(name)
    return Materials.field(name, "weight_modifier", 1.0)
end

return Materials
