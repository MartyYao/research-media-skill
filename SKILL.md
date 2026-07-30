---
name: research-media-skill
description: 搜索经管之家(bbs.pinggu.org)等中文论坛获取实证实操方案。触发：Stata/计量/平行趋势/DID/回归问题。
---

# Research Media Skill

## 概述

本技能让 AI Agent 能够搜索中文经济论坛（如经管之家 bbs.pinggu.org）并读取帖子正文。

技能分为两个独立能力：
- **Search（搜索帖子）** — Agent 依赖层，各 Agent 用自身能力完成
- **Read（读取正文）** — 通用层，任何有 HTTP 能力的 Agent 均可使用

---

## Read（通用层）：读取经管之家帖子正文

**任何 Agent 都能用**，只需一个 HTTP 客户端和登录 cookies。

### 前置要求

**登录 cookies**：无论哪种 Agent 使用本技能，都需要先让用户配置经管之家的登录 cookies。

引导用户操作（Agent 据此引导用户，不可自行猜测或编造）：
1. 在浏览器打开 https://bbs.pinggu.org 并登录
2. 按 F12 → Application → Cookies → bbs.pinggu.org
3. 找到 `Z9M6_79fc_auth` 和 `Z9M6_79fc_saltkey` 两个键
4. 将它们的值按 `Name=Value` 格式写入凭据文件（每行一个，`#` 开头为注释）
5. 设置文件权限为 `chmod 600`

凭据文件路径：各 Agent 按自身约定存储，推荐 `~/.hermes/credentials/bbs-pinggu-cookies.txt`（Hermes）或自定义位置。

### 读取命令

```bash
curl -sL --max-time 20 \
  -A "Mozilla/5.0" \
  --cookie <凭据文件路径> \
  "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html" \
  | iconv -f gbk -t utf-8
```

或使用辅助脚本（需 Python 环境）：
```bash
python3 scripts/search-bbs-pinggu.py read "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html"
```

### 内容提取
帖子正文在 `<td class="t_f" id="postmessage_XXXXX">` 中。
提取中文文本块，过滤广告关键词（「赵安豆老师微信」「送您全额奖学金」等）。

### 注意事项
- 页面编码为 GBK，需转 UTF-8（`iconv -f gbk -t utf-8`）
- Cookies 有时效，失效后提示用户重新导出
- 不要伪造帖子内容——读取失败时如实报告

---

## Search（Agent 依赖层）：搜索帖子

各 Agent 使用自身能力搜索经管之家的帖子。**核心目标**：找到 `https://bbs.pinggu.org/thread-XXXXXXX-1-1.html` 格式的 URL。

### Hermes Agent

使用 Camofox 浏览器 + 百度搜索：

```bash
./scripts/camofox-manager.sh start
```
然后用 `browser_navigate` 打开：
```
https://www.baidu.com/s?wd=site%3Abbs.pinggu.org+<关键词>
```
从搜索结果中提取帖子 URL，完成后关闭 Camofox：
```bash
./scripts/camofox-manager.sh stop
```

### Claude Code

**方式 A**（在 Hermes 内部运行 Claude Code）：与 Hermes Agent 相同，使用 Camofox。

**方式 B**（独立运行 Claude Code）：使用 Claude Code 自带的 web 搜索能力，搜索 `site:bbs.pinggu.org 关键词`，从结果中提取帖子 URL。

### Kimi Code

Kimi Code 有内置互联网搜索能力。直接在 prompt 中要求：
```
请搜索 site:bbs.pinggu.org 上的相关讨论，把帖子 URL 发给我。
```

### Pi / Codex / 其他 Agent

利用自身具备的 web 搜索工具。如果 Agent 没有搜索能力，可以让用户直接提供帖子 URL（用户在浏览器里搜，把链接给 Agent）。

### 兜底方案（所有 Agent 通用）

如果 Agent 无法自动搜索，**用户可以手动搜索后在对话中提供帖子 URL**，Agent 直接进入 Read 步骤读取正文。

---

## 文件结构

```
research-media-skill/
├── SKILL.md                       ← 本文件
├── README.md                      ← 概述 + 首次安装引导
├── AGENTS.md                      ← 跨 Agent 操作指引
├── CLAUDE.md                      ← Claude Code 专用指引
└── scripts/
    ├── camofox-manager.sh         ← Camofox 浏览器管理（Hermes 专用）
    └── search-bbs-pinggu.py       ← 帖子读取辅助脚本（通用）
```

---

## 安全说明
- 凭据值不写入技能文件。Agent 引导用户自行填写
- 凭据文件权限 `chmod 600`
- 不伪造内容。读取失败时如实报告
