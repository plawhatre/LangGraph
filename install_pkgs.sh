# Install the Ollama Python package
source .venv/bin/activate
# Install the required Python packages
python3 -m pip install -r requirements.txt
python3 -m pip install langchain-community pypdf
python3 -m pip install faiss-cpu
# vector db
pip install --upgrade setuptools
pip install protobuf==6.30.0
python3 -m pip install langchain-chroma>=0.1.2
python3 -m pip install rank_bm25
python3 -m pip install langgraph>0.2.27
python3 -m pip install bs4
python3 -m pip install pretty_errors
python3 -m pip install langchain-mcp-adapters
python3 -m pip install langgraph-supervisor
python3 -m pip install langgraph-swarm
python3 -m pip install grandalf