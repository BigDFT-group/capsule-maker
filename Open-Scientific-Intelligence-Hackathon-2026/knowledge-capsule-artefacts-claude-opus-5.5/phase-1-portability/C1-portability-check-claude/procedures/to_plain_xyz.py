"""Strip extended XYZ (extra per-atom columns) to plain 4-column XYZ for strict readers such as BigDFT.

Coordinate tokens are copied verbatim, so no precision is lost or reformatted.
Usage: python to_plain_xyz.py IN.xyz OUT.xyz "comment"
"""
import sys


def plain(src, dst, comment):
    lines = open(src).read().splitlines()
    n = int(lines[0])
    rows = [l.split()[:4] for l in lines[2:2 + n]]
    assert len(rows) == n and all(len(r) == 4 for r in rows), src
    with open(dst, "w") as f:
        f.write(f"{n}\n{comment}\n" + "".join(f"{e:<2s} {x:>16s} {y:>16s} {z:>16s}\n" for e, x, y, z in rows))


if __name__ == "__main__":
    plain(*sys.argv[1:4])
