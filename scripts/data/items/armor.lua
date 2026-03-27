---------------------------------------------------
-- data/items/armor.lua
-- All 20 Armor Skin Groups (ASG) for GemStone IV.
-- Source: server/data/items/armor/armor.py + gswiki
--
-- armor_asg    1-20 (GS4 canonical ASG number)
-- armor_group  cloth / leather / scale / chain / plate
-- cva          creature vs armor modifier
-- action_penalty  penalty to DS/AS while wearing
-- weapon_speed    roundtime penalty
-- spell_hindrance spell hindrance percentage
---------------------------------------------------

local Armor = {}

Armor.templates = {
    { base_name="normal clothing",       name="some normal clothing",         short_name="normal clothing",       noun="clothing",    item_type="armor", armor_asg=1,  armor_group="cloth",   cva=25,  action_penalty=0,   weapon_speed=0,  spell_hindrance=0,  weight=2.0,  value=10,    description="Plain everyday clothing offering no real protection." },
    { base_name="robes",                 name="some flowing robes",           short_name="flowing robes",         noun="robes",       item_type="armor", armor_asg=2,  armor_group="cloth",   cva=25,  action_penalty=0,   weapon_speed=0,  spell_hindrance=0,  weight=3.0,  value=50,    description="Loose robes favored by magic users for their lack of hindrance." },
    { base_name="padded armor",          name="some padded armor",            short_name="padded armor",          noun="armor",       item_type="armor", armor_asg=3,  armor_group="leather", cva=24,  action_penalty=0,   weapon_speed=0,  spell_hindrance=0,  weight=4.0,  value=100,   description="Thick quilted cloth offering minimal protection." },
    { base_name="leather jerkin",        name="a leather jerkin",             short_name="leather jerkin",        noun="jerkin",      item_type="armor", armor_asg=4,  armor_group="leather", cva=22,  action_penalty=0,   weapon_speed=0,  spell_hindrance=0,  weight=5.0,  value=150,   description="A simple leather vest covering the torso." },
    { base_name="light leather",         name="some light leather armor",     short_name="light leather",         noun="armor",       item_type="armor", armor_asg=5,  armor_group="leather", cva=20,  action_penalty=0,   weapon_speed=0,  spell_hindrance=0,  weight=5.0,  value=200,   description="Supple leather armor covering vital areas." },
    { base_name="full leather",          name="some full leather armor",      short_name="full leather",          noun="armor",       item_type="armor", armor_asg=6,  armor_group="leather", cva=19,  action_penalty=-1,  weapon_speed=1,  spell_hindrance=0,  weight=8.0,  value=350,   description="Complete leather armor covering the entire body." },
    { base_name="reinforced leather",    name="some reinforced leather armor",short_name="reinforced leather",    noun="armor",       item_type="armor", armor_asg=7,  armor_group="leather", cva=18,  action_penalty=-5,  weapon_speed=2,  spell_hindrance=4,  weight=12.0, value=500,   description="Leather armor reinforced with metal studs and rings." },
    { base_name="double leather",        name="some double leather armor",    short_name="double leather",        noun="armor",       item_type="armor", armor_asg=8,  armor_group="leather", cva=17,  action_penalty=-6,  weapon_speed=2,  spell_hindrance=6,  weight=15.0, value=600,   description="Two layers of hardened leather providing solid protection." },
    { base_name="leather breastplate",   name="a leather breastplate",        short_name="leather breastplate",   noun="breastplate", item_type="armor", armor_asg=9,  armor_group="scale",   cva=11,  action_penalty=-7,  weapon_speed=3,  spell_hindrance=16, weight=18.0, value=800,   description="A rigid boiled leather breastplate with metal fittings." },
    { base_name="cuirbouilli leather",   name="some cuirbouilli leather",     short_name="cuirbouilli leather",   noun="armor",       item_type="armor", armor_asg=10, armor_group="scale",   cva=10,  action_penalty=-8,  weapon_speed=4,  spell_hindrance=20, weight=20.0, value=900,   description="Leather hardened by boiling in wax, offering rigid protection." },
    { base_name="studded leather",       name="some studded leather armor",   short_name="studded leather",       noun="armor",       item_type="armor", armor_asg=11, armor_group="scale",   cva=9,   action_penalty=-10, weapon_speed=5,  spell_hindrance=24, weight=22.0, value=1000,  description="Leather armor covered with metal studs for added defense." },
    { base_name="brigandine armor",      name="some brigandine armor",        short_name="brigandine armor",      noun="armor",       item_type="armor", armor_asg=12, armor_group="scale",   cva=8,   action_penalty=-12, weapon_speed=6,  spell_hindrance=28, weight=25.0, value=1200,  description="Cloth or leather lined with small steel plates riveted inside." },
    { base_name="chain mail",            name="some chain mail",              short_name="chain mail",            noun="mail",        item_type="armor", armor_asg=13, armor_group="chain",   cva=1,   action_penalty=-13, weapon_speed=7,  spell_hindrance=40, weight=30.0, value=1500,  description="Interlocking metal rings forming a flexible metal armor." },
    { base_name="double chain",          name="some double chain mail",       short_name="double chain",          noun="mail",        item_type="armor", armor_asg=14, armor_group="chain",   cva=0,   action_penalty=-14, weapon_speed=8,  spell_hindrance=45, weight=35.0, value=2000,  description="Two layers of chain mail providing superior protection." },
    { base_name="augmented chain",       name="some augmented chain mail",    short_name="augmented chain",       noun="mail",        item_type="armor", armor_asg=15, armor_group="chain",   cva=-1,  action_penalty=-16, weapon_speed=8,  spell_hindrance=55, weight=38.0, value=2500,  description="Chain mail reinforced with metal plates at vital areas." },
    { base_name="chain hauberk",         name="a chain hauberk",              short_name="chain hauberk",         noun="hauberk",     item_type="armor", armor_asg=16, armor_group="chain",   cva=-2,  action_penalty=-18, weapon_speed=9,  spell_hindrance=60, weight=42.0, value=3000,  description="A long chain mail shirt extending to the knees with full sleeves." },
    { base_name="metal breastplate",     name="a metal breastplate",          short_name="metal breastplate",     noun="breastplate", item_type="armor", armor_asg=17, armor_group="plate",   cva=-10, action_penalty=-20, weapon_speed=9,  spell_hindrance=90, weight=40.0, value=4000,  description="A solid metal chest piece providing excellent torso protection." },
    { base_name="augmented breastplate", name="an augmented breastplate",     short_name="augmented breastplate", noun="breastplate", item_type="armor", armor_asg=18, armor_group="plate",   cva=-11, action_penalty=-25, weapon_speed=10, spell_hindrance=92, weight=45.0, value=5000,  description="A breastplate with additional pauldrons and arm guards." },
    { base_name="half plate",            name="some half plate armor",        short_name="half plate",            noun="armor",       item_type="armor", armor_asg=19, armor_group="plate",   cva=-12, action_penalty=-30, weapon_speed=11, spell_hindrance=94, weight=50.0, value=7000,  description="Plate armor covering the torso, shoulders, and upper legs." },
    { base_name="full plate",            name="a suit of full plate armor",   short_name="full plate",            noun="armor",       item_type="armor", armor_asg=20, armor_group="plate",   cva=-13, action_penalty=-35, weapon_speed=12, spell_hindrance=96, weight=60.0, value=10000, description="Complete suit of articulated steel plates covering the entire body." },
}

return Armor
