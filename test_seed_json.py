from data_engine import get_scenario_by_id
data = get_scenario_by_id("hardware_lifecycle")
print("hw saas:", data.saas_metrics)
print("hw hw:", data.hardware_metrics)
