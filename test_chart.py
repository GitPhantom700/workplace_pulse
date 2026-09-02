from data_engine import get_scenario_by_id
import json
data = get_scenario_by_id("hardware_lifecycle")
print(json.dumps(data.chart_data, indent=2))
