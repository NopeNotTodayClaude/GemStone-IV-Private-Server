---------------------------------------------------
-- data/items/weapons.lua
-- All base weapon templates for GemStone IV.
-- Source: server/data/items/weapons/*.py
--
-- Fields:
--   base_name      canonical name used for DB lookup / seeding
--   name           full display name ("a steel longsword")
--   short_name     short display name ("steel longsword")
--   noun           single noun for inventory matching
--   weapon_type    category: edged / blunt / twohanded / polearm /
--                             ranged / thrown / brawling
--   damage_factor  GS4 DF value (float)
--   weapon_speed   roundtime modifier (int)
--   damage_type    comma-separated: slash / puncture / crush
--   weight         in pounds (float)
--   value          base silver value (int)
--   description    long description shown on INSPECT/LOOK
---------------------------------------------------

local Weapons = {}

-- ── Edged Weapons ─────────────────────────────────────────────────────────────
Weapons.edged = {
    { base_name="dagger",        name="a steel dagger",        short_name="steel dagger",        noun="dagger",     damage_factor=0.250, weapon_speed=1, damage_type="slash,puncture",       weight=1.0,  value=50,   description="A small, sharp blade designed for quick strikes and thrusting attacks." },
    { base_name="main gauche",   name="a steel main gauche",   short_name="steel main gauche",   noun="gauche",     damage_factor=0.275, weapon_speed=2, damage_type="slash,puncture",       weight=2.0,  value=120,  description="A parrying dagger with a wide guard, favored by duelists." },
    { base_name="rapier",        name="a steel rapier",        short_name="steel rapier",        noun="rapier",     damage_factor=0.325, weapon_speed=2, damage_type="slash,puncture",       weight=2.5,  value=200,  description="A long, slender thrusting sword with a complex hilt." },
    { base_name="whip-blade",    name="a steel whip-blade",    short_name="steel whip-blade",    noun="whip-blade", damage_factor=0.333, weapon_speed=2, damage_type="slash",                weight=3.0,  value=350,  description="A segmented blade that can flex and lash like a whip." },
    { base_name="katar",         name="a steel katar",         short_name="steel katar",         noun="katar",      damage_factor=0.325, weapon_speed=3, damage_type="slash,puncture",       weight=2.5,  value=180,  description="A thrust-driven punch dagger with a H-shaped handle." },
    { base_name="short sword",   name="a steel short sword",   short_name="steel short sword",   noun="sword",      damage_factor=0.350, weapon_speed=3, damage_type="slash,puncture,crush", weight=3.0,  value=150,  description="A versatile short blade suitable for close combat." },
    { base_name="scimitar",      name="a steel scimitar",      short_name="steel scimitar",      noun="scimitar",   damage_factor=0.375, weapon_speed=4, damage_type="slash,puncture,crush", weight=3.5,  value=250,  description="A curved blade with a single sharp edge, favored by desert warriors." },
    { base_name="estoc",         name="a steel estoc",         short_name="steel estoc",         noun="estoc",      damage_factor=0.425, weapon_speed=4, damage_type="slash,puncture",       weight=4.0,  value=400,  description="A long, stiff thrusting sword designed to pierce armor gaps." },
    { base_name="longsword",     name="a steel longsword",     short_name="steel longsword",     noun="longsword",  damage_factor=0.425, weapon_speed=4, damage_type="slash,puncture,crush", weight=4.0,  value=300,  description="A well-balanced blade suitable for both cutting and thrusting." },
    { base_name="handaxe",       name="a steel handaxe",       short_name="steel handaxe",       noun="handaxe",    damage_factor=0.420, weapon_speed=5, damage_type="slash,crush",          weight=4.5,  value=200,  description="A short-hafted axe with a single cutting head." },
    { base_name="backsword",     name="a steel backsword",     short_name="steel backsword",     noun="backsword",  damage_factor=0.440, weapon_speed=5, damage_type="slash,puncture,crush", weight=4.5,  value=350,  description="A single-edged sword with a basket hilt for hand protection." },
    { base_name="broadsword",    name="a steel broadsword",    short_name="steel broadsword",    noun="broadsword", damage_factor=0.450, weapon_speed=5, damage_type="slash,puncture,crush", weight=5.0,  value=400,  description="A heavy blade with a wide cutting edge and simple crossguard." },
    { base_name="falchion",      name="a steel falchion",      short_name="steel falchion",      noun="falchion",   damage_factor=0.450, weapon_speed=5, damage_type="slash,crush",          weight=5.0,  value=380,  description="A broad, slightly curved cleaver-like sword." },
    { base_name="katana",        name="a steel katana",        short_name="steel katana",        noun="katana",     damage_factor=0.450, weapon_speed=5, damage_type="slash",                weight=4.0,  value=600,  description="A single-edged curved blade with a circular guard and long grip." },
    { base_name="bastard sword", name="a steel bastard sword", short_name="steel bastard sword", noun="sword",      damage_factor=0.450, weapon_speed=6, damage_type="slash,crush",          weight=5.5,  value=500,  description="A hand-and-a-half sword that can be wielded in one or two hands." },
}

-- ── Blunt Weapons ─────────────────────────────────────────────────────────────
Weapons.blunt = {
    { base_name="leather whip",     name="a leather whip",         short_name="leather whip",      noun="whip",     damage_factor=0.275, weapon_speed=2, damage_type="crush",          weight=2.0, value=80,  description="A long, braided leather whip with a weighted tip." },
    { base_name="crowbill",         name="a steel crowbill",       short_name="steel crowbill",    noun="crowbill", damage_factor=0.350, weapon_speed=3, damage_type="puncture,crush", weight=3.0, value=200, description="A hammer with a pointed beak on one side for piercing armor." },
    { base_name="cudgel",           name="a wooden cudgel",        short_name="wooden cudgel",     noun="cudgel",   damage_factor=0.350, weapon_speed=4, damage_type="crush",          weight=4.0, value=30,  description="A short, thick club made from a heavy piece of wood." },
    { base_name="mace",             name="a steel mace",           short_name="steel mace",        noun="mace",     damage_factor=0.400, weapon_speed=4, damage_type="crush",          weight=5.0, value=250, description="A flanged steel mace designed to crush through armor." },
    { base_name="ball and chain",   name="a steel ball and chain", short_name="steel ball and chain", noun="chain", damage_factor=0.400, weapon_speed=6, damage_type="crush",          weight=7.0, value=300, description="A spiked steel ball on a length of chain that strikes with tremendous force." },
    { base_name="morning star",     name="a steel morning star",   short_name="steel morning star", noun="star",    damage_factor=0.450, weapon_speed=5, damage_type="puncture,crush", weight=6.0, value=350, description="A spiked club that punctures and crushes simultaneously." },
    { base_name="hammer",           name="a steel hammer",         short_name="steel hammer",      noun="hammer",   damage_factor=0.425, weapon_speed=5, damage_type="crush",          weight=5.5, value=200, description="A solid steel hammer head mounted on a sturdy haft." },
    { base_name="war hammer",       name="a steel war hammer",     short_name="steel war hammer",  noun="hammer",   damage_factor=0.475, weapon_speed=6, damage_type="crush",          weight=7.0, value=450, description="A heavy, two-faced hammer built to shatter bone and armor." },
}

-- ── Two-Handed Weapons ────────────────────────────────────────────────────────
Weapons.twohanded = {
    { base_name="quarterstaff",   name="a wooden quarterstaff", short_name="quarterstaff",    noun="quarterstaff", damage_factor=0.450, weapon_speed=3, damage_type="crush",        weight=4.0,  value=40,  description="A sturdy wooden staff suitable for both defense and offense." },
    { base_name="runestaff",      name="a runestaff",           short_name="runestaff",       noun="runestaff",    damage_factor=0.250, weapon_speed=6, damage_type="crush",        weight=3.0,  value=500, description="An ancient staff inscribed with glowing runes of arcane power." },
    { base_name="bastard sword",  name="a bastard sword",       short_name="bastard sword",   noun="sword",        damage_factor=0.550, weapon_speed=6, damage_type="slash,crush",  weight=6.0,  value=550, description="A versatile blade that bridges the gap between longsword and greatsword." },
    { base_name="katana",         name="a katana",              short_name="katana",          noun="katana",       damage_factor=0.575, weapon_speed=6, damage_type="slash",        weight=5.0,  value=700, description="A finely-crafted curved blade forged with Eastern techniques." },
    { base_name="military pick",  name="a military pick",       short_name="military pick",   noun="pick",         damage_factor=0.500, weapon_speed=7, damage_type="puncture,crush", weight=7.0, value=400, description="A heavy two-handed pick designed to pierce through armor." },
    { base_name="flail",          name="a flail",               short_name="flail",           noun="flail",        damage_factor=0.575, weapon_speed=7, damage_type="puncture,crush", weight=8.0, value=450, description="A weighted head on a chain that crushes with tremendous force." },
    { base_name="flamberge",      name="a flamberge",           short_name="flamberge",       noun="flamberge",    damage_factor=0.600, weapon_speed=7, damage_type="slash,crush",  weight=8.0,  value=600, description="A broad sword with a wavy blade designed to shear through flesh." },
    { base_name="war mattock",    name="a war mattock",         short_name="war mattock",     noun="mattock",      damage_factor=0.550, weapon_speed=7, damage_type="crush",        weight=9.0,  value=400, description="A fearsome tool with both hammer and pick heads for battle." },
    { base_name="maul",           name="a maul",                short_name="maul",            noun="maul",         damage_factor=0.550, weapon_speed=7, damage_type="crush",        weight=10.0, value=350, description="An enormous two-handed hammer capable of shattering bone." },
    { base_name="two-handed sword", name="a two-handed sword",  short_name="two-handed sword", noun="sword",       damage_factor=0.625, weapon_speed=8, damage_type="slash,crush",  weight=9.0,  value=700, description="A massive blade requiring both hands to wield with deadly grace." },
    { base_name="battle axe",     name="a battle axe",          short_name="battle axe",      noun="axe",          damage_factor=0.650, weapon_speed=8, damage_type="slash,crush",  weight=10.0, value=650, description="A double-headed axe honed sharp enough to cleave through armor." },
    { base_name="claidhmore",     name="a claidhmore",          short_name="claidhmore",      noun="claidhmore",   damage_factor=0.625, weapon_speed=8, damage_type="slash,crush",  weight=9.0,  value=750, description="A legendary great sword of ancient Highland warriors." },
}

-- ── Polearm Weapons ───────────────────────────────────────────────────────────
Weapons.polearm = {
    { base_name="pilum",          name="a pilum",          short_name="pilum",          noun="pilum",    damage_factor=0.350, weapon_speed=3, damage_type="slash,puncture",       weight=3.0,  value=100, description="An ancient spear favored by Roman legions for ranged combat." },
    { base_name="spear",          name="a spear",          short_name="spear",          noun="spear",    damage_factor=0.425, weapon_speed=5, damage_type="slash,puncture",       weight=5.0,  value=150, description="A simple yet effective thrusting weapon balanced for throwing or melee." },
    { base_name="trident",        name="a trident",        short_name="trident",        noun="trident",  damage_factor=0.425, weapon_speed=5, damage_type="slash,puncture",       weight=6.0,  value=250, description="A three-pronged spear that catches and tears more than single-pointed arms." },
    { base_name="halberd",        name="a halberd",        short_name="halberd",        noun="halberd",  damage_factor=0.550, weapon_speed=6, damage_type="slash,puncture,crush", weight=8.0,  value=500, description="A combination weapon with axe, spear, and hook for versatile combat." },
    { base_name="naginata",       name="a naginata",       short_name="naginata",       noun="naginata", damage_factor=0.550, weapon_speed=6, damage_type="slash,puncture,crush", weight=7.0,  value=550, description="A curved blade mounted on a pole, favored by samurai and monks." },
    { base_name="jeddart-axe",    name="a jeddart-axe",    short_name="jeddart-axe",    noun="axe",      damage_factor=0.550, weapon_speed=7, damage_type="slash,crush",          weight=8.0,  value=450, description="A Scottish poleaxe with a vicious head designed for mounted combat." },
    { base_name="hammer of kai",  name="a hammer of kai",  short_name="hammer of kai",  noun="hammer",   damage_factor=0.550, weapon_speed=7, damage_type="puncture,crush",       weight=8.0,  value=800, description="A sacred hammer blessed with divine power to smite the wicked." },
    { base_name="awl-pike",       name="an awl-pike",      short_name="awl-pike",       noun="pike",     damage_factor=0.600, weapon_speed=9, damage_type="puncture,crush",       weight=10.0, value=500, description="A long pike with a narrow point designed to pierce the thickest armor." },
    { base_name="lance",          name="a lance",          short_name="lance",          noun="lance",    damage_factor=0.725, weapon_speed=9, damage_type="puncture,crush",       weight=12.0, value=700, description="A cavalry weapon of incredible reach and force when wielded from horseback." },
}

-- ── Ranged Weapons ────────────────────────────────────────────────────────────
Weapons.ranged = {
    { base_name="short bow",      name="a short bow",     short_name="short bow",     noun="bow",      damage_factor=0.325, weapon_speed=5, damage_type="puncture,slash", weight=3.0, value=200, description="A compact bow designed for maneuverability in close quarters." },
    { base_name="composite bow",  name="a composite bow", short_name="composite bow", noun="bow",      damage_factor=0.350, weapon_speed=6, damage_type="puncture,slash", weight=4.0, value=400, description="A bow constructed from multiple materials for superior power and range." },
    { base_name="long bow",       name="a long bow",      short_name="long bow",      noun="bow",      damage_factor=0.400, weapon_speed=7, damage_type="puncture,slash", weight=5.0, value=500, description="A towering bow requiring considerable strength but delivering devastating force." },
    { base_name="hand crossbow",  name="a hand crossbow", short_name="hand crossbow", noun="crossbow", damage_factor=0.275, weapon_speed=4, damage_type="puncture,slash", weight=3.0, value=300, description="A lightweight crossbow that can be fired one-handed for ambushes." },
    { base_name="light crossbow", name="a light crossbow",short_name="light crossbow",noun="crossbow", damage_factor=0.350, weapon_speed=6, damage_type="puncture,slash", weight=6.0, value=400, description="A crossbow balanced between ease of use and projectile power." },
    { base_name="heavy crossbow", name="a heavy crossbow",short_name="heavy crossbow",noun="crossbow", damage_factor=0.425, weapon_speed=7, damage_type="puncture,slash", weight=8.0, value=600, description="A siege-grade crossbow capable of piercing the heaviest plate armor." },
}

-- ── Thrown Weapons ────────────────────────────────────────────────────────────
Weapons.thrown = {
    { base_name="net",     name="a net",     short_name="net",     noun="net",     damage_factor=0.050, weapon_speed=7, damage_type="crush",    weight=3.0, value=50,  description="A weighted net that entangles foes more than it wounds them." },
    { base_name="dart",    name="a dart",    short_name="dart",    noun="dart",    damage_factor=0.125, weapon_speed=2, damage_type="puncture", weight=0.5, value=10,  description="A small pointed missile useful for quick strikes from afar." },
    { base_name="bola",    name="a bola",    short_name="bola",    noun="bola",    damage_factor=0.205, weapon_speed=5, damage_type="crush",    weight=2.0, value=80,  description="Weights connected by cord that tangle legs when thrown with skill." },
    { base_name="quoit",   name="a quoit",   short_name="quoit",   noun="quoit",   damage_factor=0.255, weapon_speed=5, damage_type="slash",    weight=1.0, value=60,  description="A razor-edged ring that cuts through the air with deadly precision." },
    { base_name="discus",  name="a discus",  short_name="discus",  noun="discus",  damage_factor=0.255, weapon_speed=5, damage_type="crush",    weight=2.0, value=70,  description="A heavy flat disc that crushes what it strikes with rotational force." },
    { base_name="javelin", name="a javelin", short_name="javelin", noun="javelin", damage_factor=0.402, weapon_speed=4, damage_type="puncture", weight=3.0, value=100, description="A well-balanced spear designed for distance throwing with accuracy." },
}

-- ── Brawling Weapons ──────────────────────────────────────────────────────────
Weapons.brawling = {
    { base_name="razorpaw",     name="a razorpaw",     short_name="razorpaw",     noun="razorpaw",  damage_factor=0.275, weapon_speed=1, damage_type="slash",              weight=1.0, value=150, description="Clawed gloves that extend the reach of a warrior's slashing strikes." },
    { base_name="paingrip",     name="a paingrip",     short_name="paingrip",     noun="paingrip",  damage_factor=0.225, weapon_speed=1, damage_type="slash,puncture,crush", weight=1.0, value=120, description="Specialized gloves that inflict multiple types of damage with versatility." },
    { base_name="cestus",       name="a cestus",       short_name="cestus",       noun="cestus",    damage_factor=0.250, weapon_speed=1, damage_type="crush",              weight=1.0, value=100, description="Leather and metal wrapped around the fist for devastating punching power." },
    { base_name="knuckle-duster",name="a knuckle-duster",short_name="knuckle-duster",noun="duster", damage_factor=0.250, weapon_speed=1, damage_type="crush",              weight=1.0, value=80,  description="Brass-studded knuckles that augment natural striking with added weight." },
    { base_name="hook-knife",   name="a hook-knife",   short_name="hook-knife",   noun="knife",     damage_factor=0.250, weapon_speed=1, damage_type="slash,puncture",     weight=0.5, value=90,  description="A curved blade that hooks and tears with each close-quarter strike." },
    { base_name="tiger-claw",   name="a tiger-claw",   short_name="tiger-claw",   noun="claw",      damage_factor=0.275, weapon_speed=1, damage_type="slash,crush",        weight=1.0, value=170, description="Fearsome curved talons mimicking a great cat's lethal grip." },
    { base_name="knuckle-blade",name="a knuckle-blade",short_name="knuckle-blade",noun="blade",     damage_factor=0.250, weapon_speed=1, damage_type="slash,crush",        weight=1.0, value=130, description="A blade integrated into knuckle armor for slashing and crushing." },
    { base_name="yierka-spur",  name="a yierka-spur",  short_name="yierka-spur",  noun="spur",      damage_factor=0.250, weapon_speed=1, damage_type="slash,puncture,crush", weight=1.0, value=200, description="A mystical spur that strikes with slashing, piercing, and crushing force." },
    { base_name="blackjack",    name="a blackjack",    short_name="blackjack",    noun="blackjack", damage_factor=0.250, weapon_speed=1, damage_type="crush",              weight=1.0, value=50,  description="A leather-wrapped weapon filled with lead that delivers a stunning blow." },
    { base_name="jackblade",    name="a jackblade",    short_name="jackblade",    noun="jackblade", damage_factor=0.250, weapon_speed=2, damage_type="slash,crush",        weight=1.5, value=140, description="A hybrid of blackjack and blade combined for improved effectiveness." },
    { base_name="troll-claw",   name="a troll-claw",   short_name="troll-claw",   noun="claw",      damage_factor=0.325, weapon_speed=2, damage_type="slash,crush",        weight=1.5, value=250, description="Claws harvested from a troll, unnaturally sharp and resilient." },
    { base_name="sai",          name="a sai",          short_name="sai",          noun="sai",       damage_factor=0.250, weapon_speed=2, damage_type="puncture",           weight=1.5, value=120, description="A three-pronged striking weapon favored by Eastern martial artists." },
    { base_name="fist-scythe",  name="a fist-scythe",  short_name="fist-scythe",  noun="scythe",    damage_factor=0.350, weapon_speed=3, damage_type="slash,puncture,crush", weight=2.0, value=300, description="A wicked scythe blade mounted on knuckles for devastating melee combat." },
}

return Weapons
