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
  (colour values only - the Norden UI - Black palette), `docs\RaceMenu Atelier - Norden UI - Black build.txt` (this
  notice, installed beside the DLL).
- **What was changed:** RaceMenu Atelier 1.0.1 (emberchain, commit `f05e2c2`) plus two commits by ApocryphaRealm:
  `09df305` (race-type entries another mod files under its own category - Apprentice - A Class Overhaul's classes and
  traits - get their own tiles and are picked through the menu's `onItemPress`, never `ChangeRace`) and `370269a`
  (palette and corner radius read from `SKSE\Plugins\RaceMenuAtelier\theme.ini` when it exists). These are the two
  changes emberchain lists for RaceMenu Atelier 1.0.2; they were offered upstream as emberchain/RaceMenuAtelier pull
  request #1.
- **Corresponding source:**
  [github.com/ApocryphaRealm/RaceMenuAtelier, commit 370269a27a7db642fa2964e33d8832472c7e036f](https://github.com/ApocryphaRealm/RaceMenuAtelier/tree/370269a27a7db642fa2964e33d8832472c7e036f)
  (branch `apprentice-classes-and-theme`, upstream history kept). Build: `git submodule update --init --recursive`,
  `xmake f -m releasedbg --skyrim_vr=n --cxflags=/d1trimfile:<clone folder>`, `xmake build RaceMenuAtelier`.
- **SHA-256:** DLL `f2e76736352e090e79789af498f8e3dcea07175a19408fd559cde2c9ffb23ca6`, PDB
  `ebd6b04370d380eb6d472d26ece5bd05ce8192f8b36e5ecf64ead9b54d47a890`.

## This repository

The tools and documents are GPL-3.0-or-later, ApocryphaRealm 2026. The repository carries no art.

If Nithog would rather this were not published, it comes down.
