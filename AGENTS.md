# AGENTS.md — 跨 Agent 操作指引

本仓库提供中文经济论坛搜索能力，适用于 Stata/计量经济学实证问题排查。

## 入口点

首次使用时，先读 `SKILL.md` 了解完整工作流和所有媒体源。

## 仓库结构

```
SKILL.md                  → 主技能（工作流 + 所有源配置）
README.md                 → 概述 + 首次安装引导
AGENTS.md                 → 本文件
CLAUDE.md                 → Claude Code 专用
scripts/
  search-bbs-pinggu.py    → 经管之家帖子读取脚本
```

## 通用使用协议

### 1. 首次运行协议（必读）
首次调用本技能时，Agent **必须主动引导用户配置凭据**，不得：
- 假设凭据已存在
- 自行编造凭据路径
- 跳过凭据验证直接使用

正确的引导流程：
```
Agent: "检测到 research-media-skill 首次使用，需要配置以下凭据：
1. Camofox 浏览器（已安装 ✓）
2. 经管之家论坛登录 cookies（需要配置）
   请打开 bbs.pinggu.org 并登录，然后 F12 → Application → Cookies，
   将 Z9M6_79fc_auth 和 Z9M6_79fc_saltkey 按 'Name=Value' 格式写入 ~/.hermes/credentials/bbs-pinggu-cookies.txt"
```

### 2. 凭据验证
配置完凭据后，Agent 应自动验证：
```bash
python3 scripts/search-bbs-pinggu.py read "https://bbs.pinggu.org/thread-7909828-1-1.html"
```
若返回空或报错，告知用户凭据无效并引导重新导出。

### 3. 搜索约定
- 搜索引擎：百度（中国大陆唯一可用）
- 搜索方式：Camofox 浏览器 → www.baidu.com
- 搜索语法：`site:bbs.pinggu.org + 关键词`

### 4. 不伪造原则
- 不伪造论坛帖子内容
- 不编造用户凭据
- 不假设帖子内容（必须实际读取后引用）
- 读取失败时如实报告，不编造替代内容

## 扩展指南

添加新媒体源时：
1. 在 `SKILL.md` 的「源配置」下新增一节
2. 注明前置要求、搜索流程、读取方式、注意事项
3. 更新本文件的「仓库结构」
