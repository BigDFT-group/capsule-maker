# Agentified paper: Irle *et al.* 2026 ("Robert 2026")

Repository: <https://github.com/TengxiangLii/P2A-Robert-2026> (single commit `bc704b2`)

## The paper

> Irle, R. M., Lazzarini, I., Hagn, F., Zacharias, M. & Bach, T. Photocatalytic
> tetrapeptides for enantioselective visible light-induced transformations.
> *Nature Synthesis* (2026). <https://doi.org/10.1038/s44160-026-01173-7>

The authors are at TU München and Helmholtz Munich. The paper was published online
on 12 October 2026 under CC BY 4.0.

The study introduces a small tetrapeptide photocatalyst (**6a**, < 750 Da). It has
an N-terminal pyroglutamic acid (Pga) that binds lactam substrates through hydrogen
bonds, and a C-terminal thioxanthone amino acid (pTxa) that absorbs visible light and
passes the energy to the bound substrate by triplet energy transfer. The two are
joined by a two-residue backbone. The catalyst is used for:

- photochemical deracemization of allenes (*rac*-**5**) and olefins (*rac*-**8**) (Fig. 4);
- enantioselective intramolecular [2 + 2] photocycloaddition of quinolones **9** → **10**
  (425 nm, −70 °C, CH₂Cl₂) (Fig. 5).

The structure of the catalyst–substrate complex was determined by NMR. MD
simulations (Fig. 3) show that the chiral backbone matters for substrate binding.

## What "agentified" means here

The repo is an **agent skill** generated with Paper2Agent's Paper2Skill pipeline.
The paper has no code repository, so this is a **paper-only skill**. It has **no MCP
server and no executable tools**. An agent uses it to find and cite evidence in the
paper and its data. It cannot run or reproduce the chemistry.

Sources covered:

- the main article (8 pages), including source data for Figs. 2 and 3;
- the Supplementary Information (200 pages);
- metadata for the Chemotion Repository collection
  [RMI_2026-01-30](https://doi.org/10.14272/collection/RMI_2026-01-30).

## Layout

```text
irle2026-tetrapeptide-photocatalysis-paper/   the skill (copy this directory)
├── SKILL.md              entry point: how to search and cite
├── references/
│   ├── index.md          navigation table: heading → what is there
│   ├── paper.md          main article (~260 lines)
│   └── supplement.md     SI S1–S15 + Chemotion notes (~2300 lines)
└── assets/
    ├── figure/           Figs. 1–5 (JPEG)
    ├── table/            Fig. 2 screening table, source data Figs. 2–3 (CSV)
    ├── supp_figs/        216 images: Figs. S1–S10, schemes, structures, NMR, HPLC
    └── supp_table/       Tables S1–S4; Chemotion reactions/molecules/analyses (CSV)
tools/crawl_chemotion.py  rebuilds the Chemotion CSVs from DataCite (metadata only)
```

## How an agent uses it

`SKILL.md` tells the agent to:

1. open `references/index.md` and choose the document and section;
2. find the exact heading with bounded `rg -n -F` / `rg -n -i -m 8` searches;
3. read 30–60 line passages with `sed -n`, not whole files;
4. open only the figure JPEG or CSV it needs;
5. cite the section, figure, table, or CSV row; keep reported findings apart from
   interpretation; mention extraction limitations.

Install: copy `irle2026-tetrapeptide-photocatalysis-paper/` into `~/.claude/skills/`
(or a project's `.claude/skills/`).

Example questions it can answer:

- Which catalysts were screened in Fig. 2, and what e.r. did each give?
- Under what conditions does **6a** deracemize allene *rac*-**5a**?
- What are the characterization data (δ, *J*, HRMS, [α]D) for product **10c**?
- Which Chemotion DOIs hold the analyses for a given molecule?

## Verification status

The upstream README says every page of both PDFs was reviewed by an agent against
the source. The bundle passes `paper_bundle.py verify --strict` with status
`reviewed_with_limitations`. That check covers text and crop fidelity and file
integrity. **It does not certify the science.**

## Known limitations (from upstream)

- Chemotion data is **metadata only** (72 reactions, 82 molecules, 256 analysis
  datasets). Raw spectra are not included; fetch them by DOI.
- NMR spectra and HPLC traces are images only. Written characterization data is
  transcribed as text.
- Some Fig. 4/5 values exist only in the figure images (e.g. the catalyst **6a** runs
  for **5c**–**5f**).
- Fig. 2 source-data defect: the "Normalized Emission" (steady state, rt) column
  normalizes the wavelength instead of the intensity. The values are kept as supplied.
- SI citation numbers look shifted by one against the main reference list, and
  [47] has no entry. Match citations by author, not by number.
- Quinolone labels **9a**–**9e** are used inconsistently in the SI.
- Notation is mixed (`1H-NMR` vs `¹H-NMR`, `<sup>3</sup>J` vs `³J`). Search for both forms.

## License

The article and SI are © the authors under CC BY 4.0. The skill's text, figures and
tables are derived from them, so cite the original article. Chemotion metadata
comes from the Chemotion Repository via DataCite.
