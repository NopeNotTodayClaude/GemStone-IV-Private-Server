-- Room 26018: Burghal Enclave, King's Court
local Room = {}

Room.id          = 26018
Room.zone_id     = 2
Room.title       = "Burghal Enclave, King's Court"
Room.description = "Sloping downward sharply, the tunnel winds its way deeply through the bedrock into the white tufa beneath.  Running northward, the passageway cuts beneath Guardian Keep, the very heart of Ta'Vaalor."

Room.exits = {
    north                = 25296,
}

Room.indoor = true
Room.safe   = true

return Room
