-- Room 10383: Hall of Justice, Courtroom
local Room = {}

Room.id          = 10383
Room.zone_id     = 2
Room.title       = "Hall of Justice, Courtroom"
Room.description = "The deep red and glimmering gold banners of House Vaalor hang unmoving from the thick wooden beams of the courtroom's high ceiling.  Ironwork sconces line the walls, casting an amber light across the polished black marble floors and dark stained thanot panelling."

Room.exits = {
    west                 = 10382,
}

Room.indoor = true
Room.safe   = true

return Room
