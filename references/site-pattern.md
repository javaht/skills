---
domain: weibo.com
aliases: [微博, weibo, 新浪微博]
updated: 2026-05-16
---

## 平台特征

- SPA 架构，虚拟滚动（vue-recycle-scroller）渲染微博列表，DOM 中仅保留约 8 条可见微博
- 反爬严格：外部 curl/脚本调用 API 会被重定向到登录页，即使携带 Cookie 也可能失效
- 需要登录态才能访问完整内容，非登录用户只能看到有限公开微博

## 有效模式

### 内部 API 抓取（推荐，2026-05-16 验证）

通过 CDP eval 在页面上下文中调用微博内部 JSON API：

```
GET /ajax/statuses/mymblog?uid={uid}&page={page}&feature=0&since_id={since_id}
```

- 每页返回 20 条微博，包含 `data.list[]` 和 `data.since_id`（用于下页翻页）
- `page=1` 时 `since_id` 可省略或设为 0
- 每条微博字段：`created_at`、`text`（HTML 格式）、`source`、`reads_count`、`attitudes_count`、`comments_count`、`reposts_count`、`visible`（type=1 公开，其他为仅自己可见）
- 需在 `weibo.com` 页面上下文中执行 fetch，直接访问 API URL 会被返回 `{"error":"Forbidden"}`
- **翻页限制**：`since_id` 链式翻页约 12 页后 API 返回空列表（约 200-300 条）。解决方案：不带 `since_id` 直接按页码访问，可回溯到数年前的微博，但数据稀疏（部分页码返回 0 条），需逐页扫描并去重。建议两阶段策略：Phase 1 用 since_id 链拿近期连续数据，Phase 2 不带 since_id 扫描深层页码。

### CDP Proxy 操作模式

- 通过 `POST /new?url={user_page}` 打开用户主页
- 通过 `POST /eval` 执行 JS 调用内部 API
- 翻页速率 0.3s/页为安全值，过快可能触发风控
- 完成后通过 `/close` 关闭 tab

## 已知陷阱

- CDP eval 的异步 fetch 有超时风险（约 15s），建议逐页循环调用而非一次性 async 循环
- 直接导航到 API URL 会返回 "Forbidden"——必须从微博页面上下文发起请求
- Cookie 包含 XSRF-TOKEN，失效后需刷新微博页面重新获取
- 微博正文存储在 HTML 字段中（含 `<br/>`、`<img>` 标签），需解析为纯文本
- `visible.type` 为 1 时是公开微博，非 1 时为仅自己可见