local JusticeNPC = {}

local function norm(text)
    return tostring(text or ""):lower():gsub("%s+", " "):gsub("^%s+", ""):gsub("%s+$", "")
end

local function one_of(topic, values)
    for _, value in ipairs(values or {}) do
        if topic == value then
            return true
        end
    end
    return false
end

function JusticeNPC.configure(NPC, ctx)
    ctx = ctx or {}
    NPC.justice_role = ctx.justice_role or NPC.justice_role or "clerk"
    NPC.justice_jurisdiction = ctx.justice_jurisdiction or NPC.justice_jurisdiction
    if not NPC.dialogues then
        NPC.dialogues = {}
    end
    if not NPC.dialogues.default then
        NPC.dialogues.default = "State your business with the law."
    end
end

function JusticeNPC.attach(NPC, ctx)
    JusticeNPC.configure(NPC, ctx)

    function NPC:on_player_talk(player, keyword)
        local topic = norm(keyword)
        local role = tostring(self.justice_role or "clerk")
        local jurisdiction = tostring(self.justice_jurisdiction or "")

        if topic == "" or topic == "hello" or topic == "talk" or topic == "justice" then
            return {
                justice_action = "status",
                justice_role = role,
                jurisdiction_id = jurisdiction,
            }
        end

        if one_of(topic, { "warrant", "warrants", "charges", "history", "banish", "banishment", "status" }) then
            return {
                justice_action = "status",
                justice_role = role,
                jurisdiction_id = jurisdiction,
                request_kind = topic,
            }
        end

        if one_of(topic, { "inquire", "sentence", "time", "release" }) then
            return {
                justice_action = "inquire",
                justice_role = role,
                jurisdiction_id = jurisdiction,
            }
        end

        if one_of(topic, { "fine", "pay", "payment", "debts" }) then
            return {
                justice_action = "pay_prompt",
                justice_role = role,
                jurisdiction_id = jurisdiction,
            }
        end

        if one_of(topic, { "task", "service", "community service", "work", "help service", "help task" }) then
            return {
                justice_action = "service_status",
                justice_role = role,
                jurisdiction_id = jurisdiction,
            }
        end

        if topic == "arrest" or topic == "criminal" or topic == "sentence choice" then
            return {
                justice_action = "judge_review",
                justice_role = role,
                jurisdiction_id = jurisdiction,
            }
        end

        if topic == "accuse" or topic == "crime" then
            return {
                justice_action = "accuse_help",
                justice_role = role,
                jurisdiction_id = jurisdiction,
            }
        end

        return nil
    end
end

return JusticeNPC
