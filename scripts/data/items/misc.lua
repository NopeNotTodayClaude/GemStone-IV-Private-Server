---------------------------------------------------
-- data/items/misc.lua
-- Miscellaneous items for GemStone IV.
-- Includes: ores, runestones, scrolls, arrows/bolts,
--           food/drink, tools, pawnshop fodder
--
-- All items verified against gswiki and ps.lichproject.org.
-- "Frog-leg" and similar hallucinated food items removed.
---------------------------------------------------

local Misc = {}

-- ── ORES & RAW MATERIALS ──────────────────────────────────────────────────────
Misc.ores = {
    { name="a chunk of iron ore",      noun="ore",      item_type="ore",  smelt_material="iron",    weight=3, value=10,   description="a chunk of iron ore" },
    { name="a chunk of copper ore",    noun="ore",      item_type="ore",  smelt_material="copper",  weight=3, value=15,   description="a chunk of copper ore" },
    { name="a chunk of silver ore",    noun="ore",      item_type="ore",  smelt_material="silver",  weight=3, value=50,   description="a chunk of silver ore" },
    { name="a chunk of gold ore",      noun="ore",      item_type="ore",  smelt_material="gold",    weight=3, value=100,  description="a chunk of gold ore" },
    { name="a chunk of mithril ore",   noun="ore",      item_type="ore",  smelt_material="mithril", weight=2, value=500,  description="a chunk of mithril ore" },
    { name="a chunk of vultite ore",   noun="ore",      item_type="ore",  smelt_material="vultite", weight=2, value=1000, description="a chunk of vultite ore" },
    { name="a chunk of ora ore",       noun="ore",      item_type="ore",  smelt_material="ora",     weight=2, value=800,  description="a chunk of ora ore" },
    { name="a chunk of rolaren ore",   noun="ore",      item_type="ore",  smelt_material="rolaren", weight=3, value=750,  description="a chunk of rolaren ore" },
    { name="a chunk of glaes",         noun="glaes",    item_type="ore",  smelt_material="glaes",   weight=2, value=900,  description="a chunk of raw glaes" },
    { name="a chunk of kelyn ore",     noun="ore",      item_type="ore",  smelt_material="kelyn",   weight=1, value=2000, description="a chunk of kelyn ore" },
}

-- ── RUNESTONES ────────────────────────────────────────────────────────────────
-- Runestones are consumed by Warriors for combat maneuvers or traded/sold.
Misc.runestones = {
    { name="a black runestone",        noun="runestone", item_type="runestone", rune_type="combat",   weight=1, value=300,  description="a black runestone etched with angular runes" },
    { name="a white runestone",        noun="runestone", item_type="runestone", rune_type="spirit",   weight=1, value=400,  description="a white runestone carved with flowing script" },
    { name="a red runestone",          noun="runestone", item_type="runestone", rune_type="fire",     weight=1, value=350,  description="a red runestone glowing faintly with inner heat" },
    { name="a blue runestone",         noun="runestone", item_type="runestone", rune_type="water",    weight=1, value=350,  description="a blue runestone that feels cool to the touch" },
    { name="a green runestone",        noun="runestone", item_type="runestone", rune_type="earth",    weight=1, value=350,  description="a green runestone flecked with tiny crystals" },
    { name="a grey runestone",         noun="runestone", item_type="runestone", rune_type="air",      weight=1, value=350,  description="a grey runestone worn smooth with age" },
    { name="a silver runestone",       noun="runestone", item_type="runestone", rune_type="arcane",   weight=1, value=500,  description="a silver runestone shimmering with arcane power" },
    { name="a golden runestone",       noun="runestone", item_type="runestone", rune_type="divine",   weight=1, value=600,  description="a golden runestone warm to the touch" },
    { name="a dark runestone",         noun="runestone", item_type="runestone", rune_type="shadow",   weight=1, value=450,  description="a dark runestone that seems to absorb light" },
}

