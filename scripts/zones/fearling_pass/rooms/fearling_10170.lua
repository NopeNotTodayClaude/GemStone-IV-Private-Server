-- Room 10170: Fearling Pass, Forest Trail
local Room = {}
Room.id          = 10170
Room.zone_id     = 9
Room.title       = "Fearling Pass, Forest Trail"
Room.description = "Beams of sunlight cut through the woods as the trees begin to thin out, though apparently more through careful lumbering than natural attrition — the stumps are cleanly cut.  The trail broadens ahead, suggesting the forest gives way to more open terrain to the north."
Room.exits = {
    northwest                = 10169,
    go_path                  = 10171,
    south                    = 10270,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
