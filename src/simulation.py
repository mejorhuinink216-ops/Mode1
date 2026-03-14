from state import VillageState


def step(state: VillageState, params: dict) -> VillageState:
    birth_rate = params["birth_rate_per_adult_female"]
    child_death_rate = params["child_death_rate"]
    adult_death_rate = params["adult_death_rate"]
    elder_death_rate = params["elder_death_rate"]
    male_birth_share = params["male_birth_share"]

    births_total = round(state.adult_female * birth_rate)
    births_male = round(births_total * male_birth_share)
    births_female = births_total - births_male

    children_to_adult_male = state.children_male // 15
    children_to_adult_female = state.children_female // 15

    adult_to_elder_male = state.adult_male // 45
    adult_to_elder_female = state.adult_female // 45

    next_children_male = state.children_male - children_to_adult_male + births_male
    next_children_female = state.children_female - children_to_adult_female + births_female

    next_adult_male = state.adult_male + children_to_adult_male - adult_to_elder_male
    next_adult_female = state.adult_female + children_to_adult_female - adult_to_elder_female

    next_elder_male = state.elder_male + adult_to_elder_male
    next_elder_female = state.elder_female + adult_to_elder_female

    child_deaths_male = round(next_children_male * child_death_rate)
    child_deaths_female = round(next_children_female * child_death_rate)

    adult_deaths_male = round(next_adult_male * adult_death_rate)
    adult_deaths_female = round(next_adult_female * adult_death_rate)

    elder_deaths_male = round(next_elder_male * elder_death_rate)
    elder_deaths_female = round(next_elder_female * elder_death_rate)

    next_state = VillageState(
        year=state.year + 1,
        farmland_mu=state.farmland_mu,
        yield_per_mu=state.yield_per_mu,

        children_male=max(0, next_children_male - child_deaths_male),
        children_female=max(0, next_children_female - child_deaths_female),

        adult_male=max(0, next_adult_male - adult_deaths_male),
        adult_female=max(0, next_adult_female - adult_deaths_female),

        elder_male=max(0, next_elder_male - elder_deaths_male),
        elder_female=max(0, next_elder_female - elder_deaths_female),

        male_labor_participation=state.male_labor_participation,
        female_labor_participation=state.female_labor_participation,
    )

    return next_state
