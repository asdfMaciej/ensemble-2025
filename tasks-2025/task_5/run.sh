#!/bin/bash

# Read as first argument the {agent_name}
agent_name=$1

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

# Remove first line of agent.py 
sed -i '1d' agent.py
# Copy entire content of utils/utils.py to start of agent.py 
sed -i '1r utils/utils.py' agent.py

cd octospace
python3 run_match.py ../agent.py ../agent.py --render_mode=human
