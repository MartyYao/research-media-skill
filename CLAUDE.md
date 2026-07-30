# CLAUDE.md — Claude Code 专用指引

Claude Code 可通过本技能搜索中文经济论坛，获取实证问题实操方案。

## 工作流

### 步骤 1：读取技能文件
```
read_file("SKILL.md")
```

### 步骤 2：引导用户配置凭据（首次使用）
用户凭据存储在 `~/.hermes/credentials/bbs-pinggu-cookies.txt`（需用户自行创建）。
内容格式：
```
# 经管之家登录 cookies
Z9M6_79fc_auth=<从浏览器复制的值>
Z9M6_79fc_saltkey=<从浏览器复制的值>
```

引导用户：
1. 在浏览器打开 https://bbs.pinggu.org/ 并登录
2. F12 → Application → Cookies → bbs.pinggu.org
3. 复制 `Z9M6_79fc_auth` 和 `Z9M6_79fc_saltkey` 的值
4. 写入 `~/.hermes/credentials/bbs-pinggu-cookies.txt`

### 步骤 3：搜索
使用 Camofox 浏览器打开百度搜索：
```
browser_navigate("https://www.baidu.com/s?wd=site%3Abbs.pinggu.org+<关键词>")
```
从搜索结果中提取帖子链接。

### 步骤 4：读取帖子
```
curl -sL --max-time 20 \
  -A "Mozilla/5.0" \
  --cookie ~/.hermes/credentials/bbs-pinggu-cookies.txt \
  "https://bbs.pinggu.org/thread-XXXXXXX-1-1.html" \
  | iconv -f gbk -t utf-8
```

### 步骤 5：提取内容
帖子正文在 `<td class="t_f" id="postmessage_XXXXX">` 中。
提取中文文本块，过滤广告（「赵安豆老师微信」「送您全额奖学金」等）。

## 禁止事项
- 不得在无凭据时尝试伪造结果
- 不得在技能文件中硬编码凭据值
- 不得假设 cookies 永久有效（过期后引导用户续期）
