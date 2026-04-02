"""
Tutorial System - The Sprite Quest
A magical sprite named Ridijy guides new characters through 5 scenarios
teaching core game mechanics. Triggered after character creation.

Scenarios:
  1. The Shrine      - Communication (SAY, ASK, LOOK)
  2. The Lost Sword  - Inventory (GET, GIVE, WEAR)
  3. The Smuggler    - Stealth (HIDE, SNEAK)
  4. The Wounded Child- Healing (FORAGE, TEND, GIVE)
  5. The Beast       - Combat (ATTACK, STANCE, INCANT)
"""

import asyncio
import logging
import time
import re

from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)

STAGE_WAITING_ACCEPT = 255

ROOM_ARRIVAL = 59000
ROOM_PATH = 59001
ROOM_CROSSROADS = 59002
ROOM_COMMUNICATION = 59010
ROOM_INVENTORY_CAMP = 59020
ROOM_INVENTORY_CLEARING = 59021
ROOM_STEALTH_ALLEY = 59030
ROOM_STEALTH_RENDEZVOUS = 59031
ROOM_HEALING_VILLAGE = 59040
ROOM_HEALING_COTTAGE = 59041
ROOM_HEALING_MEADOW = 59042
ROOM_COMBAT_ENTRANCE = 59050
ROOM_COMBAT_CAVE = 59051
ROOM_COMBAT_DEEP = 59052
ROOM_COMPLETION = 59099

TUTORIAL_ROOM_MIN = 59000
TUTORIAL_ROOM_MAX = 59099


def is_tutorial_room_id(room_id: int) -> bool:
    try:
        room_id = int(room_id)
    except Exception:
        return False
    return TUTORIAL_ROOM_MIN <= room_id <= TUTORIAL_ROOM_MAX


def _tutorial_sword_item():
    return {
        "item_id": 0,
        "id": 0,
        "inv_id": None,
        "name": "a weathered iron sword",
        "short_name": "weathered iron sword",
        "noun": "sword",
        "article": "a",
        "item_type": "weapon",
        "slot": "right_hand",
        "container_id": None,
        "tutorial_item": True,
    }


def _tutorial_herb_item():
    return {
        "item_id": 0,
        "id": 0,
        "inv_id": None,
        "name": "some fresh healing herbs",
        "short_name": "fresh healing herbs",
        "noun": "herbs",
        "article": "some",
        "item_type": "herb",
        "slot": "right_hand",
        "container_id": None,
        "tutorial_item": True,
    }


def _held_or_stowed_tutorial_sword(session):
    for item in (getattr(session, "right_hand", None), getattr(session, "left_hand", None)):
        if item and str(item.get("noun", "")).lower() == "sword":
            return item
    for item in getattr(session, "inventory", []) or []:
        if str(item.get("noun", "")).lower() == "sword":
            return item
    return None


def _remove_tutorial_sword(session):
    for attr in ("right_hand", "left_hand"):
        item = getattr(session, attr, None)
        if item and str(item.get("noun", "")).lower() == "sword":
            setattr(session, attr, None)
            return True
    inv = getattr(session, "inventory", None) or []
    for item in list(inv):
        if str(item.get("noun", "")).lower() == "sword":
            inv.remove(item)
            return True
    return False


def _sprite_line(line: str) -> str:
    """
    Colorize one line of sprite dialogue.
    Quoted speech ("...") -> BRIGHT_GREEN.
    Action/narrative text -> BRIGHT_YELLOW.
    Empty lines pass through unchanged.
    """
    if not line.strip():
        return line
    parts = re.split(r'(".*?")', line)
    if len(parts) == 1:
        return colorize(line, TextPresets.NPC_EMOTE)
    result = []
    for part in parts:
        if not part:
            continue
        if part.startswith('"') and part.endswith('"'):
            result.append(colorize(part, TextPresets.NPC_SPEECH))
        else:
            result.append(colorize(part, TextPresets.NPC_EMOTE))
    return "".join(result)


