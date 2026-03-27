---------------------------------------------------
-- data/items/lockpicks.lua
-- Lockpick material definitions for GemStone IV.
-- Source: gswiki.play.net/Lockpick  (confirmed accurate)
--
-- modifier_mid:  typical modifier (catalog/DETECT description)
-- mod_min:       lowest possible roll for this material
-- mod_max:       highest possible roll for this material
-- min_ranks:     minimum Picking Locks ranks required without penalty
-- strength:      durability tier (1=flimsy ... 11=astonishingly strong)
-- price:         base shop price in silver
-- precision:     descriptive label used in DETECT output
--
-- Note: "bronze" is not a GS4 lockpick material -- aliased to brass.
--
-- When a pick is first used, a specific modifier is rolled within
-- [mod_min, mod_max] and stored in the item's extra_data.
-- That modifier never changes for the life of the pick.
---------------------------------------------------

local Lockpicks = {}

Lockpicks.materials = {
    copper  = { modifier_mid=1.00, mod_min=0.97, mod_max=1.05, min_ranks=0,  strength=2,  price=100,    precision="very inaccurate",       desc="A crude copper lockpick, soft and imprecise." },
    brass   = { modifier_mid=1.05, mod_min=1.02, mod_max=1.11, min_ranks=0,  strength=2,  price=250,    precision="very inaccurate",       desc="A brass lockpick, slightly better than copper but still clumsy." },
    steel   = { modifier_mid=1.10, mod_min=1.07, mod_max=1.16, min_ranks=1,  strength=4,  price=500,    precision="inaccurate",            desc="A steel lockpick with decent reliability for basic locks." },
    gold    = { modifier_mid=1.20, mod_min=1.16, mod_max=1.26, min_ranks=3,  strength=3,  price=2000,   precision="somewhat inaccurate",   desc="A gold lockpick, surprisingly effective despite the soft material." },
    ivory   = { modifier_mid=1.20, mod_min=1.15, mod_max=1.27, min_ranks=1,  strength=5,  price=750,    precision="somewhat inaccurate",   desc="An ivory lockpick carved from bone, sturdy with decent precision." },
    silver  = { modifier_mid=1.30, mod_min=1.26, mod_max=1.36, min_ranks=3,  strength=4,  price=2500,   precision="inefficient",           desc="A silver lockpick with improved performance over steel." },
    mithril = { modifier_mid=1.45, mod_min=1.40, mod_max=1.52, min_ranks=5,  strength=8,  price=6000,   precision="unreliable",            desc="A mithril lockpick, surprisingly hard for its weight. Used by serious rogues." },
    ora     = { modifier_mid=1.55, mod_min=1.50, mod_max=1.62, min_ranks=5,  strength=7,  price=5000,   precision="below average",         desc="An ora lockpick with an inherent elemental resonance that aids subtle manipulation." },
    glaes   = { modifier_mid=1.60, mod_min=1.55, mod_max=1.68, min_ranks=8,  strength=10, price=9500,   precision="average",               desc="A glaes lockpick, exceptionally hard and precise." },
    laje    = { modifier_mid=1.75, mod_min=1.69, mod_max=1.83, min_ranks=12, strength=4,  price=17000,  precision="above average",         desc="A laje lockpick, spiritually attuned and favored by experienced thieves." },
    vultite = { modifier_mid=1.80, mod_min=1.74, mod_max=1.88, min_ranks=20, strength=4,  price=30000,  precision="somewhat accurate",     desc="A vultite lockpick that practically vibrates in your hand with magical energy." },
    rolaren = { modifier_mid=1.90, mod_min=1.84, mod_max=1.98, min_ranks=12, strength=8,  price=17000,  precision="favorable",             desc="A rolaren lockpick, black and gleaming, with above-average precision." },
    veniom  = { modifier_mid=2.20, mod_min=2.13, mod_max=2.27, min_ranks=25, strength=9,  price=50000,  precision="highly accurate",       desc="A veniom lockpick considered near-legendary among guild rogues." },
    invar   = { modifier_mid=2.25, mod_min=2.18, mod_max=2.34, min_ranks=35, strength=10, price=75000,  precision="highly accurate",       desc="An invar lockpick of extraordinary density and precision." },
    alum    = { modifier_mid=2.30, mod_min=2.22, mod_max=2.38, min_ranks=16, strength=3,  price=23000,  precision="excellent",             desc="An alum lockpick, light but incredibly sharp. Very brittle." },
    golvern = { modifier_mid=2.35, mod_min=2.27, mod_max=2.42, min_ranks=40, strength=11, price=95000,  precision="excellent",             desc="A golvern lockpick, the pinnacle of strength and precision." },
    kelyn   = { modifier_mid=2.40, mod_min=2.32, mod_max=2.48, min_ranks=25, strength=8,  price=62000,  precision="incredible",            desc="A kelyn lockpick of astonishing precision, almost preternaturally light." },
    vaalin  = { modifier_mid=2.50, mod_min=2.35, mod_max=2.55, min_ranks=50, strength=10, price=125000, precision="unsurpassed",           desc="A vaalin lockpick, the finest ever crafted. Masters of the guild speak of these in hushed tones." },
}

-- ── Named pick templates (shop-sold items) ────────────────────────────────────
-- These use the above materials plus a name suffix for inventory display.
Lockpicks.templates = {
    -- Starter picks (sold in shops, referenceable by item_id)
    { base_name="crude lockpick",    name="a crude lockpick",    noun="lockpick", material="copper",  item_type="lockpick", value=100,  weight=0.1, description="A crude copper lockpick, bent and imprecise." },
    { base_name="simple lockpick",   name="a simple lockpick",   noun="lockpick", material="brass",   item_type="lockpick", value=250,  weight=0.1, description="A simple brass lockpick, adequate for beginner rogues." },
    { base_name="standard lockpick", name="a standard lockpick", noun="lockpick", material="steel",   item_type="lockpick", value=500,  weight=0.1, description="A standard steel lockpick used by working rogues." },
    { base_name="ivory lockpick",    name="an ivory lockpick",   noun="lockpick", material="ivory",   item_type="lockpick", value=750,  weight=0.1, description="An ivory lockpick carved smooth, with good feel." },
    { base_name="silver lockpick",   name="a silver lockpick",   noun="lockpick", material="silver",  item_type="lockpick", value=2500, weight=0.1, description="A silver lockpick, a step up for experienced rogues." },
    { base_name="gold lockpick",     name="a gold lockpick",     noun="lockpick", material="gold",    item_type="lockpick", value=2000, weight=0.1, description="A surprisingly effective gold lockpick." },
    { base_name="mithril lockpick",  name="a mithril lockpick",  noun="lockpick", material="mithril", item_type="lockpick", value=6000, weight=0.1, description="A mithril lockpick for serious professionals." },
    { base_name="glaes lockpick",    name="a glaes lockpick",    noun="lockpick", material="glaes",   item_type="lockpick", value=9500, weight=0.1, description="A razor-sharp glaes lockpick of excellent precision." },
}

return Lockpicks
