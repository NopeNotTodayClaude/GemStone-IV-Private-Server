---------------------------------------------------
-- data/professions.lua
-- All profession definitions for GemStone IV.
-- Source: gswiki.play.net profession pages
--
-- Stat index order: STR CON DEX AGI DIS AUR LOG INT WIS INF
-- prof_type: "square" | "semi" | "pure"
-- prime_requisites: two stat indices (0-based)
-- mana_stats: two stat indices that determine mana pool
---------------------------------------------------

local Professions = {}

Professions.list = {
    { id=1,  name="Warrior",  type="square", desc="Masters of all weapons and armor. Pure melee power." },
    { id=2,  name="Rogue",    type="square", desc="Stealthy and cunning. Locks, traps, ambush, dual-wield." },
    { id=3,  name="Wizard",   type="pure",   desc="Devastating elemental magic. The classic arcane caster." },
    { id=4,  name="Cleric",   type="pure",   desc="Divine power. Healing, protection, and spiritual might." },
    { id=5,  name="Empath",   type="pure",   desc="Healers who absorb wounds. Essential support class." },
    { id=6,  name="Sorcerer", type="pure",   desc="Dark magic blending elemental and spiritual forces." },
    { id=7,  name="Ranger",   type="semi",   desc="Wilderness expert. Martial skill with nature magic." },
    { id=8,  name="Bard",     type="semi",   desc="Loremaster musician. Magic through song and verse." },
    { id=9,  name="Paladin",  type="semi",   desc="Holy warrior. Martial prowess with divine magic." },
    { id=10, name="Monk",     type="semi",   desc="Disciplined martial artist. Inner power through focus." },
}

-- ── HP and mana per level ─────────────────────────────────────────────────────
-- { hp = points per level, mana = points per level }
Professions.profession_stats = {
    [1]  = { hp=15, mana=0 },  -- Warrior
    [2]  = { hp=12, mana=0 },  -- Rogue
    [3]  = { hp=6,  mana=4 },  -- Wizard
    [4]  = { hp=8,  mana=3 },  -- Cleric
    [5]  = { hp=7,  mana=3 },  -- Empath
    [6]  = { hp=7,  mana=3 },  -- Sorcerer
    [7]  = { hp=10, mana=2 },  -- Ranger
    [8]  = { hp=9,  mana=2 },  -- Bard
    [9]  = { hp=12, mana=2 },  -- Paladin
    [10] = { hp=11, mana=2 },  -- Monk
}

-- ── Prime requisites (two stat indices each, 0-based) ─────────────────────────
-- 0=STR 1=CON 2=DEX 3=AGI 4=DIS 5=AUR 6=LOG 7=INT 8=WIS 9=INF
Professions.prime_requisites = {
    [1]  = { 0, 1 },  -- Warrior:  STR, CON
    [2]  = { 3, 2 },  -- Rogue:    AGI, DEX
    [3]  = { 5, 6 },  -- Wizard:   AUR, LOG
    [4]  = { 8, 7 },  -- Cleric:   WIS, INT
    [5]  = { 8, 9 },  -- Empath:   WIS, INF
    [6]  = { 5, 8 },  -- Sorcerer: AUR, WIS
    [7]  = { 2, 7 },  -- Ranger:   DEX, INT
    [8]  = { 9, 5 },  -- Bard:     INF, AUR
    [9]  = { 8, 0 },  -- Paladin:  WIS, STR
    [10] = { 0, 3 },  -- Monk:     STR, AGI
}

-- ── Mana stats (stat indices that determine mana regeneration) ────────────────
Professions.mana_stats = {
    [1]  = { 5, 8 },  -- Warrior:  AUR, WIS
    [2]  = { 5, 8 },  -- Rogue:    AUR, WIS
    [3]  = { 5, 6 },  -- Wizard:   AUR, LOG
    [4]  = { 8, 5 },  -- Cleric:   WIS, AUR
    [5]  = { 8, 9 },  -- Empath:   WIS, INF
    [6]  = { 5, 8 },  -- Sorcerer: AUR, WIS
    [7]  = { 8, 5 },  -- Ranger:   WIS, AUR
    [8]  = { 9, 5 },  -- Bard:     INF, AUR
    [9]  = { 8, 5 },  -- Paladin:  WIS, AUR
    [10] = { 6, 8 },  -- Monk:     LOG, WIS
}

-- ── Base stat growth rates ────────────────────────────────────────────────────
-- [STR, CON, DEX, AGI, DIS, AUR, LOG, INT, WIS, INF]
Professions.growth_rates = {
    [1]  = { 30, 25, 25, 25, 20, 15, 10, 20, 15, 20 },  -- Warrior
    [2]  = { 25, 20, 25, 30, 20, 15, 20, 25, 10, 15 },  -- Rogue
    [3]  = { 10, 15, 25, 15, 20, 30, 25, 25, 20, 20 },  -- Wizard
    [4]  = { 20, 20, 10, 15, 25, 15, 25, 25, 30, 20 },  -- Cleric
    [5]  = { 10, 20, 15, 15, 25, 20, 25, 20, 30, 25 },  -- Empath
    [6]  = { 10, 15, 20, 15, 25, 30, 25, 20, 25, 20 },  -- Sorcerer
    [7]  = { 25, 20, 30, 20, 20, 15, 15, 25, 25, 10 },  -- Ranger
    [8]  = { 25, 20, 25, 20, 15, 25, 10, 15, 20, 30 },  -- Bard
    [9]  = { 30, 25, 20, 20, 25, 15, 10, 15, 25, 20 },  -- Paladin
    [10] = { 25, 25, 20, 30, 25, 15, 20, 20, 15, 10 },  -- Monk
}

return Professions
