------------------------------------------------------------------------
-- herbs.lua
-- GemStone IV Canonical Herb Definitions
--
-- All herbs sourced from GS4 wiki and ps.lichproject.org/items.
-- Loaded by LuaEngine; used by treatment.lua and the item/loot systems.
--
-- herb_group:  which body areas this herb treats
-- heal_type:   "wound" | "scar" | "blood" | "limb_regen" | "eye_regen"
--              | "poison" | "mana"
-- max_rank:    highest wound/scar rank this herb can treat
-- hp_restore:  for blood/health herbs, flat HP restored
-- roundtime:   base roundtime to EAT/DRINK (reduced by First Aid skill)
-- bites:       how many uses per item (3 for "some", 1 for single)
-- article:     "a" | "an" | "some"
-- use_verb:    "eat" | "drink" | "pour"  (pour = dead players only)
------------------------------------------------------------------------

local Herbs = {}

-- ── Master herb table ────────────────────────────────────────────────
-- Key = canonical item noun (lowercase), matches DB items.noun field

Herbs.DATA = {

    ---------- BLOOD / HP -----------------------------------------------
    acantha_leaf = {
        name        = "acantha leaf",
        article     = "an",
        bites       = 3,
        herb_group  = { "blood" },
        heal_type   = "blood",
        max_rank    = 0,        -- not a wound herb; restores HP
        hp_restore  = 10,
        roundtime   = 10,
        use_verb    = "eat",
        desc        = "a slender green leaf with serrated edges",
        eat_msg     = "You eat the acantha leaf.  A warm sensation spreads through your body as your blood loss slows.",
    },

    ---------- NERVOUS SYSTEM -------------------------------------------
    wolifrew_lichen = {
        name        = "wolifrew lichen",
        article     = "some",
        bites       = 3,
        herb_group  = { "nervous_system" },
        heal_type   = "wound",
        max_rank    = 2,
        hp_restore  = 0,
        roundtime   = 15,
        use_verb    = "eat",
        desc        = "a pale grey-green lichen",
        eat_msg     = "You eat the wolifrew lichen.  A tingling sensation moves through your nervous system.",
    },

    bolmara_potion = {
        name        = "bolmara potion",
        article     = "a",
        bites       = 1,
        herb_group  = { "nervous_system" },
        heal_type   = "wound",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 20,
        use_verb    = "drink",
        desc        = "a small vial of shimmering blue liquid",
        eat_msg     = "You drink the bolmara potion.  An electric sensation runs through your nerves.",
    },

    woth_flower = {
        name        = "woth flower",
        article     = "a",
        bites       = 1,
        herb_group  = { "nervous_system" },
        heal_type   = "scar",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 20,
        use_verb    = "eat",
        desc        = "a delicate white flower with violet veins",
        eat_msg     = "You eat the woth flower.  The old tension in your nervous system eases.",
    },

    ---------- HEAD & NECK ----------------------------------------------
    aloeas_stem = {
        name        = "aloeas stem",
        article     = "an",
        bites       = 1,
        herb_group  = { "head", "neck" },
        heal_type   = "wound",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 15,
        use_verb    = "eat",
        desc        = "a pale yellow stem with a pithy interior",
        eat_msg     = "You eat the aloeas stem.  A cooling sensation washes over your head and neck.",
    },

    haphip_root = {
        name        = "haphip root",
        article     = "a",
        bites       = 1,
        herb_group  = { "head", "neck" },
        heal_type   = "scar",
        max_rank    = 2,
        hp_restore  = 0,
        roundtime   = 15,
        use_verb    = "eat",
        desc        = "a gnarled brownish root",
        eat_msg     = "You eat the haphip root.  The old scar tissue on your head and neck softens.",
    },

    brostheras_potion = {
        name        = "brostheras potion",
        article     = "a",
        bites       = 1,
        herb_group  = { "head", "neck" },
        heal_type   = "scar",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 20,
        use_verb    = "drink",
        desc        = "a dark green potion in a slender vial",
        eat_msg     = "You drink the brostheras potion.  Deep scar tissue around your head and neck slowly dissolves.",
    },

    ---------- TORSO & EYES ---------------------------------------------
    basal_moss = {
        name        = "basal moss",
        article     = "some",
        bites       = 3,
        herb_group  = { "chest", "abdomen", "back", "right_eye", "left_eye" },
        heal_type   = "wound",
        max_rank    = 2,
        hp_restore  = 0,
        roundtime   = 15,
        use_verb    = "eat",
        desc        = "a clump of dark, spongy moss",
        eat_msg     = "You eat the basal moss.  A warm numbness spreads across your torso.",
    },

    pothinir_grass = {
        name        = "pothinir grass",
        article     = "some",
        bites       = 3,
        herb_group  = { "chest", "abdomen", "back", "right_eye", "left_eye" },
        heal_type   = "wound",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 20,
        use_verb    = "eat",
        desc        = "a bundle of thin blue-grey grass",
        eat_msg     = "You eat the pothinir grass.  A deep warmth penetrates your torso.",
    },

    -- Eye restoration (missing eye -> restored with no scar)
    bur_clover = {
        name        = "bur-clover",
        article     = "a",
        bites       = 1,
        herb_group  = { "right_eye", "left_eye" },
        heal_type   = "eye_regen",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 30,
        use_verb    = "eat",
        desc        = "a spiky clover blossom with milky sap",
        eat_msg     = "You eat the bur-clover.  A sharp tingling sensation spreads through your eye socket, then fades to warmth.",
    },

    -- Eye scar
    aivren_berry = {
        name        = "aivren berry",
        article     = "an",
        bites       = 1,
        herb_group  = { "right_eye", "left_eye" },
        heal_type   = "scar",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 15,
        use_verb    = "eat",
        desc        = "a small purple berry",
        eat_msg     = "You eat the aivren berry.  The old scar tissue around your eye gradually softens.",
    },

    ---------- LIMBS (arms, hands, legs) --------------------------------
    ambrominas_leaf = {
        name        = "ambrominas leaf",
        article     = "an",
        bites       = 3,
        herb_group  = { "right_arm", "left_arm", "right_hand", "left_hand",
                        "right_leg", "left_leg" },
        heal_type   = "wound",
        max_rank    = 2,
        hp_restore  = 0,
        roundtime   = 15,
        use_verb    = "eat",
        desc        = "a large, waxy green leaf",
        eat_msg     = "You eat the ambrominas leaf.  Your wounds ache briefly, then begin to close.",
    },

    ephlox_moss = {
        name        = "ephlox moss",
        article     = "some",
        bites       = 3,
        herb_group  = { "right_arm", "left_arm", "right_hand", "left_hand",
                        "right_leg", "left_leg" },
        heal_type   = "wound",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 20,
        use_verb    = "eat",
        desc        = "a dense clump of grey-green moss",
        eat_msg     = "You eat the ephlox moss.  A bone-deep warmth spreads through your limbs.",
    },

    -- Limb regeneration (severed limb -> restored, no scar)
    sovyn_clove = {
        name        = "sovyn clove",
        article     = "a",
        bites       = 1,
        herb_group  = { "right_arm", "left_arm", "right_hand", "left_hand",
                        "right_leg", "left_leg" },
        heal_type   = "limb_regen",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 30,
        use_verb    = "eat",
        desc        = "a small dried clove with a faint silver sheen",
        eat_msg     = "You eat the sovyn clove.  A blazing warmth erupts from your wound as new flesh begins to knit.",
    },

    -- Limb scar
    cactacae_spine = {
        name        = "cactacae spine",
        article     = "a",
        bites       = 1,
        herb_group  = { "right_arm", "left_arm", "right_hand", "left_hand",
                        "right_leg", "left_leg" },
        heal_type   = "scar",
        max_rank    = 3,
        hp_restore  = 0,
        roundtime   = 15,
        use_verb    = "eat",
        desc        = "a slender spine with a reddish tip",
        eat_msg     = "You eat the cactacae spine.  Old scar tissue in your limbs begins to recede.",
    },

    ---------- MISC / POISON / MANA -------------------------------------
    -- Poison cure
    calamia_fruit = {
        name        = "calamia fruit",
        article     = "a",
        bites       = 1,
        herb_group  = { "all" },
        heal_type   = "poison",
        max_rank    = 0,
        hp_restore  = 0,
        roundtime   = 10,
        use_verb    = "eat",
        desc        = "a small, tart reddish fruit",
        eat_msg     = "You eat the calamia fruit.  A bitter taste fills your mouth, then the poison begins to fade.",
    },

    -- Mana restore
    glowbark_infusion = {
        name        = "glowbark infusion",
        article     = "a",
        bites       = 1,
        herb_group  = { "all" },
        heal_type   = "mana",
        max_rank    = 0,
        hp_restore  = 0,
        mana_restore = 15,
        roundtime   = 10,
        use_verb    = "drink",
        desc        = "a small vial of faintly glowing amber liquid",
        eat_msg     = "You drink the glowbark infusion.  Your mind feels refreshed as mana flows back into you.",
    },
}

