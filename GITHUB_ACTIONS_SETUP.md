# GitHub Actions Setup Guide

This project is configured to run automatically every day using GitHub Actions.

## 🔧 Setup Instructions

### Step 1: Configure GitHub Secrets

Go to your GitHub repository settings and add the following secrets:

**Settings → Secrets and variables → Actions → New repository secret**

Add these 4 secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `AWS_ACCESS_KEY_ID` | Your AWS Access Key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Your AWS Secret Access Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region for S3 bucket | `us-east-1` |
| `S3_BUCKET_NAME` | Name of your S3 bucket | `boutiqaat-data` |

### Step 2: Verify Workflow File

The workflow file is located at: `.github/workflows/daily-scraper.yml`

It's already configured to:
- ✅ Run daily at 2 AM UTC
- ✅ Allow manual triggers
- ✅ Upload results as artifacts
- ✅ Send notifications on failure

### Step 3: Test the Setup

**Option 1: Manual Trigger (Recommended for first test)**

1. Go to **Actions** tab in your GitHub repository
2. Click on **"Daily Boutiqaat Scraper"** workflow
3. Click **"Run workflow"** dropdown
4. Click the green **"Run workflow"** button

**Option 2: Wait for Scheduled Run**

The workflow will automatically run daily at 2 AM UTC (you can change this in the workflow file).

### Step 4: Monitor Execution

1. Go to **Actions** tab
2. Click on the latest workflow run
3. View logs in real-time
4. Download artifacts (results JSON and logs) when completed

## 📅 Schedule Configuration

The scraper runs daily at 2 AM UTC by default. To change the schedule:

Edit `.github/workflows/daily-scraper.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Minute Hour Day Month DayOfWeek
```

**Common schedules:**
- `'0 2 * * *'` - Every day at 2 AM UTC
- `'0 */6 * * *'` - Every 6 hours
- `'0 0 * * 0'` - Every Sunday at midnight
- `'0 9 * * 1-5'` - Weekdays at 9 AM UTC

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

## 🎯 Manual Execution

You can run the scraper manually anytime:

1. Go to **Actions** tab
2. Select **"Daily Boutiqaat Scraper"**
3. Click **"Run workflow"**
4. Select branch (usually `main`)
5. Click **"Run workflow"** button

## 📊 Output & Results

After each run:

### S3 Bucket
All data is uploaded to:
```
s3://your-bucket-name/year=YYYY/month=MM/day=DD/
```

### GitHub Artifacts
Results are saved as artifacts for 30 days:
- `pipeline_results_YYYYMMDD.json` - Statistics and summary
- `boutiqaat_scraper.log` - Detailed logs

To download artifacts:
1. Go to workflow run
2. Scroll to **Artifacts** section
3. Click to download

## 🔍 Troubleshooting

### Workflow Not Running

**Issue**: Workflow doesn't run on schedule
- **Cause**: Scheduled workflows may not run in inactive repos
- **Solution**: Make a commit or run manually to keep repo active

### AWS Credentials Error

**Issue**: `Unable to locate credentials`
- **Cause**: GitHub secrets not configured
- **Solution**: Verify all 4 secrets are added correctly (see Step 1)

### S3 Upload Fails

**Issue**: `Access Denied` when uploading to S3
- **Cause**: AWS credentials lack S3 permissions
- **Solution**: Grant your AWS key these permissions:
  - `s3:PutObject`
  - `s3:GetObject`
  - `s3:CreateBucket`
  - `s3:ListBucket`

### Workflow Fails

**Issue**: Workflow fails during execution
- **Solution**: 
  1. Check the workflow logs in Actions tab
  2. Download the log artifact for detailed errors
  3. Common fixes:
     - Update dependencies: Check `requirements.txt`
     - Verify scraping config: Check `scraping_config.py`
     - Website changes: May need to update scraper

## 🔐 Security Best Practices

✅ **DO:**
- Store credentials in GitHub Secrets only
- Use IAM user with minimal required permissions
- Regularly rotate AWS credentials
- Review workflow logs for sensitive data

❌ **DON'T:**
- Commit AWS credentials to code
- Share workflow artifacts publicly
- Use root AWS credentials
- Store credentials in workflow file

## ⚙️ Customizing What Gets Scraped

Edit `scraping_config.py` to customize:
- Categories to scrape
- Brands to scrape  
- Celebrities to scrape

Changes will apply to the next scheduled run or manual trigger.

## 📧 Notifications

### Email Notifications

GitHub sends email notifications for:
- Workflow failures (enabled by default)
- Workflow successes (optional)

Configure in: **Settings → Notifications → Actions**

### Custom Notifications

To add Slack, Discord, or other notifications, add steps to the workflow:

```yaml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 🚀 Advanced Configuration

### Parallel Execution

To scrape multiple sources in parallel, modify the workflow to use matrix:

```yaml
strategy:
  matrix:
    type: [categories, brands, celebrities]
```

### Conditional Execution

Run only on certain days:

```yaml
- name: Check if should run
  if: github.event.schedule == '0 2 * * 1'  # Only Mondays
```

### Multiple Schedules

Add multiple schedule triggers:

```yaml
schedule:
  - cron: '0 2 * * *'   # Daily at 2 AM
  - cron: '0 14 * * *'  # Daily at 2 PM
```

## 📝 Workflow Logs

View detailed logs:
1. Go to workflow run
2. Click on job name (e.g., "scrape")
3. Expand steps to see output
4. Download full log from artifacts

## 🎓 Learning Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Expression Generator](https://crontab.guru/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

## 🆘 Getting Help

If you encounter issues:
1. Check workflow logs in Actions tab
2. Review the troubleshooting section above
3. Verify all GitHub secrets are configured
4. Test locally first (see README.md for local setup)
5. Open an issue with workflow logs attached

## ✅ Checklist

Before going live:

- [ ] GitHub secrets configured (all 4)
- [ ] Test workflow runs successfully
- [ ] S3 bucket accessible
- [ ] Scraping config customized
- [ ] Notifications configured
- [ ] Schedule set to desired time
- [ ] Monitor first few runs

You're all set for automated daily scraping! 🎉
