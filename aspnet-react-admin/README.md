# ASP.NET + React Admin Demo

A minimal admin app: ASP.NET Core 8 minimal API with token-based auth and
in-memory user CRUD, plus a Vite + React + TypeScript SPA.

## Run (single host — recommended)

The React app is served as static files by the API on one port.

```bash
# 1. Build the React bundle into AdminApi/wwwroot
cd admin-ui
npm install
npm run build
mkdir -p ../AdminApi/wwwroot
cp -r dist/* ../AdminApi/wwwroot/

# 2. Start the API (serves UI + API on one port)
cd ../AdminApi
dotnet run --urls http://0.0.0.0:5080
```

Open http://localhost:5080 — login with `admin` / `admin123`.

## Run (dev mode — two ports, hot reload)

```bash
# Terminal 1
cd AdminApi && dotnet run --urls http://localhost:5080

# Terminal 2
cd admin-ui && npm run dev   # http://localhost:5173
```

In dev mode set `const API = 'http://localhost:5080'` in
`admin-ui/src/App.tsx`. CORS is preconfigured for `localhost:5173`.

## Public tunnel

To share the running app over the internet, tunnel port 5080:

```bash
# cloudflared (no account)
cloudflared tunnel --url http://localhost:5080

# or ngrok
ngrok http 5080
```

The single-host build means one tunnel covers both the UI and API.

## Endpoints

- `POST /api/auth/login` → `{ token, username, role }`
- `GET  /api/users`       (Bearer auth)
- `POST /api/users`       (Bearer auth)
- `PUT  /api/users/{id}`  (Bearer auth)
- `DELETE /api/users/{id}` (Bearer auth)
- `GET  /api/stats`       (Bearer auth)
- `GET  /swagger`         OpenAPI UI

## Notes

This is a demo. Auth is a hardcoded `admin` / `admin123` returning a
static token; the user store is in-memory and resets on restart. Do not
deploy as-is.
