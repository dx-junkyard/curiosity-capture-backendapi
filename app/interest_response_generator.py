import requests
import logging

# ログ設定（必要に応じてレベルを DEBUG に変更可能）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class InterestResponseGenerator:
    """
    ユーザーの発言に対して、興味・関心・知識・スキルに関連した会話を盛り上げる返答を生成するクラス。
    """

    def __init__(self, model: str = "{AI_MODEL}" , base_url: str = "{AI_URL}"):
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        logging.info(f"InterestResponseGenerator initialized with model: {model} and endpoint: {self.api_url}")

    def _build_prompt(self, user_input: str) -> str:
        """
        入力されたユーザーテキストに対して返答を生成するためのプロンプトを構築する。
        """
        prompt = f"""以下のユーザー発言に対して、その人の興味や知識・スキルについて会話を盛り上げるよう、自然な返答話を振ることでさらに会話が続くような話を日本語で生成してください。

【ユーザー発言】:
{user_input}

【返答】:"""
        logging.debug("Prompt constructed")
        return prompt

    def generate_response(self, user_input: str) -> str:
        """
        ユーザー発言を入力として、Ollama API を使って返答を生成する。
        """
        logging.info(f"Generating response for input: {user_input}")
        prompt = self._build_prompt(user_input)

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