-- ── SCROLLS ───────────────────────────────────────────────────────────────────
Misc.scrolls = {
    { name="a vellum scroll",          noun="scroll", item_type="scroll", scroll_type="spell",   weight=1, value=100, description="a rolled vellum scroll covered in arcane script" },
    { name="a parchment scroll",       noun="scroll", item_type="scroll", scroll_type="spell",   weight=1, value=80,  description="a parchment scroll with faded magical writing" },
    { name="a silk scroll",            noun="scroll", item_type="scroll", scroll_type="spell",   weight=1, value=200, description="a silk scroll inscribed with flowing magical script" },
    { name="a worn leather scroll",    noun="scroll", item_type="scroll", scroll_type="lore",    weight=1, value=50,  description="a worn leather scroll bearing old text" },
    { name="a parchment map",          noun="map",    item_type="scroll", scroll_type="map",     weight=1, value=250, description="a rolled parchment map showing regional geography" },
}

-- ── AMMUNITION (arrows, bolts, thrown) ────────────────────────────────────────
Misc.ammunition = {
    { name="a bundle of arrows",        noun="arrows",  item_type="ammo", ammo_type="arrow",    quantity=20, weight=1.0, value=50,  description="a bundle of twenty steel-tipped arrows" },
    { name="a bundle of oak arrows",    noun="arrows",  item_type="ammo", ammo_type="arrow",    quantity=20, weight=1.0, value=75,  description="a bundle of oak-shafted arrows with flight feathers" },
    { name="a bundle of crossbow bolts",noun="bolts",   item_type="ammo", ammo_type="bolt",     quantity=20, weight=1.5, value=60,  description="a bundle of steel crossbow bolts" },
    { name="a quiver of arrows",        noun="quiver",  item_type="ammo", ammo_type="arrow",    quantity=40, weight=2.0, value=120, description="a leather quiver holding forty arrows" },
    { name="a throwing axe",            noun="axe",     item_type="ammo", ammo_type="thrown",   quantity=1,  weight=2.0, value=100, description="a small steel throwing axe balanced for distance hurling" },
    { name="a dart",                    noun="dart",    item_type="ammo", ammo_type="thrown",   quantity=1,  weight=0.5, value=10,  description="a small weighted dart" },
}

-- ── FOOD & DRINK ──────────────────────────────────────────────────────────────
-- Verified from GS4 tavern and shop menus.
Misc.food = {
    { name="a loaf of bread",           noun="bread",     item_type="food", food_type="food",  hunger=20, weight=1, value=5,   description="a crusty loaf of freshly-baked bread" },
    { name="a meat pie",                noun="pie",       item_type="food", food_type="food",  hunger=35, weight=1, value=15,  description="a savory meat pie with a golden pastry crust" },
    { name="a wedge of cheese",         noun="cheese",    item_type="food", food_type="food",  hunger=15, weight=1, value=8,   description="a wedge of hard yellow cheese" },
    { name="a strip of dried venison",  noun="venison",   item_type="food", food_type="food",  hunger=20, weight=1, value=20,  description="a strip of salted and dried venison, chewy but filling" },
    { name="a cooked trout",            noun="trout",     item_type="food", food_type="food",  hunger=25, weight=1, value=30,  description="a whole trout cooked over an open fire" },
    { name="an apple",                  noun="apple",     item_type="food", food_type="food",  hunger=10, weight=1, value=3,   description="a crisp red apple" },
    { name="a handful of trail rations",noun="rations",   item_type="food", food_type="food",  hunger=30, weight=1, value=10,  description="a handful of dried fruits, nuts, and hardtack" },
    { name="a bowl of beef stew",       noun="stew",      item_type="food", food_type="food",  hunger=40, weight=2, value=25,  description="a steaming bowl of hearty beef stew" },
    { name="a meat-stuffed roll",       noun="roll",      item_type="food", food_type="food",  hunger=30, weight=1, value=20,  description="a soft roll stuffed with spiced minced meat" },
    -- Drinks
    { name="a mug of dark ale",         noun="ale",       item_type="food", food_type="drink", thirst=30, weight=1, value=8,   description="a brimming mug of dark, malty ale" },
    { name="a mug of light ale",        noun="ale",       item_type="food", food_type="drink", thirst=25, weight=1, value=6,   description="a cold mug of crisp light ale" },
    { name="a goblet of red wine",      noun="wine",      item_type="food", food_type="drink", thirst=20, weight=1, value=15,  description="a goblet of deep red wine" },
    { name="a flask of water",          noun="water",     item_type="food", food_type="drink", thirst=40, weight=1, value=2,   description="a clay flask of clean water" },
    { name="a cup of spiced cider",     noun="cider",     item_type="food", food_type="drink", thirst=25, weight=1, value=10,  description="a warm cup of apple cider spiced with cinnamon" },
    { name="a skin of mead",            noun="mead",      item_type="food", food_type="drink", thirst=35, weight=2, value=20,  description="a leather skin full of sweet golden mead" },
}

