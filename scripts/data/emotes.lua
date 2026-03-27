---------------------------------------------------
-- data/emotes.lua
-- All social emote definitions for GemStone IV.
--
-- Each entry:
--   verb      (string)  - the command players type
--   self      (string)  - shown to the player when no target
--   room      (string)  - shown to others when no target  ({name} = actor)
--   self_t    (string)  - shown to actor when targeting someone  ({target} = target name)
--   target_t  (string)  - shown to target  ({name} = actor)
--   room_t    (string)  - shown to everyone else  ({name} = actor, {target} = target)
--
-- Optional flags:
--   no_target (bool)    - emote makes no sense without a target (show hint if used alone)
--   self_only (bool)    - emote has no targeted variant
---------------------------------------------------

local Emotes = {}

Emotes.list = {

    -- ── GREETINGS & FAREWELLS ───────────────────────────────────────────────
    { verb="bow",
      self="You bow.",                            room="{name} bows.",
      self_t="You bow to {target}.",              target_t="{name} bows to you.",             room_t="{name} bows to {target}." },

    { verb="wave",
      self="You wave.",                           room="{name} waves.",
      self_t="You wave to {target}.",             target_t="{name} waves to you.",            room_t="{name} waves to {target}." },

    { verb="curtsy",
      self="You curtsy.",                         room="{name} curtsies.",
      self_t="You curtsy to {target}.",           target_t="{name} curtsies to you.",         room_t="{name} curtsies to {target}." },

    { verb="salute",
      self="You salute sharply.",                 room="{name} salutes.",
      self_t="You salute {target}.",              target_t="{name} salutes you.",             room_t="{name} salutes {target}." },

    { verb="greet",
      self="You extend a warm greeting.",         room="{name} extends a warm greeting.",
      self_t="You greet {target} warmly.",        target_t="{name} greets you warmly.",       room_t="{name} greets {target} warmly." },

    { verb="tip",
      self="You tip your hat.",                   room="{name} tips their hat.",
      self_t="You tip your hat to {target}.",     target_t="{name} tips their hat to you.",   room_t="{name} tips their hat to {target}." },

    { verb="beckon",
      self="You beckon invitingly.",              room="{name} beckons.",
      self_t="You beckon {target} closer.",       target_t="{name} beckons you closer.",      room_t="{name} beckons {target} closer." },

    { verb="farewell",
      self="You bid the world farewell.",         room="{name} bids everyone farewell.",
      self_t="You bid {target} farewell.",        target_t="{name} bids you farewell.",       room_t="{name} bids {target} farewell." },

    -- ── FACIAL EXPRESSIONS ──────────────────────────────────────────────────
    { verb="smile",
      self="You smile.",                          room="{name} smiles.",
      self_t="You smile at {target}.",            target_t="{name} smiles at you.",           room_t="{name} smiles at {target}." },

    { verb="grin",
      self="You grin.",                           room="{name} grins.",
      self_t="You grin at {target}.",             target_t="{name} grins at you.",            room_t="{name} grins at {target}." },

    { verb="smirk",
      self="You smirk.",                          room="{name} smirks.",
      self_t="You smirk at {target}.",            target_t="{name} smirks at you.",           room_t="{name} smirks at {target}." },

    { verb="beam",
      self="You beam with pride.",                room="{name} beams with pride.",
      self_t="You beam at {target}.",             target_t="{name} beams at you.",            room_t="{name} beams at {target}." },

    { verb="frown",
      self="You frown.",                          room="{name} frowns.",
      self_t="You frown at {target}.",            target_t="{name} frowns at you.",           room_t="{name} frowns at {target}." },

    { verb="scowl",
      self="You scowl.",                          room="{name} scowls.",
      self_t="You scowl at {target}.",            target_t="{name} scowls at you.",           room_t="{name} scowls at {target}." },

    { verb="glare",
      self="You glare.",                          room="{name} glares.",
      self_t="You glare at {target}.",            target_t="{name} glares at you.",           room_t="{name} glares at {target}." },

    { verb="wink",
      self="You wink.",                           room="{name} winks.",
      self_t="You wink at {target}.",             target_t="{name} winks at you.",            room_t="{name} winks at {target}." },

    { verb="blink",
      self="You blink.",                          room="{name} blinks.",
      self_t="You blink at {target}.",            target_t="{name} blinks at you.",           room_t="{name} blinks at {target}." },

    { verb="squint",
      self="You squint.",                         room="{name} squints.",
      self_t="You squint at {target}.",           target_t="{name} squints at you.",          room_t="{name} squints at {target}." },

    { verb="blanch",
      self="You blanch.",                         room="{name} blanches.",
      self_t="You blanch at {target}.",           target_t="{name} blanches at you.",         room_t="{name} blanches at {target}." },

    { verb="flush",
      self="Your cheeks flush.",                  room="{name}'s cheeks flush.",
      self_t="Your cheeks flush looking at {target}.", target_t="{name}'s cheeks flush as they look at you.", room_t="{name}'s cheeks flush as they look at {target}." },

    { verb="pout",
      self="You pout.",                           room="{name} pouts.",
      self_t="You pout at {target}.",             target_t="{name} pouts at you.",            room_t="{name} pouts at {target}." },

    { verb="sneer",
      self="You sneer.",                          room="{name} sneers.",
      self_t="You sneer at {target}.",            target_t="{name} sneers at you.",           room_t="{name} sneers at {target}." },

    { verb="leer",
      self="You leer.",                           room="{name} leers.",
      self_t="You leer at {target}.",             target_t="{name} leers at you.",            room_t="{name} leers at {target}." },

    -- ── LAUGHTER & AMUSEMENT ────────────────────────────────────────────────
    { verb="laugh",
      self="You laugh!",                          room="{name} laughs!",
      self_t="You laugh at {target}!",            target_t="{name} laughs at you!",           room_t="{name} laughs at {target}!" },

    { verb="chuckle",
      self="You chuckle to yourself.",            room="{name} chuckles.",
      self_t="You chuckle at {target}.",          target_t="{name} chuckles at you.",         room_t="{name} chuckles at {target}." },

    { verb="snicker",
      self="You snicker.",                        room="{name} snickers.",
      self_t="You snicker at {target}.",          target_t="{name} snickers at you.",         room_t="{name} snickers at {target}." },

    { verb="cackle",
      self="You cackle!",                         room="{name} cackles!",
      self_t="You cackle at {target}!",           target_t="{name} cackles at you!",          room_t="{name} cackles at {target}!" },

    { verb="giggle",
      self="You giggle.",                         room="{name} giggles.",
      self_t="You giggle at {target}.",           target_t="{name} giggles at you.",          room_t="{name} giggles at {target}." },

    { verb="titter",
      self="You titter with amusement.",          room="{name} titties with amusement.",
      self_t="You titter at {target}.",           target_t="{name} titters at you.",          room_t="{name} titters at {target}." },

    { verb="chortle",
      self="You chortle gleefully.",              room="{name} chortles gleefully.",
      self_t="You chortle at {target}.",          target_t="{name} chortles at you.",         room_t="{name} chortles at {target}." },

    { verb="howl",
      self="You howl with laughter!",             room="{name} howls with laughter!",
      self_t="You howl with laughter at {target}!", target_t="{name} howls with laughter at you!", room_t="{name} howls with laughter at {target}!" },

    { verb="rofl",
      self="You roll on the floor laughing!",     room="{name} rolls on the floor laughing!",
      self_t="You roll on the floor laughing at {target}!", target_t="{name} rolls on the floor laughing at you!", room_t="{name} rolls on the floor laughing at {target}!" },

    -- ── SADNESS & DISTRESS ──────────────────────────────────────────────────
    { verb="cry",
      self="You cry.",                            room="{name} cries.",
      self_t="You cry on {target}.",              target_t="{name} cries on you.",            room_t="{name} cries on {target}." },

    { verb="weep",
      self="You weep quietly.",                   room="{name} weeps quietly.",
      self_t="You weep on {target}'s shoulder.",  target_t="{name} weeps on your shoulder.",  room_t="{name} weeps on {target}'s shoulder." },

    { verb="sob",
      self="You sob.",                            room="{name} sobs.",
      self_t="You sob on {target}.",              target_t="{name} sobs on you.",             room_t="{name} sobs on {target}." },

    { verb="sniffle",
      self="You sniffle.",                        room="{name} sniffles.",
      self_t="You sniffle at {target}.",          target_t="{name} sniffles at you.",         room_t="{name} sniffles at {target}." },

    { verb="whimper",
      self="You whimper.",                        room="{name} whimpers.",
      self_t="You whimper at {target}.",          target_t="{name} whimpers at you.",         room_t="{name} whimpers at {target}." },

    { verb="mope",
      self="You mope dejectedly.",                room="{name} mopes dejectedly.",
      self_t="You mope at {target}.",             target_t="{name} mopes at you.",            room_t="{name} mopes at {target}." },

    -- ── SIGHS & REACTIONS ───────────────────────────────────────────────────
    { verb="sigh",
      self="You sigh.",                           room="{name} sighs.",
      self_t="You sigh at {target}.",             target_t="{name} sighs at you.",            room_t="{name} sighs at {target}." },

    { verb="groan",
      self="You groan.",                          room="{name} groans.",
      self_t="You groan at {target}.",            target_t="{name} groans at you.",           room_t="{name} groans at {target}." },

    { verb="gasp",
      self="You gasp!",                           room="{name} gasps!",
      self_t="You gasp at {target}!",             target_t="{name} gasps at you!",            room_t="{name} gasps at {target}!" },

    { verb="gulp",
      self="You gulp nervously.",                 room="{name} gulps nervously.",
      self_t="You gulp looking at {target}.",     target_t="{name} gulps nervously looking at you.", room_t="{name} gulps looking at {target}." },

    { verb="shudder",
      self="You shudder.",                        room="{name} shudders.",
      self_t="You shudder at {target}.",          target_t="{name} shudders at you.",         room_t="{name} shudders at {target}." },

    { verb="tremble",
      self="You tremble.",                        room="{name} trembles.",
      self_t="You tremble before {target}.",      target_t="{name} trembles before you.",     room_t="{name} trembles before {target}." },

    { verb="wince",
      self="You wince.",                          room="{name} winces.",
      self_t="You wince at {target}.",            target_t="{name} winces at you.",           room_t="{name} winces at {target}." },

    { verb="flinch",
      self="You flinch.",                         room="{name} flinches.",
      self_t="You flinch away from {target}.",    target_t="{name} flinches away from you.",  room_t="{name} flinches away from {target}." },

    { verb="cringe",
      self="You cringe.",                         room="{name} cringes.",
      self_t="You cringe away from {target}.",    target_t="{name} cringes away from you.",   room_t="{name} cringes away from {target}." },

    { verb="shrug",
      self="You shrug.",                          room="{name} shrugs.",
      self_t="You shrug at {target}.",            target_t="{name} shrugs at you.",           room_t="{name} shrugs at {target}." },

    -- ── THINKING & PONDERING ────────────────────────────────────────────────
    { verb="ponder",
      self="You appear to be deep in thought.",   room="{name} appears to be deep in thought.",
      self_t="You ponder {target} thoughtfully.", target_t="{name} ponders you thoughtfully.", room_t="{name} ponders {target} thoughtfully." },

    { verb="think",
      self="You tap your chin in thought.",       room="{name} taps their chin in thought.",
      self_t="You ponder {target} carefully.",    target_t="{name} ponders you carefully.",   room_t="{name} ponders {target} carefully." },

    { verb="wonder",
      self="You stare off into space, wondering.", room="{name} stares off into space, wondering.",
      self_t="You stare at {target} with a wondering look.", target_t="{name} stares at you with a wondering look.", room_t="{name} stares at {target} with a wondering look." },

    { verb="contemplate",
      self="You contemplate the mysteries of Elanthia.", room="{name} contemplates the mysteries of Elanthia.",
      self_t="You contemplate {target}.",         target_t="{name} contemplates you.",        room_t="{name} contemplates {target}." },

    { verb="muse",
      self="You muse quietly to yourself.",       room="{name} muses quietly.",
      self_t="You muse about {target}.",          target_t="{name} muses about you.",         room_t="{name} muses about {target}." },

    -- ── AGREEMENT & DISAGREEMENT ────────────────────────────────────────────
    { verb="nod",
      self="You nod.",                            room="{name} nods.",
      self_t="You nod to {target}.",              target_t="{name} nods to you.",             room_t="{name} nods to {target}." },

    { verb="agree",
      self="You nod in agreement.",               room="{name} nods in agreement.",
      self_t="You nod in agreement with {target}.", target_t="{name} nods in agreement with you.", room_t="{name} nods in agreement with {target}." },

    { verb="disagree",
      self="You shake your head in disagreement.", room="{name} shakes their head in disagreement.",
      self_t="You shake your head at {target}.",  target_t="{name} shakes their head at you.", room_t="{name} shakes their head at {target}." },

    { verb="protest",
      self="You protest loudly.",                 room="{name} protests loudly.",
      self_t="You protest {target}'s logic.",     target_t="{name} protests your logic.",     room_t="{name} protests {target}'s logic." },

    -- ── BODY LANGUAGE ───────────────────────────────────────────────────────
    { verb="lean",
      self="You lean against the nearest surface.", room="{name} leans casually.",
      self_t="You lean toward {target}.",         target_t="{name} leans toward you.",        room_t="{name} leans toward {target}." },

    { verb="stretch",
      self="You stretch out, cracking your back.", room="{name} stretches.",
      self_t="You stretch beside {target}.",      target_t="{name} stretches beside you.",    room_t="{name} stretches beside {target}." },

    { verb="yawn",
      self="You yawn broadly.",                   room="{name} yawns broadly.",
      self_t="You yawn at {target}.",             target_t="{name} yawns at you.",            room_t="{name} yawns at {target}." },

    { verb="fidget",
      self="You fidget restlessly.",              room="{name} fidgets restlessly.",
      self_t="You fidget nervously at {target}.", target_t="{name} fidgets nervously at you.", room_t="{name} fidgets nervously at {target}." },

    { verb="pace",
      self="You pace back and forth.",            room="{name} paces back and forth.",
      self_t="You pace in front of {target}.",    target_t="{name} paces in front of you.",   room_t="{name} paces in front of {target}." },

    { verb="tap",
      self="You tap your foot impatiently.",      room="{name} taps their foot impatiently.",
      self_t="You tap your foot looking at {target}.", target_t="{name} taps their foot looking at you.", room_t="{name} taps their foot looking at {target}." },

    { verb="crack",
      self="You crack your knuckles.",            room="{name} cracks their knuckles.",
      self_t="You crack your knuckles at {target}.", target_t="{name} cracks their knuckles at you.", room_t="{name} cracks their knuckles at {target}." },

    { verb="cross",
      self="You cross your arms.",                room="{name} crosses their arms.",
      self_t="You cross your arms at {target}.",  target_t="{name} crosses their arms at you.", room_t="{name} crosses their arms at {target}." },

    { verb="stomp",
      self="You stomp your foot.",                room="{name} stomps their foot.",
      self_t="You stomp your foot at {target}.",  target_t="{name} stomps their foot at you.", room_t="{name} stomps their foot at {target}." },

    { verb="stamp",
      self="You stamp your foot.",                room="{name} stamps their foot.",
      self_t="You stamp your foot at {target}.",  target_t="{name} stamps their foot at you.", room_t="{name} stamps their foot at {target}." },

    { verb="twiddle",
      self="You twiddle your thumbs.",            room="{name} twiddles their thumbs.",
      self_t="You twiddle your thumbs at {target}.", target_t="{name} twiddles their thumbs at you.", room_t="{name} twiddles their thumbs at {target}." },

    { verb="shiver",
      self="You shiver.",                         room="{name} shivers.",
      self_t="You shiver at {target}.",           target_t="{name} shivers at you.",          room_t="{name} shivers at {target}." },

    { verb="sweat",
      self="You break out in a nervous sweat.",   room="{name} breaks out in a nervous sweat.",
      self_t="You sweat nervously around {target}.", target_t="{name} sweats nervously around you.", room_t="{name} sweats nervously around {target}." },

    -- ── AFFECTION ───────────────────────────────────────────────────────────
    { verb="hug",
      self="You hug yourself warmly.",            room="{name} hugs themselves.",
      self_t="You hug {target}.",                 target_t="{name} hugs you.",                room_t="{name} hugs {target}." },

    { verb="kiss",
      self="You blow a kiss.",                    room="{name} blows a kiss.",
      self_t="You kiss {target} on the cheek.",   target_t="{name} kisses you on the cheek.", room_t="{name} kisses {target} on the cheek." },

    { verb="pat",
      self="You pat yourself on the back.",       room="{name} pats themselves on the back.",
      self_t="You pat {target} on the back.",     target_t="{name} pats you on the back.",    room_t="{name} pats {target} on the back." },

    { verb="ruffle",
      self="You smooth your own hair.",           room="{name} smooths their hair.",
      self_t="You ruffle {target}'s hair.",       target_t="{name} ruffles your hair.",       room_t="{name} ruffles {target}'s hair." },

    { verb="nudge",
      self="You nudge no one in particular.",     room="{name} nudges the air.",
      self_t="You nudge {target}.",               target_t="{name} nudges you.",              room_t="{name} nudges {target}." },

    { verb="poke",
      self="You poke yourself.",                  room="{name} pokes themselves.",
      self_t="You poke {target}.",                target_t="{name} pokes you.",               room_t="{name} pokes {target}." },

    { verb="pinch",
      self="You pinch yourself to make sure you're awake.", room="{name} pinches themselves.",
      self_t="You pinch {target}.",               target_t="{name} pinches you!",             room_t="{name} pinches {target}." },

    { verb="tackle",
      self="You dive at nothing in particular.",  room="{name} dives at nothing.",
      self_t="You tackle {target}!",              target_t="{name} tackles you!",             room_t="{name} tackles {target}!" },

    { verb="snuggle",
      self="You snuggle into a comfortable position.", room="{name} snuggles.",
      self_t="You snuggle up to {target}.",       target_t="{name} snuggles up to you.",      room_t="{name} snuggles up to {target}." },

    { verb="cuddle",
      self="You look around for someone to cuddle.", room="{name} looks around for someone to cuddle.",
      self_t="You cuddle {target}.",              target_t="{name} cuddles you.",             room_t="{name} cuddles {target}." },

    -- ── AGGRESSION & CHALLENGE ──────────────────────────────────────────────
    { verb="growl",
      self="You growl.",                          room="{name} growls.",
      self_t="You growl at {target}.",            target_t="{name} growls at you.",           room_t="{name} growls at {target}." },

    { verb="snarl",
      self="You snarl.",                          room="{name} snarls.",
      self_t="You snarl at {target}.",            target_t="{name} snarls at you.",           room_t="{name} snarls at {target}." },

    { verb="hiss",
      self="You hiss.",                           room="{name} hisses.",
      self_t="You hiss at {target}.",             target_t="{name} hisses at you.",           room_t="{name} hisses at {target}." },

    { verb="snort",
      self="You snort derisively.",               room="{name} snorts derisively.",
      self_t="You snort at {target}.",            target_t="{name} snorts at you.",           room_t="{name} snorts at {target}." },

    { verb="spit",
      self="You spit on the ground.",             room="{name} spits on the ground.",
      self_t="You spit at {target}'s feet.",      target_t="{name} spits at your feet!",      room_t="{name} spits at {target}'s feet." },

    { verb="flex",
      self="You flex impressively.",              room="{name} flexes impressively.",
      self_t="You flex at {target}.",             target_t="{name} flexes at you.",           room_t="{name} flexes at {target}." },

    { verb="posture",
      self="You strike an imposing posture.",     room="{name} strikes an imposing posture.",
      self_t="You posture menacingly at {target}.", target_t="{name} postures menacingly at you.", room_t="{name} postures menacingly at {target}." },

    { verb="intimidate",
      self="You attempt to look intimidating.",   room="{name} attempts to look intimidating.",
      self_t="You try to intimidate {target}.",   target_t="{name} tries to intimidate you.", room_t="{name} tries to intimidate {target}." },

    { verb="threaten",
      self="You mutter threats under your breath.", room="{name} mutters threats.",
      self_t="You threaten {target}.",            target_t="{name} threatens you!",           room_t="{name} threatens {target}." },

    -- ── PERFORMANCE & CELEBRATION ───────────────────────────────────────────
    { verb="cheer",
      self="You cheer!",                          room="{name} cheers!",
      self_t="You cheer for {target}!",           target_t="{name} cheers for you!",          room_t="{name} cheers for {target}!" },

    { verb="dance",
      self="You dance around!",                   room="{name} dances around!",
      self_t="You dance with {target}!",          target_t="{name} dances with you!",         room_t="{name} dances with {target}!" },

    { verb="spin",
      self="You spin around gracefully.",         room="{name} spins around gracefully.",
      self_t="You spin around {target}.",         target_t="{name} spins around you.",        room_t="{name} spins around {target}." },

    { verb="twirl",
      self="You twirl around!",                   room="{name} twirls around!",
      self_t="You twirl around {target}!",        target_t="{name} twirls around you!",       room_t="{name} twirls around {target}!" },

    { verb="jump",
      self="You jump up and down excitedly!",     room="{name} jumps up and down excitedly!",
      self_t="You jump up and down in front of {target}!", target_t="{name} jumps up and down in front of you!", room_t="{name} jumps up and down in front of {target}!" },

    { verb="skip",
      self="You skip around merrily.",            room="{name} skips around merrily.",
      self_t="You skip around {target}.",         target_t="{name} skips around you.",        room_t="{name} skips around {target}." },

    { verb="clap",
      self="You clap your hands.",                room="{name} claps.",
      self_t="You clap for {target}.",            target_t="{name} claps for you.",           room_t="{name} claps for {target}." },

    { verb="applaud",
      self="You applaud!",                        room="{name} applauds!",
      self_t="You applaud {target}!",             target_t="{name} applauds you!",            room_t="{name} applauds {target}!" },

    { verb="strut",
      self="You strut about proudly.",            room="{name} struts about proudly.",
      self_t="You strut in front of {target}.",   target_t="{name} struts in front of you.",  room_t="{name} struts in front of {target}." },

    { verb="swagger",
      self="You swagger about confidently.",      room="{name} swaggers about.",
      self_t="You swagger past {target}.",        target_t="{name} swaggers past you.",       room_t="{name} swaggers past {target}." },

    { verb="prance",
      self="You prance around!",                  room="{name} prances around!",
      self_t="You prance around {target}!",       target_t="{name} prances around you!",     room_t="{name} prances around {target}!" },

    { verb="cavort",
      self="You cavort about gleefully.",         room="{name} cavorts about gleefully.",
      self_t="You cavort around {target}.",       target_t="{name} cavorts around you.",      room_t="{name} cavorts around {target}." },

    -- ── SOUNDS & VOCALIZATIONS ──────────────────────────────────────────────
    { verb="whistle",
      self="You whistle a jaunty tune.",          room="{name} whistles a jaunty tune.",
      self_t="You whistle at {target}.",          target_t="{name} whistles at you.",         room_t="{name} whistles at {target}." },

    { verb="hum",
      self="You hum softly.",                     room="{name} hums softly.",
      self_t="You hum at {target}.",              target_t="{name} hums softly at you.",      room_t="{name} hums softly at {target}." },

    { verb="grumble",
      self="You grumble under your breath.",      room="{name} grumbles under their breath.",
      self_t="You grumble at {target}.",          target_t="{name} grumbles at you.",         room_t="{name} grumbles at {target}." },

    { verb="mutter",
      self="You mutter under your breath.",       room="{name} mutters under their breath.",
      self_t="You mutter something at {target}.", target_t="{name} mutters something at you.", room_t="{name} mutters something at {target}." },

    { verb="mumble",
      self="You mumble incoherently.",            room="{name} mumbles incoherently.",
      self_t="You mumble at {target}.",           target_t="{name} mumbles at you.",          room_t="{name} mumbles at {target}." },

    { verb="cough",
      self="You cough.",                          room="{name} coughs.",
      self_t="You cough at {target}.",            target_t="{name} coughs at you.",           room_t="{name} coughs at {target}." },

    { verb="sneeze",
      self="You sneeze loudly.",                  room="{name} sneezes loudly.",
      self_t="You sneeze on {target}!",           target_t="{name} sneezes on you!",          room_t="{name} sneezes on {target}!" },

    { verb="hiccup",
      self="You hiccup involuntarily.",           room="{name} hiccups involuntarily.",
      self_t="You hiccup at {target}.",           target_t="{name} hiccups at you.",          room_t="{name} hiccups at {target}." },

    { verb="burp",
      self="You burp loudly.  Charming.",         room="{name} burps loudly.",
      self_t="You burp at {target}.",             target_t="{name} burps at you!",            room_t="{name} burps at {target}." },

    { verb="snore",
      self="Zzzzzzz...",                          room="{name} snores loudly.",
      self_t="You snore in {target}'s direction.", target_t="{name} snores in your direction.", room_t="{name} snores in {target}'s direction." },

    { verb="grunt",
      self="You grunt.",                          room="{name} grunts.",
      self_t="You grunt at {target}.",            target_t="{name} grunts at you.",           room_t="{name} grunts at {target}." },

    -- ── GESTURES & SIGNALS ──────────────────────────────────────────────────
    { verb="point",
      self="You point at nothing in particular.", room="{name} points at nothing in particular.",
      self_t="You point at {target}.",            target_t="{name} points at you.",           room_t="{name} points at {target}." },

    { verb="snap",
      self="You snap your fingers.",              room="{name} snaps their fingers.",
      self_t="You snap your fingers at {target}.", target_t="{name} snaps their fingers at you.", room_t="{name} snaps their fingers at {target}." },

    { verb="clench",
      self="You clench your fist.",               room="{name} clenches their fist.",
      self_t="You clench your fist at {target}.", target_t="{name} clenches their fist at you.", room_t="{name} clenches their fist at {target}." },

    { verb="shoo",
      self="You shoo at the air.",                room="{name} shoos at the air.",
      self_t="You shoo {target} away.",           target_t="{name} shoos you away.",          room_t="{name} shoos {target} away." },

    { verb="dismiss",
      self="You wave dismissively at the air.",   room="{name} waves dismissively.",
      self_t="You dismiss {target} with a wave.", target_t="{name} dismisses you with a wave.", room_t="{name} dismisses {target} with a wave." },

    { verb="gesture",
      self="You gesture vaguely.",                room="{name} gestures vaguely.",
      self_t="You gesture toward {target}.",      target_t="{name} gestures toward you.",     room_t="{name} gestures toward {target}." },

    { verb="kneel",
      self="You drop to one knee.",               room="{name} drops to one knee.",
      self_t="You kneel before {target}.",        target_t="{name} kneels before you.",       room_t="{name} kneels before {target}." },

    { verb="prostrate",
      self="You prostrate yourself upon the ground.", room="{name} prostrates themselves upon the ground.",
      self_t="You prostrate yourself before {target}.", target_t="{name} prostrates themselves before you.", room_t="{name} prostrates themselves before {target}." },

    { verb="respect",
      self="You show your respect.",              room="{name} shows their respect.",
      self_t="You show your respect to {target}.", target_t="{name} shows you their respect.", room_t="{name} shows their respect to {target}." },

    { verb="honor",
      self="You place a fist over your heart.",   room="{name} places a fist over their heart.",
      self_t="You place a fist over your heart toward {target}.", target_t="{name} places a fist over their heart toward you.", room_t="{name} places a fist over their heart toward {target}." },

    -- ── SPECIFIC FLAVOR EMOTES ──────────────────────────────────────────────
    { verb="eyeroll",
      self="You roll your eyes.",                 room="{name} rolls their eyes.",
      self_t="You roll your eyes at {target}.",   target_t="{name} rolls their eyes at you.", room_t="{name} rolls their eyes at {target}." },

    { verb="facepalm",
      self="You facepalm.",                       room="{name} facepalms.",
      self_t="You facepalm at {target}.",         target_t="{name} facepalms at you.",        room_t="{name} facepalms at {target}." },

    { verb="headshake",
      self="You shake your head slowly.",         room="{name} shakes their head slowly.",
      self_t="You shake your head at {target}.",  target_t="{name} shakes their head at you.", room_t="{name} shakes their head at {target}." },

    { verb="beg",
      self="You beg pathetically.",               room="{name} begs pathetically.",
      self_t="You beg {target} desperately.",     target_t="{name} begs you desperately.",    room_t="{name} begs {target} desperately." },

    { verb="plead",
      self="You plead with the universe.",        room="{name} pleads with the universe.",
      self_t="You plead with {target}.",          target_t="{name} pleads with you.",         room_t="{name} pleads with {target}." },

    { verb="panic",
      self="You panic!",                          room="{name} panics!",
      self_t="You panic at {target}!",            target_t="{name} panics at you!",           room_t="{name} panics at {target}!" },

    { verb="sulk",
      self="You sulk.",                           room="{name} sulks.",
      self_t="You sulk at {target}.",             target_t="{name} sulks at you.",            room_t="{name} sulks at {target}." },

    { verb="brood",
      self="You brood in brooding silence.",      room="{name} broods silently.",
      self_t="You brood over {target}.",          target_t="{name} broods over you.",         room_t="{name} broods over {target}." },

    { verb="stare",
      self="You stare blankly ahead.",            room="{name} stares blankly ahead.",
      self_t="You stare at {target}.",            target_t="{name} stares at you.",           room_t="{name} stares at {target}." },

    { verb="gawk",
      self="You gawk.",                           room="{name} gawks.",
      self_t="You gawk at {target}.",             target_t="{name} gawks at you.",            room_t="{name} gawks at {target}." },

    { verb="ogle",
      self="You ogle the scenery.",               room="{name} ogles the scenery.",
      self_t="You ogle {target}.",                target_t="{name} ogles you.",               room_t="{name} ogles {target}." },

    { verb="drool",
      self="You drool slightly.",                 room="{name} drools slightly.",
      self_t="You drool over {target}.",          target_t="{name} drools over you.",         room_t="{name} drools over {target}." },

    { verb="scoff",
      self="You scoff.",                          room="{name} scoffs.",
      self_t="You scoff at {target}.",            target_t="{name} scoffs at you.",           room_t="{name} scoffs at {target}." },

    { verb="mock",
      self="You mock the air.",                   room="{name} mocks.",
      self_t="You mock {target}.",                target_t="{name} mocks you.",               room_t="{name} mocks {target}." },

    { verb="taunt",
      self="You taunt no one in particular.",     room="{name} taunts.",
      self_t="You taunt {target}.",               target_t="{name} taunts you.",              room_t="{name} taunts {target}." },

    { verb="tease",
      self="You feel like teasing someone.",      room="{name} looks mischievous.",
      self_t="You tease {target}.",               target_t="{name} teases you.",              room_t="{name} teases {target}." },

    { verb="stew",
      self="You stew in your own frustration.",   room="{name} stews in frustration.",
      self_t="You stew at {target}.",             target_t="{name} stews at you.",            room_t="{name} stews at {target}." },

    { verb="startle",
      self="You startle suddenly!",               room="{name} startles suddenly!",
      self_t="You startle {target}!",             target_t="{name} startles you!",            room_t="{name} startles {target}!" },

    { verb="study",
      self="You study your surroundings.",        room="{name} studies their surroundings.",
      self_t="You study {target} intently.",      target_t="{name} studies you intently.",    room_t="{name} studies {target} intently." },

    { verb="examine",
      self="You examine yourself critically.",    room="{name} examines themselves critically.",
      self_t="You examine {target} closely.",     target_t="{name} examines you closely.",    room_t="{name} examines {target} closely." },

    { verb="peer",
      self="You peer into the distance.",         room="{name} peers into the distance.",
      self_t="You peer at {target} intently.",    target_t="{name} peers at you intently.",   room_t="{name} peers at {target} intently." },

    { verb="squirm",
      self="You squirm uncomfortably.",           room="{name} squirms uncomfortably.",
      self_t="You squirm in front of {target}.",  target_t="{name} squirms in front of you.", room_t="{name} squirms in front of {target}." },

    { verb="cower",
      self="You cower.",                          room="{name} cowers.",
      self_t="You cower before {target}.",        target_t="{name} cowers before you.",       room_t="{name} cowers before {target}." },

    { verb="nuzzle",
      self="You nuzzle the air.",                 room="{name} nuzzles the air.",
      self_t="You nuzzle {target}.",              target_t="{name} nuzzles you.",             room_t="{name} nuzzles {target}." },

    { verb="tickle",
      self="You wiggle your fingers menacingly.", room="{name} wiggles their fingers menacingly.",
      self_t="You tickle {target}!",              target_t="{name} tickles you!",             room_t="{name} tickles {target}!" },

    { verb="deepbow",
      self="You bow deeply.",                     room="{name} bows deeply.",
      self_t="You bow deeply to {target}.",       target_t="{name} bows deeply to you.",      room_t="{name} bows deeply to {target}." },


    { verb="wiggle",
      self="You wiggle.",                         room="{name} wiggles.",
      self_t="You wiggle at {target}.",           target_t="{name} wiggles at you.",          room_t="{name} wiggles at {target}." },

    { verb="bounce",
      self="You bounce on your heels.",           room="{name} bounces on their heels.",
      self_t="You bounce excitedly at {target}.", target_t="{name} bounces excitedly at you.", room_t="{name} bounces excitedly at {target}." },

    { verb="flail",
      self="You flail your arms wildly.",         room="{name} flails their arms wildly.",
      self_t="You flail at {target}!",            target_t="{name} flails at you!",           room_t="{name} flails at {target}!" },


    { verb="quake",
      self="You quake with fear.",                room="{name} quakes with fear.",
      self_t="You quake before {target}.",        target_t="{name} quakes before you.",       room_t="{name} quakes before {target}." },

    { verb="glower",
      self="You glower darkly.",                  room="{name} glowers darkly.",
      self_t="You glower at {target}.",           target_t="{name} glowers at you.",          room_t="{name} glowers at {target}." },

    { verb="laze",
      self="You laze about lazily.",              room="{name} lazes about.",
      self_t="You laze beside {target}.",         target_t="{name} lazes beside you.",        room_t="{name} lazes beside {target}." },

    { verb="lounge",
      self="You lounge about casually.",          room="{name} lounges about.",
      self_t="You lounge near {target}.",         target_t="{name} lounges near you.",        room_t="{name} lounges near {target}." },

    { verb="harrumph",
      self="You harrumph indignantly.",           room="{name} harrumphs indignantly.",
      self_t="You harrumph at {target}.",         target_t="{name} harrumphs at you.",        room_t="{name} harrumphs at {target}." },

    { verb="tsk",
      self="You tsk disapprovingly.",             room="{name} tsks disapprovingly.",
      self_t="You tsk at {target}.",              target_t="{name} tsks at you.",             room_t="{name} tsks at {target}." },

    { verb="chide",
      self="You chide yourself.",                 room="{name} chides themselves.",
      self_t="You chide {target}.",               target_t="{name} chides you.",              room_t="{name} chides {target}." },

    { verb="console",
      self="You look around for someone to console.", room="{name} looks around for someone to console.",
      self_t="You try to console {target}.",      target_t="{name} tries to console you.",    room_t="{name} tries to console {target}." },

    { verb="comfort",
      self="You try to comfort yourself.",        room="{name} tries to comfort themselves.",
      self_t="You try to comfort {target}.",      target_t="{name} tries to comfort you.",    room_t="{name} tries to comfort {target}." },

    { verb="confuse",
      self="You look utterly confused.",          room="{name} looks utterly confused.",
      self_t="You look at {target} in confusion.", target_t="{name} looks at you in confusion.", room_t="{name} looks at {target} in confusion." },

    { verb="baffled",
      self="You look thoroughly baffled.",        room="{name} looks thoroughly baffled.",
      self_t="You look at {target} with complete bafflement.", target_t="{name} looks at you with complete bafflement.", room_t="{name} looks at {target} with complete bafflement." },

    { verb="impressed",
      self="You look suitably impressed.",        room="{name} looks suitably impressed.",
      self_t="You look impressed by {target}.",   target_t="{name} looks impressed by you.",  room_t="{name} looks impressed by {target}." },

    { verb="disgusted",
      self="You look disgusted.",                 room="{name} looks disgusted.",
      self_t="You look disgusted by {target}.",   target_t="{name} looks disgusted by you.",  room_t="{name} looks disgusted by {target}." },

    { verb="horrified",
      self="You look horrified!",                 room="{name} looks horrified!",
      self_t="You look horrified by {target}!",   target_t="{name} looks horrified by you!",  room_t="{name} looks horrified by {target}!" },

    { verb="amused",
      self="You look amused.",                    room="{name} looks amused.",
      self_t="You look amused by {target}.",      target_t="{name} looks amused by you.",     room_t="{name} looks amused by {target}." },

    { verb="envious",
      self="You look green with envy.",           room="{name} looks green with envy.",
      self_t="You look envious of {target}.",     target_t="{name} looks envious of you.",    room_t="{name} looks envious of {target}." },

    { verb="triumphant",
      self="You look triumphant!",                room="{name} looks triumphant!",
      self_t="You look triumphant over {target}!", target_t="{name} looks triumphant over you!", room_t="{name} looks triumphant over {target}!" },

    { verb="determined",
      self="You set your jaw with determination.", room="{name} sets their jaw with determination.",
      self_t="You look determined at {target}.",  target_t="{name} looks determined at you.", room_t="{name} looks determined at {target}." },

    { verb="resigned",
      self="You sigh with resignation.",          room="{name} sighs with resignation.",
      self_t="You look resigned toward {target}.", target_t="{name} looks resigned toward you.", room_t="{name} looks resigned toward {target}." },

    { verb="dubious",
      self="You look extremely dubious.",         room="{name} looks extremely dubious.",
      self_t="You look dubious at {target}.",     target_t="{name} looks dubious at you.",    room_t="{name} looks dubious at {target}." },

    { verb="suspicious",
      self="You look suspicious.",                room="{name} looks suspicious.",
      self_t="You eye {target} with suspicion.",  target_t="{name} eyes you with suspicion.", room_t="{name} eyes {target} with suspicion." },

    { verb="curious",
      self="You look curious.",                   room="{name} looks curious.",
      self_t="You eye {target} curiously.",       target_t="{name} eyes you curiously.",      room_t="{name} eyes {target} curiously." },

    -- ── EATING & DRINKING FLAVOUR ───────────────────────────────────────────
    { verb="lick",
      self="You lick your lips.",                 room="{name} licks their lips.",
      self_t="You lick {target}.",                target_t="{name} licks you.  Weird.", room_t="{name} licks {target}." },

    { verb="savor",
      self="You savor the moment.",               room="{name} savors the moment.",
      self_t="You savor the sight of {target}.",  target_t="{name} savors the sight of you.", room_t="{name} savors the sight of {target}." },

    -- ── MISC / FUN ──────────────────────────────────────────────────────────



    { verb="air",
      self="You stare into the air dramatically.", room="{name} stares into the air dramatically.",
      self_t="You dramatically indicate {target}.", target_t="{name} dramatically indicates you.", room_t="{name} dramatically indicates {target}." },


    { verb="ugh",
      self="You make a sound of pure disgust.",   room="{name} makes a sound of pure disgust.",
      self_t="You make a sound of pure disgust at {target}.", target_t="{name} makes a sound of pure disgust at you.", room_t="{name} makes a sound of pure disgust at {target}." },

    { verb="hmm",
      self="You say, \"Hmmm...\"",               room="{name} hmmms thoughtfully.",
      self_t="You hmmm at {target}.",             target_t="{name} hmmms at you.",            room_t="{name} hmmms at {target}." },

    { verb="woah",
      self="You say, \"Woah!\"",                  room="{name} says, \"Woah!\"",
      self_t="You say \"Woah!\" at {target}.",    target_t="{name} says \"Woah!\" at you.",   room_t="{name} says \"Woah!\" at {target}." },

    { verb="ew",
      self="You recoil and say, \"Ew!\"",         room="{name} recoils and says, \"Ew!\"",
      self_t="You say \"Ew!\" at {target}.",      target_t="{name} says \"Ew!\" at you.",     room_t="{name} says \"Ew!\" at {target}." },

    { verb="eureka",
      self="You shout, \"Eureka!\"",              room="{name} shouts, \"Eureka!\"",
      self_t="You point at {target} and shout, \"Eureka!\"", target_t="{name} points at you and shouts, \"Eureka!\"", room_t="{name} points at {target} and shouts, \"Eureka!\"" },

    { verb="congrats",
      self="You congratulate yourself.",          room="{name} congratulates themselves.",
      self_t="You congratulate {target}!",        target_t="{name} congratulates you!",       room_t="{name} congratulates {target}!" },

    { verb="thanks",
      self="You give thanks to the gods.",        room="{name} gives thanks to the gods.",
      self_t="You thank {target}.",               target_t="{name} thanks you.",              room_t="{name} thanks {target}." },

    { verb="sorry",
      self="You look apologetic.",                room="{name} looks apologetic.",
      self_t="You apologize to {target}.",        target_t="{name} apologizes to you.",       room_t="{name} apologizes to {target}." },

}

return Emotes
