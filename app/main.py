import requests
from fastapi import FastAPI, Request, HTTPException
from typing import Dict
import logging

# config.pyからトークンやAPIエンドポイントをインポート
from app.config import LINE_CHANNEL_ACCESS_TOKEN, BACKEND_API_URL
from app.CuriosityLogRepository import CuriosityLogRepository
from app.interest_response_generator import InterestResponseGenerator

app = FastAPI()

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LINEのWebhookエンドポイント
@app.post("/webhook")
async def webhook(request: Request) -> str:
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
   
    repo = CuriosityLogRepository()
    generator = InterestResponseGenerator()
    events = body.get("events", [])
    for event in events:
        # テキストメッセージの場合のみ処理
        if event.get("type") == "message" and event.get("message", {}).get("type") == "text":
            user_id = event.get("source", {}).get("userId")
            message_text = event.get("message", {}).get("text")
            
            logger.info(f"[LINE] user_id={user_id}, message='{message_text}'")
            repo.insert_log(
                user_id=user_id,
                speaker_type=1,
                message=message_text,
                msg_cate=101,
                msg_type=1
            )

            # 全体要約を作成
            #all_summary = repo.get_latest_messages(limit=100)
            my_text = repo.get_latest_my_messages_joined(user_id=user_id, limit=100, format="raw")
            my_summary = generator.summarize_messages(my_text)
            joined_other_text = repo.get_latest_messages_joined(user_id=user_id, limit=100, format="raw")
            other_summary = generator.summarize_messages(joined_other_text)
            logger.info(f"[My要約] summary='{my_summary}'")
            logger.info(f"[全体要約] summary='{other_summary}'")

            # AIによる返しを生成
            push_text = generator.generate_response(message_text, my_summary, other_summary)
            
            # LINEのプッシュメッセージAPIでユーザーに返信
            push_payload = {
                "to": user_id,
                "messages": [
                    {
                        "type": "text",
                        "text": push_text
                    }
                ]
            }
            push_response = requests.post(
                "https://api.line.me/v2/bot/message/push",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
                },
                json=push_payload
            )
            if push_response.status_code != 200:
                logger.error(f"プッシュメッセージ送信失敗: {push_response.text}")
    
    return "OK"

# 既存のユーザーアクションをログ出力するエンドポイント
@app.post("/api/v1/user-actions")
async def post_useractions(request: Request) -> Dict[str, str]:
    try:
        data = await request.json()
        logger.info(f"Received user action data: {data}")
        return {"status": "success", "message": "Data received and logged"}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