-- ── ADVENTURING TOOLS ─────────────────────────────────────────────────────────
Misc.tools = {
    { name="a hooded lantern",          noun="lantern",   item_type="light",  weight=2, value=75,  description="a brass hooded lantern that casts a warm circle of light" },
    { name="a torch",                   noun="torch",     item_type="light",  weight=1, value=5,   description="a pitch-soaked pine torch that burns for about an hour" },
    { name="a vial of lamp oil",        noun="oil",       item_type="tool",   weight=1, value=10,  description="a small vial of clear lamp oil" },
    { name="a coil of rope",            noun="rope",      item_type="tool",   weight=3, value=20,  description="a fifty-foot coil of sturdy hemp rope" },
    { name="a grappling hook",          noun="hook",      item_type="tool",   weight=2, value=50,  description="a four-pronged iron grappling hook" },
    { name="a small mirror",            noun="mirror",    item_type="tool",   weight=1, value=15,  description="a polished silver hand mirror" },
    { name="a compass",                 noun="compass",   item_type="tool",   weight=1, value=100, description="a brass compass with a trembling magnetite needle" },
    { name="a fishing pole",            noun="pole",      item_type="tool",   weight=3, value=30,  description="a simple bamboo fishing pole with line and hook" },
    { name="a skinning knife",          noun="knife",     item_type="tool",   weight=1, value=25,  description="a short curved knife for skinning animals" },
    { name="a flint and steel",         noun="flint",     item_type="tool",   weight=1, value=5,   description="a piece of flint and a steel striker for making fire" },
    { name="a copper symbol",           noun="symbol",    item_type="component", weight=1, value=50,  description="a copper arcane symbol used as a magic component" },
    { name="a holy symbol",             noun="symbol",    item_type="component", weight=1, value=100, description="a religious holy symbol inscribed with sacred glyphs" },
    { name="a vaalin stylus",           noun="stylus",    item_type="component", weight=1, value=200, description="a slender vaalin stylus for scribing magical formulae" },
    { name="a simple wooden lute",      noun="lute",      item_type="instrument", weight=3, value=300, description="a simply-made wooden lute with gut strings" },
    { name="a bone flute",              noun="flute",     item_type="instrument", weight=1, value=150, description="a smooth bone flute producing a haunting melodic tone" },
    { name="a small drum",              noun="drum",      item_type="instrument", weight=2, value=200, description="a small hand drum with a taut animal-skin head" },
}

-- ── PAWNSHOP FODDER (sellable misc loot) ──────────────────────────────────────
Misc.pawnables = {
    { name="a small ivory carving",     noun="carving",   item_type="misc", weight=1, value=75,   description="a small carving of an animal worked from ivory" },
    { name="a brass candlestick",       noun="candlestick",item_type="misc",weight=1, value=30,   description="a tarnished brass candlestick" },
    { name="a worn leather purse",      noun="purse",     item_type="misc", weight=1, value=10,   description="a worn leather purse, mostly empty" },
    { name="a tin medallion",           noun="medallion", item_type="misc", weight=1, value=20,   description="a tin medallion bearing an unrecognizable crest" },
    { name="a copper earring",          noun="earring",   item_type="jewelry", weight=1, value=40,  description="a simple copper hoop earring" },
    { name="a silver ring",             noun="ring",      item_type="jewelry", weight=1, value=250, description="a plain silver band ring" },
    { name="a gold ring",               noun="ring",      item_type="jewelry", weight=1, value=800, description="a smooth gold band ring" },
    { name="a tarnished silver necklace",noun="necklace", item_type="jewelry", weight=1, value=300, description="a tarnished silver chain necklace" },
    { name="a golden locket",           noun="locket",    item_type="jewelry", weight=1, value=600, description="a small golden locket on a thin chain" },
    { name="a pearl bracelet",          noun="bracelet",  item_type="jewelry", weight=1, value=750, description="a bracelet of matched freshwater pearls" },
}

return Misc
