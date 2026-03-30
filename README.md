GemStone IV Private Server

Single-player/private GemStone IV server project using Lua, SQL, and a custom client.
Yes it has coop capability & even a custom party system for it. (Party start join end commands)

(Yes this runs a full private server with a custom client that tries to emulate Gemstone 4 with some single player tweaks)
Currently the city of Ta'avalor is the preferred starting city. Other cities have a few shops, and "maybe" some monsters too, but nothing close to retail. The elf city however has almost everything wired up to it. (Still work in progress)
If you are worried about the client working as good as lich with scripts, it's being worked on, but already surpasses wrayth + lich in various ways as is.

IMPORTANT
This is not an exact 1 to 1 copy project. Certain "liberties" have been taken to make this a 1 player game with coop support. It is still gemstone 4 at it's soul though.

What This Includes

Game server
Client

Lua scripts/loaders

SQL dump for world/content data

Optional media folder for music and sound effects

Requirements

MariaDB or MySQL

Python 3

PIP Install pillow (For map click navigation)

Setup
----------------------------------------------------------------------------------------------------
Download entire project as a zip > extract where ever you like. Default server was built off of N:\GemStoneIVServer   

I cannot tell you if AI planned for this to be on another drive or folder ahead of time (Yes this was made entirely with AI, zero human input other than "hey do this"). I would imagine you could ask Claude how to fix any directory problems you run into, being as he was one of the AI that built it (Codex AI also)

Install MariaDB or MySQL.

Make sure SQL login matches:

user: root

password: none

Create a database named gemstone_dev.

Import USETHIS.sql into gemstone_dev. (If you have Heidi SQL installed you can literally just double click that file to setup the SQL)

Install Python. 

Then open command prompts and run "PIP install Pillow" so the map naviation/clicking works in the client

Start the game server. (Start_server.bat) Edit to your file/folders

Start the client. (Client folder > gsiv_hud.py file)

Connect to:

127.0.0.1

port 4901

Or other with ports open if you want

Play the game

Useful info
---------------------------------------------------------------------------------------------------------------

Database Notes

Main DB name: gemstone_dev

USETHIS.sql is the import file. After you setup Maria DB make sure you make a database named gemstone_dev then import or run the SQL file (USETHIS.SQL).

If you have HEIDI SQL installed you can simply double click that file to get it "installed".

Optional Media

Optional music and sound effects go in:

clientmedia/music

clientmedia/sfx

These are not required for the server to run.

Notes

This is a private educational project

Lua and SQL are used wherever possible

Room mapping relies on LICH IDs

Some systems are customized for single-player quality-of-life

First Run

After importing the DB and starting the server/client:

create a new character

enter the world

test movement, shops, and commands

Troubleshooting
If the client cannot connect, confirm the server is running on port 4901. You could simply use 127.0.0.1 to connect to it too though.
Also open 4902 for the live sync connection between server and client HUD or you will have panel info that does not function.
If the DB fails, confirm gemstone_dev exists and imported correctly
If optional audio is missing, the game should still run without clientmedia

P.S. None of this was leaked from GS4 devs, this was made entirely from scratch, 100% AI made between Claude & Codex 
(More credit to Codex for the WAY higher usage limits)
