### 実行手順

UVインストールと有効化
```terminal

# linux
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

```

UV初期化

```terminal
cd <project name>
uv init
uv install python 3.12 # option
uv add <library name>
```

UV実行
```terminal
uv run <target python file>
```
