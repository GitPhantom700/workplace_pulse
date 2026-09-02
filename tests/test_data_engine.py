"""
Tier 1 Unit Tests: Synthetic Enterprise Telemetry Data Engine
Validates scenario registry, mathematical integrity of generated metrics, chart data structures, and edge cases.
"""

import pytest
from data_engine import (
    get_scenario_by_id,
    list_available_scenarios,
    generate_saas_finops_scenario,
    generate_hardware_lifecycle_scenario,
    generate_itsm_surge_scenario,
    SCENARIO_REGISTRY,
    ScenarioDataPayload,
    SaaSAppMetric,
    HardwareFleetMetric,
    ITSMIncidentMetric,
)


def test_list_available_scenarios_structure():
    """Verify that catalog lists all 3 enterprise presets with correct schema."""
    scenarios = list_available_scenarios()
    assert isinstance(scenarios, list)
    assert len(scenarios) == 3

    scenario_ids = [s["id"] for s in scenarios]
    assert "saas_finops" in scenario_ids
    assert "hardware_lifecycle" in scenario_ids
    assert "itsm_surge" in scenario_ids

    for item in scenarios:
        assert "id" in item and item["id"]
        assert "title" in item and item["title"]
        assert "description" in item and item["description"]


def test_get_valid_scenarios_return_payload():
    """Verify each registered scenario returns a well-formed ScenarioDataPayload."""
    for scenario_id in ["saas_finops", "hardware_lifecycle", "itsm_surge"]:
        payload = get_scenario_by_id(scenario_id)
        assert payload is not None
        assert isinstance(payload, ScenarioDataPayload)
        assert payload.scenario_id == scenario_id
        assert payload.title != ""
        assert payload.domain != ""
        assert payload.summary != ""
        assert payload.timestamp != ""
        assert payload.chart_data is not None
        assert isinstance(payload.chart_data, dict)
        assert payload.grounding_context != ""


def test_scenario_registry_contains_all_generators():
    """Verify SCENARIO_REGISTRY maps keys to callable functions."""
    assert "saas_finops" in SCENARIO_REGISTRY
    assert "hardware_lifecycle" in SCENARIO_REGISTRY
    assert "itsm_surge" in SCENARIO_REGISTRY
    assert callable(SCENARIO_REGISTRY["saas_finops"])
    assert callable(SCENARIO_REGISTRY["hardware_lifecycle"])
    assert callable(SCENARIO_REGISTRY["itsm_surge"])


def test_get_scenario_invalid_id_behavior():
    """Verify behavior for invalid scenario IDs (returns None if not found)."""
    payload_invalid = get_scenario_by_id("non_existent_scenario_xyz")
    assert payload_invalid is None


def test_saas_finops_mathematical_integrity():
    """
    Verify mathematical consistency for SaaS FinOps metrics:
    - total_licenses == active_last_30d + inactive_60d_plus
    - annual_potential_savings == inactive_60d_plus * cost_per_seat_monthly * 12
    - utilization_rate_pct == round((active_last_30d / total_licenses) * 100, 1)
    - Chart data labels match app names
    """
    payload = generate_saas_finops_scenario()
    assert payload.scenario_id == "saas_finops"
    assert len(payload.saas_metrics) >= 7

    total_waste_calculated = 0.0
    for m in payload.saas_metrics:
        assert isinstance(m, SaaSAppMetric)
        # Partition rule: active + inactive == total
        assert m.total_licenses == m.active_last_30d + m.inactive_60d_plus
        # Savings calculation rule
        expected_savings = round(m.inactive_60d_plus * m.cost_per_seat_monthly * 12, 2)
        assert m.annual_potential_savings == expected_savings
        # Utilization percentage rule
        expected_util = round((m.active_last_30d / m.total_licenses) * 100, 1)
        assert m.utilization_rate_pct == expected_util
        total_waste_calculated += m.annual_potential_savings

    # Verify chart structure
    chart = payload.chart_data
    assert chart["type"] == "bar"
    assert "labels" in chart
    assert len(chart["labels"]) == len(payload.saas_metrics)
    assert len(chart["datasets"]) == 2
    assert chart["datasets"][0]["label"] == "Active Users (Last 30d)"
    assert chart["datasets"][1]["label"] in ["Zombie/Inactive (60d+)", "Stale/Inactive (60d+)"]


def test_hardware_lifecycle_mathematical_integrity():
    """
    Verify mathematical consistency for Hardware Lifecycle metrics:
    - estimated_replacement_budget_usd == projected_failures_next_quarter * cost
    - total_units >= battery_critical_units
    - Chart datasets match fleet counts
    """
    payload = generate_hardware_lifecycle_scenario()
    assert payload.scenario_id == "hardware_lifecycle"
    assert len(payload.hardware_metrics) >= 4

    total_capex = 0.0
    for m in payload.hardware_metrics:
        assert isinstance(m, HardwareFleetMetric)
        assert m.total_units >= m.battery_critical_units
        assert m.total_units >= m.out_of_warranty_units
        assert m.projected_failures_next_quarter <= m.total_units
        assert m.jamf_compliance_rate_pct >= 0.0 and m.jamf_compliance_rate_pct <= 100.0
        total_capex += m.estimated_replacement_budget_usd

    # Verify chart structure
    chart = payload.chart_data
    assert chart["type"] == "bar"
    assert "labels" in chart
    assert len(chart["labels"]) == len(payload.hardware_metrics)
    assert len(chart["datasets"]) == 2
    assert chart["datasets"][0]["label"] == "Healthy Battery (<800 cycles)"
    assert chart["datasets"][1]["label"] == "Critical / Swelling Risk (>800 cycles)"


def test_itsm_surge_incident_metrics_integrity():
    """
    Verify ITSM incident metrics integrity:
    - month_end_surge_daily_avg >= historical_daily_avg
    - risk score in range [1, 10]
    - Chart type is line with 2 datasets
    """
    payload = generate_itsm_surge_scenario()
    assert payload.scenario_id == "itsm_surge"
    assert len(payload.itsm_metrics) >= 5

    found_erp_surge = False
    for m in payload.itsm_metrics:
        assert isinstance(m, ITSMIncidentMetric)
        assert m.month_end_surge_daily_avg >= m.historical_daily_avg
        assert 1 <= m.escalation_risk_score_1_to_10 <= 10
        assert m.average_resolution_time_hrs > 0
        assert m.primary_bottleneck != ""
        if m.category == "Financial Close & ERP Access":
            found_erp_surge = True
            assert m.escalation_risk_score_1_to_10 == 9
            assert m.historical_daily_avg == 6
            assert m.month_end_surge_daily_avg == 42

    assert found_erp_surge, "ERP Access category not found in ITSM metrics"

    # Verify chart structure
    chart = payload.chart_data
    assert chart["type"] == "line"
    assert "labels" in chart
    assert len(chart["datasets"]) == 2
    assert chart["datasets"][0]["label"] == "Standard Daily Ticket Volume"
    assert chart["datasets"][1]["label"] == "Month-End Surge Daily Volume (Projected)"
