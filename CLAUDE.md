# CLAUDE.md — Claude Code 专用指引

## 两种使用场景

### 场景 A：在 Hermes Agent 内部调度（推荐）
由 Hermes 统一管理 Camofox 浏览器和搜索流程。Claude Code 作为执行层，负责读取和解析帖子内容。

### 场景 B：独立使用 Claude Code

Claude Code 独立运行时，用自身 web 搜索能力查找经管之家帖子：
1. 搜索 `site:bbs.pinggu.org <关键词>`
2. 从结果提取 thread URL
3. 用 curl + cookies 读取正文
4. 提取内容并总结

## 引导用户配置（首次使用）

```
请配置经管之家论坛的登录 cookies：
1. 打开 https://bbs.pinggu.org 并登录
2. F12 → Application → Cookies → bbs.pinggu.org
3. 复制 Z9M6_79fc_auth 和 Z9M6_79fc_saltkey 的值
4. 写入凭据文件（如 ~/.hermes/credentials/bbs-pinggu-cookies.txt）
```

格式：
```
Z9M6_79fc_auth=<从浏览器复制的值>
Z9M6_79fc_saltkey=<从浏览器复制的值>
```

## 读取帖子
推荐使用辅助脚本（自动处理 cookie 检查、续期、GBK 解码、内容提取）：
```bash
python3 scripts/search-bbs-pinggu.py read "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html"
```

或手动 curl（需自行确保 cookies 有效）：
```bash
curl -sL --max-time 20 \
  -A "Mozilla/5.0" \
  --cookie ~/.hermes/credentials/bbs-pinggu-cookies.txt \
  "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html" \
  | iconv -f gbk -t utf-8
```

## 内容提取
- 帖子正文在 `<td class="t_f" id="postmessage_XXXXX">` 中
- 过滤广告（「赵安豆老师微信」「送您全额奖学金」等）
- 页面编码 GBK，需转 UTF-8

## 禁止事项
- 不得在无凭据时伪造结果
- 不得在技能文件中写入凭据值
- cookies 过期时：Hermes 场景下 `search-bbs-pinggu.py read` 会自动从 Camofox 会话续期；其他场景提示用户手动重新导出
