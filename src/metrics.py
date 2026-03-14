from state import VillageState

def population_total(s: VillageState):
    return (
        s.children_male + s.children_female +
        s.adult_male + s.adult_female +
        s.elder_male + s.elder_female
    )
