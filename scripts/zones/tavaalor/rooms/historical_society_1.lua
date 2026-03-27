-- Room 10336: Ta'Vaalor Historical Society
local Room = {}

Room.id          = 10336
Room.zone_id     = 2
Room.title       = "Ta'Vaalor Historical Society"
Room.description = "The ebonwood and mahogany parquet floor forms an unbroken pattern from one side of this grand entryway to the other.  A pair of tall, narrow windows frame the iron-hinged front door, spilling sunlight into the nearly empty room.  Set at a slight angle just by the entrance is a sparsely ornamented writing desk."

Room.exits = {
    north                = 10337,
    west                 = 10339,
}

Room.indoor = true
Room.safe   = true

return Room
