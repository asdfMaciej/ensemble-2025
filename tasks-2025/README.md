# Tasks for EnsembleAI Hackathon 2025

This repo consists of codes, which will be helpful for solving tasks during hackathon.

All dependencies shuould be in requirements.txt.
```
pip install -r requirements.txt
```

## Tasks 1 - 4:
Example codes for submissions for Tasks 1 - 4 can be directly executed, after filling up some places.

## Task 5:
Task 5 has an example submission code, but also a script to play a match between 2 bots. To run it, go to the *task_5/octospace* directory and execute:
```
python run_match.py <path_to_agent_1> <path_to_agent_2> --render_mode=human
```
As an example, you can use an empty Agent class in agent.py:
```
python run_match.py ../agent.py ../agent.py --render_mode=human --turn_on_music=True
```

## Troubleshooting
If you'd notice any strange behavior or error, please contact the Infrastructure Team on Discord or on-site.
