# Gradio Experimentation Lab - Deployment Guide

## Quick Start (Local Testing)

```bash
# 1. Install dependencies
cd backend/experimentation
pip install -r requirements.txt

# 2. Run simple demo (works immediately)
python gradio_simple_demo.py

# 3. Or run full version (requires pipeline integration)
python gradio_pipeline_lab.py
```

## Deploy to Railway

### Option 1: Add to Existing Backend Service

```bash
# 1. Update your main requirements.txt
cd backend
echo "gradio==4.44.0" >> requirements.txt
echo "PyPDF2==3.0.1" >> requirements.txt

# 2. Create a startup script
cat > start.sh << 'EOF'
#!/bin/bash
# Start Gradio in background
python experimentation/gradio_pipeline_lab.py &
# Start main FastAPI app
uvicorn app.main:app --host 0.0.0.0 --port $PORT
EOF

chmod +x start.sh

# 3. Update Railway start command to: ./start.sh

# 4. Deploy
railway up
```

### Option 2: Separate Railway Service (Recommended)

```bash
# 1. Create new Railway service
railway service create gradio-lab

# 2. Create Dockerfile for Gradio
cat > Dockerfile.gradio << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY experimentation/requirements.txt .
RUN pip install -r requirements.txt

COPY experimentation/ ./experimentation/
COPY pipeline/ ./pipeline/

EXPOSE 7860

CMD ["python", "experimentation/gradio_pipeline_lab.py"]
EOF

# 3. Deploy Gradio service
railway up --service gradio-lab

# 4. Set environment variables in Railway dashboard
# - Add any API keys needed for pipeline stages
```

## Environment Variables

Add these to Railway dashboard:

```bash
# For pipeline stages
OPENROUTER_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here  # If using Stage 0 enrichment

# For Gradio (optional)
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SHARE=true  # Creates public URL
```

## Access Your Gradio App

### Local
```
http://localhost:7860
```

### Railway (after deployment)
```
https://your-service-name.up.railway.app
```

### Share Link (if GRADIO_SHARE=true)
```
Gradio will output: Running on public URL: https://xxxxx.gradio.live
Share this with your founder for testing
```

## Integrating with Your Pipeline

Replace mock functions in `gradio_pipeline_lab.py`:

```python
# Instead of mock implementation
from backend.pipeline.stages.stage_0 import enrich_brand_profile
from backend.pipeline.stages.stage_1 import decompose_trends
from backend.pipeline.stages.stage_2 import synthesize_insights
# ... etc

# Use actual pipeline functions
enriched_brand = await enrich_brand_profile(brand_profile, stage_0_version)
trends = await decompose_trends(report_text, stage_1_version)
insights = await synthesize_insights(trends, enriched_brand, stage_2_version)
```

## Features Your Founder Can Use

1. **Upload Any PDF**: Drag & drop trend reports
2. **Add Notes**: Every experiment can have founder commentary
3. **Save Experiments**: All runs saved to SQLite database
4. **Compare Versions**: A/B test different stage configurations
5. **See All Outputs**: Toggle to show/hide intermediate stages
6. **Track Quality**: Automatic scoring of outputs

## Database Location

Experiments are saved to `experiments.db` in the working directory.

To backup/download from Railway:

```bash
railway run --service gradio-lab -- cat experiments.db > local_backup.db
```

## Troubleshooting

### PDF Upload Not Working
- Check PyPDF2 is installed
- Ensure file size < 10MB
- Try different PDF if corrupted

### Gradio Not Accessible
- Check Railway logs: `railway logs --service gradio-lab`
- Ensure port 7860 is exposed in Dockerfile
- Try setting GRADIO_SHARE=true for public URL

### Pipeline Stages Failing
- Add error handling to each stage
- Check API keys in environment variables
- Review stage version compatibility

## Next Steps

1. Start with `gradio_simple_demo.py` for immediate testing
2. Integrate real pipeline stages one by one
3. Add authentication if needed: `auth=("founder", "password")`
4. Customize quality scoring metrics for your needs
5. Export successful experiments to production pipeline