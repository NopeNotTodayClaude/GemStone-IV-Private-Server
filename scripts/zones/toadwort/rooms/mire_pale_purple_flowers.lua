-- Room 10515: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10515
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "Moist, soft grass blankets most of the ground in this portion of the swamp, and seemingly dry sand devoid of any visible signs of life covers the rest.  Odd, pale-purple flowers with a touch of yellow in one spot boldly poke their heads high above the grass.  The petals of the flowers are twisted in such a way that they strongly resemble the face of a monkey.  Unseen, but clearly heard, yellow throats call out to one another, and a small nest is located at the base of a stunted, unidentified bush."

Room.exits = {
    north                    = 10514,
    west                     = 10516,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
