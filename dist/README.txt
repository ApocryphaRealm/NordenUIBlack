Norden UI - Black
=================
Version 1.0.2

Norden UI with its panel grey taken to black. Norden's #333333 panels become pure black; its
lighter greys keep half their distance above the panel, so headers, hover states and dividers stay
readable. Text, borders, the slate and coloured accents, and every opacity and fade are Norden's own
and unchanged. Requires Norden UI; does nothing on its own.

WHAT IT COVERS
--------------
Every menu Norden UI restyles with a panel grey: inventory, magic, container, barter, crafting,
journal and quest journal, map and map markers, favourites, tween, stats and perks, level-up,
dialogue, book, lockpicking, sleep/wait, training, tutorial, message boxes, loading, start menu,
the HUD and its widgets (SkyUI, moreHUD, SkyHUD, the InfinityUI / Dragon's Eye Minimap files, True
Directional Movement, Better Third Person Selection), Norden's Wheeler art and its moreHUD presets.

RACEMENU - THROUGH DIP, LIKE NORDEN
-----------------------------------
RaceMenu's race menu and bottom bar live inside RaceMenu.bsa, and RaceMenu's files are not
redistributed, patched or not. So, exactly like Norden UI's own RaceMenu download, this package
ships a Dynamic Interface Patcher patch ("Norden Black RaceMenu DIP") - small deltas that DIP
applies to YOUR RaceMenu.bsa to produce the black menus - plus the descriptor the Automatic DIP
Patcher reads. Character Progression Control's level-up screen is ours and ships finished.

WHAT CHANGED
------------

Version 1.0.2
RaceMenu's race menu and bottom bar are no longer shipped as finished files; the package carries
their DIP deltas and the Automatic DIP Patcher descriptor instead, the way Norden UI does.
Everything else is unchanged.

Version 1.0.0
First release: Norden UI 1.2.6 recoloured to black.

INSTALLATION
------------
1. Install Norden UI (1.2.6) with the options you want.
2. Install this as its own mod, loading AFTER (below) Norden UI, so its files win. No plugin, no INI.
3. For the black RaceMenu menus: install Dynamic Interface Patcher (DIP) and, ideally, the Automatic
   DIP Patcher, which then applies "Norden Black RaceMenu DIP" for you at launch. Without the
   Automatic patcher, run DIP once and point it at this mod's "Norden Black RaceMenu DIP" folder.
4. Do NOT also apply Norden UI's own RaceMenu DIP patch: both patch the same two files, and whichever
   runs last wins. Disable Norden's RaceMenu DIP patch when using this one.

The package carries black copies of every Norden option it was built from. A black copy of a menu
for a mod you do not have is never loaded, so it does no harm.

CREDIT
------
Norden UI by Nithog - https://www.nexusmods.com/skyrimspecialedition/mods/166086 - every piece of
art in this package is his, recoloured. RaceMenu by expired6978, whose race menu Norden restyles;
none of RaceMenu's files are included. Dynamic Interface Patcher by Cutleast.

LICENCE
-------
The tools that build this package are GPL-3.0-or-later (LICENSE). The art is Norden UI's and is
used under its permissions (modification and release on Nexus, with credit); it is not relicensed.
