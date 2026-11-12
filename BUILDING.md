# Building from source

Back to [README.md](README.md).

This repository contains no file from another mod: you supply them in `inputs/`, and `build.py` copies SMIM's two
sign meshes and changes one texture path in each. The plugin is ours: `src/plugin/` (Spriggit YAML) is
deserialized, round-tripped and checked.

## Platforms

Tested: macOS (arm64) only. `nif-tool.exe` (used by AutoMod) is a Windows program; on macOS it runs through
CrossOver (Skyrim AI toolkit, `docs/macos-crossover.md` section 1). Windows and Linux: expected to work with the
AutoMod wrapper, not run.

## What you need

- Python 3.9+.
- The [Skyrim AI toolkit](https://github.com/kxgcayh/skyrim-agents-toolkit) with AutoMod CLI v1.11.2 built and `nif-tool` placed (toolkit `docs/installing-tools.md`).
  Clone it next to this repo (or next to a parent folder), or set `SKYRIM_TOOLKIT` to its folder.
- These two files in `inputs/` (create the folder):

| File in `inputs/` | Where it comes from |
|---|---|
| `signnightgateinn01.nif` | [SMIM](https://www.nexusmods.com/skyrimspecialedition/mods/659?tab=files&file_id=59069) SE 2.08, main file "SMIM SE 2-08" (file ID 59069), `06 Chains 3D - Signs/meshes/clutter/signage/inns/` in the archive |
| `signrtbeeandbarb01.nif` | the same archive, `06 Chains 3D - Signs/meshes/clutter/signage/riften/` |

`build.py` checks each against `inputs.sha256` and stops on a missing or different file.

## Run

```bash
python3 build.py
```

Writes `build/` (`SMIM-Bruma-Patch.esp` and `meshes/bscyrodiil/clutter/signage/bruma/*.nif`) and prints each file's
hash and size. Packaging is done by the workspace release tool from `release.toml`:

```bash
python3 ../../tools/mod-release/release.py . nexus     # files only
python3 ../../tools/mod-release/release.py . github    # files plus MO2 meta.ini and <zip>.meta
python3 ../../tools/mod-release/release.py . package   # both
```

Nothing is uploaded without `--publish`.

## Changing the patch

- A new SMIM version: put its two meshes in `inputs/`, update `inputs.sha256`, rebuild, and check that SMIM's
  sign-face texture path is still the `old` string in `build.py` (the build stops if it is not).
- Bruma's own post texture instead of SMIM's: add a second replacement, `textures\architecture\farmhouse\WoodPost02`
  -> `textures\bscyrodiil\architecture\bruma\brumawoodpost02` (covers the normal map too). Not done: the UV fit on
  SMIM's post is unverified.

## Repository layout

```
build.py              Build and checks
src/plugin/           The plugin as Spriggit YAML (one override of BSHeartland 003AB2)
inputs.sha256         Hashes of the input files this was written against
release.toml          Archive contents and release targets (workspace tools/mod-release)
README.md             What the patch does, install, credits
BUILDING.md           How to build from source
LICENSE               MIT, for the code and documentation
inputs/               Your copies of the original files (not tracked)
build/, dist/         Generated (not tracked)
backups/              Local snapshots (not tracked)
```
