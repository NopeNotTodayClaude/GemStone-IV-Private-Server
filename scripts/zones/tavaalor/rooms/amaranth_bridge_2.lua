-- Room 6104: Ta'Vaalor, Amaranth Bridge
local Room = {}

Room.id          = 6104
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Bridge"
Room.description = "The far end of the Amaranth Bridge meets the northern bank of the Mistydeep River, where a cobblestone road continues northwest toward Fearling Pass.  The bridge's pale limestone railing is carved with reliefs of elven soldiers in disciplined formation.  Behind you to the southeast, the first span of the bridge leads back toward the Amaranth Gate."

Room.exits = {
    southeast                = 6103,
    northwest                = 3557,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
