#!/usr/bin/env python3
"""Build thioxanthone PBE single-point inputs at the C1 PBE-optimized geometries,
using the NLCC pseudopotential class where available.

Same calculation as capsule C1 Phase 1 (thioxanthone, PBE, hgrid 0.35 bohr,
rmult (6,9), gnrm_cv 1e-5, free BC, T1 = nspin 2 / mpol 2), at the PBE-optimized
S0 and T1 geometries (no re-optimisation). Only the pseudopotential class is
changed, per instruction:

  Step 1: set the same psppar as capsule C1 (Krack PBE HGH-K, XC 11) for all
          elements C/H/O/S  (C1/bigdft/psppar/psppar.<el>.yaml).
  Step 2: set the NLCC psppar (PyBigDFT Database SS set, type 'HGH-K + NLCC',
          Saha 2015). This overwrites the C1 psppar for every element where
          NLCC is available (C, H, O). S is missing from the SS set and keeps
          the C1 Krack PBE psppar.

Templates: C1/bigdft/inputs/tx_{S0,T1}_pbe0_at_{S0,T1}pbe.yaml — C1's
Phase 1b single-point inputs, which already contain the PBE-optimized
geometries and no geopt section. ixc is switched PBE0 -> PBE.
"""
import os
import sys

import yaml

ROOT = '/home/user/Work/osi-hackathon-2026'
C1_PSPPAR = os.path.join(ROOT, 'C1', 'bigdft', 'psppar')
NLCC_DIR = '/home/user/Work/build/PyBigDFT/lib/BigDFT/Database/psppar/SS'
TEMPLATES = os.path.join(ROOT, 'C1', 'bigdft', 'inputs')
OUT = os.path.join(ROOT, 'tx_nlcc', 'inputs')
ELEMENTS = ['C', 'H', 'O', 'S']


def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


def merge_psppar():
    """Two-step psppar setup: C1 first (all elements), NLCC second (overwrites available)."""
    psp = {}
    for el in ELEMENTS:  # step 1: same psppar as capsule C1
        psp[el] = load_yaml(os.path.join(C1_PSPPAR, f'psppar.{el}.yaml'))
    for el in ELEMENTS:  # step 2: NLCC, overwrites where available
        path = os.path.join(NLCC_DIR, f'psppar.{el}.yaml')
        if os.path.exists(path):
            psp[el] = load_yaml(path)
        else:
            print(f'  note: no NLCC psppar for {el}; keeping capsule C1 Krack PBE', flush=True)
    return psp


def count_atoms(positions):
    counts = {}
    for pos in positions:
        (el, _) = next(iter(pos.items()))
        counts[el] = counts.get(el, 0) + 1
    return counts


def build(name, template, dft_overrides):
    tpl = load_yaml(os.path.join(TEMPLATES, f'{template}.yaml'))
    tpl['dft'].update(dft_overrides)
    psp = merge_psppar()
    for key in [k for k in tpl if k.startswith('psppar.')]:
        del tpl[key]
    for el in ELEMENTS:
        tpl[f'psppar.{el}'] = psp[el]
    os.makedirs(OUT, exist_ok=True)
    outpath = os.path.join(OUT, f'{name}.yaml')
    with open(outpath, 'w') as fh:
        yaml.safe_dump(tpl, fh, sort_keys=False)
    counts = count_atoms(tpl['posinp']['positions'])
    ne = sum(psp[el]['No. of Electrons'] * counts.get(el, 0) for el in ELEMENTS)
    assert ne == 72, f'{name}: expected 72 electrons, got {ne}'
    print(f'{name}: atoms={counts} electrons={ne} -> {outpath}', flush=True)
    return outpath


def main():
    print('PSP merge (C1 Krack PBE first, NLCC SS second):', flush=True)
    psp = merge_psppar()
    for el in ELEMENTS:
        print(f'  {el}: type={psp[el].get("Pseudopotential type")!r} '
              f'xc={psp[el].get("Pseudopotential XC")!r}', flush=True)
    common = dict(ixc='PBE')
    build('tx_S0_pbe_nlcc_at_S0pbe', 'tx_S0_pbe0_at_S0pbe', common)
    build('tx_T1_pbe_nlcc_at_T1pbe', 'tx_T1_pbe0_at_T1pbe',
          dict(common, nspin=2, mpol=2))
    print('done', flush=True)


if __name__ == '__main__':
    sys.exit(main())
