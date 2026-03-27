-- Room 10270: Fearling Pass, Cobbled Road
local Room = {}
Room.id          = 10270
Room.zone_id     = 9
Room.title       = "Fearling Pass, Cobbled Road"
Room.description = "Young maples flourish amid more stately trees and much of the landscape gives way to brush as the dirt trail merges with a stretch of old cobblestone road.  The road bends sharply here, worn ruts in the stone marking years of heavy use.  A rocky trail branches northeast."
Room.exits = {
    southwest                = 6101,
    northeast                = 10121,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
