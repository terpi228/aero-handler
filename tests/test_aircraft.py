import pytest

from src.aircraft import Aircraft


def test_aircraft_strips_text_fields():
    aircraft = Aircraft("  FLT123  ", "  Spain  ", 250.5, 10300.0)

    assert aircraft.callsign == "FLT123"
    assert aircraft.registration_country == "Spain"
    assert aircraft.velocity == 250.5
    assert aircraft.altitude == 10300.0


@pytest.mark.parametrize(
    ("callsign", "country", "velocity", "altitude"),
    [
        ("", "Spain", 200.0, 1000.0),
        ("AB123", "", 200.0, 1000.0),
        ("AB123", "Spain", -1.0, 1000.0),
        ("AB123", "Spain", 200.0, -1.0),
    ],
)
def test_aircraft_validation_errors(callsign, country, velocity, altitude):
    with pytest.raises(ValueError):
        Aircraft(callsign, country, velocity, altitude)


def test_cast_to_object_list_skips_invalid_rows():
    valid_state = [
        "abc123",
        "  AB123  ",
        "  Spain  ",
        None,
        None,
        None,
        None,
        10500.0,
        None,
        230.0,
    ]
    invalid_state_negative_velocity = [
        "def456",
        "CD456",
        "France",
        None,
        None,
        None,
        None,
        9000.0,
        None,
        -10.0,
    ]

    result = Aircraft.cast_to_object_list(
        [valid_state, invalid_state_negative_velocity]
    )

    assert len(result) == 1
    assert result[0].callsign == "AB123"
    assert result[0].registration_country == "Spain"
