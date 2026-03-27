-- Room 34455: Yasrenila, Wisteria Walk
local Room = {}

Room.id          = 34455
Room.zone_id     = 5
Room.title       = "Yasrenila, Wisteria Walk"
Room.description = "Lush curtains of wisteria drape from gnarled boughs that bend over the petal-strewn path leading through the trees.  Reflecting the moonlight breaking through the floral canopy, a fall of thirteen glass teardrops glints within the plethora of royal purple blooms.  Bats flit chaotically through the cloud-like shroud, diving toward the glittering droplets to pilfer a snack in the silver-cast forest.  A live-edge juniper bench nestles between a web of exposed roots."

Room.exits = {
    southeast                = 34453,
    north                    = 34459,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
