# Changelog - Norden UI - Black

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
