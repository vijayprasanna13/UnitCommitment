# unit-commitment
Load sharing of generators with FLAPC based priority using backpropagation. Each feasible state in the hour-generator combination aims to match the required load. The FLAPC sorted generators are assigned generation values using Economic Dispatch Algorithm.
This python program allows the user to enter 'N' generators and load variation for 24 hours. All values that fall within the maximum generation limits will yield one or more feasible states or terminate the run time if cumilative maximum generation is not able to meet the hour's demand.

## Packages used
1. [PrettyTable](https://pypi.python.org/pypi/PrettyTable)

## Instructions
1. Clone or download the project repository as zip. 
2. `cd` to the repo and edit the `generator_env.py` file with required load and generator values
3. run `python unit.py` to get the values of generation over load variation in 24 hours

Feel free to contribute!
