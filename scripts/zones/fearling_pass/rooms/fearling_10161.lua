-- Room 10161: Fearling Pass, Rocky Trail
local Room = {}
Room.id          = 10161
Room.zone_id     = 9
Room.title       = "Fearling Pass, Rocky Trail"
Room.description = "A sudden rise in the landscape and the trail stair-steps up among a small crown of boulders.  From this vantage point, the Mistydeep River glints silver to the southwest and the towers of Ta'Vaalor are just visible against the sky.  The trail descends northeast into a ravine."
Room.exits = {
    south                    = 10160,
    northeast                = 10162,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
