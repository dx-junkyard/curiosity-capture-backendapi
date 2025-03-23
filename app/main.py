from fastapi import FastAPI, Request
from typing import List, Dict, Any
import logging

app = FastAPI()

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/v1/user-actions")
async def post_useractions(request: Request) -> Dict[str, str]:
    """
    受け取ったJSONデータをログに出力する
    """
    try:
        data = await request.json()
        logger.info(f"Received user action data: {data}")
        return {"status": "success", "message": "Data received and logged"}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"status": "error", "message": str(e)}
