import json
import sys
from pathlib import Path

import pandas as pd


FINAL_STATUSES = {"решена", "закрыта"}
OPEN_STATUSES = {"новая", "в работе"}


def _comments_count(value: str) -> int:
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return 0
    return len(parsed) if isinstance(parsed, list) else 0


def load_raw(raw_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        "users": pd.read_csv(raw_dir / "users.csv"),
        "categories": pd.read_csv(raw_dir / "categories.csv"),
        "support_staff": pd.read_csv(raw_dir / "support_staff.csv"),
        "tickets": pd.read_csv(raw_dir / "tickets.csv"),
    }


def transform(raw: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tickets = raw["tickets"].copy()
    users = raw["users"][["user_id", "full_name", "level"]].rename(
        columns={"full_name": "user_full_name", "level": "user_level"}
    )
    categories = raw["categories"][["category_id", "name"]].rename(columns={"name": "category"})
    staff = raw["support_staff"][["staff_id", "full_name", "department"]].rename(
        columns={"full_name": "staff_full_name"}
    )

    tickets["created_at"] = pd.to_datetime(tickets["created_at"])
    tickets["updated_at"] = pd.to_datetime(tickets["updated_at"])
    tickets["resolved_at"] = pd.to_datetime(tickets["resolved_at"], errors="coerce")
    tickets["staff_id"] = pd.to_numeric(tickets["staff_id"], errors="coerce")
    tickets["comments_count"] = tickets["comments_json"].apply(_comments_count)
    tickets["is_final_status"] = tickets["status"].isin(FINAL_STATUSES)

    tickets["resolution_time"] = tickets["resolved_at"] - tickets["created_at"]
    tickets["resolution_hours"] = tickets["resolution_time"].dt.total_seconds() / 3600
    tickets.loc[~tickets["is_final_status"], "resolution_hours"] = pd.NA

    enriched = (
        tickets.merge(users, on="user_id", how="left")
        .merge(categories, on="category_id", how="left")
        .merge(staff, on="staff_id", how="left")
    )
    return enriched


def create_support_kpi(enriched: pd.DataFrame, staff_df: pd.DataFrame) -> pd.DataFrame:
    grouped = enriched.groupby("staff_id", dropna=True).agg(
        tickets_resolved=("is_final_status", "sum"),
        avg_resolution_time_hours=("resolution_hours", "mean"),
        backlog=("status", lambda values: values.isin(OPEN_STATUSES).sum()),
    )

    support_kpi = (
        staff_df[["staff_id", "full_name"]]
        .merge(grouped, on="staff_id", how="left")
        .fillna({"tickets_resolved": 0, "backlog": 0})
    )
    support_kpi["tickets_resolved"] = support_kpi["tickets_resolved"].astype(int)
    support_kpi["backlog"] = support_kpi["backlog"].astype(int)
    support_kpi["avg_resolution_time_hours"] = support_kpi["avg_resolution_time_hours"].round(2)
    return support_kpi


def create_ticket_stats(enriched: pd.DataFrame) -> pd.DataFrame:
    ticket_stats = (
        enriched.groupby(["category", "priority"], dropna=False)
        .agg(
            avg_resolution_time=("resolution_hours", "mean"),
            total_tickets=("ticket_id", "count"),
        )
        .reset_index()
    )
    ticket_stats["avg_resolution_time"] = ticket_stats["avg_resolution_time"].round(2)
    return ticket_stats.sort_values(["category", "priority"]).reset_index(drop=True)


def run_transform(raw_dir: Path, stg_dir: Path) -> pd.DataFrame:
    stg_dir.mkdir(parents=True, exist_ok=True)
    raw = load_raw(raw_dir)
    enriched = transform(raw)
    enriched.to_csv(stg_dir / "ticket_enriched.csv", index=False)
    return enriched


def run_create_marts(raw_dir: Path, stg_dir: Path, mart_dir: Path) -> dict[str, pd.DataFrame]:
    mart_dir.mkdir(parents=True, exist_ok=True)
    raw = load_raw(raw_dir)
    enriched_path = stg_dir / "ticket_enriched.csv"
    if enriched_path.exists():
        enriched = pd.read_csv(enriched_path)
    else:
        enriched = transform(raw)

    support_kpi = create_support_kpi(enriched, raw["support_staff"])
    ticket_stats = create_ticket_stats(enriched)

    support_kpi.to_csv(mart_dir / "support_kpi.csv", index=False)
    ticket_stats.to_csv(mart_dir / "ticket_stats.csv", index=False)

    return {
        "support_kpi": support_kpi,
        "ticket_stats": ticket_stats,
    }


def create_all_marts(raw_dir: Path, stg_dir: Path, mart_dir: Path) -> dict[str, pd.DataFrame]:
    enriched = run_transform(raw_dir, stg_dir)
    marts = run_create_marts(raw_dir, stg_dir, mart_dir)
    return {"ticket_enriched": enriched, **marts}


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parents[1]
    raw_dir = project_dir / "data" / "raw"
    stg_dir = project_dir / "data" / "stg"
    mart_dir = project_dir / "data" / "mart"

    command = sys.argv[1] if len(sys.argv) > 1 else "all"
    if command == "transform":
        run_transform(raw_dir, stg_dir)
    elif command == "marts":
        run_create_marts(raw_dir, stg_dir, mart_dir)
    elif command == "all":
        create_all_marts(raw_dir, stg_dir, mart_dir)
    else:
        raise SystemExit(f"Unknown command: {command}")
