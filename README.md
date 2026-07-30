# Research Media Skill

搜索中文经济论坛（经管之家等）获取实证论文中遇到问题时的实操方案。

## 适用场景
- Stata / 计量经济学问题排查
- 平行趋势检验失败
- DID 结果不显著或符号相反
- 想要查看中文论坛上的类似案例和讨论

## 使用方式

### 首次安装
Agent 首次使用本技能时，**必须主动引导用户完成凭据配置**：
1. 运行 `./scripts/camofox-manager.sh status` 检查 Camofox
2. 引导用户经管之家论坛 cookies：
   - 浏览器打开 https://bbs.pinggu.org/ 并登录
   - F12 → Application → Cookies
   - 找到 `Z9M6_79fc_auth` 和 `Z9M6_79fc_saltkey`
   - 写入 `~/.hermes/credentials/bbs-pinggu-cookies.txt`
3. 验证凭据：读取一个帖子确认能获取正文

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
