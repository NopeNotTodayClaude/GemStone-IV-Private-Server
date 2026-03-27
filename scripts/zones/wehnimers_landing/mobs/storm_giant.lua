-- Creature: storm giant
-- Zone: Upper Trollfang / Sentoph Deep  |  Level: 39
local Creature = {}
Creature.id              = 9417
Creature.name            = "storm giant"
Creature.level           = 39
Creature.family          = "giant"
Creature.classification  = "living"
Creature.body_type       = "biped"
Creature.hp_base         = 525
Creature.hp_variance     = 28
Creature.ds_melee        = 328
Creature.ds_bolt         = 155
Creature.td_spiritual    = 126
Creature.td_elemental    = 126
Creature.udf             = 0
Creature.armor_asg       = 14
Creature.armor_natural   = false
Creature.attacks = {
    { type="greatsword", as=392, damage_type="slash" },
    { type="fist", as=382, damage_type="crush" },
    { type="lightning_bolt", as=375, damage_type="electricity" },
}
Creature.spells = {
    { name="lightning_strike", cs=198, as=0 },
    { name="call_storm", cs=192, as=0 },
}
Creature.abilities = {
    "call_lightning",
    "thunder_stomp",
    "hurl_boulder",
    "weather_command",
}
Creature.immune    = {
    "electricity",
}
Creature.resist    = {
    "cold",
    "fire",
}
Creature.loot_coins  = true
Creature.loot_gems   = true
Creature.loot_magic  = true
Creature.loot_boxes  = true
Creature.skin        = "a storm giant scale"
Creature.special_loot = {
    "a stormbrand fragment",
    "a lightning-etched runestone",
}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = {
    7767,
    7768,
    7769,
    7770,
    7771,
    7772,
    7773,
    7774,
    6830,
    6831,
    6832,
    6833,
    6834,
    6835
    }
Creature.roam_rooms = {
    7767,
    7768,
    7769,
    7770,
    7771,
    7772,
    7773,
    7774,
    6830,
    6831,
    6832,
    6833,
    6834,
    6835
    }
Creature.roam_chance     = 5
Creature.respawn_seconds = 1200
Creature.max_count       = 1
Creature.description = "The storm giant is less a creature and more an event — a fifty-foot column of barely-contained thunderstorm given living form.  Its skin is grey-blue and crackling with static electricity, and its eyes hold the pale white of lightning about to strike.  When it speaks, the words arrive with the delay of thunder following a flash.  Adventurers have compared engaging one to fighting a thunderstorm with a sharp stick."
return Creature
