#!/usr/bin/env python3
"""Build "Bruma Signs SMIM Patch" on the current SMIM SE meshes.

The 2017 patch (Nexus 10924) ships LE-format (user_version_2 83, NiTriShape) copies of an old SMIM. This copies
SMIM SE 2.08's own SSE meshes (BSTriShape) and swaps only the sign-face texture for Bruma's, with AutoMod
`nif replace-textures`. The ESP (one MSTT override of BSHeartland 003AB2, CYRSignSnowStoneRest: alternate texture on
3D index 1 of SMIM's SignWindpeakInn01) is built from src/plugin (Bruma 2.0.0's record), ESL-flagged.

Inputs: see BUILDING.md; `inputs.sha256` pins them. Output: build/ (packaged by release.py, see release.toml).
Needs the Skyrim AI toolkit's AutoMod wrapper with nif-tool (SKYRIM_TOOLKIT, or a skyrim-agents-toolkit clone next to this repo or a parent folder).

Usage: python3 build.py
"""
import hashlib
import json
import os
import shutil
import struct
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


def spriggit(verb, src, dst, *more):
    r = subprocess.run(["bash", str(find_toolkit() / "tools/spriggit-cli.sh"), verb, "--InputPath", str(src),
                        "--OutputPath", str(dst), *more], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"spriggit {verb} failed:\n{r.stdout}\n{r.stderr}")


def check_plugin(b):  # independent of Spriggit: ESL flag, masters, one MSTT override of BSHeartland 003AB2
    assert b[:4] == b"TES4", "not a plugin"
    size, flags = struct.unpack_from("<I", b, 4)[0], struct.unpack_from("<I", b, 8)[0]
    assert flags & 0x200, "ESL flag missing"
    d, i, masters = b[24:24 + size], 0, []
    while i < len(d):
        t, n = d[i:i + 4], struct.unpack_from("<H", d, i + 4)[0]
        if t == b"MAST":
            masters.append(d[i + 6:i + 6 + n].rstrip(b"\0").decode("cp1252"))
        i += 6 + n
    assert masters == ["Skyrim.esm", "BSHeartland.esm"], masters
    pos, recs = 24 + size, []
    while pos < len(b):  # GRUP -> records
        gsize = struct.unpack_from("<I", b, pos + 4)[0]
        q = pos + 24
        while q < pos + gsize:
            rsize, fid = struct.unpack_from("<I", b, q + 4)[0], struct.unpack_from("<I", b, q + 12)[0]
            recs.append((b[q:q + 4], fid))
            q += 24 + rsize
        pos += gsize
    assert recs == [(b"MSTT", 0x01003AB2)], recs  # master index 1 = BSHeartland.esm: an override, no new form


def build_plugin():
    """SMIM-Bruma-Patch.esp from src/plugin (Bruma 2.0.0's record with the alternate texture on 3D index 1),
    round-tripped through Spriggit and checked by check_plugin."""
    esp = BUILD / ESP
    spriggit("deserialize", HERE / "src/plugin", esp)
    rt = BUILD / "rt"
    spriggit("serialize", esp, rt, "--GameRelease", "SkyrimSE", "--PackageName", "Spriggit.Yaml.Skyrim",
             "--PackageVersion", "0.41.0", "-u")
    for f in (HERE / "src/plugin").rglob("*.yaml"):
        assert (rt / f.relative_to(HERE / "src/plugin")).read_text() == f.read_text(), f"round trip changed {f.name}"
    shutil.rmtree(rt)
    check_plugin(esp.read_bytes())


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
    build_plugin()
    for p in sorted(BUILD.rglob("*")):
        if p.is_file():
            print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.stat().st_size, p.relative_to(BUILD))


if __name__ == "__main__":
    main()
