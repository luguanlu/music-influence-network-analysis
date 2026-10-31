"""Build weighted music-influence edges and rank artists by combined influence.

The weighting rule follows the original course-project implementation:
cross-genre links receive twice the base weight, and the weight increases with
the gap between the artists' recorded active-start years. A link where the
follower predates the influencer receives an amplified time factor.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "influencer_id",
    "influencer_name",
    "influencer_main_genre",
    "influencer_active_start",
    "follower_id",
    "follower_name",
    "follower_main_genre",
    "follower_active_start",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create weighted music-influence edges and artist scores."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/influence_data.csv"),
        help="CSV file containing influencer-follower relationships.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for weighted_edges.csv and influence_scores.csv.",
    )
    return parser.parse_args()


def edge_weight(row: pd.Series) -> float:
    """Compute the original project weight for one influence relationship."""
    year_gap = row["follower_active_start"] - row["influencer_active_start"]
    genre_multiplier = (
        2.0
        if row["follower_main_genre"] != row["influencer_main_genre"]
        else 1.0
    )
    time_factor = 1.4 * abs(year_gap) if year_gap < 0 else year_gap
    return genre_multiplier * math.exp(time_factor / 80.0)


def main() -> None:
    args = parse_args()
    influence = pd.read_csv(args.input)

    missing = REQUIRED_COLUMNS.difference(influence.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Input data is missing required columns: {missing_text}")

    influence = influence.dropna(subset=REQUIRED_COLUMNS).copy()
    influence["weight"] = influence.apply(edge_weight, axis=1)

    edges = influence[
        [
            "influencer_id",
            "influencer_name",
            "influencer_main_genre",
            "follower_id",
            "follower_name",
            "follower_main_genre",
            "weight",
        ]
    ].sort_values("weight", ascending=False)

    direct_scores = influence.groupby("influencer_id")["weight"].sum()
    downstream_scores = (
        influence.assign(follower_direct_score=influence["follower_id"].map(direct_scores))
        .groupby("influencer_id")["follower_direct_score"]
        .sum()
        .fillna(0.0)
    )

    artists = pd.concat(
        [
            influence[
                ["influencer_id", "influencer_name", "influencer_main_genre"]
            ].rename(
                columns={
                    "influencer_id": "artist_id",
                    "influencer_name": "artist_name",
                    "influencer_main_genre": "main_genre",
                }
            ),
            influence[
                ["follower_id", "follower_name", "follower_main_genre"]
            ].rename(
                columns={
                    "follower_id": "artist_id",
                    "follower_name": "artist_name",
                    "follower_main_genre": "main_genre",
                }
            ),
        ],
        ignore_index=True,
    ).drop_duplicates("artist_id")

    artists["direct_influence_score"] = artists["artist_id"].map(direct_scores).fillna(0.0)
    artists["downstream_influence_score"] = artists["artist_id"].map(downstream_scores).fillna(0.0)
    artists["combined_influence_score"] = (
        artists["direct_influence_score"] + artists["downstream_influence_score"]
    )
    artists = artists.sort_values("combined_influence_score", ascending=False)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    edges.to_csv(args.output_dir / "weighted_edges.csv", index=False)
    artists.to_csv(args.output_dir / "influence_scores.csv", index=False)

    print(f"Processed {len(influence):,} influence relationships.")
    print(f"Wrote {args.output_dir / 'weighted_edges.csv'}")
    print(f"Wrote {args.output_dir / 'influence_scores.csv'}")
    print("Top 10 artists by combined influence score:")
    print(artists[["artist_name", "combined_influence_score"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
