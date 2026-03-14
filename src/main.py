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
from simulation import step, compute_yield_factor


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state() -> VillageState:
    root_dir = Path(__file__).resolve().parent.parent
    data_path = root_dir / "data" / "initial_state.json"
    data = load_json(data_path)
    return VillageState(**data)


def load_params() -> dict:
    root_dir = Path(__file__).resolve().parent.parent
    params_path = root_dir / "data" / "params.json"
    return load_json(params_path)


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


def validate_params(params: dict) -> None:
    required_keys = [
        "birth_rate_per_adult_female",
        "child_death_rate",
        "adult_death_rate",
        "elder_death_rate",
        "male_birth_share",
        "grain_need_per_person",
        "famine_birth_scaler",
        "famine_child_death_multiplier",
        "famine_adult_death_multiplier",
        "famine_elder_death_multiplier",
        "optimal_labor_density",
        "labor_shortage_sensitivity",
        "labor_surplus_sensitivity",
        "min_yield_factor",
        "max_yield_factor",
    ]

    for key in required_keys:
        if key not in params:
            raise ValueError(f"缺少参数: {key}")

    zero_one_keys = [
        "birth_rate_per_adult_female",
        "child_death_rate",
        "adult_death_rate",
        "elder_death_rate",
        "male_birth_share",
        "min_yield_factor",
        "max_yield_factor",
    ]

    for key in zero_one_keys:
        value = params[key]
        if not 0 <= value <= 1:
            raise ValueError(f"{key} 必须在 0 到 1 之间")

    if params["grain_need_per_person"] <= 0:
        raise ValueError("grain_need_per_person 必须大于 0")

    if params["optimal_labor_density"] <= 0:
        raise ValueError("optimal_labor_density 必须大于 0")

    non_negative_keys = [
        "famine_birth_scaler",
        "famine_child_death_multiplier",
        "famine_adult_death_multiplier",
        "famine_elder_death_multiplier",
        "labor_shortage_sensitivity",
        "labor_surplus_sensitivity",
    ]

    for key in non_negative_keys:
        if params[key] < 0:
            raise ValueError(f"{key} 不能小于 0")

    if params["min_yield_factor"] > params["max_yield_factor"]:
        raise ValueError("min_yield_factor 不能大于 max_yield_factor")


def print_report(title: str, s: VillageState, params: dict) -> None:
    output = total_output(s)
    food_need = population_total(s) * params["grain_need_per_person"]
    food_balance = output - food_need
    food_ratio = output / food_need if food_need > 0 else 1.0
    labor_density = labor_total(s) / s.farmland_mu if s.farmland_mu > 0 else 0.0
    yield_factor = compute_yield_factor(labor_density, params)

    print("====", title, "====")
    print("year:", s.year)
    print("farmland_mu:", s.farmland_mu)
    print("yield_per_mu:", round(s.yield_per_mu, 4))
    print("population_total:", population_total(s))
    print("male_total:", male_total(s))
    print("female_total:", female_total(s))
    print("children_total:", children_total(s))
    print("adult_total:", adult_total(s))
    print("elder_total:", elder_total(s))
    print("labor_male:", round(labor_male(s), 2))
    print("labor_female:", round(labor_female(s), 2))
    print("labor_total:", round(labor_total(s), 2))
    print("labor_density:", round(labor_density, 4))
    print("yield_factor_from_labor:", round(yield_factor, 4))
    print("total_output:", round(output, 2))
    print("food_need:", round(food_need, 2))
    print("food_balance:", round(food_balance, 2))
    print("food_ratio:", round(food_ratio, 4))
    print("child_ratio:", round(child_ratio(s), 4))
    print("elder_ratio:", round(elder_ratio(s), 4))
    print("labor_ratio:", round(labor_ratio(s), 4))
    print("dependency_ratio:", round(dependency_ratio(s), 4))
    print()


def main():
    state = load_state()
    params = load_params()

    validate_state(state)
    validate_params(params)

    next_state = step(state, params)
    validate_state(next_state)

    print_report("current_state", state, params)
    print_report("next_state", next_state, params)


if __name__ == "__main__":
    main()
