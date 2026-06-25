from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


plt.rcParams["font.family"] = "DejaVu Sans"


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_avg_resolution_by_staff(support_kpi: pd.DataFrame, output_dir: Path) -> None:
    data = support_kpi.sort_values("avg_resolution_time_hours", ascending=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(data["full_name"], data["avg_resolution_time_hours"], color="#4C78A8")
    ax.set_title("Среднее время решения по сотрудникам")
    ax.set_xlabel("Часы")
    ax.set_ylabel("Сотрудник")
    _save(fig, output_dir / "avg_resolution_by_staff.png")


def plot_tickets_by_category(ticket_stats: pd.DataFrame, output_dir: Path) -> None:
    data = ticket_stats.groupby("category", as_index=False)["total_tickets"].sum().sort_values("total_tickets")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(data["category"], data["total_tickets"], color="#59A14F")
    ax.set_title("Количество заявок по категориям")
    ax.set_xlabel("Количество заявок")
    ax.set_ylabel("Категория")
    _save(fig, output_dir / "tickets_by_category.png")


def plot_ticket_creation_daily(enriched: pd.DataFrame, output_dir: Path) -> None:
    data = enriched.copy()
    data["created_day"] = pd.to_datetime(data["created_at"]).dt.date
    daily = data.groupby("created_day", as_index=False).size()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(daily["created_day"], daily["size"], color="#F28E2B", linewidth=1.8)
    ax.set_title("Динамика создания заявок по дням")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Количество заявок")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, output_dir / "ticket_creation_daily.png")


def plot_ticket_status_pie(enriched: pd.DataFrame, output_dir: Path) -> None:
    data = enriched["status"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(data.values, labels=data.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Распределение статусов заявок")
    _save(fig, output_dir / "ticket_status_pie.png")


def create_all_visualizations(stg_dir: Path, mart_dir: Path, output_dir: Path) -> None:
    enriched = pd.read_csv(stg_dir / "ticket_enriched.csv")
    support_kpi = pd.read_csv(mart_dir / "support_kpi.csv")
    ticket_stats = pd.read_csv(mart_dir / "ticket_stats.csv")

    plot_avg_resolution_by_staff(support_kpi, output_dir)
    plot_tickets_by_category(ticket_stats, output_dir)
    plot_ticket_creation_daily(enriched, output_dir)
    plot_ticket_status_pie(enriched, output_dir)


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parents[1]
    create_all_visualizations(
        project_dir / "data" / "stg",
        project_dir / "data" / "mart",
        project_dir / "outputs" / "figures",
    )
