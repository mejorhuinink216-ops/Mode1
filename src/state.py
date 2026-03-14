from dataclasses import dataclass

@dataclass
class VillageState:
    year: int
    farmland_mu: float
    yield_per_mu: float

    children_male: int
    children_female: int
    adult_male: int
    adult_female: int
    elder_male: int
    elder_female: int

    male_labor_participation: float
    female_labor_participation: float