# Sprite dialogue keyed by (room_id, tutorial_stage)
# Stage is auto-advanced when player enters certain rooms or takes certain actions.

SPRITE_DIALOGUE = {
    # ===== ARRIVAL =====
    (ROOM_ARRIVAL, 0): [
        "",
        "A tiny, shimmering sprite materializes in front of you with a burst of",
        "silver sparks.  She's barely six inches tall, with gossamer wings that",
        "beat so fast they're almost invisible, and an impish grin on her face.",
        "",
        'The sprite curtsies in midair.  "Well hello there!  I\'m Ridijy, and I\'ve',
        'been sent to help you find your way in this world.  Lucky you!"',
        "",
        'She flutters around your head excitedly.  "First things first -- try',
        "walking around!  You can move by typing directions like NORTH, SOUTH,",
        "EAST, WEST, or abbreviations like N, S, E, W.  You can also LOOK at",
        'any room to see what\'s around you."',
        "",
        'Ridijy points north.  "Shall we?  Go NORTH to start our adventure!"',
    ],

    (ROOM_PATH, 1): [
        "",
        'Ridijy zips ahead of you.  "See?  Easy!  You\'re a natural!"',
        "",
        '"Every room has a description, exits, and sometimes other people or',
        'things to interact with.  Try typing LOOK to see this room again."',
        "",
        '"When you\'re ready, keep going NORTH.  I\'ll be right behind you!"',
    ],

    (ROOM_CROSSROADS, 2): [
        "",
        "Ridijy lands on your shoulder, her tiny feet barely perceptible.",
        '"Ooh, a crossroads!  Each path leads to a different little adventure',
        'that will teach you something useful."',
        "",
        "  NORTHEAST  - Learn to talk to people  (Communication)",
        "  NORTHWEST  - Learn about items and gear (Inventory)",
        "  EAST       - Learn the art of stealth   (Sneaking)",
        "  WEST       - Learn to heal wounds        (Healing)",
        "  NORTH      - Learn to fight!              (Combat)",
        "",
        '"You can do them in any order, or skip straight to the ones that',
        "interest you.  I'd suggest starting with NORTHEAST -- talking to",
        'people is kind of important!"',
        "",
        '"Oh, and when you\'ve had enough tutorials, just say SKIP TUTORIAL',
        'and I\'ll whisk you straight to your home city."',
    ],

    # ===== SCENARIO 1: COMMUNICATION =====
    (ROOM_COMMUNICATION, 10): [
        "",
        'Ridijy whispers conspiratorially, "See that hooded figure?  They look',
        "like they could use some company.  Or maybe they're up to no good.",
        'Only one way to find out!"',
        "",
        '"Try using SAY to speak aloud.  For example:',
        "  SAY Hello there",
        "",
        "You can also ASK someone about something:",
        "  ASK FIGURE ABOUT shrine",
        "",
        'Go ahead, give it a try!"',
    ],

    (ROOM_COMMUNICATION, 11): [
        "",
        'The hooded figure looks up at you with tired eyes.  "A traveler...',
        "This shrine once blessed all who visited.  Now it lies neglected.",
        'Perhaps... you could search the base for an old offering?"',
        "",
        'Ridijy nudges you.  "Try SEARCH to look for hidden things in a room!"',
    ],

    (ROOM_COMMUNICATION, 12): [
        "",
        "You find a small silver coin buried beneath the moss at the shrine's base!",
        "",
        'Ridijy claps her tiny hands.  "Nice work!  You found something!',
        "SEARCH is super useful for finding hidden treasures, exits, and clues.",
        'Remember it!"',
        "",
        '"When you\'re ready, head back SOUTHWEST to the crossroads for more',
        'adventures!"',
    ],

    # ===== SCENARIO 2: INVENTORY =====
    (ROOM_INVENTORY_CAMP, 20): [
        "",
        'Ridijy flutters over to the sad warrior.  "Oh dear, he looks miserable.',
        'Ask him what\'s wrong!"',
        "",
        "The young warrior sighs heavily.  \"I've lost my sword somewhere in the",
        "clearing to the north.  Without it, I can't complete my training.\"",
        "",
        'Ridijy whispers to you, "This is a good chance to learn about items!',
        "Head NORTH to the clearing and look for his sword.  When you find it,",
        "use GET to pick it up.  Like this:",
        "  GET SWORD",
        "",
        "Then bring it back and GIVE it to him:",
        '  GIVE SWORD TO WARRIOR"',
    ],

    (ROOM_INVENTORY_CLEARING, 21): [
        "",
        'Ridijy spots the glinting metal.  "There it is!  In the grass!"',
        "",
        '"Use GET SWORD to pick it up.  Items you pick up go into your',
        "inventory.  You can check what you're carrying with INVENTORY or INV.",
        "",
        "Other useful item commands:",
        "  WEAR    - Put on armor or clothing",
        "  REMOVE  - Take off something you're wearing",
        '  DROP    - Drop something on the ground"',
    ],

    (ROOM_INVENTORY_CAMP, 22): [
        "",
        'Ridijy bounces excitedly.  "You got the sword!  Now GIVE SWORD TO',
        'WARRIOR to return it!"',
    ],

    (ROOM_INVENTORY_CAMP, 23): [
        "",
        "The warrior's face lights up.  \"My sword!  Thank you, friend!\"",
        "He presses a few silver coins into your hand as thanks.",
        "",
        'Ridijy beams.  "See?  Being helpful pays off -- literally!',
        "Head back SOUTHEAST to the crossroads when you're ready!\"",
    ],

    # ===== SCENARIO 3: STEALTH =====
    (ROOM_STEALTH_ALLEY, 30): [
        "",
        'Ridijy dims her glow and whispers, "Ooh, intrigue!  See that guard?',
        "He's watching for a smuggler who's supposed to make a drop in the",
        'alley to the east."',
        "",
        '"This is a great chance to learn about STEALTH!  As a rogue-type,',
        "these will be your bread and butter:",
        "  HIDE      - Attempt to hide in the shadows",
        "  SNEAK     - Move while hidden (use before a direction)",
        "  UNHIDE    - Come out of hiding",
        "",
        "Try HIDE first, then SNEAK EAST to slip past the guard unnoticed!\"",
    ],

    (ROOM_STEALTH_RENDEZVOUS, 31): [
        "",
        'Ridijy gives you a tiny thumbs-up.  "Nicely done!  The smuggler',
        "doesn't even notice you're here.  In the real game, HIDE and SNEAK",
        "are essential for rogues.  You can also STEAL from creatures -- but",
        'let\'s save that for later."',
        "",
        '"Sneak back WEST when you\'re done snooping!"',
    ],

    # ===== SCENARIO 4: HEALING =====
    (ROOM_HEALING_VILLAGE, 40): [
        "",
        'Ridijy\'s expression turns serious.  "Oh no... that girl is crying.',
        'Something is wrong.  Try SAYing something to her."',
        "",
        "The girl sniffles.  \"My sister... she's hurt.  She fell and cut her",
        "arm badly.  She's inside.  Please, can you help?\"",
        "",
        '"You can go inside the COTTAGE to see the wounded girl.  Or head',
        "NORTH to the meadow to FORAGE for healing herbs.  Here's how:",
        "  FORAGE    - Search the area for useful herbs and plants",
        "  TEND      - Treat someone's wounds (basic first aid)",
        "",
        'Get some herbs first, then tend to the girl inside!"',
    ],

    (ROOM_HEALING_MEADOW, 41): [
        "",
        'Ridijy surveys the meadow.  "This place is full of medicinal plants!',
        "Try FORAGE to gather some healing herbs.  You might find moss or",
        'white herb -- both are great for treating wounds."',
    ],

    (ROOM_HEALING_MEADOW, 42): [
        "",
        "You carefully gather some fresh herbs!",
        "",
        'Ridijy nods approvingly.  "Good!  Now head SOUTH and go into the',
        'COTTAGE to tend to the wounded girl.  Use TEND to help her."',
    ],

    (ROOM_HEALING_COTTAGE, 43): [
        "",
        'Ridijy hovers near the cot.  "Poor thing.  Try TEND GIRL to help',
        'clean and bandage her wound.  The herbs you gathered will help."',
    ],

    (ROOM_HEALING_COTTAGE, 44): [
        "",
        "You carefully tend to the girl's wound, applying the herbs as a",
        "poultice and wrapping it in fresh bandages.  Her breathing steadies",
        "and some color returns to her cheeks.",
        "",
        'The girl whispers, "Thank you..."',
        "",
        'Ridijy wipes a tiny tear from her eye.  "You did good.  Healing',
        "is one of the most important things in Elanthia.  Empaths can heal",
        'magically, but everyone can use TEND and herbs for basic first aid."',
        "",
        '"Head OUT and back EAST to the crossroads!"',
    ],

    # ===== SCENARIO 5: COMBAT =====
    (ROOM_COMBAT_ENTRANCE, 50): [
        "",
        'Ridijy\'s wings beat nervously.  "Okay... this is the combat lesson.',
        "There's something nasty living in that cave.  Before we go in, let me",
        'teach you the basics."',
        "",
        "  STANCE OFFENSIVE  - Maximum attack power, less defense",
        "  STANCE DEFENSIVE  - Maximum defense, less attack",
        "  ATTACK             - Attack a creature",
        "  INCANT <spell#>   - Cast a spell (for magic users)",
        "",
        '"Start by typing STANCE OFFENSIVE to get ready for a fight.',
        "Then GO CAVE when you're prepared!\"",
    ],

    (ROOM_COMBAT_CAVE, 51): [
        "",
        "Something growls in the darkness ahead...",
        "",
        'Ridijy clings to your hair.  "A giant rat!  Quick -- ATTACK it!',
        'Type ATTACK to swing at it!"',
    ],

    (ROOM_COMBAT_DEEP, 52): [
        "",
        "A larger, more menacing creature lurks in the shadows here.",
        "",
        'Ridijy squeaks, "A cave troll!  This one is tougher.  Remember your',
        "stance -- STANCE OFFENSIVE for more damage, STANCE DEFENSIVE if you're",
        'getting hurt.  ATTACK when ready!"',
    ],

    (ROOM_COMBAT_DEEP, 53): [
        "",
        "The creature falls!  Experience flows into you as the thrill of",
        "victory courses through your veins.",
        "",
        'Ridijy cheers wildly, doing loop-de-loops in the air.  "You did it!',
        "You're a natural adventurer!  Don't forget to LOOT fallen creatures",
        'to pick up any treasure they drop."',
        "",
        '"Head back OUT and SOUTH to the crossroads.  I think you\'re ready',
        'for the real world!"',
    ],

    # ===== COMPLETION =====
    (ROOM_COMPLETION, 90): [
        "",
        "Ridijy lands on the mantelpiece and stretches her wings.",
        '"Well, here we are -- Silverwood Manor.  This is where new',
        'adventurers rest before heading out into the world."',
        "",
        "She produces a tiny round mirror from somewhere and offers it to you.",
        '"A little souvenir of our time together!  You\'ve learned movement,',
        "communication, inventory, stealth, healing, and combat.  That's more",
        'than most!"',
        "",
        '"Step through the PORTAL when you\'re ready and it will take you',
        'to your home city.  Good luck out there, adventurer!"',
        "",
        'Ridijy waves goodbye, her glow fading.  "Don\'t forget about me!"',
        "",
        "  Type: GO PORTAL to enter the world.",
    ],
}


