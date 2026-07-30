# AGENTS.md — 跨 Agent 操作指引

本仓库提供中文经济论坛内容检索能力。分为两层：
- **Read（通用层）** — 任何 Agent 都能用
- **Search（Agent 依赖层）** — 各 Agent 用自己的方式搜索

## 通用协议

### 1. 首次使用引导

首次使用时，Agent **必须主动引导用户配置 cookies**，不得假设已存在或自行编造。

引导标准话术：
```
检测到 research-media-skill 首次使用，需要配置经管之家登录 cookies：
1. 打开 https://bbs.pinggu.org 并登录
2. 按 F12 → Application → Cookies → bbs.pinggu.org
3. 找到 Z9M6_79fc_auth 和 Z9M6_79fc_saltkey 两个键
4. 将值按 'Name=Value' 格式写入凭据文件
```

### 2. 凭据验证

配置完成后验证：
```bash
curl -sL --max-time 20 -A "Mozilla/5.0" \
  --cookie <凭据文件> \
  "https://bbs.pinggu.org/thread-7909828-1-1.html" \
  | iconv -f gbk -t utf-8
```
如果输出为空或报错，提示用户凭据无效。

### 3. 不伪造原则
- 不伪造论坛内容（必须实际读取后引用）
- 不编造用户凭据
- 不假设搜索结果（必须实际搜索后提取）

### 4. 搜索策略（按 Agent 选择）

| Agent | 搜索方式 |
|-------|---------|
| **Hermes Agent** | Camofox + 百度：`browser_navigate` |
| **Claude Code（Hermes 内）** | 同上，使用 Camofox |
| **Claude Code（独立）** | 使用自身 web 搜索能力 |
| **Kimi Code** | 内置互联网搜索，直接索要 `site:bbs.pinggu.org` 结果 |
| **Pi / Codex** | 使用自身 web 搜索工具 |
| **兜底** | 用户手动提供帖子 URL |

### 5. 帖子 URL 格式
所有搜索结果提取目标：`https://bbs.pinggu.org/thread-XXXXXXX-1-1.html`
