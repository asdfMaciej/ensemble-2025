#!/bin/bash

# Read as first argument the {agent_name}
agent_name=$1

# Read macos or linux as second argument - by default linux if not set 
os=$2
if [ -z "$os" ]
then
    os="linux"
fi

# Check that os must be linux or macos
if [ "$os" != "linux" ] && [ "$os" != "macos" ]
then
    echo "Please provide a valid os as the second argument"
    echo "Example: ./run.sh agent_1 <linux/macos>"
    exit 1
fi

# If agent_name not set, exit with a description how to run this command
if [ -z "$agent_name" ]
then
    echo "Please provide the agent name as the first argument"
    echo "Example: ./run.sh agent_1"
    exit 1
fi


# Tell the user the agent name
echo "Running agent: $agent_name"

cp agents/$agent_name/agent.py ./agent.py

if [ "$os" == "macos" ]
then
    # Remove the first line of agent.py
    sed -i '' '1d' agent.py
    # Copy the entire content of utils/utils.py to the start of agent.py
    sed -i '' '1r utils/utils.py' agent.py
else
    # Remove the first line of agent.py
    sed -i '1d' agent.py
    # Copy the entire content of utils/utils.py to the start of agent.py
    sed -i '1r utils/utils.py' agent.py
fi

cd octospace
python3 run_match.py ../agent.py ../agent.py --render_mode=human
