# Norden UI - Black

[Norden UI](https://www.nexusmods.com/skyrimspecialedition/mods/166086) (by Nithog) with its panel
grey taken to black. Norden's `#333333` panels become pure black; its lighter greys keep half their
distance above the panel, so headers, hover states and dividers stay distinct. Text, borders, hued
accents, alpha and every fade are Norden's own and untouched. Requires Norden UI; sits above it.

## What is in this repository

Tools and documents only - **no art**. Norden UI's permissions allow a modified release on Nexus with
credit, and forbid uploading it to other sites, so every file that carries Norden's art (the SWFs,
the SVGs, the DIP deltas, the intermediate XML) is git-ignored and lives only on the build machine.

| file | what it does |
| --- | --- |
| `tools/export-xml.py` | every Norden UI SWF to JPEXS XML (`ffdec-cli -swf2xml`) in `build/xml` |
| `tools/survey.py` | the colour census that chose the rule below |
| `tools/recolour.py --build` | darkens every neutral grey (channel spread <= 3) at or below 102: `v' = max(0, round((v - 51) * 0.5))`, then `-xml2swf` into the mod folder |
| `tools/recolour-svg.py --write` | the same rule on Norden's Wheeler SVGs |
| `tools/build-fomod.py` | the FULL build (1.0.3+): every option of Norden UI's installer, recoloured, as a FOMOD that mirrors Norden's own steps and options; run export-xml / recolour / recolour-svg first with `NORDEN_XML`, `NORDEN_XML_BLACK`, `NORDEN_BLACK` (and `NORDEN_SVG_ALL=1`) pointed at `buildull-*` |
| `tools/build-package.py` | assembles the package, proves the RaceMenu deltas and builds the CPC file offline, and reads the colour back |

Three menus are not loose Norden files - RaceMenu's race menu and bottom bar (inside `RaceMenu.bsa`; since 1.0.1 shipped as a DIP patch of deltas, never as finished files)
and Character Progression Control's level-up screen. Norden restyles such menus through the Dynamic
Interface Patcher at run time. For RaceMenu the package does the same: it ships the black **deltas** as a
DIP patch (`Norden Black RaceMenu DIP`) with the Automatic DIP Patcher descriptor, and DIP builds the files
from the player's own `RaceMenu.bsa` - RaceMenu's files are never distributed. The build applies the deltas
offline only to prove they still fit and to read the colour back. Character Progression Control is our own
mod, so its level-up screen is built offline with `xdelta` and shipped finished.

Version: `VERSION` (stamped by the version gate). Tools GPL-3.0-or-later (`LICENSE`); the art is
Nithog's (`NOTICE.md`).
