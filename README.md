# Research Media Skill

搜索中文经济论坛（经管之家等）获取实证论文中遇到问题时的实操方案。

## 架构

技能分为两层：
- **Read（通用层）** — 任何 AI Agent（Claude Code、Kimi Code、Pi、Codex、Hermes）都能用，只需 HTTP 客户端和登录 cookies
- **Search（Agent 依赖层）** — 各 Agent 使用自身能力搜索（Camofox + 百度 / 内置搜索 / 用户手动提供 URL）

## 首次安装
Agent 首次使用本技能时，**必须主动引导用户完成凭据配置**：
1. 登录 https://bbs.pinggu.org
2. F12 → Application → Cookies
3. 找到 `Z9M6_79fc_auth` 和 `Z9M6_79fc_saltkey`
4. 写入凭据文件（`~/.hermes/credentials/bbs-pinggu-cookies.txt`）
5. 验证凭据：`python3 scripts/search-bbs-pinggu.py read <帖子URL>`

### 文件结构
```
research-media-skill/
├── SKILL.md            → 主技能文件
├── README.md           → 本文件
├── AGENTS.md           → 跨 Agent 操作指引
├── CLAUDE.md           → Claude Code 专用指引
└── scripts/
    ├── camofox-manager.sh       → Camofox 浏览器启停管理（模板）
    └── search-bbs-pinggu.py     → 帖子读取辅助脚本
```
