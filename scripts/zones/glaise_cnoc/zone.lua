---------------------------------------------------
-- Glaise Cnoc Cemetery & Plains of Bone
-- Ancient elven burial ground outside Ta'Vaalor
-- Connected to Timmorain Road (south) and Aradhul Road (north)
-- Level range: 1-20 (cemetery) / 8-20 (Plains of Bone)
---------------------------------------------------

local Zone = {}

Zone.id        = 3
Zone.name      = "Glaise Cnoc"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 20
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Glaise Cnoc Cemetery loaded.")
end

function Zone.onTick(elapsed)
end

function Zone.onPlayerEnter(player)
end

function Zone.onPlayerLeave(player)
end

Zone.ambient_messages = {
    "A cool breeze stirs the leaves overhead, sending a few spiraling to the ground.",
    "Somewhere in the distance, a crow calls out once, then falls silent.",
    "The sweet scent of wildflowers mingles with the faint smell of damp earth.",
    "A chipmunk darts between headstones and vanishes into the underbrush.",
    "The iron fence creaks softly as the wind passes through it.",
    "Fat bumblebees drone lazily between the flowers lining the path.",
    "Sunlight filters through the canopy in shifting patterns of gold and green.",
    "A songbird trills briefly from somewhere high in the branches above.",
    "The gravel path crunches softly underfoot in the stillness.",
    "A distant rustling in the brush betrays the movement of some unseen creature.",
    -- Plains of Bone ambients (triggered only in those rooms via onEnter)
}

Zone.ambient_interval = 120

return Zone
