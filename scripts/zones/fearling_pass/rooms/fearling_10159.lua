-- Room 10159: Fearling Pass, Rocky Trail
local Room = {}
Room.id          = 10159
Room.zone_id     = 9
Room.title       = "Fearling Pass, Rocky Trail"
Room.description = "Guelder rose and sarsaparilla bushes crop up in tiny patches along the sides of the pass, the terrain growing a bit more rugged underfoot.  The trail winds between mossy boulders, their surfaces slick with morning damp."
Room.exits = {
    south                    = 10158,
    north                    = 10160,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
