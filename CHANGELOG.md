# Changelog - Norden UI - Black


## Unreleased

### Added
- Optional, last installer page: **HUD Position Manager - its widgets in Norden Black** (the owner, 2026-10-04: "make it
  a FOMOD option if they use HUD Position Manager ... we need to maintain compatibility with the current"). HPM 1.1 builds
  its own HUD widgets; this dresses its eight (breath, casting, shout cooldown, detection, level, gold, carry weight, game
  time) in Norden UI - Black's own art, grafted by tools/hpm-widgets.py from the casting bar, oxygen meter and STB widget
  files into HPM's clip contract. Recommended when HUDPositionManager.dll is installed, otherwise optional and unticked;
  nothing else in the package changes. Tested 2026-10-04 in game (Njordlinger Test, SE 1.5.97): all eight loaded
  Norden's art, the meters filled from the left (casting 0.5, detection 0.35 tinted red, breath 0.7, shout 0.6), and the
  text widgets drew in Norden's font with its icons (07:08, 1, 72, 2 / 300).
- The HPM option also carries resist.swf (STB's resist row: its eight icons and fields), equip.swf (STB's equip cross -
  Norden's four leaf backs with their turns kept, the item-type, shout and arrow icons with every frame for HPM to step,
  the ammo in a right-aligned copy of STB's arrow field beside the left back) and playtime.swf (Norden UI - Black has no
  play-time skin; it wears the game-time widget's). Tested in game 2026-10-04 with every icon type HPM sends.
- The HPM option also carries level_badge.swf: Norden's own level badge (hudmenu.swf's LevelMeter - the diamond, its
  141-frame XP fill as HPM's Meter, its level text as Value), only that badge's dependency closure copied out of the
  HUD file (14 characters, 1.4 KB). Tested in game: reads the level, fills with the XP.
- build-fomod.py reads the extras (RaceMenu DIP, CPC screen, buttonart) from the previous FOMOD when the old flat
  package is gone.

## 1.0.3 - 2026-09-24 - working

* **All of Norden UI, not just one install's choices** (the owner, 2026-09-24: "recolor all of Norden UI ... so that I
  have a more comprehensive build to post to Nexus"). Earlier builds recoloured the Norden UI folder as installed here -
  one set of installer choices, 345 SWFs. 1.0.3 recolours Norden UI 1.2.6's whole archive - every option of its
  installer (926 SWFs, 150 Wheeler SVGs) and its separate QuickLoot IE 4.0 BETA file - with the same rule, and ships as
  a FOMOD that asks Norden's own questions: pick the same answers as for Norden UI. Options with nothing to recolour
  install nothing. A last page offers the menus that are not Norden's loose files (RaceMenu through the Automatic DIP
  Patcher, Character Progression Control's level-up screen, QuickLoot 4.0 BETA). The moreHUD layout (inventory widget
  right-aligned) is applied to both resolutions' presets. Textures and the INI/JSON presets are Norden's own: none
  carries a panel grey at or below the rule's threshold.
* The RaceMenu option also installs Norden's loose `Interface
acemenuuttonart.swf`, black, as 1.0.2 did (the
  first 1.0.3 installer had no entry for it).

## 1.0.2 - 2026-09-22

* The Automatic DIP Patcher descriptor shipped `"alreadyPatched": true`, the flag that tells the patcher a patch is
  already applied, so it skipped ours and the race menu stayed vanilla (the owner, at a new game's race menu). It
  ships `false` now, as that patcher's own documentation specifies. Norden UI's own RaceMenu descriptor carries
  `true` as well, so his patch never applies through the automatic patcher either - worth telling Nithog.

## 1.0.1 - 2026-09-22

* RaceMenu's race menu and bottom bar are shipped as a Dynamic Interface Patcher patch (xdelta deltas in
  `Norden Black RaceMenu DIP\Patch\RaceMenu.bsa\...` plus `SKSE\Plugins\AutomaticPatcher\DIP\Norden-Black-RaceMenu.json`),
  no longer as finished SWFs - RaceMenu's team takes down anything that distributes their files, patched or
  not (borokoshow to the owner, 2026-09-22). The build still applies the deltas to a temporary folder to prove
  they fit the current RaceMenu.bsa and reads the colour back; nothing of that is shipped. Character
  Progression Control's level-up screen (our own mod) still ships finished. Players need DIP (and ideally the
  Automatic DIP Patcher) for the RaceMenu part, as with Norden UI's own RaceMenu download.

## 1.0.0

First release (the owner, 2026-09-18: *"then norden in black color while maintaining nordens opacity
or fading level as a mod for our list"*; 2026-09-22: *"just finalize norden ui black in its entirity"*).

* Every Norden UI 1.2.6 SWF with a panel grey recoloured: neutral greys at or below 102 darkened by
  `v' = max(0, round((v - 51) * 0.5))` - 51 to 0, 64 to 6, 88 to 18, 102 to 26. Alpha, colour
  transforms, text, borders and hued accents untouched.
* Norden's Wheeler SVGs recoloured by the same rule; its moreHUD presets included.
* RaceMenu's race menu and bottom bar, and Character Progression Control's level-up screen, built
  offline from the black DIP deltas and shipped as finished SWFs - no Dynamic Interface Patcher needed.
* Seen in game on Njordlinger 2026-09-18 (inventory, magic, container, journal, map, favourites, tween:
  panels black, fades kept, text light); the offline race-menu builds are byte-identical to the files
  the Automatic DIP Patcher produced in that game.
