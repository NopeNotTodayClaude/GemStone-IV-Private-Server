------------------------------------------------------------------------
-- scripts/globals/magic/spell_circles.lua
-- Canonical spell circle data for GemStone IV.
-- Source: gswiki.play.net/Spell_circle, /Magic, /Spell_Research
--
-- Loaded by any magic subsystem that needs circle metadata.
-- Mirrors the spell_circles and spell_circle_access SQL tables.
--
-- Prof IDs: 1=Warrior 2=Rogue 3=Wizard 4=Cleric 5=Empath
--           6=Sorcerer 7=Ranger 8=Bard 9=Paladin 10=Monk
------------------------------------------------------------------------

local SpellCircles = {}

-- ── Circle definitions ────────────────────────────────────────────────
-- sphere:       elemental | spiritual | mental | hybrid_es | hybrid_em | hybrid_sm | arcane
-- number_prefix: the leading digit(s) * 100 → spell number range
-- cs_stat:      which stat drives CS warding rolls for this circle
-- td_stat:      which stat resists this circle's warding attacks
-- is_trainable: false = Arcane (not available via Spell Research)
SpellCircles.circles = {
    [1]  = { id=1,  name="Minor Spiritual", abbrev="MnS",
             sphere="spiritual",  prefix=1,
             cs_stat="wisdom",       td_stat="wisdom",
             is_trainable=true },
    [2]  = { id=2,  name="Major Spiritual", abbrev="MjS",
             sphere="spiritual",  prefix=2,
             cs_stat="wisdom",       td_stat="wisdom",
             is_trainable=true },
    [3]  = { id=3,  name="Cleric Base",     abbrev="Cle",
             sphere="spiritual",  prefix=3,
             cs_stat="wisdom",       td_stat="wisdom",
             is_trainable=true },
    [4]  = { id=4,  name="Minor Elemental", abbrev="MnE",
             sphere="elemental",  prefix=4,
             cs_stat="aura",         td_stat="aura",
             is_trainable=true },
    [5]  = { id=5,  name="Major Elemental", abbrev="MjE",
             sphere="elemental",  prefix=5,
             cs_stat="aura",         td_stat="aura",
             is_trainable=true },
    [6]  = { id=6,  name="Ranger Base",     abbrev="Ran",
             sphere="spiritual",  prefix=6,
             cs_stat="wisdom",       td_stat="wisdom",
             is_trainable=true },
    [7]  = { id=7,  name="Sorcerer Base",   abbrev="Sor",
             sphere="hybrid_es",  prefix=7,
             cs_stat="avg_aura_wis", td_stat="avg_aura_wis",
             is_trainable=true },
    [8]  = { id=8,  name="Wizard Base",     abbrev="Wiz",
             sphere="elemental",  prefix=9,
             cs_stat="aura",         td_stat="aura",
             is_trainable=true },
    [9]  = { id=9,  name="Bard Base",       abbrev="Bar",
             sphere="hybrid_em",  prefix=10,
             cs_stat="aura",         td_stat="aura",
             is_trainable=true },
    [10] = { id=10, name="Empath Base",     abbrev="Emp",
             sphere="hybrid_sm",  prefix=11,
             cs_stat="wisdom",       td_stat="wisdom",
             is_trainable=true },
    [11] = { id=11, name="Paladin Base",    abbrev="Pal",
             sphere="spiritual",  prefix=16,
             cs_stat="wisdom",       td_stat="wisdom",
             is_trainable=true },
    [12] = { id=12, name="Minor Mental",    abbrev="MnM",
             sphere="mental",     prefix=12,
             cs_stat="logic",        td_stat="discipline",
             is_trainable=true },
    [13] = { id=13, name="Major Mental",    abbrev="MjM",
             sphere="mental",     prefix=13,
             cs_stat="avg_inf_log",  td_stat="discipline",
             is_trainable=false },  -- Savant-only / non-research circle in this ruleset
    [14] = { id=14, name="Savant Base",     abbrev="Sav",
             sphere="mental",     prefix=14,
             cs_stat="avg_dis_log",  td_stat="discipline",
             is_trainable=false },  -- Reserved for the Savant profession path
    [15] = { id=15, name="Arcane",          abbrev="Arc",
             sphere="arcane",     prefix=17,
             cs_stat="aura",         td_stat="avg_aura_wis",
             is_trainable=false },  -- Not available via Spell Research
}

