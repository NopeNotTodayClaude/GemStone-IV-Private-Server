-- Room 10397: Saphrie's Herbs and Tinctures
local Room = {}

Room.id          = 10397
Room.zone_id     = 2
Room.title       = "Saphrie's Herbs and Tinctures"
Room.description = "Sturdy wooden cots line the walls of this narrow room, each covered with pristine white linens.  High shelves loaded with herbs and bandages are mounted on the whitewashed walls above the cots.  A gentle breeze, redolent with the fragrance of acantha and blaeston, stirs the gauzy curtains framing the open windows."

Room.exits = {
    west                 = 10396,
}

Room.indoor = true
Room.safe   = true

return Room
