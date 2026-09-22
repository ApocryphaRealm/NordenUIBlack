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
| `tools/build-package.py` | assembles the package, builds the three DIP outputs offline, and reads the colour back from the packaged files |

Three menus are not loose Norden files - RaceMenu's race menu and bottom bar (inside `RaceMenu.bsa`)
and Character Progression Control's level-up screen. Norden restyles such menus through the Dynamic
Interface Patcher at run time. Here the black delta is applied **offline** with `xdelta` and the
finished SWF is shipped, so a player needs neither DIP nor the Automatic DIP Patcher.

Version: `VERSION` (stamped by the version gate). Tools GPL-3.0-or-later (`LICENSE`); the art is
Nithog's (`NOTICE.md`).