class TutorialManager:
    """Manages the tutorial state machine for new characters."""

    def __init__(self, server):
        self.server = server

    async def start_tutorial(self, session):
        """Begin the tutorial for a new character."""
        session.state = "playing"
        session.tutorial_stage = STAGE_WAITING_ACCEPT
        session.tutorial_complete = False
        session.tutorial_pester_count = 0

        # Save initial tutorial state to DB
        if self.server.db and session.character_id:
            self.server.db.save_quest_progress(
                session.character_id, STAGE_WAITING_ACCEPT, False
            )
            self.server.db.save_character_room(session.character_id, ROOM_ARRIVAL)

        # Place in tutorial arrival room
        room = self.server.world.get_room(ROOM_ARRIVAL)
        if not room:
            # Tutorial zone not loaded, skip to town
            log.warning("Tutorial zone not loaded, skipping tutorial.")
            await self._skip_to_town(session)
            return

        session.current_room = room
        self.server.world.add_player_to_room(session, ROOM_ARRIVAL)

        # Show the room
        await self.server.commands.handle(session, "look")

        # Show sprite teaser and wait for ACCEPT
        await self._play_teaser(session)

    async def _play_teaser(self, session):
        """Short sprite intro shown before ACCEPT."""
        lines = [
            "",
            "A tiny, shimmering sprite materializes in front of you with a burst of",
            "silver sparks.  She's barely six inches tall, with gossamer wings that",
            "beat so fast they're almost invisible, and an impish grin on her face.",
            "",
            'The sprite curtsies in midair.  "Well hello there!  I\'m Ridijy, and I\'ve',
            'been sent to help you find your way in this world.  Lucky you!"',
            "",
            'She flutters hopefully.  "I could really show you the ropes, if you\'ll let me!"',
            "",
        ]
        for line in lines:
            await session.send_line(_sprite_line(line) if line.strip() else line)
        await session.send_line(
            _sprite_line(
                'Ridijy clasps her tiny hands together.  "So -- what do you say?  '
                'Type ACCEPT to follow me, or SKIP TUTORIAL to head straight to town."'
            )
        )
        await session.send_line("")

    async def resume_tutorial(self, session):
        """Resume tutorial for a returning player still in the tutorial zone."""
        if session.tutorial_complete:
            return

        room_id = session.current_room.id if session.current_room else ROOM_ARRIVAL
        stage = session.tutorial_stage

        # Re-display dialogue for current stage
        if stage == STAGE_WAITING_ACCEPT:
            await self._play_teaser(session)
        elif (room_id, stage) in SPRITE_DIALOGUE:
            await self._play_dialogue(session, room_id, stage)

        # Show helpful hint
        await session.send_line("")
        await session.send_line(
            _sprite_line('Ridijy appears beside you briefly.  "Type SKIP TUTORIAL at any time to leave the tutorial."')
        )
        await session.send_line("")

    SPRITE_PESTER = [
        'A tiny sprite darts in front of your face.  "Excuse me!  Type ACCEPT!"',
        'Ridijy tugs on your sleeve.  "Hey!  Just type ACCEPT -- it\'s easy!"',
        'Ridijy flutters impatiently.  "I will follow you EVERYWHERE until you type ACCEPT."',
        'The sprite plants her tiny fists on her hips.  "ACCEPT.  Two syllables.  You can do it!"',
        'Ridijy hovers in front of your nose.  "Not leaving until you type ACCEPT.  Just so you know."',
    ]

    async def on_room_enter(self, session, room_id):
        """Called when a player in tutorial mode enters a new room."""
        if session.tutorial_complete:
            return

        stage = session.tutorial_stage

        # Still waiting for ACCEPT -- pester every 3 moves
        if stage == STAGE_WAITING_ACCEPT:
            session.tutorial_pester_count = getattr(session, "tutorial_pester_count", 0) + 1
            if session.tutorial_pester_count % 3 == 0:
                idx = (session.tutorial_pester_count // 3 - 1) % len(self.SPRITE_PESTER)
                await session.send_line("")
                await session.send_line(_sprite_line(self.SPRITE_PESTER[idx]))
                await session.send_line("")
            return

        # ── Crossroads handling ─────────────────────────────────────────────
        # Must be evaluated before any stage-advance logic so the sprite
        # never goes silent when a player backtracks from any scenario.
        if room_id == ROOM_CROSSROADS:
            if stage >= 53:
                # Both tutorial fights done — teleport to completion room.
                await self._teleport_to_completion(session)
                return
            if stage >= 2:
                # Re-entering crossroads mid-tutorial from any direction.
                # Always replay the directions menu so the sprite is never silent.
                await self._play_dialogue(session, ROOM_CROSSROADS, 2)
                return

        # Auto-advance stage based on room + current stage
        # Exact-match transitions for linear path rooms
        linear_transitions = {
            (ROOM_PATH, 0): 1,
            (ROOM_CROSSROADS, 1): 2,
            (ROOM_INVENTORY_CLEARING, 20): 21,
            (ROOM_STEALTH_RENDEZVOUS, 30): 31,
            (ROOM_HEALING_MEADOW, 40): 41,
            (ROOM_HEALING_COTTAGE, 42): 43,
            (ROOM_HEALING_COTTAGE, 40): 43,
            (ROOM_COMBAT_CAVE, 50): 51,
        }

        # Scenario entry rooms fire whenever stage >= 2 but < scenario base stage.
        # This handles any order of scenario completion.
        scenario_entry = {
            ROOM_COMMUNICATION: 10,
            ROOM_INVENTORY_CAMP: 20,
            ROOM_STEALTH_ALLEY: 30,
            ROOM_HEALING_VILLAGE: 40,
            ROOM_COMBAT_ENTRANCE: 50,
        }

        new_stage = None
        if room_id in scenario_entry:
            target_stage = scenario_entry[room_id]
            if stage >= 2 and stage < target_stage:
                new_stage = target_stage
        if new_stage is None:
            new_stage = linear_transitions.get((room_id, stage))
        if new_stage is not None:
            session.tutorial_stage = new_stage
            # Save to DB immediately
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(
                    session.character_id, new_stage, False
                )

            # Spawn creatures at appropriate stages
            if new_stage == 51 and room_id == ROOM_COMBAT_CAVE:
                # Spawn tutorial rat in cave
                await self._spawn_creature_in_room("tutorial_rat", ROOM_COMBAT_CAVE)
            elif new_stage == 52 and room_id == ROOM_COMBAT_DEEP:
                # Spawn tutorial troll in deep cave
                await self._spawn_creature_in_room("tutorial_troll", ROOM_COMBAT_DEEP)

            await self._play_dialogue(session, room_id, new_stage)
        elif (room_id, stage) in SPRITE_DIALOGUE:
            await self._play_dialogue(session, room_id, stage)

    async def _spawn_creature_in_room(self, template_id, room_id):
        """Spawn a creature in a specific room."""
        if not hasattr(self.server, 'creatures'):
            log.warning("Creatures manager not available")
            return

        try:
            creature = self.server.creatures.spawn_creature(template_id, room_id)
            if creature:
                log.info("Spawned %s in room %d", template_id, room_id)
            else:
                log.warning("Failed to spawn %s in room %d", template_id, room_id)
        except Exception as e:
            log.error("Error spawning %s: %s", template_id, e)

    async def _teleport_to_completion(self, session):
        """Teleport player from crossroads to completion room and advance stage."""
        if session.tutorial_stage < 53:
            return

        completion_room = self.server.world.get_room(ROOM_COMPLETION)
        if not completion_room:
            log.warning("Completion room (%d) not found", ROOM_COMPLETION)
            return

        # Remove from crossroads
        if session.current_room:
            self.server.world.remove_player_from_room(session, session.current_room.id)

        # Add to completion room
        session.current_room = completion_room
        self.server.world.add_player_to_room(session, ROOM_COMPLETION)

        # Advance stage to completion
        session.tutorial_stage = 90
        if self.server.db and session.character_id:
            self.server.db.save_quest_progress(session.character_id, 90, False)
            self.server.db.save_character_room(session.character_id, ROOM_COMPLETION)

        # Show room and dialogue
        from server.core.commands.player.movement import cmd_look
        await cmd_look(session, "look", "", self.server)
        await self._play_dialogue(session, ROOM_COMPLETION, 90)

    async def on_creature_death(self, session, creature):
        """Called when a creature dies in a tutorial room. Advances combat stages."""
        if session.tutorial_complete:
            return

        stage = session.tutorial_stage
        room_id = creature.current_room_id if hasattr(creature, 'current_room_id') else 0

        if stage == 51 and room_id == ROOM_COMBAT_CAVE:
            # Rat killed - advance to deep cave
            session.tutorial_stage = 52
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(session.character_id, 52, False)

            await session.send_line("")
            await session.send_line(_sprite_line('Ridijy cheers.  "Nice work!  But I hear something bigger deeper in the cave... head NORTH if you dare!"'))
            await session.send_line("")

        elif stage == 52 and room_id == ROOM_COMBAT_DEEP:
            # Troll killed - combat complete
            session.tutorial_stage = 53
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(session.character_id, 53, False)

            await self._play_dialogue(session, room_id, 53)

    async def on_command(self, session, command, args):
        """Called when a tutorial player uses a command. Advances scenarios."""
        stage = session.tutorial_stage
        room_id = session.current_room.id if session.current_room else 0

        # Skip tutorial command
        if command == "skip" and args.lower().startswith("tutorial"):
            await self._skip_to_town(session)
            return True

        # ACCEPT -- begin tutorial proper
        if command == "accept" and stage == STAGE_WAITING_ACCEPT:
            session.tutorial_stage = 0
            session.tutorial_pester_count = 0
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(session.character_id, 0, False)
            await session.send_line("")
            await session.send_line(_sprite_line('Ridijy beams.  "Wonderful!  Let\'s get started!"'))
            await session.send_line("")
            await self._play_dialogue(session, room_id, 0)
            return True

        # NOD SPRITE -- context-sensitive repeat hint
        if command == "nod" and "sprite" in args.lower():
            if stage == STAGE_WAITING_ACCEPT:
                # Treat as implicit ACCEPT
                await session.send_line(_sprite_line('Ridijy grins.  "I\'ll take that as a yes!  Let\'s go!"'))
                session.tutorial_stage = 0
                session.tutorial_pester_count = 0
                if self.server.db and session.character_id:
                    self.server.db.save_quest_progress(session.character_id, 0, False)
                await self._play_dialogue(session, room_id, 0)
            elif room_id == ROOM_CROSSROADS:
                await self._play_dialogue(session, ROOM_CROSSROADS, 2)
            else:
                await session.send_line("")
                await session.send_line(_sprite_line(
                    'Ridijy smiles encouragingly.  "You\'re doing great!  '
                    'Head back to the crossroads when you\'re ready for the next quest."'
                ))
                await session.send_line("")
            return True

        # Scenario 1: Communication
        if stage == 10 and command in ("say", "ask"):
            session.tutorial_stage = 11
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(
                    session.character_id, session.tutorial_stage, False
                )
            await self._play_dialogue(session, room_id, 11)
            return False

        if stage == 11 and command == "search":
            session.tutorial_stage = 12
            session.silver += 10
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(
                    session.character_id, session.tutorial_stage, False
                )
            await self._play_dialogue(session, room_id, 12)
            return False

        # Scenario 2: Inventory
        if stage == 21 and command == "get" and "sword" in (args or "").lower():
            if _held_or_stowed_tutorial_sword(session):
                await session.send_line("You already have the weathered iron sword.")
                return True
            sword = _tutorial_sword_item()
            if not getattr(session, "right_hand", None):
                sword["slot"] = "right_hand"
                session.right_hand = sword
            elif not getattr(session, "left_hand", None):
                sword["slot"] = "left_hand"
                session.left_hand = sword
            else:
                await session.send_line("You need a free hand to pick up the weathered iron sword.")
                return True
            session.tutorial_stage = 22
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(
                    session.character_id, session.tutorial_stage, False
                )
            await session.send_line("You pick up a weathered iron sword.")
            await self._play_dialogue(session, ROOM_INVENTORY_CAMP, 22)
            return True

        if stage == 22 and command == "give" and "sword" in (args or "").lower() and "warrior" in (args or "").lower():
            if not _remove_tutorial_sword(session):
                await session.send_line("You are not holding the weathered iron sword.")
                return True
            session.tutorial_stage = 23
            session.silver += 25
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(
                    session.character_id, session.tutorial_stage, False
                )
            await self._play_dialogue(session, ROOM_INVENTORY_CAMP, 23)
            return True

        # Scenario 3: Stealth
        if stage == 30 and command == "hide":
            await session.send_line("You blend into the shadows.")
            session.hidden = True
            return True

        # Scenario 4: Healing
        if stage == 41 and command == "forage":
            herb = _tutorial_herb_item()
            if not getattr(session, "right_hand", None):
                herb["slot"] = "right_hand"
                session.right_hand = herb
            elif not getattr(session, "left_hand", None):
                herb["slot"] = "left_hand"
                session.left_hand = herb
            elif hasattr(session, "inventory"):
                herb["slot"] = None
                session.inventory.append(herb)
            session.tutorial_stage = 42
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(
                    session.character_id, session.tutorial_stage, False
                )
            await self._play_dialogue(session, room_id, 42)
            return True

        if stage == 43 and command == "tend":
            session.tutorial_stage = 44
            if self.server.db and session.character_id:
                self.server.db.save_quest_progress(
                    session.character_id, session.tutorial_stage, False
                )
            await self._play_dialogue(session, room_id, 44)
            return True

        # Portal — works once both tutorial fights are done (stage >= 53),
        # regardless of which room the player is in.  Stage 90 is the
        # completion room but we don't force players to walk back there.
        if stage >= 53 and command == "go" and "portal" in args.lower():
            await self._skip_to_town(session)
            return True

        return False

    async def _play_dialogue(self, session, room_id, stage):
        """Send sprite dialogue to the player."""
        lines = SPRITE_DIALOGUE.get((room_id, stage), [])
        for line in lines:
            await session.send_line(_sprite_line(line) if line.strip() else line)

    async def _skip_to_town(self, session):
        """Transport player from tutorial to their selected starter town."""
        session.tutorial_complete = True
        session.tutorial_stage = 99

        # Save completion to DB immediately
        if self.server.db and session.character_id:
            self.server.db.save_quest_progress(
                session.character_id, 99, True
            )

        start_room_id = int(
            getattr(session, "starting_room_id", 0)
            or getattr(session, "home_room_id", 0)
            or 221
        )
        room = self.server.world.get_room(start_room_id)
        if not room:
            # Zone not loaded yet — fall back to Wehnimer's Landing gate
            log.warning("_skip_to_town: room %d not loaded for character %s, falling back to 221",
                        start_room_id, getattr(session, "character_id", -1))
            room = self.server.world.get_room(221)

        # Remove from tutorial room
        if session.current_room:
            self.server.world.remove_player_from_room(session, session.current_room.id)

        town = (getattr(room, "zone_name", "") or (room.zone.name if room and room.zone else "")) or "the world"

        await session.send_line("")
        await session.send_line("=" * 55)
        await session.send_line("  The world shimmers around you...")
        await session.send_line(f"  You find yourself in {town}.")
        await session.send_line("=" * 55)
        await session.send_line("")

        session.current_room = room
        self.server.world.add_player_to_room(session, room.id)
        await self.server.commands.handle(session, "look")

        # Save progress
        if self.server.db and session.character_id:
            self.server.db.save_character(session)
