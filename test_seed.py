import requests

def test():
    # Assuming server is running, but let's test the functions directly!
    from data_engine import get_scenario_by_id
    data = get_scenario_by_id("hardware_lifecycle")
    print("saas_metrics len:", len(data.saas_metrics) if data.saas_metrics else "None")
    print("hw_metrics len:", len(data.hardware_metrics) if data.hardware_metrics else "None")

test()
