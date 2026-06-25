from pathlib import Path
import shutil

from src.create_marts import create_all_marts
from src.generate_data import generate_all
from src.visualize import create_all_visualizations


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    raw_dir = project_dir / "data" / "raw"
    stg_dir = project_dir / "data" / "stg"
    mart_dir = project_dir / "data" / "mart"
    figures_dir = project_dir / "outputs" / "figures"

    for path in (raw_dir, stg_dir, mart_dir, figures_dir):
        if path.exists():
            shutil.rmtree(path)

    generate_all(raw_dir)
    create_all_marts(raw_dir, stg_dir, mart_dir)
    create_all_visualizations(stg_dir, mart_dir, figures_dir)

    print("Pipeline completed")
    print(f"Raw data: {raw_dir}")
    print(f"Staging: {stg_dir}")
    print(f"Marts: {mart_dir}")
    print(f"Figures: {figures_dir}")


if __name__ == "__main__":
    main()
