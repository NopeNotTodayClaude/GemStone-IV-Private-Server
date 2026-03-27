local Customize = {}

Customize.order_wait = {
    min_seconds = 0,
    max_seconds = 60,
    no_material_seconds = 0,
    default_material_seconds = 10,

    instant_materials = {
        iron = true,
        steel = true,
        bronze = true,
    },

    material_seconds = {
        silver = 5,
        gold = 5,
        invar = 10,
        mithril = 15,
        ora = 20,
        imflass = 25,
        laje = 28,
        carmiln = 30,
        faenor = 34,
        gornar = 36,
        rhimar = 38,
        zorchar = 40,
        drakar = 42,
        razern = 44,
        vaalorn = 46,
        glaes = 48,
        mithglin = 50,
        veniom = 50,
        eahnor = 52,
        vultite = 54,
        rolaren = 55,
        eonake = 56,
        kelyn = 57,
        urglaes = 58,
        golvern = 59,
        krodera = 60,
        kroderine = 60,
        coraesine = 60,
    },
}

return Customize
