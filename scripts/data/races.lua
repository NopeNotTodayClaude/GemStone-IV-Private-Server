---------------------------------------------------
-- data/races.lua
-- All playable race definitions for GemStone IV.
-- Source: gswiki.play.net individual race pages
--
-- Stat index order: STR CON DEX AGI DIS AUR LOG INT WIS INF
-- (matches STAT_KEYS in character_creation.py)
---------------------------------------------------

local Races = {}

-- ── Playable races ────────────────────────────────────────────────────────────
Races.list = {
    { id=1,  name="Human",         desc="Adaptable and ambitious, humans thrive in any role." },
    { id=2,  name="Elf",           desc="Graceful and long-lived, masters of magic and archery." },
    { id=3,  name="Dark Elf",      desc="Mysterious and cunning, dwellers of shadow." },
    { id=4,  name="Half-Elf",      desc="Born of two worlds, blending human grit with elven grace." },
    { id=5,  name="Dwarf",         desc="Stout and stubborn, master craftsmen and fierce warriors." },
    { id=6,  name="Halfling",      desc="Small but quick-witted, natural rogues and survivalists." },
    { id=7,  name="Giantman",      desc="Towering and powerful, unmatched in raw strength." },
    { id=8,  name="Forest Gnome",  desc="Clever tinkerers at home in the wild, natural mages." },
    { id=9,  name="Burghal Gnome", desc="Urban gnomes with sharp minds and nimble fingers." },
    { id=10, name="Sylvankind",    desc="Woodland elves deeply connected to nature." },
    { id=11, name="Aelotoi",       desc="Winged refugees from another realm, empathic and agile." },
    { id=12, name="Erithian",      desc="Disciplined scholars from the eastern continent." },
    { id=13, name="Half-Krolvin",  desc="Hardy half-breeds of humans and seafaring Krolvin." },
}

-- ── Stat modifiers per race ───────────────────────────────────────────────────
-- [STR, CON, DEX, AGI, DIS, AUR, LOG, INT, WIS, INF]
Races.stat_mods = {
    [1]  = {  5,   0,   0,   0,   0,   0,   5,   5,   0,   0 },  -- Human
    [2]  = {  0,   0,   5,  15, -15,   5,   0,   0,   0,  10 },  -- Elf
    [3]  = {  0,  -5,  10,   5, -10,  10,   0,   5,   5,  -5 },  -- Dark Elf
    [4]  = {  0,   0,   5,  10,  -5,   0,   0,   0,   0,   5 },  -- Half-Elf
    [5]  = { 10,  15,   0,  -5,  10, -10,   5,   0,   0, -10 },  -- Dwarf
    [6]  = {-15,  10,  15,  10,  -5,  -5,   5,  10,   0,  -5 },  -- Halfling
    [7]  = { 15,  10,  -5,  -5,   0,  -5,  -5,   0,   0,   5 },  -- Giantman
    [8]  = {-10,  10,   5,  10,   5,   0,   5,   0,   5,  -5 },  -- Forest Gnome
    [9]  = {-15,  10,  10,  10,  -5,   5,  10,   5,   0,  -5 },  -- Burghal Gnome
    [10] = {  0,   0,  10,   5,  -5,   5,   0,   0,   0,   0 },  -- Sylvankind
    [11] = { -5,   0,   5,  10,   5,   0,   5,   5,   0,  -5 },  -- Aelotoi
    [12] = { -5,  10,   0,   0,   5,   0,   5,   0,   0,  10 },  -- Erithian
    [13] = { 10,  10,   0,   5,   0,   0, -10,   0,  -5,  -5 },  -- Half-Krolvin
}

-- ── Racial stat growth modifiers ──────────────────────────────────────────────
-- Added to profession base growth rates
Races.growth_mods = {
    [1]  = {  2,  2,  0,  0,  0,  0,  0,  2,  0,  0 },  -- Human
    [2]  = {  0, -5,  5,  3, -5,  5,  0,  0,  0,  3 },  -- Elf
    [3]  = {  0, -2,  5,  5, -2,  0,  0,  0,  0,  0 },  -- Dark Elf
    [4]  = {  2,  0,  2,  2, -2,  0,  0,  0,  0,  2 },  -- Half-Elf
    [5]  = {  5,  5, -3, -5,  3,  0,  0,  0,  3, -2 },  -- Dwarf
    [6]  = { -5,  5,  5,  5, -2,  0, -2,  0,  0,  0 },  -- Halfling
    [7]  = {  5,  3, -2, -2,  0,  0,  0,  2,  0,  0 },  -- Giantman
    [8]  = { -3,  2,  2,  3,  2,  0,  0,  0,  0,  0 },  -- Forest Gnome
    [9]  = { -5,  0,  3,  3, -3, -2,  5,  5,  0,  0 },  -- Burghal Gnome
    [10] = { -3, -2,  5,  5, -5,  3,  0,  0,  0,  3 },  -- Sylvankind
    [11] = {  0, -2,  3,  3,  2,  0,  0,  2,  0, -2 },  -- Aelotoi
    [12] = { -2,  0,  0,  0,  3,  0,  2,  0,  0,  3 },  -- Erithian
    [13] = {  3,  5,  2,  2,  0, -2, -2,  0,  0, -2 },  -- Half-Krolvin
}

-- Starter towns
-- Standard starter towns per GSWiki Character creation:
-- Wehnimer's Landing, Icemule Trace, Ta'Vaalor.
-- Premium starter towns can be layered in later when account-tier routing exists.
Races.starter_towns = {
    { room_id = 221,  name = "Wehnimer's Landing" },
    { room_id = 2300, name = "Icemule Trace" },
    { room_id = 5907, name = "Ta'Vaalor" },
}

Races.default_starting_room = 221

-- ── Default starting rooms by race_id ────────────────────────────────────────
-- These are defaults only. Character creation and the tutorial exit can now
-- select a starter town directly instead of hardwiring it by race.
Races.starting_rooms = {
    [1]  = 221,
    [2]  = 5907,
    [3]  = 5907,
    [4]  = 221,
    [5]  = 2300,
    [6]  = 2300,
    [7]  = 221,
    [8]  = 2300,
    [9]  = 2300,
    [10] = 5907,
    [11] = 5907,
    [12] = 5907,
    [13] = 221,
}

-- ── Town name by starting room id ────────────────────────────────────────────
Races.town_names = {
    [221]   = "Wehnimer's Landing",
    [7]     = "Ta'Illistim",
    [5907]  = "Ta'Vaalor",
    [4]     = "Zul Logoth",
    [2300]  = "Icemule Trace",
    [4638]  = "Cysaegir",
    [10840] = "River's Rest",
}

return Races
