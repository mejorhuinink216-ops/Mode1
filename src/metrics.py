from state import VillageState


def population_total(s: VillageState) -> int:
    return (
        s.children_male + s.children_female +
        s.adult_male + s.adult_female +
        s.elder_male + s.elder_female
    )


def male_total(s: VillageState) -> int:
    return s.children_male + s.adult_male + s.elder_male


def female_total(s: VillageState) -> int:
    return s.children_female + s.adult_female + s.elder_female


def children_total(s: VillageState) -> int:
    return s.children_male + s.children_female


def adult_total(s: VillageState) -> int:
    return s.adult_male + s.adult_female


def elder_total(s: VillageState) -> int:
    return s.elder_male + s.elder_female


def labor_male(s: VillageState) -> float:
    return s.adult_male * s.male_labor_participation


def labor_female(s: VillageState) -> float:
    return s.adult_female * s.female_labor_participation


def labor_total(s: VillageState) -> float:
    return labor_male(s) + labor_female(s)


def total_output(s: VillageState) -> float:
    return s.farmland_mu * s.yield_per_mu


def child_ratio(s: VillageState) -> float:
    total = population_total(s)
    if total == 0:
        return 0.0
    return children_total(s) / total


def elder_ratio(s: VillageState) -> float:
    total = population_total(s)
    if total == 0:
        return 0.0
    return elder_total(s) / total


def labor_ratio(s: VillageState) -> float:
    total = population_total(s)
    if total == 0:
        return 0.0
    return labor_total(s) / total


def dependency_ratio(s: VillageState) -> float:
    adults = adult_total(s)
    if adults == 0:
        return 0.0
    return (children_total(s) + elder_total(s)) / adults