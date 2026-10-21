# FusionPBX Pilot API

REST API for managing [FusionPBX](https://www.fusionpbx.com) domains and extensions, and for provisioning SIP credentials to softphones/webphones. Built with FastAPI on top of [fusionpbx-pilot](https://github.com/marujofln/fusionpbx-pilot), which drives the FusionPBX web UI through Selenium.

## How it works

```
client ──(OAuth2 bearer)──> FastAPI ──> Selenium Grid (Firefox) ──> FusionPBX web UI
                              │
                              ├──> Fief (auth server: token validation, user info)
                              └──> Redis (provisioning cache)
```

- **Authentication** is delegated to a [Fief](https://www.fief.dev) server (OAuth2 authorization code). Each endpoint requires specific permissions, e.g. `pbx:domain:read`, `pbx:extension:write`.
- **FusionPBX access** happens through a remote Selenium WebDriver: every request opens a browser session in the Selenium Grid, logs in to FusionPBX and performs the operation through the UI.
- **Provisioning** reads the user's `pbx_domain`, `pbx_extension`, `pbx_transport` and `display_name` fields from Fief, fetches the extension's SIP password from FusionPBX and caches it in Redis, so subsequent calls don't hit the browser.

## Endpoints

All routes are under `/v1`. Interactive docs are served at `/docs`.

| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/me` | authenticated | Access token info |
| GET | `/domains` | `pbx:domain:read` | List domains |
| GET | `/domain/{domain}` | `pbx:domain:read` | Get a domain |
| PUT | `/domain/{domain}` | `pbx:domain:write` | Create a domain |
| PATCH | `/domain/{domain}/name/{new_name}` | `pbx:domain:write` | Rename a domain |
| DELETE | `/domain/{domain}` | `pbx:domain:write` | Delete a domain |
| GET | `/domain/{domain}/extensions` | `pbx:extension:read` | List extensions |
| GET | `/domain/{domain}/extension/{extension}` | `pbx:extension:read` | Get an extension |
| PUT | `/domain/{domain}/extension/{extension}` | `pbx:extension:write` | Create an extension |
| PATCH | `/domain/{domain}/extension/{extension}/name/{new_name}` | `pbx:extension:write` | Rename an extension |
| DELETE | `/domain/{domain}/extension/{extension}` | `pbx:extension:write` | Delete an extension |
| PUT | `/domain/{domain}/extension/{extension}/voicemail` | `pbx:extension:write` | Toggle voicemail |
| PUT | `/domain/{domain}/extension/{extension}/voicemail/mail_to/{mail_to}` | `pbx:extension:write` | Set voicemail e-mail |
| PATCH | `/domain/{domain}/extension/{extension}/password/{new_password}` | `pbx:extension:write` | Set SIP password |
| GET | `/provisioning` | `pbx:domain:read`, `pbx:extension:read` | SIP credentials for the authenticated user |

Example `/provisioning` response:

```json
{
  "display_name": "John Doe",
  "user": "1001",
  "password": "********",
  "domain": "pbx.example.com",
  "uri": "wss://pbx.example.com:7443"
}
```

`uri` depends on the user's `pbx_transport` field: `wss`, `udp`, `tcp` or `tls`.

## Configuration

Settings are read from environment variables or a `.env` file (see [`.env.sample`](.env.sample)):

| Variable | Default | Description |
|---|---|---|
| `FUSIONPBX_URL` | — | FusionPBX base URL |
| `FUSIONPBX_USER` / `FUSIONPBX_PASSWORD` | — | FusionPBX admin credentials |
| `FUSIONPBX_WSS_PORT` / `_UDP_PORT` / `_TCP_PORT` / `_TLS_PORT` | 7443 / 5060 / 5060 / 5061 | Ports used to build the SIP URI |
| `RESTAPI_HOST` / `RESTAPI_PORT` | `0.0.0.0` / `8000` | Listen address |
| `RESTAPI_ORIGINS` | localhost variants | Allowed CORS origins (JSON list) |
| `FIEF_BASE_URL` | — | Fief server URL (required) |
| `FIEF_CLIENT_ID` / `FIEF_CLIENT_SECRET` | — | Fief OAuth2 client |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` | `redis` / `6379` / `0` | Redis connection |
| `REDIS_USERNAME` / `REDIS_PASSWORD` | empty | Redis auth (optional) |
| `SELENIUM_GRID_URL` | `http://selenium-hub:4444/wd/hub` | Selenium Grid endpoint |
| `SELENIUM_HEADLESS` | `true` | Run Firefox headless |

## Running

### Docker Compose

The compose file brings up the API, Redis, a Selenium Grid (hub + 2 Firefox nodes) and Caddy as a TLS reverse proxy. It mounts `/etc/fusionpbx-api/settings.conf` as the API's `.env`:

```bash
git clone https://github.com/marujofln/fusionpbx_pilot_api.git
cd fusionpbx_pilot_api
sudo mkdir -p /etc/fusionpbx-api
sudo cp .env.sample /etc/fusionpbx-api/settings.conf   # then edit it
# adjust the Caddy hostname in docker-compose.yml
docker compose up -d --build
```

### Local development

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/), plus reachable Redis and Selenium Grid instances:

```bash
uv sync
cp .env.sample .env   # then edit it
./run.sh              # fastapi run fusionpbx_pilot_api/services/restapi.py
```

## Notes

- Each request spins up a browser session, so operations take seconds rather than milliseconds. Size the Selenium Grid (`SE_NODE_MAX_SESSIONS`, replicas) for the expected concurrency.
- The SIP password is passed in the URL path by `PATCH .../password/{new_password}`, so keep it behind TLS and avoid logging request paths.
