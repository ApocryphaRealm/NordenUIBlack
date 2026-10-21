# Whose work this is

**The art is Nithog's.** Norden UI - Black is Norden UI recoloured: every file in the package is one
of Norden UI's own files with its panel grey darkened, or a menu Norden restyles through the Dynamic
Interface Patcher, built offline with the black delta applied. Nothing is drawn from scratch.

## Norden UI

[Nexus 166086](https://www.nexusmods.com/skyrimspecialedition/mods/166086), by **Nithog** (version
1.2.6, with its RaceMenu DIP patch 1.2.2). Its permissions allow modifying and releasing the files
with credit, on Nexus only. This package requires Norden UI and is released on Nexus only, with credit.

## What Norden restyles

RaceMenu (by expired6978), Character Progression Control, SkyUI, moreHUD, Wheeler, SkyHUD, True
Directional Movement, Better Third Person Selection, Dragon's Eye Minimap / InfinityUI and the map
marker resource mods are the menus Norden UI restyles; their authors' credit is on Norden UI's page.
Since 1.0.1 nothing of RaceMenu's is shipped at all: the package carries xdelta deltas for its two menus and
the Dynamic Interface Patcher builds the black files on the player's machine, as Norden UI's own RaceMenu
download does. Where a menu's original lives inside another mod's archive (RaceMenu.bsa, Character Progression
Control), the package ships the patched result only, exactly as Norden's own DIP patch produces it at
run time - that archive is not redistributed.

## RaceMenu Atelier (the optional "RaceMenu Atelier" installer option, 1.0.4+)

The option installs a modified build of **RaceMenu Atelier** by **emberchain**
([Nexus 193865](https://www.nexusmods.com/skyrimspecialedition/mods/193865),
[github.com/emberchain/RaceMenuAtelier](https://github.com/emberchain/RaceMenuAtelier)), licensed under the **GNU
General Public License version 3** - the same licence text as `LICENSE` in this download. It is shipped with
emberchain's permission, and emberchain is its author; nothing of RaceMenu (expired6978) is included.

- **Files:** `SKSE\Plugins\RaceMenuAtelier.dll` and `.pdb` (object code), `SKSE\Plugins\RaceMenuAtelier\theme.ini`
  (the Norden UI - Black palette and the log level), `docs\RaceMenu Atelier - Norden UI - Black build.txt` (this
  notice, installed beside the DLL).
- **What was changed:** RaceMenu Atelier 1.0.1 (emberchain, commit `f05e2c2`) plus three commits by ApocryphaRealm:
  `09df305` (race-type entries another mod files under its own category - Apprentice - A Class Overhaul's classes and
  traits - get their own tiles and are picked through the menu's `onItemPress`, never `ChangeRace`) and `370269a`
  (palette and corner radius read from `SKSE\Plugins\RaceMenuAtelier\theme.ini` when it exists) and `62b288c` (the
  log level, `uLogLevel`, read from that same file). The first two are the changes emberchain lists for RaceMenu
  Atelier 1.0.2; they were offered upstream as emberchain/RaceMenuAtelier pull request #1.
- **Corresponding source:**
  RaceMenu Atelier by emberchain (GPL-3.0), patched build from commit 62b288c74f9fa26ae05dcf9dd41b8df084e9990a
  (branch `upstream-apprentice`, upstream history kept). Build: `git submodule update --init --recursive`,
  `xmake f -m releasedbg --skyrim_vr=n --cxflags=/d1trimfile:<clone folder>`, `xmake build RaceMenuAtelier`.
- **SHA-256:** DLL `585c1707475bb7f4ca507ef1fb0cfbdeae6946fb1ebd6c4b968c4ac22d2fb8d0`, PDB
  `15c2519732dd57181e43c3a99d0e54c3d6ef17f52de237ad7fd2b40fb481c8cc`.

## Inventory Reforged for SkyUI (the optional "Inventory Reforged" installer options, 1.0.5+)

[Inventory Reforged for SkyUI](https://www.nexusmods.com/skyrimspecialedition/mods/195826) is its author's work. Its page
says everything in the mod is open: anyone may use, change, translate, convert, reupload and include any part of it in
their own mods, free or not, without asking, and credit is welcome. This package includes one small part of it: the
mod's default settings file `SKSE\Plugins\InventoryReforged.ini`, with only `iAccentColor` and `iTextColor` in `[Look]`
changed to Norden UI - Black's palette (a copy of the file is in `extras/inventory-reforged/`). No art (SWF) and no code
(DLL) of Inventory Reforged is included. The second option installs Norden UI's own "SkyUI Default" 3D item position
file (Nithog), unchanged.

## This repository

The tools and documents are GPL-3.0-or-later, ApocryphaRealm 2026. The repository carries no art.

If Nithog would rather this were not published, it comes down.
