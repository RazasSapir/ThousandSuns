from hourly_simulation import strategies

demand_files = {"Hatzor": r'data/consumption_hatzor.csv',
                "Ramat David": r'data/consumption_ramat_david.csv'}

use_strategies = {"Greedy Demand": strategies.greedy_use_strategy}
