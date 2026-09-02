from data_engine import get_scenario_by_id
data = get_scenario_by_id("hardware_lifecycle")
print(data.model_dump_json())
