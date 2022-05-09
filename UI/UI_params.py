from hourly_simulation import strategies

demand_files = {"Hatzor": r'data/consumption_hatzor.csv',
                "Ramat David": r'data/consumption_ramat_david.csv',
                "Tel Nof": r'data/consumption_tel_nof.csv',
                "Nevatim": r'data/consumption_nevatim.csv',
                "Palmahim": r'data/consumption_palmahim.csv',
                "Hatzerim": r'data/consumption_Hatzerim.csv'}

use_strategies = {"Greedy Demand": strategies.greedy_use_strategy}
