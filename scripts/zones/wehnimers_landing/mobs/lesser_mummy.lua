-- Creature: lesser mummy
-- Zone: wehnimers_landing / The Graveyard  |  Level: 6
-- Source: gswiki.play.net/Lesser_mummy
-- HP: 91 | AS: claw 108 / ensnare 118 AS | DS: 37 | bolt DS: 33 | TD: 18
-- ASG: 8N | Body: biped
-- Treasure: coins+boxes | Skin: a mummy's shroud
local Creature = {}
Creature.id              = 9335
Creature.name            = "lesser mummy"
Creature.level           = 6
Creature.family          = "humanoid"
Creature.classification  = "corporeal_undead"
Creature.body_type       = "biped"
Creature.hp_base         = 91
Creature.hp_variance     = 9
Creature.ds_melee        = 37
Creature.ds_bolt         = 33
Creature.td_spiritual    = 18
Creature.td_elemental    = 18
Creature.udf             = 60
Creature.armor_asg       = 8
Creature.armor_natural   = true
Creature.attacks = {
    { type = "claw", as = 108, damage_type = "slash" },
    { type = "ensnare", as = 118, damage_type = "crush" },
}
Creature.spells = {

}
Creature.abilities = { "disease_touch" }
Creature.immune    = { "disease", "poison", "fear" }
Creature.resist    = {}
Creature.loot_coins   = true
Creature.loot_gems    = true
Creature.loot_magic   = true
Creature.loot_boxes   = true
Creature.skin         = "a mummy's shroud"
Creature.special_loot = {}
Creature.decay_seconds = 300
Creature.crumbles      = false
Creature.decay_message = ""
Creature.spawn_rooms = { 7163, 7164, 7165, 7166, 7167, 7168, 7169, 7170, 7171, 7172, 7173, 7174, 7175, 7200, 7201, 7202, 7203, 7204, 7205, 7206, 7207, 7208, 7209, 7210, 7211, 7212, 7245, 7246, 7247, 7248, 7249, 7250, 7251, 7252, 7253, 7254 }
Creature.roam_rooms  = { 7163, 7164, 7165, 7166, 7167, 7168, 7169, 7170, 7171, 7172, 7173, 7174, 7175, 7200, 7201, 7202, 7203, 7204, 7205, 7206, 7207, 7208, 7209, 7210, 7211, 7212, 7245, 7246, 7247, 7248, 7249, 7250, 7251, 7252, 7253, 7254 }
Creature.roam_chance     = 20
Creature.respawn_seconds = 250
Creature.max_count       = 5
Creature.description = "The lesser mummy shuffles with the dead weight of something that should not be moving at all. Its wrappings are ancient, stained dark in old patterns that might once have been ceremonial, and they have been compressed so tightly against the desiccated form beneath that every joint bends wrong. The ensnare it delivers has nothing to do with training — the bandage wrappings simply lash out."
return Creature
