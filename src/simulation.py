from state import VillageState


def step(state: VillageState) -> VillageState:
    children_to_adult_male = state.children_male // 15
    children_to_adult_female = state.children_female // 15

    adult_to_elder_male = state.adult_male // 45
    adult_to_elder_female = state.adult_female // 45

    next_state = VillageState(
        year=state.year + 1,
        farmland_mu=state.farmland_mu,
        yield_per_mu=state.yield_per_mu,

        children_male=state.children_male - children_to_adult_male,
        children_female=state.children_female - children_to_adult_female,

        adult_male=state.adult_male + children_to_adult_male - adult_to_elder_male,
        adult_female=state.adult_female + children_to_adult_female - adult_to_elder_female,

        elder_male=state.elder_male + adult_to_elder_male,
        elder_female=state.elder_female + adult_to_elder_female,

        male_labor_participation=state.male_labor_participation,
        female_labor_participation=state.female_labor_participation,
    )

    return next_state