-- ── Lookup helpers ───────────────────────────────────────────────────

-- Find herb data by noun (item noun from DB)
function Herbs.find_by_noun(noun)
    local n = (noun or ""):lower():gsub("%s+", "_")
    return Herbs.DATA[n]
end

-- Find herb data by name fragment (loose search)
function Herbs.find_by_name(name_fragment)
    local frag = (name_fragment or ""):lower()
    for key, herb in pairs(Herbs.DATA) do
        if herb.name:find(frag, 1, true) then
            return herb, key
        end
    end
    return nil
end

-- Returns true if this herb can treat the given location at the given wound rank
function Herbs.can_treat(herb, location, rank, heal_type)
    if herb.heal_type ~= (heal_type or herb.heal_type) then return false end
    if herb.max_rank > 0 and rank > herb.max_rank then return false end

    -- Check group membership
    for _, g in ipairs(herb.herb_group) do
        if g == "all" or g == location then return true end
    end
    return false
end

-- Base roundtime (reduced 1 sec per 20 FA bonus points by GS4 wiki)
function Herbs.get_roundtime(herb, first_aid_bonus)
    local base = herb.roundtime or 10
    local reduction = math.floor((first_aid_bonus or 0) / 20)
    return math.max(3, base - reduction)
end

return Herbs
