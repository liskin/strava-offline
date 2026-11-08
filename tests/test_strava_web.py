from strava_offline.strava import _normalize_start_date
from strava_offline.strava import _parse_bike_name
from strava_offline.strava import _training_activity_to_summary
from strava_offline.strava import _web_gear_id
from strava_offline.sync import _has_location_data


def test_parse_bike_name():
    # Real bike detail page shape: "Strava | <athlete> | <bike name>".
    assert _parse_bike_name("<title>Strava | Luigi Gangitano | SEHT</title>") == "SEHT"
    # Falls back to <h1> when the title isn't the 3-part form.
    assert _parse_bike_name("<title>Strava</title><h1>My Bike</h1>") == "My Bike"
    assert _parse_bike_name("<html>no name here</html>") is None


def test_normalize_start_date():
    assert _normalize_start_date("2026-06-08T14:38:34+0000") == "2026-06-08T14:38:34Z"
    assert _normalize_start_date(None) is None


def test_web_gear_id():
    assert _web_gear_id({'bike_id': 456}) == "b456"
    assert _web_gear_id({'athlete_gear_id': 789}) == "g789"
    assert _web_gear_id({'bike_id': 456, 'athlete_gear_id': 789}) == "b456"
    assert _web_gear_id({}) is None


def test_training_activity_to_summary_full():
    # Field shape taken from a real /athlete/training_activities response.
    model = {
        'id': 19191363870,
        'name': "Afternoon Ride",
        'start_time': "2026-07-05T13:36:24+0000",
        'moving_time_raw': 830,
        'elapsed_time_raw': 6716,
        'distance_raw': 2173.2,
        'elevation_gain_raw': 71.0,
        'sport_type': "MountainBikeRide",
        'display_type': "Mountain Bike Ride",
        'activity_type_display_name': "Ride",
        'bike_id': 5610892,
        'athlete_gear_id': None,
        'commute': False,
        'trainer': False,
        'has_latlng': True,
    }
    summary = _training_activity_to_summary(model)
    assert summary == {
        'id': 19191363870,
        'upload_id': None,
        'name': "Afternoon Ride",
        'start_date': "2026-07-05T13:36:24Z",
        'moving_time': 830,
        'elapsed_time': 6716,
        'distance': 2173.2,
        'total_elevation_gain': 71.0,
        'gear_id': "b5610892",
        # coarse category matching the API's `type`, not the "Mountain Bike Ride" label
        'type': "Ride",
        'sport_type': "MountainBikeRide",
        'commute': False,
        'trainer': False,
        'has_location_data': True,
    }


def test_training_activity_to_summary_shoes_and_no_gps():
    # A hike uses shoe gear (athlete_gear_id -> "g<id>") and may lack GPS.
    model = {
        'id': 1,
        'name': "Yoga",
        'start_time': "2026-01-01T00:00:00+0000",
        'moving_time_raw': 60,
        'elapsed_time_raw': 60,
        'distance_raw': 0.0,
        'elevation_gain_raw': 0.0,
        'sport_type': "Yoga",
        'activity_type_display_name': "Workout",
        'bike_id': None,
        'athlete_gear_id': None,
        'commute': False,
        'trainer': True,
        'has_latlng': False,
    }
    summary = _training_activity_to_summary(model)
    assert summary['gear_id'] is None
    assert summary['has_location_data'] is False
    assert summary['trainer'] is True
    assert summary['type'] == "Workout"
    assert summary['sport_type'] == "Yoga"


def test_has_location_data_prefers_explicit_flag():
    # Website-sourced activities carry the explicit boolean...
    assert _has_location_data({'has_location_data': True}) is True
    assert _has_location_data({'has_location_data': False}) is False
    # ...API-sourced activities derive it from start_latlng.
    assert _has_location_data({'start_latlng': [50.0, 14.0]}) is True
    assert _has_location_data({'start_latlng': []}) is False
    assert _has_location_data({'start_latlng': None}) is False
