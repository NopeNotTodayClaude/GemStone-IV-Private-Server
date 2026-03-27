local Quest = {}

Quest.key_name    = "trevor_dabbings_lesson"
Quest.title       = "A Gentleman of Trace"
Quest.description = "Listen to Trevor Dabbings and answer his starter questions."
Quest.repeatable  = false
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 2

Quest.start_npc_template_id  = "trevor_dabbings"
Quest.turnin_npc_template_id = "trevor_dabbings"
Quest.start_room_id          = 9005
Quest.start_lich_room_id     = 4043275
Quest.start_message          = "Let us see whether your attention is as sharp as your ambition."

Quest.stages = {
    {
        objective_event = "trevor_dabbings_lesson_complete",
        required_count  = 1,
        objective       = "Answer Trevor Dabbings's questions correctly.",
        hint            = "Use ANSWER <response> while seated with Trevor Dabbings.",
        quiz_questions  = {
            {
                question = "When you put something away safely, what possessive should you use?  1) your  2) my  3) their",
                answers  = { "2", "my" },
                right    = "Quite right.",
                wrong    = "No.  Try again.",
            },
            {
                question = "Items lying in town should be treated as abandoned property.  (T/F)",
                answers  = { "f", "false" },
                right    = "A sound answer.",
                wrong    = "No.  Mind your manners and your hands.",
            },
            {
                question = "If you happen upon a fight already in progress, what is the polite first move?  1) Ask if help is needed  2) Take the coins  3) Interrupt loudly",
                answers  = { "1", "ask if help is needed", "ask" },
                right    = "Good judgment.",
                wrong    = "No.  Courtesy is rarely wasted.",
            },
            {
                question = "Which command helps locate helpful services near you?  1) SERVICE  2) GLANCE  3) CALENDAR",
                answers  = { "1", "service" },
                right    = "Yes.",
                wrong    = "No.  SERVICE is the one you want.",
            },
            {
                question = "Where are adventurers sent for formal bounty work?  1) Adventurer's Guild  2) Temple  3) Pawnshop",
                answers  = { "1", "adventurer's guild", "guild" },
                right    = "Precisely.",
                wrong    = "No.  The Adventurer's Guild.",
            },
            {
                question = "If an item matters to you, what should you do?  1) Register it  2) Leave it on the ground  3) Forget where you set it",
                answers  = { "1", "register", "register it" },
                right    = "Excellent.",
                wrong    = "No.  Register important belongings.",
            },
        },
    },
}

Quest.rewards = {
    experience = 300,
    silver     = 150,
}

return Quest
