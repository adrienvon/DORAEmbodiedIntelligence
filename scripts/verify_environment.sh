#!/bin/bash

# 环境验证脚本
# 验证 uv 虚拟环境和所有依赖是否正确配置

set -e

echo "========================================"
echo "CARLA-DORA 环境验证"
echo "========================================"
echo

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "1. 检查 Python 版本..."
.venv/bin/python --version

echo
echo "2. 检查核心依赖..."
.venv/bin/python -c "
import numpy
import pygame
import PIL
import msgpack
import yaml
import pyarrow
print('  ✅ numpy:', numpy.__version__)
print('  ✅ pygame:', pygame.__version__)
print('  ✅ PIL/pillow:', PIL.__version__)
print('  ✅ msgpack:', msgpack.version)
print('  ✅ pyyaml:', yaml.__version__)
print('  ✅ pyarrow:', pyarrow.__version__)
"

echo
echo "3. 检查 CARLA Leaderboard 依赖..."
.venv/bin/python -c "
import dictor
import requests
import cv2
import tabulate
import pexpect
import transforms3d
import networkx
print('  ✅ dictor')
print('  ✅ requests:', requests.__version__)
print('  ✅ opencv-python:', cv2.__version__)
print('  ✅ tabulate:', tabulate.__version__)
print('  ✅ pexpect:', pexpect.__version__)
print('  ✅ transforms3d:', transforms3d.__version__)
print('  ✅ networkx:', networkx.__version__)
"

echo
echo "4. 检查 CARLA Python API (通过 PYTHONPATH)..."
if [ -z "$CARLA_ROOT" ]; then
    echo "  ⚠️  CARLA_ROOT 未设置，跳过 CARLA API 检查"
else
    CARLA_EGG="$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.14-py3.7-linux-x86_64.egg"
    if [ -f "$CARLA_EGG" ]; then
        PYTHONPATH="$CARLA_EGG:$PYTHONPATH" .venv/bin/python -c "
import carla
print('  ✅ CARLA Python API 成功导入')
print('  📦 Egg 文件:', '$CARLA_EGG')
"
    else
        echo "  ⚠️  CARLA egg 文件未找到: $CARLA_EGG"
    fi
fi

echo
echo "5. 检查 DORA..."
if command -v dora &> /dev/null; then
    echo "  ✅ dora CLI: $(dora --version 2>&1 | head -1)"
else
    echo "  ⚠️  dora CLI 未安装"
fi

if .venv/bin/python -c "import dora" 2>/dev/null; then
    .venv/bin/python -c "import dora; print('  ✅ dora-rs Python 包已安装')"
else
    echo "  ⚠️  dora-rs Python 包未安装"
fi

echo
echo "========================================"
echo "环境验证完成！"
echo "========================================"
echo
echo "虚拟环境位置: $PROJECT_ROOT/.venv"
echo "Python 解释器: $PROJECT_ROOT/.venv/bin/python"
echo "管理工具: uv (基于 Conda py37 的 Python 3.7.16)"
