---------------------------------------------------
-- data/items/gems.lua
-- All gem templates for GemStone IV.
-- Source: gswiki.play.net/List_of_gems  (verified 2026-03)
--
-- Only gems confirmed on the official wiki list are included.
-- Gems removed from the original Python file as unverified:
--   "blood marble" is listed under the "marble" type (kept as correct name)
--   "piece of cat's eye quartz" → corrected to match wiki listing
--
-- value: base appraisal value in silvers (range shown as midpoint where known)
-- gem_family: loose grouping for appraisal and lore purposes
-- region: primary drop region ("any" = found everywhere)
---------------------------------------------------

local Gems = {}

Gems.list = {

    -- ── AGATE family ──────────────────────────────────────────────────────────
    { name="a banded agate",           noun="agate",      gem_family="agate",    value=10,   weight=1, region="any",            description="a banded agate" },
    { name="a fire agate",             noun="agate",      gem_family="agate",    value=150,  weight=1, region="any",            description="a fire agate" },
    { name="a frost agate",            noun="agate",      gem_family="agate",    value=15,   weight=1, region="any",            description="a frost agate" },
    { name="a mottled agate",          noun="agate",      gem_family="agate",    value=50,   weight=1, region="any",            description="a mottled agate" },
    { name="a moss agate",             noun="agate",      gem_family="agate",    value=30,   weight=1, region="any",            description="a moss agate" },
    { name="a blue lace agate",        noun="agate",      gem_family="agate",    value=40,   weight=1, region="icemule",        description="a blue lace agate" },
    { name="a cloud agate",            noun="agate",      gem_family="agate",    value=45,   weight=1, region="zul_logoth",     description="a cloud agate" },
    { name="a chameleon agate",        noun="agate",      gem_family="agate",    value=4000, weight=1, region="teras_isle",     description="a chameleon agate" },
    { name="a tigereye agate",         noun="agate",      gem_family="agate",    value=100,  weight=1, region="elven_nations",  description="a tigereye agate" },

    -- ── AMBER ─────────────────────────────────────────────────────────────────
    { name="a piece of golden amber",  noun="amber",      gem_family="amber",    value=400,  weight=1, region="any",            description="a piece of golden amber" },

    -- ── AMETHYST ──────────────────────────────────────────────────────────────
    { name="a deep purple amethyst",   noun="amethyst",   gem_family="amethyst", value=250,  weight=1, region="any",            description="a deep purple amethyst" },
    { name="a smoky amethyst",         noun="amethyst",   gem_family="amethyst", value=750,  weight=1, region="reim",           description="a smoky amethyst" },
    { name="a brilliant wyrm's-tooth amethyst", noun="amethyst", gem_family="amethyst", value=3000, weight=1, region="the_rift", description="a brilliant wyrm's-tooth amethyst" },

    -- ── AQUAMARINE ────────────────────────────────────────────────────────────
    { name="an aquamarine gem",        noun="aquamarine", gem_family="aquamarine", value=750, weight=1, region="any",           description="an aquamarine gem" },

    -- ── BERYL ─────────────────────────────────────────────────────────────────
    { name="a golden beryl gem",       noun="beryl",      gem_family="beryl",    value=200,  weight=1, region="any",            description="a golden beryl gem" },
    { name="a Kezmonian honey beryl",  noun="beryl",      gem_family="beryl",    value=2500, weight=1, region="solhaven",       description="a Kezmonian honey beryl" },

    -- ── BLOODSTONE ────────────────────────────────────────────────────────────
    { name="a dark red-green bloodstone", noun="bloodstone", gem_family="bloodstone", value=50, weight=1, region="any",        description="a dark red-green bloodstone" },

    -- ── CARBUNCLE ─────────────────────────────────────────────────────────────
    { name="a deep red carbuncle",     noun="carbuncle",  gem_family="carbuncle",value=175,  weight=1, region="elven_nations",  description="a deep red carbuncle" },

    -- ── CHALCEDONY ────────────────────────────────────────────────────────────
    { name="a piece of grey chalcedony", noun="chalcedony", gem_family="chalcedony", value=500, weight=1, region="zul_logoth", description="a piece of grey chalcedony" },

    -- ── CORAL ─────────────────────────────────────────────────────────────────
    { name="a piece of blue ridge coral", noun="coral",   gem_family="coral",    value=50,   weight=1, region="solhaven",       description="a piece of blue ridge coral" },
    { name="some polished black coral",  noun="coral",    gem_family="coral",    value=50,   weight=1, region="any",            description="some polished black coral" },
    { name="some polished blue coral",   noun="coral",    gem_family="coral",    value=25,   weight=1, region="any",            description="some polished blue coral" },
    { name="some polished pink coral",   noun="coral",    gem_family="coral",    value=500,  weight=1, region="any",            description="some polished pink coral" },
    { name="some polished red coral",    noun="coral",    gem_family="coral",    value=300,  weight=1, region="any",            description="some polished red coral" },

    -- ── CORDIERITE ────────────────────────────────────────────────────────────
    { name="a blue cordierite",        noun="cordierite", gem_family="cordierite", value=50,  weight=1, region="any",           description="a blue cordierite" },

    -- ── CRYSTAL ───────────────────────────────────────────────────────────────
    { name="a quartz crystal",         noun="crystal",    gem_family="crystal",  value=30,   weight=1, region="any",            description="a quartz crystal" },
    { name="a rock crystal",           noun="crystal",    gem_family="crystal",  value=25,   weight=1, region="any",            description="a rock crystal" },
    { name="a shard of tigerfang crystal", noun="crystal", gem_family="crystal", value=75,   weight=1, region="icemule",        description="a shard of tigerfang crystal" },
    { name="a glaesine crystal",       noun="crystal",    gem_family="crystal",  value=200,  weight=1, region="teras_isle",     description="a glaesine crystal" },

    -- ── DEATHSTONE ────────────────────────────────────────────────────────────
    { name="a black deathstone",       noun="deathstone", gem_family="deathstone", value=500, weight=1, region="teras_isle",    description="a black deathstone" },

    -- ── DIAMOND ───────────────────────────────────────────────────────────────
    { name="an uncut diamond",         noun="diamond",    gem_family="diamond",  value=4500, weight=1, region="any",            description="an uncut diamond" },
    { name="a large yellow diamond",   noun="diamond",    gem_family="diamond",  value=5000, weight=1, region="icemule",        description="a large yellow diamond" },

    -- ── DIOPSIDE ──────────────────────────────────────────────────────────────
    { name="a star diopside",          noun="diopside",   gem_family="diopside", value=25,   weight=1, region="any",            description="a star diopside" },

    -- ── DREAMSTONE ────────────────────────────────────────────────────────────
    { name="a black dreamstone",       noun="dreamstone", gem_family="dreamstone", value=175, weight=1, region="teras_isle",    description="a black dreamstone" },
    { name="a blue dreamstone",        noun="dreamstone", gem_family="dreamstone", value=175, weight=1, region="teras_isle",    description="a blue dreamstone" },
    { name="a green dreamstone",       noun="dreamstone", gem_family="dreamstone", value=175, weight=1, region="teras_isle",    description="a green dreamstone" },
    { name="a red dreamstone",         noun="dreamstone", gem_family="dreamstone", value=175, weight=1, region="teras_isle",    description="a red dreamstone" },
    { name="a white dreamstone",       noun="dreamstone", gem_family="dreamstone", value=175, weight=1, region="teras_isle",    description="a white dreamstone" },

    -- ── EMERALD ───────────────────────────────────────────────────────────────
    { name="an uncut emerald",         noun="emerald",    gem_family="emerald",  value=4500, weight=1, region="any",            description="an uncut emerald" },
    { name="a star emerald",           noun="emerald",    gem_family="emerald",  value=4500, weight=1, region="teras_isle",     description="a star emerald" },
    { name="a dragonfire emerald",     noun="emerald",    gem_family="emerald",  value=2000, weight=1, region="teras_isle",     description="a dragonfire emerald" },

    -- ── FAENOR-BLOOM ──────────────────────────────────────────────────────────
    { name="an olivine faenor-bloom",  noun="faenor-bloom", gem_family="faenor-bloom", value=200, weight=1, region="elven_nations", description="an olivine faenor-bloom" },

    -- ── FIRESTONE ─────────────────────────────────────────────────────────────
    { name="a firestone",              noun="firestone",  gem_family="firestone", value=6000, weight=1, region="teras_isle",     description="a firestone" },

    -- ── GARNET ────────────────────────────────────────────────────────────────
    { name="an almandine garnet",      noun="garnet",     gem_family="garnet",   value=50,   weight=1, region="any",            description="an almandine garnet" },
    { name="a blood red garnet",       noun="garnet",     gem_family="garnet",   value=250,  weight=1, region="icemule",        description="a blood red garnet" },
    { name="a green garnet",           noun="garnet",     gem_family="garnet",   value=175,  weight=1, region="any",            description="a green garnet" },
    { name="an orange spessartine garnet", noun="garnet", gem_family="garnet",   value=700,  weight=1, region="elven_nations",  description="an orange spessartine garnet" },
    { name="a sanguine wyrm's-eye garnet", noun="garnet", gem_family="garnet",  value=1750, weight=1, region="the_rift",        description="a sanguine wyrm's-eye garnet" },

    -- ── GEMS (generic noun) ───────────────────────────────────────────────────
    { name="a bright chrysoberyl gem", noun="gem",        gem_family="chrysoberyl", value=175, weight=1, region="any",          description="a bright chrysoberyl gem" },
    { name="a green chrysoprase gem",  noun="gem",        gem_family="chrysoprase", value=150, weight=1, region="any",          description="a green chrysoprase gem" },

    -- ── GLIMAERSTONE (Elven Nations exclusive) ───────────────────────────────
    { name="a smoky glimaerstone",     noun="glimaerstone", gem_family="glimaerstone", value=500,  weight=1, region="elven_nations", description="a smoky glimaerstone" },
    { name="a clear glimaerstone",     noun="glimaerstone", gem_family="glimaerstone", value=1000, weight=1, region="elven_nations", description="a clear glimaerstone" },
    { name="a green glimaerstone",     noun="glimaerstone", gem_family="glimaerstone", value=900,  weight=1, region="elven_nations", description="a green glimaerstone" },
    { name="a golden glimaerstone",    noun="glimaerstone", gem_family="glimaerstone", value=2000, weight=1, region="elven_nations", description="a golden glimaerstone" },

    -- ── HELIODOR ──────────────────────────────────────────────────────────────
    { name="a pale yellow heliodor",   noun="heliodor",   gem_family="heliodor", value=175,  weight=1, region="elven_nations",  description="a pale yellow heliodor" },

    -- ── HYACINTH ──────────────────────────────────────────────────────────────
    { name="a yellow hyacinth",        noun="hyacinth",   gem_family="hyacinth", value=400,  weight=1, region="elven_nations",  description="a yellow hyacinth" },

    -- ── JACINTH ───────────────────────────────────────────────────────────────
    { name="a fiery jacinth",          noun="jacinth",    gem_family="jacinth",  value=1100, weight=1, region="elven_nations",  description="a fiery jacinth" },

    -- ── JADE ──────────────────────────────────────────────────────────────────
    { name="a piece of brown jade",    noun="jade",       gem_family="jade",     value=175,  weight=1, region="icemule",        description="a piece of brown jade" },
    { name="a piece of green jade",    noun="jade",       gem_family="jade",     value=1000, weight=1, region="icemule",        description="a piece of green jade" },
    { name="a piece of white jade",    noun="jade",       gem_family="jade",     value=500,  weight=1, region="icemule",        description="a piece of white jade" },
    { name="a piece of yellow jade",   noun="jade",       gem_family="jade",     value=175,  weight=1, region="icemule",        description="a piece of yellow jade" },

    -- ── JASPER ────────────────────────────────────────────────────────────────
    { name="a piece of black jasper",  noun="jasper",     gem_family="jasper",   value=50,   weight=1, region="any",            description="a piece of black jasper" },
    { name="a piece of red jasper",    noun="jasper",     gem_family="jasper",   value=50,   weight=1, region="any",            description="a piece of red jasper" },
    { name="a piece of yellow jasper", noun="jasper",     gem_family="jasper",   value=50,   weight=1, region="any",            description="a piece of yellow jasper" },

    -- ── LAPIS LAZULI ──────────────────────────────────────────────────────────
    { name="some blue lapis lazuli",   noun="lazuli",     gem_family="lapis",    value=175,  weight=1, region="any",            description="some blue lapis lazuli" },

    -- ── MARBLE ────────────────────────────────────────────────────────────────
    { name="a piece of blood marble",  noun="marble",     gem_family="marble",   value=50,   weight=1, region="any",            description="a piece of blood marble" },

    -- ── ONYX ──────────────────────────────────────────────────────────────────
    { name="a black onyx",             noun="onyx",       gem_family="onyx",     value=75,   weight=1, region="any",            description="a black onyx" },

    -- ── OPAL ──────────────────────────────────────────────────────────────────
    { name="a fire opal",              noun="opal",       gem_family="opal",     value=750,  weight=1, region="any",            description="a fire opal" },
    { name="a water opal",             noun="opal",       gem_family="opal",     value=500,  weight=1, region="any",            description="a water opal" },
    { name="a black opal",             noun="opal",       gem_family="opal",     value=1500, weight=1, region="any",            description="a black opal" },

    -- ── PEARL ─────────────────────────────────────────────────────────────────
    { name="a lustrous black pearl",   noun="pearl",      gem_family="pearl",    value=400,  weight=1, region="solhaven",       description="a lustrous black pearl" },
    { name="a lustrous white pearl",   noun="pearl",      gem_family="pearl",    value=350,  weight=1, region="any",            description="a lustrous white pearl" },
    { name="a golden pearl",           noun="pearl",      gem_family="pearl",    value=500,  weight=1, region="solhaven",       description="a golden pearl" },

    -- ── RUBY ──────────────────────────────────────────────────────────────────
    { name="an uncut ruby",            noun="ruby",       gem_family="ruby",     value=3500, weight=1, region="any",            description="an uncut ruby" },
    { name="a star ruby",              noun="ruby",       gem_family="ruby",     value=4000, weight=1, region="teras_isle",     description="a star ruby" },

    -- ── SAPPHIRE ──────────────────────────────────────────────────────────────
    { name="an uncut sapphire",        noun="sapphire",   gem_family="sapphire", value=3500, weight=1, region="any",            description="an uncut sapphire" },
    { name="a blue sapphire",          noun="sapphire",   gem_family="sapphire", value=1500, weight=1, region="any",            description="a blue sapphire" },
    { name="a star sapphire",          noun="sapphire",   gem_family="sapphire", value=4000, weight=1, region="teras_isle",     description="a star sapphire" },
    { name="a cat's-eye sapphire",     noun="sapphire",   gem_family="sapphire", value=2000, weight=1, region="elven_nations",  description="a cat's-eye sapphire" },

    -- ── TOPAZ ─────────────────────────────────────────────────────────────────
    { name="a yellow topaz",           noun="topaz",      gem_family="topaz",    value=500,  weight=1, region="any",            description="a yellow topaz" },
    { name="a blue topaz",             noun="topaz",      gem_family="topaz",    value=400,  weight=1, region="any",            description="a blue topaz" },
    { name="a golden topaz",           noun="topaz",      gem_family="topaz",    value=600,  weight=1, region="elven_nations",  description="a golden topaz" },

    -- ── TOURMALINE ────────────────────────────────────────────────────────────
    { name="a polished pink tourmaline", noun="tourmaline", gem_family="tourmaline", value=300, weight=1, region="any",         description="a polished pink tourmaline" },
    { name="a polished green tourmaline", noun="tourmaline", gem_family="tourmaline", value=350, weight=1, region="any",        description="a polished green tourmaline" },

    -- ── ZIRCON ────────────────────────────────────────────────────────────────
    { name="a yellow zircon",          noun="zircon",     gem_family="zircon",   value=110,  weight=1, region="any",            description="a yellow zircon" },
    { name="a green zircon",           noun="zircon",     gem_family="zircon",   value=150,  weight=1, region="any",            description="a green zircon" },
    { name="a red zircon",             noun="zircon",     gem_family="zircon",   value=175,  weight=1, region="any",            description="a red zircon" },
    { name="a blue zircon",            noun="zircon",     gem_family="zircon",   value=120,  weight=1, region="any",            description="a blue zircon" },

    -- ── DUST (gold/platinum) ──────────────────────────────────────────────────
    { name="a pinch of gold dust",     noun="dust",       gem_family="dust",     value=800,  weight=1, region="any",            description="a pinch of gold dust" },
    { name="a dram of gold dust",      noun="dust",       gem_family="dust",     value=2200, weight=1, region="any",            description="a dram of gold dust" },
    { name="a handful of gold dust",   noun="dust",       gem_family="dust",     value=3400, weight=1, region="icemule",        description="a handful of gold dust" },
}

return Gems