-- ── Profession → allowed circle IDs ──────────────────────────────────
-- Source: gswiki.play.net/Spell_Research table
SpellCircles.profession_circles = {
    [1]  = { 1, 4 },          -- Warrior:  MnS, MnE
    [2]  = { 1, 4 },          -- Rogue:    MnS, MnE
    [3]  = { 4, 5, 8 },       -- Wizard:   MnE, MjE, Wiz
    [4]  = { 1, 2, 3 },       -- Cleric:   MnS, MjS, Cle
    [5]  = { 1, 2, 10 },      -- Empath:   MnS, MjS, Emp
    [6]  = { 1, 4, 7 },       -- Sorcerer: MnS, MnE, Sor
    [7]  = { 1, 6 },          -- Ranger:   MnS, Ran
    [8]  = { 4, 9 },          -- Bard:     MnE, Bar
    [9]  = { 1, 11 },         -- Paladin:  MnS, Pal
    [10] = { 1, 12 },         -- Monk:     MnS, MnM
}

-- ── Lookup: spell number → circle_id ─────────────────────────────────
-- Given a spell number (e.g. 401, 901, 1612), find the circle.
function SpellCircles.circle_for_spell(spell_number)
    -- Arcane: 1700-1799
    if spell_number >= 1700 and spell_number <= 1799 then return 15 end
    -- Paladin: 1600-1699
    if spell_number >= 1600 and spell_number <= 1699 then return 11 end
    -- Empath: 1100-1199
    if spell_number >= 1100 and spell_number <= 1199 then return 10 end
    -- Bard: 1000-1099
    if spell_number >= 1000 and spell_number <= 1099 then return 9 end
    -- Minor Mental: 1200-1299
    if spell_number >= 1200 and spell_number <= 1299 then return 12 end
    -- Major Mental: 1300-1399
    if spell_number >= 1300 and spell_number <= 1399 then return 13 end
    -- Wizard Base: 900-999
    if spell_number >= 900  and spell_number <= 999  then return 8 end
    -- Sorcerer: 700-799
    if spell_number >= 700  and spell_number <= 799  then return 7 end
    -- Ranger: 600-699
    if spell_number >= 600  and spell_number <= 699  then return 6 end
    -- Major Elemental: 500-599
    if spell_number >= 500  and spell_number <= 599  then return 5 end
    -- Minor Elemental: 400-499
    if spell_number >= 400  and spell_number <= 499  then return 4 end
    -- Cleric: 300-399
    if spell_number >= 300  and spell_number <= 399  then return 3 end
    -- Major Spiritual: 200-299
    if spell_number >= 200  and spell_number <= 299  then return 2 end
    -- Minor Spiritual: 100-199
    if spell_number >= 100  and spell_number <= 199  then return 1 end
    return nil
end

-- ── Lookup: get a circle table by id ─────────────────────────────────
function SpellCircles.get(circle_id)
    return SpellCircles.circles[circle_id]
end

-- ── Check: can a profession train a given circle? ────────────────────
function SpellCircles.can_train(profession_id, circle_id)
    local allowed = SpellCircles.profession_circles[profession_id]
    if not allowed then return false end
    for _, cid in ipairs(allowed) do
        if cid == circle_id then return true end
    end
    return false
end

-- ── Get a character's primary circle for a spell ─────────────────────
-- The primary circle is the one the spell belongs to.
-- Returns the circle table or nil.
function SpellCircles.primary_for_spell(spell_number)
    local cid = SpellCircles.circle_for_spell(spell_number)
    if cid then return SpellCircles.circles[cid] end
    return nil
end

return SpellCircles
