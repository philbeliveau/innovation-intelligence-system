# Railway PostgreSQL Backup Configuration

## Overview

Railway provides automated daily backups for PostgreSQL databases. This document describes how to configure and use Railway's backup features for the Innovation Intelligence System experiments database.

## Automated Backups

### Configuration

Railway automatically creates daily snapshots of your PostgreSQL database:

- **Frequency:** Daily (automatic)
- **Retention:**
  - Free tier: 7 days
  - Paid tiers: 30 days
- **Timing:** Backups run automatically during low-traffic hours

### Accessing Backups

1. **Via Railway Dashboard:**
   - Navigate to: Railway Dashboard → Project → Database Service
   - Click on "Backups" tab
   - View list of available snapshots with timestamps

2. **Via Railway CLI:**
   ```bash
   railway service backups list
   ```

### Restore from Backup

**Via Dashboard:**
1. Go to Database Service → Backups
2. Select desired backup snapshot
3. Click "Restore" button
4. Confirm restoration (this will overwrite current database)

**Via CLI:**
```bash
# List backups
railway service backups list

# Restore from specific backup
railway service backups restore <backup-id>
```

## Manual Backup Strategy

In addition to Railway's automated backups, the system supports manual backups to Vercel Blob storage for long-term retention.

### Manual Backup via Cleanup Script

The cleanup script includes backup functionality:

```bash
# Create manual backup before cleanup (with archival to Vercel Blob)
python backend/scripts/cleanup_old_experiments.py --dry-run

# Archive without cleanup
python -c "
from backend.app.prisma_client import PrismaAPIClient
from backend.experimentation.export.backup_manager import backup_experiments, archive_to_blob
import asyncio

async def manual_backup():
    client = PrismaAPIClient()
    backup_path = await backup_experiments(client, compress=True)
    blob_url = await archive_to_blob(backup_path)
    print(f'Backup uploaded to: {blob_url}')

asyncio.run(manual_backup())
"
```

### Manual Backup via Gradio UI

The Gradio experimentation UI includes a "Backup to Vercel Blob" button that:
1. Exports all experiments to compressed JSON
2. Uploads to Vercel Blob storage
3. Returns download link

## Environment Variables

Required for manual backup to Vercel Blob:

```bash
# Railway Environment Variables
DATABASE_URL=postgresql://...  # Provided by Railway
VERCEL_BLOB_READ_WRITE_TOKEN=vercel_blob_...  # From Vercel Dashboard
```

## Backup Verification

### Test Backup Integrity

```bash
# Verify Railway backup
railway service backups list

# Verify manual backup
python -c "
from backend.experimentation.export.backup_manager import verify_backup
import asyncio

async def verify():
    result = await verify_backup('/path/to/backup.json.gz')
    print(f'Valid: {result[\"valid\"]}')
    print(f'Experiments: {result[\"total_experiments\"]}')

asyncio.run(verify())
"
```

## Disaster Recovery Procedure

### Full Recovery from Railway Backup

1. **Restore Database from Railway:**
   ```bash
   railway service backups restore <backup-id>
   ```

2. **Verify Database Integrity:**
   ```bash
   # Connect to database
   railway run psql $DATABASE_URL

   # Check experiment count
   SELECT COUNT(*) FROM experiments;

   # Check recent experiments
   SELECT run_id, timestamp, quality_tag FROM experiments
   ORDER BY timestamp DESC LIMIT 10;
   ```

3. **Test Application Connectivity:**
   ```bash
   # Test Next.js API
   curl -X GET https://innovation-web-rho.vercel.app/api/experiments?page=1&pageSize=5
   ```

### Restore from Vercel Blob Archive

If Railway backups are unavailable, restore from Vercel Blob:

```bash
# Download archive from Vercel Blob
curl -o backup.json.gz https://blob.vercel-storage.com/backups/archive.json.gz

# Restore using backup manager
python -c "
from backend.app.prisma_client import PrismaAPIClient
from backend.experimentation.export.backup_manager import restore_from_backup
import asyncio

async def restore():
    client = PrismaAPIClient()
    stats = await restore_from_backup(client, 'backup.json.gz', skip_existing=True)
    print(f'Restored: {stats[\"restored_count\"]} experiments')

asyncio.run(restore())
"
```

## Backup Best Practices

1. **Regular Verification:**
   - Test restore procedure monthly
   - Verify backup integrity weekly

2. **Retention Policy:**
   - Railway: Keep automated daily backups (7-30 days)
   - Vercel Blob: Keep manual archives for 1 year
   - Local: Keep critical backups offline

3. **Before Major Changes:**
   - Create manual backup before schema migrations
   - Create manual backup before bulk deletions
   - Test restore in development environment first

4. **Monitor Backup Health:**
   ```bash
   # Check Railway backup status
   railway service backups list | head -5

   # Verify latest backup timestamp
   railway service backups list --json | jq '.[0].createdAt'
   ```

## Troubleshooting

### Backup Not Created

**Symptoms:** No backups appear in Railway dashboard

**Solutions:**
1. Verify database service is running: `railway service status`
2. Check service logs: `railway logs`
3. Contact Railway support if backups missing > 48 hours

### Restore Fails

**Symptoms:** Restore operation fails or times out

**Solutions:**
1. Check database size and Railway service tier limits
2. Verify sufficient disk space
3. Try restoring to a new database service
4. Contact Railway support for assistance

### Manual Backup Upload Fails

**Symptoms:** `archive_to_blob()` raises IOError

**Solutions:**
1. Verify `VERCEL_BLOB_READ_WRITE_TOKEN` is set
2. Check Vercel Blob storage quota
3. Verify network connectivity
4. Check blob token permissions (read/write required)

## Monitoring

### Backup Metrics to Track

- **Railway Backups:** Daily backup count (should be 1/day)
- **Vercel Blob Archives:** Monthly archive count
- **Backup Size:** Monitor growth trends
- **Restore Success Rate:** Test quarterly

### Alerts to Configure

1. **Missing Railway Backup:**
   - Alert if no backup created in 48 hours
   - Check: `railway service backups list`

2. **Vercel Blob Quota:**
   - Alert at 80% quota usage
   - Check: Vercel Dashboard → Storage

3. **Large Backup Size:**
   - Alert if backup > 100MB (indicates data growth)
   - Consider implementing data retention policy

## References

- **Railway Backup Docs:** https://docs.railway.app/databases/postgresql#backups
- **Vercel Blob Storage:** https://vercel.com/docs/storage/vercel-blob
- **Story 11.4b:** `/docs/stories/11.4b.database-export-retention-backup.md`
- **Cleanup Script:** `/backend/scripts/cleanup_old_experiments.py`
- **Backup Manager:** `/backend/experimentation/export/backup_manager.py`
