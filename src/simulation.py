from state import VillageState
from metrics import population_total, total_output, labor_total


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def compute_yield_factor(labor_density: float, params: dict) -> float:
    optimal_labor_density = params["optimal_labor_density"]
    labor_shortage_sensitivity = params["labor_shortage_sensitivity"]
    labor_surplus_sensitivity = params["labor_surplus_sensitivity"]
    min_yield_factor = params["min_yield_factor"]
    max_yield_factor = params["max_yield_factor"]

    if optimal_labor_density <= 0:
        return 1.0

    relative_gap = (labor_density - optimal_labor_density) / optimal_labor_density

    if relative_gap < 0:
        factor = 1.0 + relative_gap * labor_shortage_sensitivity
    else:
        factor = 1.0 - relative_gap * labor_surplus_sensitivity

    return clamp(factor, min_yield_factor, max_yield_factor)


def step(state: VillageState, params: dict) -> VillageState:
    birth_rate = params["birth_rate_per_adult_female"]
    child_death_rate = params["child_death_rate"]
    adult_death_rate = params["adult_death_rate"]
    elder_death_rate = params["elder_death_rate"]
    male_birth_share = params["male_birth_share"]

    grain_need_per_person = params["grain_need_per_person"]
    famine_birth_scaler = params["famine_birth_scaler"]
    famine_child_death_multiplier = params["famine_child_death_multiplier"]
    famine_adult_death_multiplier = params["famine_adult_death_multiplier"]
    famine_elder_death_multiplier = params["famine_elder_death_multiplier"]

    current_population = population_total(state)
    current_output = total_output(state)
    current_food_need = current_population * grain_need_per_person

    if current_food_need <= 0:
        food_ratio = 1.0
    else:
        food_ratio = current_output / current_food_need

    shortage = max(0.0, 1.0 - food_ratio)

    effective_birth_rate = birth_rate * max(0.0, 1.0 - shortage * famine_birth_scaler)

    effective_child_death_rate = clamp(
        child_death_rate * (1.0 + shortage * famine_child_death_multiplier),
        0.0,
        1.0,
    )
    effective_adult_death_rate = clamp(
        adult_death_rate * (1.0 + shortage * famine_adult_death_multiplier),
        0.0,
        1.0,
    )
    effective_elder_death_rate = clamp(
        elder_death_rate * (1.0 + shortage * famine_elder_death_multiplier),
        0.0,
        1.0,
    )

    births_total = round(state.adult_female * effective_birth_rate)
    births_male = round(births_total * male_birth_share)
    births_female = births_total - births_male

    children_to_adult_male = state.children_male // 15
    children_to_adult_female = state.children_female // 15

    adult_to_elder_male = state.adult_male // 45
    adult_to_elder_female = state.adult_female // 45

    next_children_male_before_death = (
        state.children_male - children_to_adult_male + births_male
    )
    next_children_female_before_death = (
        state.children_female - children_to_adult_female + births_female
    )

    next_adult_male_before_death = (
        state.adult_male + children_to_adult_male - adult_to_elder_male
    )
    next_adult_female_before_death = (
        state.adult_female + children_to_adult_female - adult_to_elder_female
    )

    next_elder_male_before_death = state.elder_male + adult_to_elder_male
    next_elder_female_before_death = state.elder_female + adult_to_elder_female

    child_deaths_male = round(next_children_male_before_death * effective_child_death_rate)
    child_deaths_female = round(next_children_female_before_death * effective_child_death_rate)

    adult_deaths_male = round(next_adult_male_before_death * effective_adult_death_rate)
    adult_deaths_female = round(next_adult_female_before_death * effective_adult_death_rate)

    elder_deaths_male = round(next_elder_male_before_death * effective_elder_death_rate)
    elder_deaths_female = round(next_elder_female_before_death * effective_elder_death_rate)

    next_children_male = max(0, next_children_male_before_death - child_deaths_male)
    next_children_female = max(0, next_children_female_before_death - child_deaths_female)

    next_adult_male = max(0, next_adult_male_before_death - adult_deaths_male)
    next_adult_female = max(0, next_adult_female_before_death - adult_deaths_female)

    next_elder_male = max(0, next_elder_male_before_death - elder_deaths_male)
    next_elder_female = max(0, next_elder_female_before_death - elder_deaths_female)

    temp_next_state = VillageState(
        year=state.year + 1,
        farmland_mu=state.farmland_mu,
        yield_per_mu=state.yield_per_mu,

        children_male=next_children_male,
        children_female=next_children_female,
        adult_male=next_adult_male,
        adult_female=next_adult_female,
        elder_male=next_elder_male,
        elder_female=next_elder_female,

        male_labor_participation=state.male_labor_participation,
        female_labor_participation=state.female_labor_participation,
    )

    if temp_next_state.farmland_mu <= 0:
        next_labor_density = 0.0
    else:
        next_labor_density = labor_total(temp_next_state) / temp_next_state.farmland_mu

    yield_factor = compute_yield_factor(next_labor_density, params)
    next_yield_per_mu = max(0.0, state.yield_per_mu * yield_factor)

    next_state = VillageState(
        year=temp_next_state.year,
        farmland_mu=temp_next_state.farmland_mu,
        yield_per_mu=next_yield_per_mu,

        children_male=temp_next_state.children_male,
        children_female=temp_next_state.children_female,
        adult_male=temp_next_state.adult_male,
        adult_female=temp_next_state.adult_female,
        elder_male=temp_next_state.elder_male,
        elder_female=temp_next_state.elder_female,

        male_labor_participation=temp_next_state.male_labor_participation,
        female_labor_participation=temp_next_state.female_labor_participation,
    )

    return next_state
