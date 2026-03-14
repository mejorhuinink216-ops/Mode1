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
    child_ratio,
    elder_ratio,
    labor_ratio,
    dependency_ratio,
)
from simulation import step, compute_yield_factor, compute_policy_effects


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


def load_policy() -> dict:
    root_dir = Path(__file__).resolve().parent.parent
    policy_path = root_dir / "data" / "policy.json"
    return load_json(policy_path)


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
        "reclaim_base_rate",
        "abandon_base_rate",
        "reclaim_food_pressure_sensitivity",
        "abandon_food_surplus_sensitivity",
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
        "reclaim_base_rate",
        "abandon_base_rate",
    ]

    for key in zero_one_keys:
        value = params[key]
        if not 0 <= value <= 1:
            raise ValueError(f"{key} 必须在 0 到 1 之间")

    if params["grain_need_per_person"] <= 0:
        raise ValueError("grain_need_per_person 必须大于 0")

    if params["optimal_labor_density"] <= 0:
        raise ValueError("optimal_labor_density 必须大于 0")

    if params["min_yield_factor"] <= 0:
        raise ValueError("min_yield_factor 必须大于 0")

    if params["max_yield_factor"] <= 0:
        raise ValueError("max_yield_factor 必须大于 0")

    non_negative_keys = [
        "famine_birth_scaler",
        "famine_child_death_multiplier",
        "famine_adult_death_multiplier",
        "famine_elder_death_multiplier",
        "labor_shortage_sensitivity",
        "labor_surplus_sensitivity",
        "reclaim_food_pressure_sensitivity",
        "abandon_food_surplus_sensitivity",
    ]

    for key in non_negative_keys:
        if params[key] < 0:
            raise ValueError(f"{key} 不能小于 0")

    if params["min_yield_factor"] > params["max_yield_factor"]:
        raise ValueError("min_yield_factor 不能大于 max_yield_factor")


def validate_policy(policy: dict) -> None:
    required_keys = [
        "tax_rate",
        "corvee_rate",
        "corvee_time_share",
        "corvee_wage_per_worker",
        "corvee_willingness_base",
        "corvee_wage_sensitivity",
        "corvee_efficiency",
    ]

    for key in required_keys:
        if key not in policy:
            raise ValueError(f"缺少政策参数: {key}")

    zero_one_keys = [
        "tax_rate",
        "corvee_rate",
        "corvee_time_share",
        "corvee_willingness_base",
        "corvee_efficiency",
    ]

    for key in zero_one_keys:
        value = policy[key]
        if not 0 <= value <= 1:
            raise ValueError(f"{key} 必须在 0 到 1 之间")

    non_negative_keys = [
        "corvee_wage_per_worker",
        "corvee_wage_sensitivity",
    ]

    for key in non_negative_keys:
        if policy[key] < 0:
            raise ValueError(f"{key} 不能小于 0")


def print_report(title: str, s: VillageState, params: dict, policy: dict) -> None:
    policy_effects = compute_policy_effects(s, params, policy)

    population = population_total(s)
    food_need = population * params["grain_need_per_person"]
    food_balance = policy_effects["available_grain"] - food_need
    food_ratio = policy_effects["available_grain"] / food_need if food_need > 0 else 1.0

    raw_labor_total = policy_effects["raw_labor_total"]
    effective_agri_labor = policy_effects["effective_agri_labor"]

    raw_labor_density = raw_labor_total / s.farmland_mu if s.farmland_mu > 0 else 0.0
    effective_labor_density = effective_agri_labor / s.farmland_mu if s.farmland_mu > 0 else 0.0

    raw_land_pressure_ratio = (
        raw_labor_density / params["optimal_labor_density"]
        if params["optimal_labor_density"] > 0
        else 1.0
    )
    effective_land_pressure_ratio = (
        effective_labor_density / params["optimal_labor_density"]
        if params["optimal_labor_density"] > 0
        else 1.0
    )

    yield_factor = compute_yield_factor(effective_labor_density, params)

    print("====", title, "====")
    print("year:", s.year)
    print("farmland_mu:", round(s.farmland_mu, 4))
    print("yield_per_mu:", round(s.yield_per_mu, 4))
    print("population_total:", population)
    print("male_total:", male_total(s))
    print("female_total:", female_total(s))
    print("children_total:", children_total(s))
    print("adult_total:", adult_total(s))
    print("elder_total:", elder_total(s))
    print("labor_male:", round(labor_male(s), 2))
    print("labor_female:", round(labor_female(s), 2))
    print("labor_total:", round(raw_labor_total, 2))
    print("raw_labor_density:", round(raw_labor_density, 4))
    print("effective_agri_labor:", round(effective_agri_labor, 2))
    print("effective_labor_density:", round(effective_labor_density, 4))
    print("raw_land_pressure_ratio:", round(raw_land_pressure_ratio, 4))
    print("effective_land_pressure_ratio:", round(effective_land_pressure_ratio, 4))
    print("yield_factor_from_effective_labor:", round(yield_factor, 4))
    print("gross_output:", round(policy_effects["gross_output"], 2))
    print("tax_grain:", round(policy_effects["tax_grain"], 2))
    print("corvee_target_labor:", round(policy_effects["corvee_target_labor"], 2))
    print("corvee_wage_adequacy:", round(policy_effects["wage_adequacy"], 4))
    print("corvee_participation:", round(policy_effects["corvee_participation"], 4))
    print("actual_corvee_labor:", round(policy_effects["actual_corvee_labor"], 2))
    print("corvee_agri_labor_loss:", round(policy_effects["corvee_agri_labor_loss"], 2))
    print("corvee_wage_grain:", round(policy_effects["corvee_wage_grain"], 2))
    print("corvee_effective_service:", round(policy_effects["corvee_effective_service"], 2))
    print("available_grain:", round(policy_effects["available_grain"], 2))
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
    policy = load_policy()

    validate_state(state)
    validate_params(params)
    validate_policy(policy)

    next_state = step(state, params, policy)
    validate_state(next_state)

    print_report("current_state", state, params, policy)
    print_report("next_state", next_state, params, policy)


if __name__ == "__main__":
    main()
