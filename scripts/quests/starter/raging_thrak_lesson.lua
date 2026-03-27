local Quest = {}

Quest.key_name    = "raging_thrak_lesson"
Quest.title       = "Thrak's Hard Lessons"
Quest.description = "Hear out Raging Thrak and prove you were listening."
Quest.repeatable  = false
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 2

Quest.start_npc_template_id  = "raging_thrak"
Quest.turnin_npc_template_id = "raging_thrak"
Quest.start_room_id          = 8722
Quest.start_lich_room_id     = 4041001
Quest.start_message          = "Good.  Listen close, answer straight, and don't embarrass yourself."

Quest.stages = {
    {
        objective_event = "raging_thrak_lesson_complete",
        required_count  = 1,
        objective       = "Answer Raging Thrak's questions correctly.",
        hint            = "Use ANSWER <response> while speaking with Raging Thrak.",
        quiz_questions  = {
            {
                question = "When you stash something important, what word should you use before the item name?  1) your  2) my  3) ours",
                answers  = { "2", "my" },
                right    = "Right enough.",
                wrong    = "No.  Try again and think like the item is yours.",
            },
            {
                question = "If you spot an item lying on the ground in town, should you assume it is free for the taking?  (T/F)",
                answers  = { "f", "false" },
                right    = "Good.  Other people's things stay other people's things.",
                wrong    = "Wrong.  That's how fools get a reputation they don't want.",
            },
            {
                question = "If a stunned adventurer is fighting and needs help, what should you do?  1) Ask if help is wanted and assist  2) Grab the treasure  3) Laugh and leave",
                answers  = { "1", "ask if help is wanted and assist", "assist" },
                right    = "Aye.  Decent folk remember that.",
                wrong    = "No.  Start over and try acting like someone worth fighting beside.",
            },
            {
                question = "Which of these is a sensible way to find common town services?  1) GLANCE  2) SERVICE  3) REGISTER",
                answers  = { "2", "service" },
                right    = "That one matters more than you'd think.",
                wrong    = "No.  SERVICE, not blind luck.",
            },
            {
                question = "Where do you go for task-based bounty work?  1) Adventurer's Guild  2) Town fountain  3) Any pawnshop",
                answers  = { "1", "adventurer's guild", "guild" },
                right    = "Good.  At least you were awake for that part.",
                wrong    = "No.  If you want bounties, you go to the Adventurer's Guild.",
            },
            {
                question = "If you care about an item, what should you do with it?  1) Register it  2) Drop it in town  3) Loan it to strangers",
                answers  = { "1", "register", "register it" },
                right    = "Exactly.",
                wrong    = "Wrong.  Register the thing and spare yourself the grief.",
            },
        },
    },
}

Quest.rewards = {
    experience = 300,
    silver     = 150,
}

return Quest
