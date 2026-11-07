# Bruma Signs SMIM Patch

**Version 1.0.0**

Gives the seven shop and inn signs of **Beyond Skyrim: Bruma** the **Static Mesh Improvement Mod (SMIM)** sign models,
rebuilt on the current SMIM SE meshes. It is an update of the 2017
[Bruma Signs SMIM patch - SE](https://www.nexusmods.com/skyrimspecialedition/mods/10924) by Forzane, which shipped
Oldrim-format copies of an older SMIM.

Skyrim Special Edition and Anniversary Edition. Seven meshes and one plugin; no textures.

## Requirements

- [Beyond Skyrim - Bruma SE](https://www.nexusmods.com/skyrimspecialedition/mods/10917)
- [Static Mesh Improvement Mod - SMIM](https://www.nexusmods.com/skyrimspecialedition/mods/659) SE, with the
  "Chains 3D - Signs" option. SMIM's metal-chain texture (`textures\smim\clutter\signage\metalwork01_brown.dds`) and
  its post texture come from it.

### Target versions
Built from SMIM SE 2.08 (file "SMIM SE 2-08", option `06 Chains 3D - Signs`) and checked against Beyond Skyrim - Bruma SE
1.6.4 (`BSHeartland.esm`). If SMIM changes these two sign meshes, rebuild (see [BUILDING.md](BUILDING.md)).

## The Problem

Bruma's signs are its own meshes (`meshes\bscyrodiil\clutter\signage\bruma\`), so SMIM does not improve them. The
2017 patch replaced them with SMIM's signs, but its meshes are Oldrim-format (NiTriShape, user version 83) copies of
the SMIM of that time. SMIM SE now ships Special Edition meshes (BSTriShape) of the same signs.

## What the Patch Does

- **Seven meshes**, each a copy of the current SMIM SE sign mesh with only the sign-face texture changed to Bruma's
  board:
  - `inns\signnightgateinn01.nif` as the base for A Cut Above, Jerall View Inn and The Restful Watchman;
  - `riften\signrtbeeandbarb01.nif` for the Fighters Guild, Icewind Traders, Northern Arms and the Synod.
- **`SMIM-Bruma-Patch.esp`**: one record, the Snow Stone Rest sign (`CYRSignSnowStoneRest`, BSHeartland `003AB2`).
  Bruma reuses the vanilla Windpeak Inn sign with a texture swap on its first shape; SMIM's version of that mesh has
  the sign board as the second shape, so the plugin moves the swap there. Nothing else in the record changes.

## Install

1. Install SMIM SE with the "Chains 3D - Signs" option, and Beyond Skyrim - Bruma SE.
2. Install this archive with your mod manager. If you have the 2017 patch (Nexus 10924), disable or remove it: this
   replaces the same files.
3. File priority: nothing else ships these paths in a usual setup, so anywhere works. Sort plugins with LOOT.

**Saves:** the plugin adds no records, only one override; safe to add or remove mid-playthrough.

## Build from Source

See [BUILDING.md](BUILDING.md). The repository contains no file from another mod.

## Verification Status

- All seven meshes are Special Edition format, have SMIM's block layout, differ from SMIM's mesh only in the
  `BSShaderTextureSet` block (every other block byte-identical), and pass AutoMod `nif verify`.
- All seven Bruma sign textures exist in `BSHeartland - Textures.bsa`.
- The plugin's record matches Bruma's except the alternate-texture 3D index (0 -> 1), and SMIM SE 2.08's
  `SignWindpeakInn01.nif` has the `SignBanneredMare:29` shape at index 1.
- **Not tested in game.** Bruma's sign boards are laid out for the vanilla sign face, as SMIM's are; that the
  pictures line up on SMIM's boards is the same assumption the 2017 patch made.

## Credits and Permissions

Read on 2026-11-05 from each page's Permissions section.

### Static Mesh Improvement Mod - SMIM
- **Author:** Brumbek. **Page:** [SMIM](https://www.nexusmods.com/skyrimspecialedition/mods/659).
- **Used:** the two sign meshes above, with one texture path changed. No textures.
- **Permissions:** asset use allowed without permission or credit; not in sold mods; not in mods earning Donation
  Points without permission. Author notes: "users have permission to use SMIM assets freely in any mod. You can create
  any compatibility patches or add-ons that you want using SMIM stuff."

### Beyond Skyrim - Bruma SE
- **Authors:** The Beyond Skyrim - Cyrodiil Development Team. **Page:**
  [Bruma SE](https://www.nexusmods.com/skyrimspecialedition/mods/10917).
- **Used:** `BSHeartland.esm` as a master and the paths of its sign textures. No Bruma files.
- **Author's instructions:** "You are free and welcome to distribute addons and compatibility patches for Beyond
  Skyrim: Bruma."

### Bruma Signs SMIM patch - SE
- **Author:** Forzane. **Page:** [10924](https://www.nexusmods.com/skyrimspecialedition/mods/10924).
- **Used:** the idea, the sign-to-base pairing, and `SMIM-Bruma-Patch.esp` (copied unchanged).
- **Permissions:** none stated for its own files. Permission for the plugin has not been obtained.

## License

The code and documentation in this repository (`build.py`, `inputs.sha256`, `release.toml`, the Markdown files) are
under the [MIT License](LICENSE). The built meshes are derived from SMIM and stay under its permissions.
