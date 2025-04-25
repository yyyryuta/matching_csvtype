"""
AIビジネスマッチングエージェント起動スクリプト
環境変数の読み込みとサーバー起動
"""

import os
from dotenv import load_dotenv
from app import app

# .env ファイルから環境変数を読み込み
load_dotenv()

if __name__ == '__main__':
    # 環境変数から設定を読み込み
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    # APIキーの確認
    if not os.environ.get('OPENAI_API_KEY'):
        print("警告: OPENAI_API_KEYが設定されていません。アプリケーションは起動しますが、マッチング機能は動作しません。")
    
    # アプリケーション起動
    app.run(debug=debug_mode, host=host, port=port)