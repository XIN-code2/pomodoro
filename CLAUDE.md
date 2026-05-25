# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

一个基于 Python tkinter 的单文件番茄钟桌面应用，界面为中文。

## 运行

```bash
python3 pomodoro.py
```

无需安装额外依赖，tkinter 是 Python 标准库的一部分。

## 架构

单文件应用 `pomodoro.py`，包含一个 `PomodoroApp` 类：

- **模式 (mode)**: `"focus"` (专注) 和 `"break"` (休息)，计时结束后自动切换
- **状态 (state)**: `"idle"` → `"running"` → `"paused"`，由开始/暂停/重置按钮控制
- **计时机制**: 使用 `tk.after(1000, callback)` 实现每秒更新，非多线程
- **预设**: 专注时长 [15, 25, 30, 45, 60] 分钟，休息时长 [3, 5, 10, 15] 分钟，仅在 idle 状态下可切换

配色和尺寸常量集中在文件顶部。`_build_ui()` 负责构建全部界面组件，窗口固定 420×480 居中显示。
