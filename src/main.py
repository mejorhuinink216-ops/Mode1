import json
from pathlib import Path

from state import VillageState
from metrics import (
    population_total,
    male_total,
    female_total,
    children_total,
    adult_total,
    elder_total,
    labor_male,
    labor_female,
    labor_total,
    total_output,
    child_ratio,
    elder_ratio,
    labor_ratio,
    dependency_ratio,
)


def load_state() -> VillageState:
    root_dir = Path(__file__).resolve().parent.parent
    data_path = root_dir / "data" / "initial_state.json"

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return VillageState(**data)


def validate_state(s: VillageState) -> None:
    number_fields = [
        s.farmland_mu,
        s.yield_per_mu,
        s.children_male,
        s.children_female,
        s.adult_male,
        s.adult_female,
        s.elder_male,
        s.elder_female,
    ]

    for value in number_fields:
        if value < 0:
            raise ValueError("状态中存在负数，数据非法")

    if not 0 <= s.male_labor_participation <= 1:
        raise ValueError("male_labor_participation 必须在 0 到 1 之间")

    if not 0 <= s.female_labor_participation <= 1:
        raise ValueError("female_labor_participation 必须在 0 到 1 之间")


def print_report(s: VillageState) -> None:
    print("year:", s.year)
    print("farmland_mu:", s.farmland_mu)
    print("yield_per_mu:", s.yield_per_mu)
    print("population_total:", population_total(s))
    print("male_total:", male_total(s))
    print("female_total:", female_total(s))
    print("children_total:", children_total(s))
    print("adult_total:", adult_total(s))
    print("elder_total:", elder_total(s))
    print("labor_male:", round(labor_male(s), 2))
    print("labor_female:", round(labor_female(s), 2))
    print("labor_total:", round(labor_total(s), 2))
    print("total_output:", round(total_output(s), 2))
    print("child_ratio:", round(child_ratio(s), 4))
    print("elder_ratio:", round(elder_ratio(s), 4))
    print("labor_ratio:", round(labor_ratio(s), 4))
    print("dependency_ratio:", round(dependency_ratio(s), 4))


def main():
    state = load_state()
    validate_state(state)
    print_report(state)


if __name__ == "__main__":
    main()
