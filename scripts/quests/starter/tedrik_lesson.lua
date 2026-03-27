local Quest = {}

Quest.key_name    = "tedrik_lesson"
Quest.title       = "Tedrik's Officer's Briefing"
Quest.description = "Sit with Tedrik and prove you absorbed the basics."
Quest.repeatable  = false
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 2

Quest.start_npc_template_id  = "tedrik"
Quest.turnin_npc_template_id = "tedrik"
Quest.start_room_id          = 21223
Quest.start_lich_room_id     = 14102009
Quest.start_message          = "Listen up.  The basics keep more soldiers alive than talent does."

Quest.stages = {
    {
        objective_event = "tedrik_lesson_complete",
        required_count  = 1,
        objective       = "Answer Tedrik's questions correctly.",
        hint            = "Use ANSWER <response> while talking to Tedrik.",
        quiz_questions  = {
            {
                question = "When you're putting away your own gear, what word helps avoid mistakes?  1) your  2) my  3) ours",
                answers  = { "2", "my" },
                right    = "Correct.",
                wrong    = "No.  Try it again.",
            },
            {
                question = "Should you assume loose items in town are yours to grab?  (T/F)",
                answers  = { "f", "false" },
                right    = "Good.",
                wrong    = "Wrong.  That's how discipline fails.",
            },
            {
                question = "If you find another adventurer in trouble, what's the proper move?  1) Offer help  2) Grab loot  3) Walk off",
                answers  = { "1", "offer help", "help" },
                right    = "That's the answer I wanted.",
                wrong    = "No.  Start acting like someone fit for a line unit.",
            },
            {
                question = "Which command is useful when looking for town services?  1) SERVICE  2) THINK  3) STARE",
                answers  = { "1", "service" },
                right    = "Exactly.",
                wrong    = "No.  SERVICE.",
            },
            {
                question = "Where do you report for bounty contracts?  1) Adventurer's Guild  2) Barracks kitchen  3) Any bank",
                answers  = { "1", "adventurer's guild", "guild" },
                right    = "Right.",
                wrong    = "No.  Adventurer's Guild.",
            },
            {
                question = "If an item matters, what should you do with it?  1) Register it  2) Loan it around  3) Drop it in the street",
                answers  = { "1", "register", "register it" },
                right    = "Good.",
                wrong    = "No.  Register it and save yourself trouble.",
            },
        },
    },
}

Quest.rewards = {
    experience = 300,
    silver     = 150,
}

return Quest
