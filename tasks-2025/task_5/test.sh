#!/bin/bash

agent_name1=$1
agent_name2=$2

os=$3
n_matches=$4

if [ -z "$os" ]
then
    os="linux"
fi

# Check that os must be linux or macos
if [ "$os" != "linux" ] && [ "$os" != "macos" ]
then
    echo "Please provide a valid os as the third argument"
    echo "Example: ./run.sh agent_1 agent_2 <linux/macos> <n_matches>"
    exit 1
fi

# If agent names are not set, exit with a description how to run this command
if [ -z "$agent_name1" ] || [ -z "$agent_name2" ]
then
    echo "Please provide two agent names as the first and second arguments"
    echo "Example: ./run.sh agent_1 agent_2 <linux/macos> <n_matches>"
    exit 1
fi

# If number of matches is not provided, default to 1
if [ -z "$n_matches" ]
then
    n_matches=1
fi

# Tell the user the agent names
echo "Running match between: $agent_name1 and $agent_name2"
echo "Number of matches: $n_matches"

# Copy agent files
cp agents/$agent_name1/agent.py ./agent1.py
cp agents/$agent_name2/agent.py ./agent2.py

if [ "$os" == "macos" ]
then
    # Modify agent1.py
    sed -i '' '1d' agent1.py
    sed -i '' '1r utils/utils.py' agent1.py

    # Modify agent2.py
    sed -i '' '1d' agent2.py
    sed -i '' '1r utils/utils.py' agent2.py
else
    # Modify agent1.py
    sed -i '1d' agent1.py
    sed -i '1r utils/utils.py' agent1.py

    # Modify agent2.py
    sed -i '1d' agent2.py
    sed -i '1r utils/utils.py' agent2.py
fi

cd octospace
python3 run_match.py ../agent1.py ../agent2.py  --n_matches=$n_matches