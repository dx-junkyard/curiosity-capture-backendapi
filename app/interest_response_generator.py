import requests
import logging
from app.config import AI_MODEL, AI_URL

# ログ設定（必要に応じてレベルを DEBUG に変更可能）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class InterestResponseGenerator:
    """
    ユーザーの発言に対して、興味・関心・知識・スキルに関連した会話を盛り上げる返答を生成するクラス。
    """

    def __init__(self, model: str = AI_MODEL, base_url: str = AI_URL):
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        logging.info(f"InterestResponseGenerator initialized with model: {model} and endpoint: {self.api_url}")

    def _build_prompt(self, user_input: str, my_summary: str, summary: str) -> str:
        """
        入力されたユーザーテキストに対して返答を生成するためのプロンプトを構築する。
        """
        prompt = f"""以下の【ユーザー発言】に対して、楽しい会話が続くよう【本人の発言サマリー】と、【他の人達のサマリー】を考慮して返答を生成してほしい。

【ユーザー発言】:
{user_input}

【本人の発言サマリー】:
{my_summary}

【他の人達のサマリー】:
{summary}

【返答】:"""
        logging.debug("Prompt constructed")
        return prompt

    def generate_response(self, user_input: str, my_summary: str, summary: str) -> str:
        """
        ユーザー発言を入力として、Ollama API を使って返答を生成する。
        """
        logging.info(f"Generating response for input: {user_input}")
        prompt = self._build_prompt(user_input,str(my_summary), str(summary))

        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            logging.info("Response successfully generated")
            return result

        except requests.RequestException as e:
            logging.error(f"API呼び出しに失敗しました: {e}")
            return "すみません、うまく返答を生成できませんでした。"
        except Exception as e:
            logging.exception(f"予期せぬエラーが発生しました: {e}")
            return "すみません、予期しない問題が発生しました。"

    def summarize_user_messages(self, user_id: str, messages: list[dict]) -> str:
        """
        ユーザーの複数発言から、興味・関心・スキルをまとめる要約を生成。
        """
        message_lines = [f"- {msg['message']}" for msg in messages if msg.get("message")]
        if not message_lines:
            return "発言が見つかりませんでした。"

        joined_messages = "\n".join(message_lines)

        prompt = f"""以下はあるユーザーの発言ログの一覧です。このユーザーが何を行っているのか要約をだけおしえてください。

【ユーザーの発言ログ】:
{joined_messages}

【まとめ】:"""

        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            response.raise_for_status()
            return response.json().get("response", "").strip()

        except Exception as e:
            logging.error(f"[{user_id}] 要約失敗: {e}")
            return "すみません、ユーザー情報の要約に失敗しました。"

    def summarize_messages(self, messages: list[str]) -> str:
        """
        ユーザー全体の発言ログを要約する（興味・知識・スキルの傾向など）。
        """
        joined = "\n".join(f"- {msg}" for msg in messages if msg.strip())
    
        prompt = f"""以下は複数のユーザーの発言です。どのような会話がおこなわれているのか、簡潔におしえてください。
    
    【ユーザー発言一覧】:
    {joined}
    
    【まとめ】:"""
    
        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            logging.error(f"[✗] 要約生成失敗: {e}")
            return "すみません、要約できませんでした。"
