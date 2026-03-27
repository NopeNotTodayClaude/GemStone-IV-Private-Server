-- Room 10166: Fearling Pass, Crevasse
local Room = {}
Room.id          = 10166
Room.zone_id     = 9
Room.title       = "Fearling Pass, Crevasse"
Room.description = "Up close, the wall of towering boulders looks impenetrable, but a thin stream slips around behind one of the lichen-etched stones, revealing a narrow squeeze through the rock.  Moss-covered walls press in on either side.  Beyond the crevasse, the sound of wind through trees suggests open forest."
Room.exits = {
    southwest                = 10165,
    northeast                = 10167,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
