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

## Inventory Reforged for SkyUI (the optional "Inventory Reforged" installer options, 1.1.0+)

[Inventory Reforged for SkyUI](https://www.nexusmods.com/skyrimspecialedition/mods/195826) is its author's work. Its page
says everything in the mod is open: anyone may use, change, translate, convert, reupload and include any part of it in
their own mods, free or not, without asking, and credit is welcome. This package includes one small part of it: the
mod's default settings file `SKSE\Plugins\InventoryReforged.ini`, with only `iAccentColor` and `iTextColor` in `[Look]`
changed to Norden UI - Black's palette (a copy of the file is in `extras/inventory-reforged/`). The colours option
includes no art (SWF) and no code (DLL) of Inventory Reforged. The "item preview size" option installs Norden UI's own
"SkyUI Default" 3D item position file (Nithog), unchanged. The separate, unticked "larger centred item preview" option
(1.1.0) installs `Interface\InventoryReforged\panel.swf` of Inventory Reforged 1.4.0 with TWO scripts changed
(DoAction_21 and 22: where and how large the 3D item is aimed, and an Item preview section of the settings popup, the Character button staying at the bottom, and the item card no longer following the window), made by `tools/ir-preview-patch.py` from the
original file (SHA-256 in `extras/inventory-reforged/panel-1.2.4.sha256` and `panel-1.3.0.sha256`) - changed and included under the permission
quoted above; the file is not in this repository. A second "panel fixes" choice (1.1.1) installs `Interface\InventoryReforged\panel.swf` of Inventory Reforged 1.6.3 with three scripts changed (DoAction_24, 25 and 30: black, opaque fills only), made by the same tool from the original file (SHA-256 in `extras/inventory-reforged/panel-1.6.3.sha256`), under the same permission. No DLL of Inventory Reforged is ever included.

## This repository

The tools and documents are GPL-3.0-or-later, ApocryphaRealm 2026. The repository carries no art.

If Nithog would rather this were not published, it comes down.
