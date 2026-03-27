-- Room 10169: Fearling Pass, Forest Trail
local Room = {}
Room.id          = 10169
Room.zone_id     = 9
Room.title       = "Fearling Pass, Forest Trail"
Room.description = "The wind whips down this corridor created by a canyon of old-growth trees, tearing at a faded banner flapping from a branch overhead.  The banner's colors have long since bled away, leaving only a tattered grey rag.  The trail continues north and south."
Room.exits = {
    south                    = 10168,
    north                    = 10170,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
