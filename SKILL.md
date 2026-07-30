---
name: research-media-skill
description: 搜索经管之家(bbs.pinggu.org)等中文论坛获取实证实操方案。触发：Stata/计量/平行趋势/DID/回归问题。
---

# Research Media Skill

## 概述

本技能让 AI Agent 能够搜索中文经济论坛（如经管之家 bbs.pinggu.org）并读取帖子正文，在写论文遇到实证问题时从中文论坛获取实操经验，而非仅凭模型知识回答。

设计为可扩展结构，后续可添加更多媒体源（如微信公众号、知乎等）。

## 使用前提

### 运行环境
- macOS（依赖本地脚本和 Camofox 浏览器）
- Camofox 浏览器（搜索用）：`./scripts/camofox-manager.sh start`
- 登录凭据：各源可能需要账号 cookies（详见各源说明）

### 首次安装引导

**安装完成后，Agent 必须主动引导用户完成以下配置：**

1. **Camofox 浏览器**：检查是否已安装。如需安装，引导用户参考 Camofox 文档。
2. **各媒体源凭据**：对每个启用的媒体源，Agent 应：
   - 告诉用户需要什么凭据（如论坛 cookies）
   - 说明如何从浏览器导出（F12 → Application → Cookies）
   - 指导用户将凭据保存到 `~/.hermes/credentials/<source-name>.txt`
   - 验证凭据有效性
   - 告知用户凭据过期后如何更换

## 源配置

### 源 1：经管之家（bbs.pinggu.org）

#### 前置要求
- Camofox 浏览器
- 登录 cookies 文件：`~/.hermes/credentials/bbs-pinggu-cookies.txt`
  - 需要包含 `Z9M6_79fc_auth` 和 `Z9M6_79fc_saltkey` 两个键
  - 格式：每行 `Name=Value`，注释行以 `#` 开头
  - 从浏览器开发者工具（F12 → Application → Cookies → bbs.pinggu.org）导出

#### 搜索流程
1. **准备浏览器**：本技能依赖 Camofox 或兼容的浏览器自动化工具。
   - Hermes Agent 用户：`./scripts/camofox-manager.sh start`
   - 其他 Agent：确保浏览器工具可用（如 Playwright、Puppeteer 等），监听端口 9377
2. **搜索**：
   - Claude Code/ Hermes：使用 `browser_navigate` 打开百度搜索
   - 其他 Agent：用 HTTP 客户端请求百度搜索页面并解析结果
   ```
   https://www.baidu.com/s?wd=site%3Abbs.pinggu.org+<关键词>
   ```
3. 从搜索结果提取帖子 URL（格式：`thread-XXXXXXX-1-1.html`）
4. 用 curl + cookies 读取帖子正文（见下节）
5. 关闭浏览器：`./scripts/camofox-manager.sh stop`（或相应命令）

#### 读取帖子
```bash
curl -sL --max-time 20 \
  -A "Mozilla/5.0" \
  --cookie ~/.hermes/credentials/bbs-pinggu-cookies.txt \
  "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html" \
  | iconv -f gbk -t utf-8
```

或使用辅助脚本：
```bash
python3 scripts/search-bbs-pinggu.py read "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html"
```

#### 注意事项
- 百度是中国大陆唯一可用的搜索引擎（Google 不可用）
- 帖子编码为 GBK，需转为 UTF-8
- 正文中含广告/邀请信息，需过滤
- Cookies 有时效，失效后引导用户重新导出

### 源 2：[预留-新源名称]

#### 前置要求
> 待添加。每个新源必须包含 Prerequisites、Search Workflow、Read Workflow、Pitfalls 子结构。

---

## 辅助脚本

### search-bbs-pinggu.py
路径：`scripts/search-bbs-pinggu.py`
功能：读取经管之家帖子正文
用法：`python3 search-bbs-pinggu.py read <帖子URL>`
说明：脚本会读取 `~/.hermes/credentials/bbs-pinggu-cookies.txt` 中的 cookies

---

## 安全说明
- 凭据文件存储位置固定，但值不写入技能代码
- Agent 引导用户自行填写凭据，不得擅自猜测或编造
- 凭据文件权限应设置为 600（仅所有者可读写）
