# Changelog - Norden UI - Black


## 1.0.5 - 2026-10-21 - untested

### Added
- **Inventory Reforged for SkyUI** (Nexus 195826) - two new options on the installer's last page (the owner, 2026-10-21:
  "adding support in Norden Black to have it recoloured for Norden Black").
  - "Inventory Reforged - Norden Black colours": Inventory Reforged takes every colour but two from the skin it sits
    on (its sheet, edges and buttons are already black under Norden UI - Black); the two it owns are its gold accent
    and its parchment text. The option installs that mod's own default settings file, SKSE\Plugins\InventoryReforged.ini,
    with only `iAccentColor` (14069864 -> 12303807, Norden's silver #BBBDBF) and `iTextColor` (15130824 -> 15066597,
    #E5E5E5) changed. No art and no code of Inventory Reforged is shipped (its page also allows reuse of any part of the
    mod, credit welcome - NOTICE.md). Its MCM settings still win key by key. Recommended when Inventory Reforged's DLL
    is installed, otherwise optional and unticked. Norden UI - Black needs a higher priority than Inventory Reforged.
  - "Inventory Reforged - item preview size": optional, never preselected. Inventory Reforged places and sizes the 3D
    item of its item window from the game's 3D-item position the first time the inventory opens, and the layout chosen in
    Norden UI's installer sets that position for Norden's own item card (Slimventory: scale 0.6, offsets 53 / -45), so the
    item shows far smaller than the window was made for. The option installs Norden UI's own "SkyUI Default" 3D item file
    (scale 1.5), the same as picking "SkyUI Default" under Inventory Patches > 3D Item Location. Players on another layout
    set the 3D item scale to 1.5 and the offsets to 0 in SkyUI's MCM instead (the option's text says so).
  - "Inventory Reforged 1.2.4 / 1.3.0 - panel fixes: item preview, Character button, Norden's own item card": optional, never preselected
    (the owner, 2026-10-21: with the 3D item scale at 1.5 the item grew 3x but stayed about a fifth of the box and sat
    high in a tall black panel; with a first fix it was "a little bit too big", and a bow, a sword and a cuirass left
    the window; and: "a setting that actually controlled the size of the model and its positioning ... the item
    preview instead of the character"). Cause, read from Inventory Reforged's panel.swf and DLL: its item window keeps
    the 3D item in a box of 130 stage units at the window's top and asks the plugin (PlacePreview) for an item
    (130 - 16) / screen height tall - a plain scale, not a fit - while under Norden UI the window is much taller. The
    option replaces panel.swf with a copy where two scripts changed (DoAction_22: preview and popup; DoAction_21: the Character tab): `Equipment.aimPreview` aims the
    item at the middle of the whole part of the window above its stats and asks min(area, window width) x fit x size,
    fit 0.95 for weapons and ammo (a sword is as long as the height asked for, a bow 0.86 of it each way, measured on
    the owner's screenshots) and 1.1 for everything else (a cuirass reached 0.875 of the 1.35 request), so every item
    fits at 100 percent. The settings popup gets an ITEM PREVIEW section (Size, Sideways, Up and down, Reset size and
    place) when "Show the character" is off. They are the character's three saved numbers (iScale, iShiftRight,
    iShiftUp of [Doll] - the plugin saves only its known keys and its setter ignores others, so a new key cannot be saved
    without changing the DLL), so they are remembered across sessions; with the character on they drive the character
    and the item uses the defaults. Range 60-140 percent and plus or minus 40 percent, as the plugin clamps them.
    tools/ir-preview-patch.py makes the file from the original (SHA-256 checked) and reads back that no other script
    One more change (the owner, 2026-10-21) rides in the same file - a mod folder holds one panel.swf: the CHARACTER tab
    stays at the bottom of the screen when the drawer opens (the drawer opens above it; the drawer's room is one tab
    height smaller) instead of riding the drawer's top edge. Inventory Reforged's own gamepad navigation (right stick
    click, D-pad, A, B, X) is left as it is - the owner tested it and wants no change.
    A third change (the owner, 2026-10-21: "the items card, which while using Norden UI would normally be locked in
    position below the inventory list, is now moving up and down" and "it was using a different item card than the one
    that Norden Black uses"; "find a way for Norden Black to ... override it properly to keep it in place and use Norden
    Black's position and size and design"). The card IS Norden Black's: in the test profile test Norden UI - Black 1.0.5
    wins inventorymenu.swf, skyui\itemcard.swf and every deardiary_dm\inventory\itemcard_N_BG.swf (same files as Norden
    UI Black 1.0.3; nothing above it ships any; Dragonborn UI is off; the overwrite folder has none). Inventory Reforged
    takes that card into its own window and restyles it (DoAction_18 of 1.2.4 and 1.3.0): placeWindow moves it (_x, _y) and
    hides its background art and Stolen text and adds a kind line, shifting the card's parts down 26 units; sizeWindow and
    windowUnits rescale it to the window width; the window height reserves its bounds; effectLines re-breaks its effect
    text; keepFrameHidden re-hides the background every frame; and, from 1.3.0, showWindow hides the whole card whenever
    IR's window is hidden. So the card showed small, without Norden's art, sliding up and down with the window - never as
    Norden draws it. The option now redefines those seven functions (in DoAction_22, a later tag, so they win) without
    those lines and with a fixed 150-unit room instead of the card's bounds: Norden's card shows as Norden made it, in
    Norden's place below the list, at its own size, all the time, and the item window still follows the row with the fitted
    preview. The kind line cannot stay: it is a text field added INTO the card and the card's parts are shifted to make
    room for it, which is exactly the modification Norden's card must not get; IR's window keeps its own quiet tags.
    There is one option per Inventory Reforged version (1.2.4 and 1.3.0, each a SHA-256-locked panel.swf; a group that takes
    at most one); tools/ir-preview-patch.py builds both and refuses any other file.
    A fourth change (the owner, 2026-10-21: "a setting for determining where the item preview window appears so that it
    doesn't follow the cursor ... left and right sliders ... within the bounds of the inventory list"; at row 1 the window
    covered Norden's card by ~25 px and, flipped above a row, the loadout bar and the filter gear): the cog popup's Item
    window section gets "Fixed place" (with the character off) and, when it is on, Sideways and Up and down in steps of 10
    percent. Fixed, `placeFixed` puts the window inside the item list's frame (measured at run time: the list background clip's bounds in panel coordinates, cut above the card text's top; round 3 found the first version used the wrong coordinates, so the window was 555-585 px tall and spilled over the category icons, the loadout bar and the card), sizes the preview to the room left under the stats (up to 260 units, so the whole window is never taller than that room and all four edges are clamped inside it)
    and fits the item in it; Sideways 0 is the list's left edge, 100 its right edge (the old resting place); Up and down 0
    is the top. It is off by default, so nothing changes for anyone who does not tick it; a player who wants Fixed from
    the start ticks it once. Persistence: Inventory Reforged's setter writes any key (the plugin source), but only its
    known keys can be read back by the panel, so the choice and the two positions are packed into [Doll] fTurnSpeed (read
    back as `turnSpeed`; the doll's turn speed, which does nothing while the character is hidden): 0.5 (the default)
    is Follow the row; 0.800 + 0.002 x (sideways step x 11 + up/down step) is Fixed, at most 1.04. Switching the character
    on puts it back to 0.5. The ITEM PREVIEW and Fixed controls are no longer dimmed while the character is off (the stock
    popup dimmed the character rows then).
    Round 4: the list background clip is not the frame under Norden (its shape spans the whole panel), so the bounds are now the
    list's own anchors: left at the lists' panel origin, top at the item list's origin, right at the rows' right edge (the
    stock window anchor), bottom above the card text (else above the bottom bar); the window is cut to that room and every
    placement logs a PANELTEST fixed line to the SKSE log with the bounds, room and window size.
    Round 5: the anchors were right but the visible frame sits above them (header 20 units above the list origin, card heading 26 above the
    name text, frame ends 24 above the card heading), and the right edge was the list edge, not the stock window edge. Fixed place now
    uses those offsets, the stock window inset on the right, and keeps 24 units of slack so Up and down always has room to move.

- build-fomod.py builds both from `extras/inventory-reforged/InventoryReforged.ini` and Norden UI's own
  "Norden default 3D item position 1.1" file.

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
- 2026-10-07: the HUD Position Manager option is built only with `NORDEN_INCLUDE_HPM=1` (default off). HPM is not
  finished and its page waits, so 1.0.4 ships without it (the owner, 2026-10-07); the work above stays here for the
  release that carries it.

## 1.0.4 - 2026-10-07 - untested

### Added
- **RaceMenu Atelier** - a new option on the installer's last page (the owner, 2026-10-07): RaceMenu Atelier (by
  emberchain) in Norden UI - Black's palette - black panels, Norden's silver #BBBDBF lines and accents, #8E9396 borders,
  square corners. Installs `SKSE\Plugins\RaceMenuAtelier\theme.ini` and, because Atelier 1.0.0 / 1.0.1 cannot read a
  theme, replaces `SKSE\Plugins\RaceMenuAtelier.dll` (+ `.pdb`) with a build that reads one: Atelier 1.0.1 plus
  `09df305` (Apprentice - A Class Overhaul's classes and traits as their own tiles), `370269a` (the optional theme
  file) - the two changes emberchain lists for Atelier 1.0.2 - and `62b288c` (the log level, `uLogLevel = 2`, read
  from that theme file) (RaceMenu Atelier by emberchain, GPL-3.0, patched build from commit
  `62b288c`; with emberchain's permission; NOTICE.md and an installed `docs\RaceMenu Atelier - Norden UI -
  Black build.txt` carry the notice and the source pointer). Recommended when RaceMenuAtelier.dll is installed,
  otherwise optional and unticked. Norden UI - Black must have a higher priority than RaceMenu Atelier (in MO2's left
  pane, below it). Nothing else in the package changed: every other file is byte-identical to 1.0.3.

### Fixed
- **The dialogue box is black now** (a player's report, 2026-10-08: the conversation box still showed Norden's colour).
  Norden's dialogue menu draws its selected-topic box in Norden's slate (42,52,57 and 91,103,109). The recolour rule
  only darkens neutral greys, so that slate was never touched and the box kept its original colour. A new build step,
  tools/recolour-dialogue.py, applies the same darkening rule to the slate colours of the dialogue movies and nothing
  else: dialoguemenu.swf in all three Norden variants (16x9, 21x9, Smart Talk DBVO) and the deardiary_dm dialoguemenu
  pieces. Alpha is unchanged, so the box fades as before; other menus keep their slate selection colour as in 1.0.3.

### Fixed (build only)
- build-fomod.py's hand-tuned carry-over (tween menu, hudmenu, QuestItemList) looked for the installed Black folder
  under its old name and silently carried nothing; it finds "Norden UI Black" now and stops when no folder is found.
- LICENSE and NOTICE.md come from the repo, no longer copied from the previous release.
- The package lands in `7. current test builds\Skyrim - Norden UI - Black\` (the project's package-path resolver).

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
* The RaceMenu option also installs Norden's loose `Interface\racemenu\buttonart.swf`, black, as 1.0.2 did (the
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
