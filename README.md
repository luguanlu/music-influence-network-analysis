# Music Influence Network Analysis

This project models relationships of musical influence as a weighted directed network. Each artist is a node, and each reported influence relationship is an edge from an influencer to a follower. The analysis combines genre distance and the artists' recorded active-start years to weight each edge, then ranks artists using direct and downstream influence scores.

It was developed as a social network analysis course project and is accompanied by the original report in [`docs/`](docs/music-influence-network-report.pdf).

## What the project answers

- Which artists have the largest combined influence scores in the observed network?
- How do within-genre and cross-genre relationships contribute to edge strength?
- How does the timing of artists' careers affect the model's influence weights?
- Does the resulting influence distribution exhibit a scale-free pattern?

## Repository structure

```text
data/influence_data.csv              Input artist-influence relationships
src/analyze_influence.py             Reproducible scoring pipeline
docs/music-influence-network-report.pdf  Original project report
outputs/                             Generated edge and artist-score tables
```

## Data

`data/influence_data.csv` contains 42,770 influencer-follower relationships. Every record identifies an influencer and follower, their main genres, and their recorded active-start years.

The course report describes the dataset as a collection of musical-influence relationships sourced from AllMusic. These links represent observed or reported influence relationships and should not be interpreted as causal proof.

## Method

For an influence edge from artist `i` to artist `j`, the script computes a weight using the original project rule:

```text
weight = genre_multiplier * exp(time_factor / 80)
```

- `genre_multiplier` is `2` for cross-genre relationships and `1` for within-genre relationships.
- `time_factor` is the active-start-year gap when the follower starts later. When the follower starts earlier, the absolute gap is multiplied by `1.4`.

For each artist, the pipeline reports:

- `direct_influence_score`: sum of weights on the artist's outgoing influence edges.
- `downstream_influence_score`: sum of the direct scores of the artist's followers.
- `combined_influence_score`: direct plus downstream influence.

The report also discusses degree centrality, PageRank-inspired eigenvector centrality, maximum likelihood estimation, power-law fitting, and subnetwork analyses.

## Quick start

Requirements: Python 3.10 or later.

```bash
git clone https://github.com/luguanlu/music-influence-network-analysis.git
cd music-influence-network-analysis

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/analyze_influence.py
```

To use another dataset or output location:

```bash
python src/analyze_influence.py \
  --input path/to/influence_data.csv \
  --output-dir path/to/results
```

## Outputs

The command creates an ignored `outputs/` directory containing:

- `weighted_edges.csv`: every influence edge and its computed weight.
- `influence_scores.csv`: artists ranked by direct, downstream, and combined influence scores.

## Reproducibility notes

The command-line script is a portable version of the original course-project code. It preserves the project's scoring rule while replacing the original Google Drive-specific input path and Chinese output filenames with explicit command-line paths and English filenames.

## License

No license has been selected for this project. Do not redistribute the code or data without the owner's permission.
