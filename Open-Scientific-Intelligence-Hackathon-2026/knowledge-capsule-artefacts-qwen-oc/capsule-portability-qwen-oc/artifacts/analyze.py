#!/usr/bin/env python3
"""Parse the NLCC PBE thioxanthone run logs; compute adiabatic E_T; compare to C1."""
import json
import re

ROOT = '/home/user/Work/osi-hackathon-2026/tx_nlcc'
HA_TO_EV = 27.211386248
EV_TO_KJ = 96.48533212
HA_TO_KJ = HA_TO_EV * EV_TO_KJ  # 2625.497 kJ/mol per Hartree


def final_eks(path):
    log = open(path).read()
    e = re.findall(r'EKS\s*:\s*([-+0-9.eEdD]+)', log)
    return float(e[-1].replace('D', 'e').replace('d', 'e')) if e else None


def log_lines(path, patterns):
    out = []
    for line in open(path):
        for pat in patterns:
            if pat in line:
                out.append(line.strip()[:120])
    return out


s0_log = f'{ROOT}/runs/s0/log-tx_S0_pbe_nlcc_at_S0pbe.yaml'
t1_log = f'{ROOT}/runs/t1/log-tx_T1_pbe_nlcc_at_T1pbe.yaml'

s0 = final_eks(s0_log)
t1 = final_eks(t1_log)
et_ha = t1 - s0
result = {
    'calculation': 'thioxanthone adiabatic Delta-SCF E_T, PBE, hgrid 0.35, rmult (6,9), '
                   'at C1 PBE-optimized S0/T1 geometries (no re-optimisation)',
    'psppar': {'C': 'NLCC (SS, HGH-K+NLCC, Saha 2015)',
               'H': 'NLCC (SS set)',
               'O': 'NLCC (SS, HGH-K+NLCC, Saha 2015)',
               'S': 'Krack PBE HGH-K (capsule C1; no NLCC in SS set)'},
    'E_S0_ha': s0,
    'E_T1_ha': t1,
    'E_T_ha': et_ha,
    'E_T_eV': et_ha * HA_TO_EV,
    'E_T_kJ_mol': et_ha * HA_TO_KJ,
    'C1_PBE_reference_ha': {'S0': -104.958932176445, 'T1': -104.868778644431,
                            'E_T_kJ_mol': 236.70},
    'delta_vs_C1_kJ_mol': et_ha * HA_TO_KJ - 236.70,
    't1_magnetization_lines': log_lines(t1_log, ['agnetization'])[:4],
    'xc_warning_lines_s0': log_lines(s0_log, ['different XC', 'XC of'])[:4],
}
with open(f'{ROOT}/result.json', 'w') as fh:
    fh.write(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
