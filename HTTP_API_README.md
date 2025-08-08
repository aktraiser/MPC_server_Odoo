# Odoo MCP HTTP API Server

The Odoo MCP server now exposes an HTTP API instead of using stdio communication. This makes it easier to integrate with Odoo modules and other applications.

## API Endpoints

### Health Check
- `GET /` - Returns server status and available endpoints
- `GET /health` - Simple health check

### Connection
- `POST /connect` - Connect to an Odoo instance

Request body:
```json
{
    "url": "https://your-odoo-instance.com",
    "database": "your-database",
    "username": "your-username",
    "password": "your-password"
}
```

### Operations

All operations require a connection to be established first.

#### Search Records
- `POST /search`

Request body:
```json
{
    "model": "res.partner",
    "domain": [["is_company", "=", true]],
    "fields": ["name", "email"],
    "limit": 100
}
```

#### Create Record
- `POST /create`

Request body:
```json
{
    "model": "res.partner",
    "values": {
        "name": "New Partner",
        "email": "partner@example.com"
    }
}
```

#### Update Records
- `POST /write`

Request body:
```json
{
    "model": "res.partner",
    "ids": [1, 2, 3],
    "values": {
        "city": "New York"
    }
}
```

#### Delete Records
- `POST /unlink`

Request body:
```json
{
    "model": "res.partner",
    "ids": [1, 2, 3]
}
```

#### Call Method
- `POST /call`

Request body:
```json
{
    "model": "res.partner",
    "method": "name_search",
    "args": ["John"],
    "kwargs": {"limit": 10}
}
```

#### Get Models
- `POST /models`

Request body:
```json
{
    "filter": "res"
}
```

#### Get Fields
- `POST /fields`

Request body:
```json
{
    "model": "res.partner"
}
```

#### Count Records
- `POST /count`

Request body:
```json
{
    "model": "res.partner",
    "domain": [["is_company", "=", true]]
}
```

## Running the Server

### Local Development
```bash
python -m odoo_mcp_server
```

The server will start on `http://localhost:8000` by default.

### Docker
```bash
docker-compose up
```

### Environment Variables

You can set default Odoo connection parameters:
- `ODOO_URL` - Default Odoo server URL
- `ODOO_DATABASE` - Default database name
- `ODOO_USERNAME` - Default username
- `ODOO_PASSWORD` - Default password
- `PORT` - HTTP server port (default: 8000)

## Testing

Use the provided test script:
```bash
python test_http_api.py
```

Or test with curl:
```bash
# Connect
curl -X POST http://localhost:8000/connect \
  -H "Content-Type: application/json" \
  -d '{"url": "https://demo.odoo.com", "database": "demo", "username": "demo", "password": "demo"}'

# Search partners
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"model": "res.partner", "limit": 5}'
```

## Integration with Odoo

This HTTP API can be easily integrated into Odoo modules using Python's `requests` library or Odoo's built-in HTTP client capabilities.