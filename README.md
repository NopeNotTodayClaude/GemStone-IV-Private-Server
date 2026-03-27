GemStone IV Private Server

Single-player/private GemStone IV server project using Lua, SQL, and a custom client.

(Yes this runs a full private server with a custom client that tries to emulate Gemstone 4 with some single player tweaks)

What This Includes

Game server
Client

Lua scripts/loaders

SQL dump for world/content data

Optional media folder for music and sound effects

Requirements

Fresh Windows 11 install with:

MariaDB or MySQL

Python 3

Git

GitHub Desktop optional

Setup

Install MariaDB or MySQL.

Create a database named gemstone_dev.

Import USETHIS.sql into gemstone_dev.

Make sure SQL login matches:

user: root

password: none

Install Python dependencies if needed.

Start the game server.

Start the client.

Connect to:

127.0.0.1

port 4901

Or other with ports open if you want

Database Notes

Main DB name: gemstone_dev

USETHIS.sql is the import file for another machine

account and character data are intentionally stripped from the export

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
If the client cannot connect, confirm the server is running on port 4901
Also open 4902 for the live sync connection between server and client HUD or you will have panel info that does not function.
If the DB fails, confirm gemstone_dev exists and imported correctly
If optional audio is missing, the game should still run without clientmedia
