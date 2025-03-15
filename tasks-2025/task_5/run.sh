#!/bin/bash

cp agents/deepseek-generated/agent.py ./agent.py

# Remove first line of agent.py 
sed -i '1d' agent.py
# Copy entire content of utils/utils.py to start of agent.py 
sed -i '1r utils/utils.py' agent.py

cd octospace
python3 run_match.py ../agent.py ../agent.py --render_mode=human
