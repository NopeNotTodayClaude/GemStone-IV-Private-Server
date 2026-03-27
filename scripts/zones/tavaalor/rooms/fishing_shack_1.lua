-- Room 13482: Ta'Vaalor, Fishing Shack
local Room = {}

Room.id          = 13482
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Fishing Shack"
Room.description = "A small wooden counter with various shelves underneath is the only adornment to this cramped shack.  Various fishing poles have been hung on the walls, and the counter shelves hold lures, weights, chests, and other fishing items.  A withered looking elf mans the counter, muttering to himself on occasion.  An opening lies on the east wall, through which a smoky aroma with an undercurrent of seared fish wafts."

Room.exits = {
    out                  = 10381,
    east                 = 14032,
}

Room.indoor = true
Room.safe   = true

return Room
