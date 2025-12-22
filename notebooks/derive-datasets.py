import pandas as pd

population = pd.read_csv("data/s-population.csv")
regvehicle = pd.read_csv("data/s-regvehicles.csv")
fatalities = pd.read_csv("data/s-fatalities.csv")
motor_rate = regvehicle * 1000 * 1000 / population
fatal_1k_veh = fatalities / regvehicle
motor_rate["Year"] = population["Year"]
fatal_1k_veh["Year"] = population["Year"]
motor_rate.to_csv("data/s-motorrate.csv", index=False)
fatal_1k_veh.to_csv("data/s-fatal1000v.csv", index=False)
