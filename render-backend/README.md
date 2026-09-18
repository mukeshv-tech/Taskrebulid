# TaskRebuild Render Backend
This is the backend API for TaskRebuild.

## Deployment to Render
1. Connect this repo to Render.
2. Select the `render-backend` folder as the root directory.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
