-- Room 15931: Fearling Pass, Ridge
local Room = {}
Room.id          = 15931
Room.zone_id     = 9
Room.title       = "Fearling Pass, Ridge"
Room.description = "To the north, a large lake spans the view, its dark expanse both eerie and still, while in the opposite direction the Mistydeep River valley falls away below.  The ridge is narrow and windswept, the footing treacherous with loose shale.  A rickety shack clings to the eastern slope below."
Room.exits = {
    southeast                = 10168,
    go_shack                 = 15939,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
