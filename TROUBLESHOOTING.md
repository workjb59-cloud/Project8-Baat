# Troubleshooting Guide

## Common Issues and Solutions

### 1. Import Errors

#### Error: `ModuleNotFoundError: No module named 'requests'`
**Cause**: Dependencies not installed  
**Solution**:
```bash
pip install -r requirements.txt
```

#### Error: `No module named 'src'`
**Cause**: Running from wrong directory  
**Solution**:
```bash
# Make sure you're in the project root
cd /path/to/Project8-Baat
python -m src.main
```

### 2. AWS/S3 Errors

#### Error: `InvalidAccessKeyId` or `SignatureDoesNotMatch`
**Cause**: Wrong AWS credentials  
**Solution**:
1. Verify credentials in GitHub Secrets (Settings → Secrets)
2. Check AWS Access Key ID and Secret Access Key
3. Ensure no extra spaces or newlines in secrets
4. Generate new credentials if necessary

#### Error: `NoSuchBucket`
**Cause**: S3 bucket doesn't exist or wrong name  
**Solution**:
```bash
# List available buckets
aws s3 ls

# Create bucket if needed
aws s3 mb s3://your-bucket-name
```

#### Error: `AccessDenied`
**Cause**: IAM user doesn't have S3 permissions  
**Solution**: Add S3 policy to IAM user:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    }
  ]
}
```

### 3. Web Scraping Errors

#### Error: `ConnectTimeout` or `ReadTimeout`
**Cause**: Website not responding or slow connection  
**Solution**:
```python
# In config.py, increase timeout
REQUEST_TIMEOUT = 60  # Increase from 30
RETRY_DELAY = 5      # Increase from 2
```

#### Error: `403 Forbidden` when scraping
**Cause**: Website blocking bot traffic  
**Solution**:
```python
# In scraper.py, update User-Agent
self.session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
```

#### Error: `404 Not Found` for images
**Cause**: Image URL expired or inaccessible  
**Solution**: The scraper handles this gracefully - check logs:
```bash
# Look for warning messages about image downloads
python -m src.main 2>&1 | grep -i "error\|warning"
```

### 4. GitHub Actions Issues

#### Workflow not running
**Cause**: GitHub Actions not enabled or schedule issue  
**Solution**:
1. Enable Actions: Settings → Actions → General → Allow all actions
2. Check workflow file syntax:
   ```bash
   # View status at: Actions tab
   ```

#### "secrets.AWS_ACCESS_KEY_ID is not defined"
**Cause**: Secret name mismatch  
**Solution**:
- Go to Settings → Secrets
- Ensure exact names: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`

#### Workflow fails with "resource exhausted"
**Cause**: Too many concurrent scraping requests  
**Solution**:
```python
# In config.py, add delay between requests
time.sleep(2)  # Add to scraper loops
```

### 5. File and Encoding Issues

#### Error: `UnicodeDecodeError`
**Cause**: Encoding issues with Arabic text  
**Solution**:
```python
# Already handled in openpyxl, but verify:
response = requests.get(url, encoding='utf-8')
```

#### Excel file corrupted or won't open
**Cause**: File still being written  
**Solution**:
1. Wait for process to complete
2. Check file size > 0 bytes
3. Re-run if needed

### 6. Memory and Performance Issues

#### Error: `MemoryError` or process killed
**Cause**: Too many products loaded at once  
**Solution**:
```python
# Process in batches in src/main.py
# Or limit products per category in config.py
```

#### Slow performance scraping
**Cause**: Network issues or server overload  
**Solution**:
```python
# In config.py
REQUEST_TIMEOUT = 45
RETRY_DELAY = 5
# Also check network connection
```

### 8. Local Testing Issues

#### "Error: ModuleNotFoundError" even after install
**Cause**: Virtual environment not activated  
**Solution**:
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verify with (venv) prefix in terminal
```

#### `python: not found`
**Cause**: Python not installed or not in PATH  
**Solution**:
```bash
# Check Python installation
python --version
python3 --version

# Use correct command (python3 on some systems)
python3 -m src.main
```

## Diagnostic Commands

### Test AWS Connection
```bash
aws s3 ls s3://your-bucket-name/
```

### Test Website Access
```bash
curl https://www.boutiqaat.com/
```

### Check Python Packages
```bash
pip list | grep -E "requests|beautifulsoup4|boto3|openpyxl"
```

### View Detailed Logs
```bash
python -m src.main 2>&1 | tee scraper.log
```

### Check GitHub Actions Logs
1. Go to repository Actions tab
2. Click on workflow run
3. Expand job logs
4. Search for ERROR or WARNING

### Validate Configuration
```bash
python test_setup.py
```

## Performance Optimization

### Reduce Scraping Time
1. **Skip image downloads**: Comment out image upload code
2. **Limit categories**: Modify scraper to process selected categories
3. **Increase timeouts**: Allow more time for requests

### Reduce S3 Costs
1. **Enable versioning**: S3 → Versioning
2. **Set lifecycle policies**: Auto-delete old data
3. **Use S3 Intelligent-Tiering**: Automatic cost optimization

## Getting Help

### Check Logs First
```bash
# GitHub Actions logs
# Settings → Actions secrets check
# Workflow run logs → Expand steps

# Local logs
grep -i "error" scraper.log
```

### Common Questions

**Q: How often does it run?**
A: By default, daily at 2 AM UTC (configurable in workflow)

**Q: Can I run it manually?**
A: Yes! Actions tab → "Run workflow" button

**Q: How much data will be stored?**
A: Depends on number of products × image size × categories

**Q: Can I change the S3 path structure?**
A: Yes, edit `S3_IMAGES_PATH` and `S3_EXCEL_PATH` in config.py

**Q: What if the website structure changes?**
A: Update CSS selectors in scraper.py and test locally first

### Further Support

- 📖 Read full [README.md](README.md)
- 🚀 Check [QUICKSTART.md](QUICKSTART.md)
- 🐛 Create GitHub Issue
- 💬 Check existing Issues

---

**Last Updated**: 2026-03-03
