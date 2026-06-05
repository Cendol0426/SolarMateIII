"""Simulation logic for a small smart-grid neighborhood.

This module follows the updated reference model:
- houses may or may not have solar panels
- solar output depends on hour, max panel power, and GUI-selected weather
- household consumption has morning, midday, and evening load bumps
- house status is SELLER, BUYER, or BALANCED based on net energy

The Streamlit GUI imports this module and receives JSON-friendly snapshots.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from typing import Dict, Iterable, List, Optional


SHOP_TYPES = [
    "Bakery",
    "Clinic",
    "Cafe",
    "Mechanic",
    "Restaurant",
    "Laundry",
    "Pharmacy",
    "Supermarket",
    "Hardware Shop",
    "Mini Market",
]

RESIDENTIAL_TYPES = [
    "Solar Home",
    "Townhouse",
    "Bungalow",
    "Terrace House",
    "Corner House",
    "Luxury House",
]

WEATHER_CONFIG = {
    "Sunny": {
        "multiplier_range": (0.85, 1.0),
        "curve_power": 1.5,
        "variation_phase": 0.3,
    },
    "Cloudy": {
        "multiplier_range": (0.25, 0.55),
        "curve_power": 1.8,
        "variation_phase": 1.7,
    },
    "Rainy": {
        "multiplier_range": (0.05, 0.25),
        "curve_power": 2.2,
        "variation_phase": 2.6,
    },
}


class House:
    """One mutable building in the smart-grid simulation.

    The original API still exposes ``house_id`` for compatibility, while the
    GUI can use the richer building fields to draw homes and shop lots.
    """

    house_id: int
    building_id: int
    building_type: str
    display_name: str
    has_solar: bool
    max_power: float
    generation: float
    consumption: float

    def __init__(
        self,
        house_id: int,
        has_solar: bool,
        max_power: float,
        building_type: Optional[str] = None,
        display_name: Optional[str] = None,
    ):
        self.house_id = house_id
        self.building_id = house_id
        self.building_type = building_type or ("Solar Home" if has_solar else "Shop")
        self.display_name = display_name or f"{self.building_type} {house_id}"
        self.has_solar = has_solar
        self.max_power = max_power
        self.generation = 0.0
        self.consumption = 0.0

    @property
    def net_energy(self) -> float:
        return self.generation - self.consumption

    @property
    def status(self) -> str:
        if self.net_energy > 0:
            return "SELLER"
        if self.net_energy < 0:
            return "BUYER"
        return "BALANCED"


@dataclass(frozen=True)
class HouseSnapshot:
    """Read-only state for one house at one hour."""

    house_id: int
    building_id: int
    building_type: str
    display_name: str
    has_solar: bool
    max_power: float
    generation: float
    consumption: float
    net_energy: float
    status: str
    weather: str


def solar_output(
    hour: int,
    max_power: float,
    weather: str = "Sunny",
    rng: Optional[random.Random] = None,
) -> float:
    """Calculate raw solar output for a given hour and panel capacity."""

    _validate_hour(hour)

    if hour < 6 or hour > 18:
        return 0.0

    normalized_weather = normalize_weather(weather)
    config = WEATHER_CONFIG[normalized_weather]
    sun_factor = math.sin(math.pi * (hour - 6) / 12) ** config["curve_power"]
    weather_factor = weather_multiplier(normalized_weather, hour=hour)

    return max_power * sun_factor * weather_factor


def household_consumption(hour: int, rng: Optional[random.Random] = None) -> float:
    """Calculate household consumption for a given hour."""

    _validate_hour(hour)

    source = rng or random
    load = source.uniform(0.2, 0.5)

    if 11 <= hour <= 17:
        load += source.uniform(0.8, 2.0)

    if 18 <= hour <= 23:
        load += source.uniform(2.5, 5.0)

    if 6 <= hour <= 8:
        load += source.uniform(1.0, 2.5)

    return load


def generate_house(
    house_num: int,
    solar_probability: float = 0.5,
    rng: Optional[random.Random] = None,
    has_solar: Optional[bool] = None,
) -> House:
    """Create one house using the updated reference probabilities."""

    source = rng or random
    solar_probability = min(max(solar_probability, 0.0), 1.0)
    if has_solar is None:
        has_solar = source.random() < solar_probability
    max_power = source.uniform(15, 40) if has_solar else 0.0
    building_type = source.choice(RESIDENTIAL_TYPES if has_solar else SHOP_TYPES)
    display_name = f"{building_type} {house_num}" if has_solar else _shop_display_name(building_type, house_num)

    return House(
        house_id=house_num,
        has_solar=has_solar,
        max_power=max_power,
        building_type=building_type,
        display_name=display_name,
    )


def simulate_houses(
    num_houses: int,
    solar_probability: float = 0.5,
    seed: Optional[int] = None,
) -> List[House]:
    """Generate the requested number of houses."""

    if num_houses < 1:
        raise ValueError("num_houses must be at least 1")

    source = random.Random(seed) if seed is not None else random
    solar_probability = min(max(solar_probability, 0.0), 1.0)
    solar_count = min(num_houses, max(0, int(num_houses * solar_probability + 0.5)))
    solar_indices = set(source.sample(range(num_houses), solar_count))

    return [
        generate_house(
            i + 1,
            solar_probability=solar_probability,
            rng=source,
            has_solar=i in solar_indices,
        )
        for i in range(num_houses)
    ]


def simulation(
    houses: Iterable[House],
    hour: int,
    weather: str = "Sunny",
    rng: Optional[random.Random] = None,
) -> None:
    """Mutate houses with generation and consumption for the selected hour."""

    _validate_hour(hour)
    source = rng or random

    for house in houses:
        if house.has_solar:
            solar = solar_output(hour, house.max_power, weather=weather, rng=source)
            house.generation = solar * panel_variation(hour, house.house_id, weather)
        else:
            house.generation = 0.0

        house.consumption = household_consumption(hour, rng=source)


def simulate_hour(
    houses: Iterable[House],
    hour: int,
    weather: str = "Sunny",
    rng: Optional[random.Random] = None,
) -> List[HouseSnapshot]:
    """Simulate one hour and return immutable snapshots."""

    house_list = list(houses)
    normalized_weather = normalize_weather(weather)
    simulation(house_list, hour, weather=normalized_weather, rng=rng)
    return [_snapshot_house(house, normalized_weather) for house in house_list]


def simulate_day(
    houses: Iterable[House],
    weather: str = "Sunny",
    seed: Optional[int] = None,
) -> Dict[int, List[HouseSnapshot]]:
    """Simulate all 24 hours for a fixed set of houses."""

    house_list = list(houses)
    source = random.Random(seed) if seed is not None else random
    normalized_weather = normalize_weather(weather)
    return {
        hour: simulate_hour(house_list, hour, weather=normalized_weather, rng=source)
        for hour in range(24)
    }


def summarize_hour(snapshots: Iterable[HouseSnapshot]) -> Dict[str, float]:
    """Create total generation, consumption, and net energy for one hour."""

    snapshot_list = list(snapshots)
    total_generation = round(sum(snapshot.generation for snapshot in snapshot_list), 2)
    total_consumption = round(sum(snapshot.consumption for snapshot in snapshot_list), 2)
    return {
        "generation": total_generation,
        "consumption": total_consumption,
        "net_energy": round(total_generation - total_consumption, 2),
    }


def summarize_day(day_snapshots: Dict[int, List[HouseSnapshot]]) -> Dict[str, float]:
    """Create daily totals from hourly snapshots."""

    hourly_totals = [summarize_hour(snapshots) for snapshots in day_snapshots.values()]
    daily_generation = round(sum(hour["generation"] for hour in hourly_totals), 2)
    daily_consumption = round(sum(hour["consumption"] for hour in hourly_totals), 2)

    return {
        "generation": daily_generation,
        "consumption": daily_consumption,
        "net_energy": round(daily_generation - daily_consumption, 2),
    }


def build_simulation_payload(
    house_count: int,
    solar_ratio: float = 0.5,
    seed: int = 42,
    weather: str = "Sunny",
) -> Dict[str, object]:
    """Build deterministic, JSON-friendly data for the GUI."""

    normalized_weather = normalize_weather(weather)
    houses = simulate_houses(
        num_houses=house_count,
        solar_probability=solar_ratio,
        seed=seed,
    )
    day = simulate_day(houses, weather=normalized_weather, seed=seed + 100_000)

    return {
        "weather": normalized_weather,
        "houses": [_house_to_dict(house) for house in houses],
        "hours": {
            str(hour): [asdict(snapshot) for snapshot in snapshots]
            for hour, snapshots in day.items()
        },
        "hourly_totals": {
            str(hour): summarize_hour(snapshots) for hour, snapshots in day.items()
        },
        "daily_totals": summarize_day(day),
    }


def weather_multiplier(weather: str, hour: Optional[int] = None) -> float:
    """Return a smooth weather multiplier for solar output."""

    normalized_weather = normalize_weather(weather)
    config = WEATHER_CONFIG[normalized_weather]
    low, high = config["multiplier_range"]

    if hour is None:
        return round((low + high) / 2, 3)

    _validate_hour(hour)
    daylight_position = min(max((hour - 6) / 12, 0.0), 1.0)
    phase = config["variation_phase"]
    broad_wave = 0.5 + 0.5 * math.sin(math.pi * daylight_position + phase)
    soft_wave = 0.5 + 0.5 * math.sin(2 * math.pi * daylight_position + phase / 2)
    smooth_factor = 0.72 * broad_wave + 0.28 * soft_wave

    return low + (high - low) * smooth_factor


def panel_variation(hour: int, house_id: int, weather: str) -> float:
    """Small deterministic panel variation without sudden weather spikes."""

    normalized_weather = normalize_weather(weather)
    span = {
        "Sunny": 0.08,
        "Cloudy": 0.04,
        "Rainy": 0.025,
    }[normalized_weather]
    phase = house_id * 0.73
    smooth = 0.5 + 0.5 * math.sin((hour / 24) * 2 * math.pi + phase)

    return 1.0 - span + span * smooth


def normalize_weather(weather: str) -> str:
    """Normalize user-facing weather text."""

    normalized = str(weather).strip().title()
    if normalized not in {"Sunny", "Cloudy", "Rainy"}:
        return "Sunny"
    return normalized


def _snapshot_house(house: House, weather: str) -> HouseSnapshot:
    generation = round(house.generation, 2)
    consumption = round(house.consumption, 2)
    net_energy = round(generation - consumption, 2)

    return HouseSnapshot(
        house_id=house.house_id,
        building_id=house.building_id,
        building_type=house.building_type,
        display_name=house.display_name,
        has_solar=house.has_solar,
        max_power=round(house.max_power, 2),
        generation=generation,
        consumption=consumption,
        net_energy=net_energy,
        status=house.status,
        weather=weather,
    )


def _house_to_dict(house: House) -> Dict[str, object]:
    return {
        "house_id": house.house_id,
        "building_id": house.building_id,
        "building_type": house.building_type,
        "display_name": house.display_name,
        "has_solar": house.has_solar,
        "max_power": round(house.max_power, 2),
    }


def _shop_display_name(building_type: str, house_num: int) -> str:
    if building_type.endswith("Shop") or building_type.endswith("Market"):
        return f"{building_type} {house_num}"
    return f"{building_type} Shop {house_num}"


def _validate_hour(hour: int) -> None:
    if hour < 0 or hour > 23:
        raise ValueError("hour must be in the range 0..23")
