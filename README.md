Personal LLM Assistant - セットアップ手順

1. 環境構築
   必要なもの
   Python 3.9 以上（推奨: 3.11）
   uv（高速 Python パッケージマネージャー）
   Anthropic API Key
   uv のインストール
   bash

# Mac/Linux

curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)

powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# または、pipx を使用

pipx install uv
プロジェクトのセットアップ
bash

# 1. プロジェクトディレクトリに移動

cd personal-llm-assistant

# 2. 仮想環境の作成と依存関係のインストール（一括実行）

uv sync

# 3. 仮想環境の有効化

# Windows

.venv\Scripts\activate

# Mac/Linux

source .venv/bin/activate 2. 環境変数の設定
.env ファイルを作成し、以下を記入:

ANTHROPIC_API_KEY=your_actual_api_key_here
DATABASE_URL=sqlite:///llm_app.db
CLAUDE_SONNET_4_5_INPUT_COST=3.0
CLAUDE_SONNET_4_5_OUTPUT_COST=15.0 3. アプリケーションの起動
bash

# uv を使って直接実行

uv run streamlit run app.py

# または、仮想環境を有効化してから実行

source .venv/bin/activate # Mac/Linux
streamlit run app.py
ブラウザで http://localhost:8501 が自動的に開きます。

4. 使い方
   アバターの選択
   サイドバーから以下の 3 つのアバターを選択できます:

🌸 メンタルサポート: 共感的な対話、心のケア
💻 技術アドバイザー: 技術的な質問・相談
📋 秘書: スケジュール管理、タスク整理
基本機能
チャット形式で会話
会話履歴は自動保存
アバターごとに会話履歴が分離
API 使用量の追跡（実装予定） 5. ファイル構成
project/
├── app.py # メインアプリケーション
├── database.py # データベース操作
├── avatar_configs.py # アバター設定
├── pyproject.toml # プロジェクト設定・依存関係
├── .python-version # Python バージョン指定
├── .env # 環境変数（要作成）
├── llm_app.db # SQLite データベース（自動生成）
├── uv.lock # 依存関係ロックファイル（自動生成）
└── README.md # このファイル 6. 便利な uv コマンド
bash

# 新しいパッケージの追加

uv add package-name

# 開発用パッケージの追加

uv add --dev package-name

# 依存関係の更新

uv sync --upgrade

# 仮想環境内でコマンド実行

uv run python script.py

# 依存関係の確認

uv pip list
次のステップ
現在の基本実装に以下の機能を追加予定:

使用量の可視化ダッシュボード
スケジュール管理機能（LLM 連動）
会話履歴の検索・エクスポート
より詳細な統計情報
トラブルシューティング
uv がインストールされているか確認
bash
uv --version
API Key エラーが出る場合
.env ファイルが正しく作成されているか確認
ANTHROPIC_API_KEY が正しく設定されているか確認
データベースエラーが出る場合
llm_app.db を削除して再起動
SQLite が正しくインストールされているか確認
依存関係の問題が発生した場合
bash

# ロックファイルを削除して再同期

rm uv.lock
uv sync
