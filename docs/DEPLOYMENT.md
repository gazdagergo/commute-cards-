# Deployment Guide

## Environments

| Environment | App | Database | Region | URL |
|-------------|-----|----------|--------|-----|
| **Production** | sociology-learning-pwa | sociology-learning-pwa-db | fra (Frankfurt) | https://sociology-learning-pwa.fly.dev |
| **Staging** | sociology-learning-pwa-staging | sociology-db-staging | ams (Amsterdam) | https://sociology-learning-pwa-staging.fly.dev |

---

## Deploy Commands

### Production

```bash
fly deploy
```

Uses `fly.toml` configuration.

### Staging

```bash
fly deploy --config fly.staging.toml
```

Uses `fly.staging.toml` configuration.

---

## Configuration Files

| File | Environment | Notes |
|------|-------------|-------|
| `fly.toml` | Production | 1GB RAM, Frankfurt |
| `fly.staging.toml` | Staging | 256MB RAM, Amsterdam |

---

## Database Access

### Production

```bash
# SSH into production
fly ssh console

# Run Python DB queries
fly ssh console -C "python -c \"
import os, psycopg
conn = psycopg.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM cards')
print(cur.fetchone())
\""
```

### Staging

```bash
# SSH into staging
fly ssh console --app sociology-learning-pwa-staging

# Run Python DB queries
fly ssh console --app sociology-learning-pwa-staging -C "python -c \"
import os, psycopg
conn = psycopg.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM cards')
print(cur.fetchone())
\""
```

---

## Health Checks

```bash
# Production
curl https://sociology-learning-pwa.fly.dev/health

# Staging
curl https://sociology-learning-pwa-staging.fly.dev/health
```

---

## Workflow

1. **Develop** locally or on a feature branch
2. **Deploy to staging** for testing:
   ```bash
   fly deploy --config fly.staging.toml
   ```
3. **Test** on https://sociology-learning-pwa-staging.fly.dev
4. **Deploy to production** when ready:
   ```bash
   fly deploy
   ```

---

## Troubleshooting

### App scaled to zero

Fly.io auto-scales apps to zero when idle. Wake it up:

```bash
# Production
curl https://sociology-learning-pwa.fly.dev/health

# Staging
curl https://sociology-learning-pwa-staging.fly.dev/health
```

### View logs

```bash
# Production
fly logs

# Staging
fly logs --app sociology-learning-pwa-staging
```

### Check app status

```bash
# Production
fly status

# Staging
fly status --app sociology-learning-pwa-staging
```

---

## Infrastructure Costs

Both environments use minimal resources:

- **App VMs**: Shared CPU, auto-stop when idle (free tier eligible)
- **PostgreSQL**: 1GB volume each (~$0.15/GB/month)

Staging can be stopped entirely when not in use:

```bash
fly scale count 0 --app sociology-learning-pwa-staging
```

Restart when needed:

```bash
fly scale count 1 --app sociology-learning-pwa-staging
```
