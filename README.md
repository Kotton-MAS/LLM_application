# Personal LLM Assistant - セットアップ手順

## 1. 環境構築

- 必要なもの
  - Python 3.9 以上（推奨: 3.11）
  - uv（高速 Python パッケージマネージャー）
  - Anthropic API Key

## 2. 仮想環境の作成と依存関係のインストール（一括実行）

```bash
uv sync
```

- uv を使って直接実行

```bash
uv run streamlit run app.py
```

- または、仮想環境を有効化してから実行

```bash
source .venv/bin/activate # Mac/Linux
streamlit run app.py
# ブラウザで http://localhost:8501 が自動的に開きます。
```

## 3. 使い方

- アバターの選択

  - サイドバーから以下の 3 つのアバターを選択可能:

- 🌸 メンタルサポート: 共感的な対話、心のケア
- 💻 技術アドバイザー: 技術的な質問・相談
- 📋 秘書: スケジュール管理、タスク整理

- 基本機能
  - チャット形式で会話
  - 会話履歴は自動保存
  - アバターごとに会話履歴が分離
  - API 使用量の追跡（実装予定）

### 4. ファイル構成

```
project/
├── app.py # メインアプリケーション
├── database.py # データベース操作
├── avatar_configs.py # アバター設定
├── pyproject.toml # プロジェクト設定・依存関係
├── .python-version # Python バージョン指定
├── .env # 環境変数（要作成）
├── llm_app.db # SQLite データベース（自動生成）
├── uv.lock # 依存関係ロックファイル（自動生成）
└── README.md # このファイル

```

## 5. uv コマンド

- 新しいパッケージの追加

```bash
uv add package-name
```

- 開発用パッケージの追加

```bash
uv add --dev package-name
```

- 依存関係の更新

```bash
uv sync --upgrade
```

- 仮想環境内でコマンド実行

```bash
uv run python script.py
```

- 依存関係の確認

```bash
uv pip list
```

- 依存関係の問題が発生した場合
- ロックファイルを削除して再同期

```bash
rm uv.lock
uv sync
```

## 実装予定機能

- 現在の基本実装に以下の機能を追加予定:

  - 使用量の可視化ダッシュボード
  - スケジュール管理機能（LLM 連動）
  - 会話履歴の検索・エクスポート
  - より詳細な統計情報
