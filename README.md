# Research Media Skill

搜索中文经济论坛（经管之家等）获取实证论文中遇到问题时的实操方案。
**Hermes Agent 下 cookies 可自动续期，无需手动维护。**

## 架构

技能分为两层：
- **Read（通用层）** — 任何 AI Agent（Claude Code、Kimi Code、Pi、Codex、Hermes）都能用，只需 HTTP 客户端和登录 cookies
- **Search（Agent 依赖层）** — 各 Agent 使用自身能力搜索（Camofox + 百度 / 内置搜索 / 用户手动提供 URL）

### 自动 cookie 续期（Hermes Agent）

**原理**：用户在 Camofox 浏览器里登录一次经管之家后，Firefox 会把全部 cookies（包括 HttpOnly 的 `Z9M6_79fc_auth`）存到 profile 的 `cookies.sqlite`。脚本从中直接提取，无需登录表单、无需验证码。

当 Hermes Agent 调用 `search-bbs-pinggu.py read <URL>` 读取帖子时，会自动：
1. 检查 cookies 文件是否有效 → 有效则直接读帖
2. 无效 → 从 Camofox profile 的 `cookies.sqlite` 提取 auth cookies → 写入文件 → 继续读帖
3. 全程自动，无需用户操作

**前提**：Camofox 里保持登录态（登录会话与文件 cookies 独立，Camofox 会话有效即可续期）。

## 首次安装

Agent 首次使用本技能时，**必须主动引导用户完成凭据配置**：

### 基础配置（所有 Agent）
1. 登录 https://bbs.pinggu.org
2. F12 → Application → Cookies → bbs.pinggu.org
3. 找到 `Z9M6_79fc_auth` 和 `Z9M6_79fc_saltkey`，复制值
4. 写入 `~/.hermes/credentials/bbs-pinggu-cookies.txt`，并设置权限 `chmod 600`
   ```
   Z9M6_79fc_auth=从浏览器复制的值
   Z9M6_79fc_saltkey=从浏览器复制的值
   ```
5. 验证：`python3 scripts/search-bbs-pinggu.py check`

### 自动续期配置（Hermes Agent 推荐）
1. 在 Camofox 浏览器中打开 https://bbs.pinggu.org 并登录（一次性操作，保持会话即可）
2. 验证：`python3 scripts/search-bbs-pinggu.py login`（从 Camofox 会话提取并写入 cookies）

配置完成后，每次读帖都会自动检查并从 Camofox 会话续期 cookies。

## 文件结构

```
research-media-skill/
├── SKILL.md                       ← 主技能文件
├── README.md                      ← 本文件
├── AGENTS.md                      ← 跨 Agent 操作指引
├── CLAUDE.md                      ← Claude Code 专用指引
└── scripts/
    ├── camofox-manager.sh         ← Camofox 浏览器启停管理（模板）
    └── search-bbs-pinggu.py       ← 帖子读取 + 自动 cookie 续期（从 Camofox 会话提取）
```
