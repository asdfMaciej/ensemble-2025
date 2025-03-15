#!/bin/bash

# Przykład użycia:
# ./run.sh agent_1 agent_2 linux
# ./run.sh agent_1 agent_2 macos
# lub jeśli trzeci argument nie zostanie podany, domyślnie skrypt użyje "linux".

# Czytamy nazwy agentów
agent_name_1=$1
agent_name_2=$2

# Czytamy opcjonalnie system operacyjny (linux/macos)
os=$3
if [ -z "$os" ]
then
    os="linux"
fi

# Sprawdzamy, czy os jest poprawny
if [ "$os" != "linux" ] && [ "$os" != "macos" ]
then
    echo "Please provide a valid os as the third argument"
    echo "Example: ./run.sh agent_1 agent_2 <linux/macos>"
    exit 1
fi

# Jeśli nie podano agent_name_1 lub agent_name_2
if [ -z "$agent_name_1" ] || [ -z "$agent_name_2" ]
then
    echo "Please provide two agent names as the first and second arguments"
    echo "Example: ./run.sh agent_1 agent_2"
    exit 1
fi

# Wyświetlamy, jakie agenty uruchamiamy
echo "Running match between agents: $agent_name_1 vs $agent_name_2"

# Kopiujemy pliki agentów do głównego katalogu jako agent_1.py i agent_2.py
cp agents/$agent_name_1/agent.py ./agent_1.py
cp agents/$agent_name_2/agent.py ./agent_2.py

# Funkcja pomocnicza do usuwania i wklejania zawartości utils.py
process_agent_file() {
  local filename=$1
  if [ "$os" == "macos" ]
  then
    sed -i '' '1d' $filename
    sed -i '' '1r utils/utils.py' $filename
  else
    sed -i '1d' $filename
    sed -i '1r utils/utils.py' $filename
  fi
}

# Przetwarzamy oba pliki agentów
process_agent_file "agent_1.py"
process_agent_file "agent_2.py"

# Przechodzimy do folderu octospace
cd octospace

# Uruchamiamy mecz z dwoma agentami
python3 run_match.py ../agent_1.py ../agent_2.py --render_mode=human
