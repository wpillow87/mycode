@echo off
title 文件移动工具
echo 正在启动文件移动工具...
streamlit run "%~dp0文件移动工具_GUI.py" --server.headless true
pause 