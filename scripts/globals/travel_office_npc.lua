local Registry = require("data.travel_offices")

local TravelOfficeNPC = {}

local function norm(text)
    return tostring(text or ""):lower():gsub("%s+", " "):gsub("^%s+", ""):gsub("%s+$", "")
end

function TravelOfficeNPC.attach(NPC, office_id)
    local offices = (Registry and Registry.offices) or {}
    local office = offices[office_id] or {}

    function NPC:on_player_talk(player, keyword)
        local topic = norm(keyword)
        if topic == "" then
            return nil
        end

        if topic == "travel" or topic == "routes" or topic == "route" or topic == "destinations"
            or topic == "fares" or topic == "fare" or topic == "prices" or topic == "price"
            or topic == "help" or topic == "schedule" or topic == "time" or topic == "times"
            or topic == "departure" or topic == "departures" or topic == "tickets" or topic == "ticket"
            or topic == "pass" or topic == "day pass" or topic == "day passes" then
            return {
                travel_action = "list_destinations",
                office_id = office_id,
                request_kind = topic,
            }
        end

        local request_kind = "travel"
        local route_topic = topic

        if route_topic:find("^ticket ", 1, true) then
            request_kind = "ticket"
            route_topic = norm(route_topic:sub(8))
        elseif route_topic:find("^pass ", 1, true) then
            request_kind = "pass"
            route_topic = norm(route_topic:sub(6))
        elseif route_topic:find("^day pass ", 1, true) then
            request_kind = "pass"
            route_topic = norm(route_topic:sub(10))
        elseif route_topic:find("^for ", 1, true) then
            route_topic = norm(route_topic:sub(5))
        elseif route_topic:find("^travel ", 1, true) then
            route_topic = norm(route_topic:sub(8))
        end

        return {
            travel_action = "route_request",
            office_id = office_id,
            request_kind = request_kind,
            route_key = route_topic,
        }
    end

    if not NPC.dialogues then
        NPC.dialogues = {}
    end
    if not NPC.dialogues.default then
        local label = tostring(office.clerk_label or NPC.name or "the clerk")
        NPC.dialogues.default = label .. " waits for you to name a destination."
    end
end

return TravelOfficeNPC
