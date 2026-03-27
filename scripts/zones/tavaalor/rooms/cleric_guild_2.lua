-- Room 10377: Cleric Guild, Courtyard
local Room = {}

Room.id          = 10377
Room.zone_id     = 2
Room.title       = "Cleric Guild, Courtyard"
Room.description = "Thin columns of ivory form a circular design around the golden domed building situated in the northern end of the courtyard, the metal gleaming in the sunlight.  Pale white cobblestones lead toward the shallow steps of the low structure.  Vines are twined around the large iron gates enclosing the area, the verdant growths blocking all but the tallest buildings of the city from view."

Room.exits = {
    south                = 10376,
}

Room.indoor = true
Room.safe   = true

return Room
