# JDMemberCloseAccount

## Describe
该分支仅用于从`main`分支拉取最新代码并利用`pyinstall`进行打包，不会将其合并至`main`

## Step

# mac
pyinstaller --onefile --icon=logo.icns --clean --noconfirm main.py
pyinstaller --clean --noconfirm --onefile main.spec

# win
pyinstaller --windowed --onefile --icon=logo.ico --clean --noconfirm main.py
pyinstaller --clean --noconfirm --windowed --onefile main.spec
## Copy file

1. 复制 `dirvers` 目录

2. 复制 `config.yaml` 文件