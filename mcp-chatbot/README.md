# MCP Chatbot

Full-stack chatbot to query an orders database using natural language.

## Stack
- Backend: FastAPI, SQLAlchemy (Postgres/MySQL/SQLite) or MongoDB, JWT auth
- NL: LangChain wiring + heuristic fallback
- Frontend: React + Vite + Tailwind
- Docker: backend, frontend, Postgres, Mongo

## Run Backend (local)
```bash
pip install -r mcp-chatbot/backend/requirements.txt
# PowerShell env examples
$env:DB_BACKEND="sql"  # or "mongo"
$env:SQLALCHEMY_DATABASE_URL="sqlite:///./orders.db"
$env:JWT_SECRET="change_me"
uvicorn app.main:app --reload --app-dir mcp-chatbot/backend
```
Seed sample data:
```bash
python -m app.seed
```

## Run Frontend (local)
```bash
cd mcp-chatbot/frontend
npm install
npm run dev
```
Open http://localhost:5173. Configure API base with `VITE_API_BASE`.

## Docker Compose
```bash
cd mcp-chatbot/docker
docker compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## MCP Server
Run the MCP server over stdio:
```bash
python -m app.mcp_server --module mcp-chatbot/backend
```
Exposed tools:
- list_orders()
- get_order(orderId)
- list_errors()
- nl_query(query)

### Cursor MCP config example
Copy `mcp-chatbot/mcp.example.json` into your Cursor MCP config (e.g., settings JSON) and adjust paths/secrets as needed:
```json
{
  "mcpServers": {
    "orders-mcp": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "mcp-chatbot/backend",
      "env": {
        "DB_BACKEND": "sql",
        "SQLALCHEMY_DATABASE_URL": "sqlite:///./orders.db",
        "JWT_SECRET": "change_me"
      }
    }
  }
}
```

## API
- POST /auth/login (form: username=admin, password=password)
- GET /orders
- GET /orders/{orderId}
- GET /orders/errors
- POST /nl-query { "query": "Show me failed orders today" }

## Env Vars
- DB_BACKEND: sql | mongo
- SQLALCHEMY_DATABASE_URL
- MONGO_URI, MONGO_DB_NAME
- JWT_SECRET
- OPENAI_API_KEY (optional)

## Notes
- Replace secrets before production. Enable proper CORS/HTTPS.
