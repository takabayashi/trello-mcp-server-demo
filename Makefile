install:
	uv venv --clear 
	source .venv/bin/activate
	uv sync

run:
	uv run mcp dev server.py

claude:
	uv run mcp install --with-editable . server.py --env-file .env

run_client:
	uv run client.py
