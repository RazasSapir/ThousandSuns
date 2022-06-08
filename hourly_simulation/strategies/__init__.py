from hourly_simulation.strategies.greedy_strategy import greedy_use_strategy
from hourly_simulation.strategies.selling_strategy import first_selling_strategy
from hourly_simulation.strategies.smart_storing import smart_storing_strategy

use_strategies = {"Greedy Strategy": greedy_strategy.greedy_use_strategy,
                  # "Smart Storing Strategy": smart_storing.smart_storing_strategy,
                  "Selling Strategy": selling_strategy.first_selling_strategy}
