#!/usr/bin/env python3
"""Build "Bruma Signs SMIM Patch" on the current SMIM SE meshes.

The 2017 patch (Nexus 10924) ships LE-format (user_version_2 83, NiTriShape) copies of an old SMIM. This copies
SMIM SE 2.08's own SSE meshes (BSTriShape) and swaps only the sign-face texture for Bruma's, with AutoMod
`nif replace-textures`. The ESP (one MSTT override of BSHeartland 003AB2, CYRSignSnowStoneRest: alternate texture on
3D index 1 of SMIM's SignWindpeakInn01) is still right for SMIM SE 2.08 and is copied unchanged.

Inputs: see BUILDING.md; `inputs.sha256` pins them. Output: build/ (packaged by release.py, see release.toml).
Needs the Skyrim AI toolkit's AutoMod wrapper with nif-tool (SKYRIM_TOOLKIT, or a skyrim-agents-toolkit clone next to this repo or a parent folder).

Usage: python3 build.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
BUILD = HERE / "build"
TOOLKIT_REPO = "https://github.com/kxgcayh/skyrim-agents-toolkit"


def find_toolkit():
    """SKYRIM_TOOLKIT if set, else a skyrim-agents-toolkit or skyrim-ai-toolkit folder next to this repo or a parent folder."""
    if os.environ.get("SKYRIM_TOOLKIT"):
        return Path(os.environ["SKYRIM_TOOLKIT"])
    for folder in Path(__file__).resolve().parents:
        for name in ("skyrim-agents-toolkit", "skyrim-ai-toolkit"):
            if (folder / name / "tools").is_dir():
                return folder / name
    sys.exit(f"Skyrim AI toolkit not found: clone {TOOLKIT_REPO} next to this repo or set SKYRIM_TOOLKIT.")
OUT_REL = "meshes/bscyrodiil/clutter/signage/bruma"
BRUMA_TEX = r"textures\bscyrodiil\clutter\signage\bruma"
ESP = "SMIM-Bruma-Patch.esp"

INN = ("signnightgateinn01.nif", r"textures\clutter\signage\inns\SignNightgateInn01.dds")
RIFTEN = ("signrtbeeandbarb01.nif", r"textures\clutter\signage\riften\SignRTBeeandBarb01.dds")
# output mesh -> (SMIM base, Bruma sign texture); the base shapes match the 2017 meshes one for one
SIGNS = {
    "signbrumaacutabove01.nif": (INN, "signacutabove01.dds"),
    "signbrumajerallviewinn01.nif": (INN, "signjerallviewinn01.dds"),
    "signbrumarestfulwatchman01.nif": (INN, "signrestfulwatchman01.dds"),
    "signbrumafightersguild01.nif": (RIFTEN, "signfightersguild01.dds"),
    "signbrumaicewindtraders01.nif": (RIFTEN, "signicewindtraders01.dds"),
    "signbrumanorthernarms01.nif": (RIFTEN, "signnorthernarms01.dds"),
    "signbrumasynod01.nif": (RIFTEN, "signsynod01.dds"),
}


def check_inputs():
    bad = []
    for line in (HERE / "inputs.sha256").read_text().splitlines():
        want, name = line.split(None, 1)
        p = INPUTS / name.strip()
        if not p.is_file():
            bad.append(f"missing: inputs/{name.strip()}")
        elif hashlib.sha256(p.read_bytes()).hexdigest() != want:
            bad.append(f"different file (not the version this was written against): inputs/{name.strip()}")
    if bad:
        sys.exit("Inputs do not match inputs.sha256 (see BUILDING.md):\n  " + "\n  ".join(bad))


def automod(*args):
    r = subprocess.run(["bash", str(find_toolkit() / "tools/automod-cli.sh"), "nif", *args, "--json"],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"automod nif {args[0]} gave no JSON:\n{r.stdout}\n{r.stderr}")
    if not d.get("success"):
        sys.exit(f"automod nif {args[0]} failed: {d}")
    return d["result"]["output"]


def main():
    check_inputs()
    if BUILD.exists():
        shutil.rmtree(BUILD)
    out = BUILD / OUT_REL
    out.mkdir(parents=True)
    for name, ((base, old_tex), new_tex) in SIGNS.items():
        dst = out / name
        shutil.copyfile(INPUTS / base, dst)
        new = f"{BRUMA_TEX}\\{new_tex}"
        automod("replace-textures", str(dst), "--old", old_tex, "--new", new)
        (out / (name + ".bak")).unlink(missing_ok=True)
        tex = automod("list-textures", str(dst)).lower()
        assert new.lower() in tex and old_tex.lower() not in tex, (name, tex)
        assert "1 passed, 0 failed" in automod("verify", str(dst)), name
    shutil.copyfile(INPUTS / ESP, BUILD / ESP)
    for p in sorted(BUILD.rglob("*")):
        if p.is_file():
            print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.stat().st_size, p.relative_to(BUILD))


if __name__ == "__main__":
    main()
