import pytest

from spectral_feature_bridge import (
    FeatureSpec,
    V8_COORDINATES,
    extract_spectral_features,
    project_features_to_v8,
)
from spectral_provenance import SpectralObservation


def observation():
    return SpectralObservation.create(
        observation_id="bridge-001",
        modality="UV-Vis",
        raw_measurements={
            "wavelength": [400.0, 500.0, 600.0],
            "intensity": [0.9, 0.7, 0.5],
            "temperature": 298.15,
        },
        units={"wavelength": "nm", "intensity": "fraction", "temperature": "K"},
        derived_values={"absorbance": [0.04576, 0.15490, 0.30103]},
    )


def specs():
    return [
        FeatureSpec("mean_wavelength", "raw", "wavelength", "nm", "mean"),
        FeatureSpec("intensity_rms", "raw", "intensity", "fraction", "rms"),
        FeatureSpec("temperature", "raw", "temperature", "K"),
        FeatureSpec("peak_absorbance", "derived", "absorbance", "AU", "max"),
    ]


def test_feature_extraction_is_explicit_and_keeps_observation_link():
    obs = observation()
    vector = extract_spectral_features(obs, specs())
    assert vector.observation_id == obs.observation_id
    assert vector.observation_digest == obs.digest
    assert vector.modality == "uv-vis"
    assert vector.features["mean_wavelength"].value == pytest.approx(500.0)
    assert vector.features["intensity_rms"].value == pytest.approx(
        ((0.9**2 + 0.7**2 + 0.5**2) / 3) ** 0.5
    )
    assert vector.features["peak_absorbance"].value == pytest.approx(0.30103)
    assert vector.features["mean_wavelength"].unit == "nm"


def test_v8_projection_requires_explicit_complete_mapping_and_is_reproducible():
    vector = extract_spectral_features(observation(), specs())
    mapping = {coordinate: {"mean_wavelength": 0.0} for coordinate in V8_COORDINATES}
    mapping["h"] = {"mean_wavelength": 0.001, "peak_absorbance": 2.0}
    mapping["R"] = {"intensity_rms": 3.0}
    projection = project_features_to_v8(
        vector, mapping=mapping, offsets={"d": 0.25, "f": -1.0}
    )
    assert projection.state.h == pytest.approx(1.10206)
    assert projection.state.R == pytest.approx(3.0 * vector.features["intensity_rms"].value)
    assert projection.state.d == pytest.approx(0.25)
    assert projection.state.f == pytest.approx(-1.0)
    assert projection.observation_digest == vector.observation_digest
    assert projection == project_features_to_v8(
        vector, mapping=mapping, offsets={"d": 0.25, "f": -1.0}
    )


def test_projection_records_mapping_and_units():
    import json

    vector = extract_spectral_features(observation(), specs())
    mapping = {coordinate: {"temperature": 0.0} for coordinate in V8_COORDINATES}
    projection = project_features_to_v8(vector, mapping=mapping)
    record = json.loads(projection.mapping_json)
    assert record["schema"] == "pan-spectral-feature-to-v8-map-v1"
    assert record["feature_units"]["temperature"] == "K"
    assert set(record["mapping"]) == set(V8_COORDINATES)


@pytest.mark.parametrize(
    "bad_specs",
    [
        [],
        [FeatureSpec("x", "raw", "missing", "unit")],
        [FeatureSpec("x", "raw", "temperature", "K"),
         FeatureSpec("x", "raw", "intensity", "fraction", "mean")],
        [FeatureSpec("x", "derived", "absorbance", "AU", "scalar")],
    ],
)
def test_invalid_feature_specs_and_sources_are_rejected(bad_specs):
    with pytest.raises((TypeError, ValueError, KeyError)):
        extract_spectral_features(observation(), bad_specs)


def test_projection_rejects_incomplete_or_unknown_mappings():
    vector = extract_spectral_features(observation(), specs())
    incomplete = {coordinate: {"temperature": 1.0} for coordinate in V8_COORDINATES[:-1]}
    with pytest.raises(ValueError, match="exactly"):
        project_features_to_v8(vector, mapping=incomplete)
    unknown = {coordinate: {"not_a_feature": 1.0} for coordinate in V8_COORDINATES}
    with pytest.raises(KeyError):
        project_features_to_v8(vector, mapping=unknown)


def test_projection_rejects_nonfinite_coefficients_and_offsets():
    vector = extract_spectral_features(observation(), specs())
    mapping = {coordinate: {"temperature": 1.0} for coordinate in V8_COORDINATES}
    mapping["chi"] = {"temperature": float("nan")}
    with pytest.raises(ValueError):
        project_features_to_v8(vector, mapping=mapping)
    mapping["chi"] = {"temperature": 1.0}
    with pytest.raises(ValueError):
        project_features_to_v8(vector, mapping=mapping, offsets={"h": float("inf")})


def test_raw_feature_unit_must_match_observation_unit():
    bad = [FeatureSpec("wavelength", "raw", "wavelength", "cm")]
    with pytest.raises(ValueError, match="does not match"):
        extract_spectral_features(observation(), bad)