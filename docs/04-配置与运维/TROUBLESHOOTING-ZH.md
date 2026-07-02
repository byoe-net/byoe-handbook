# BYOE 故障排查手册（Troubleshooting）

---

## 1. 启动失败

### 现象

`byoe web` 启动报端口占用。

### 处理

```bash
byoe web --port 8080
```

---

## 2. 模型调用失败

### 现象

401 / 403 / 连接超时。

### 排查

1. 检查 API Key 是否正确
2. 检查 `OPENAI_BASE_URL` 是否可访问
3. 检查模型名是否存在（`byoe models`）

---

## 3. 调度任务不触发

### 排查

1. 查看任务是否为 active
2. 确认 heartbeat 是否开启
3. 检查 trigger 格式是否正确

支持示例：

```text
interval:30s
interval:5m
interval:1h
once:2026-07-01T09:00:00
*/15 * * * *
```

---

## 4. 调度任务反复失败

### 建议

1. 在 TaskPanel 查看错误次数
2. 调整重试策略（base/multiplier/max/max_errors）
3. 查看调度审计事件定位失败阶段

相关 API：

```http
GET  /api/schedule/retry
POST /api/schedule/retry
GET  /api/schedule/audit?limit=100
```

---

## 5. 会话恢复异常

### 排查

```bash
byoe sessions
byoe sessions show <id>
```

若会话损坏：删除异常会话后重试。

```bash
byoe sessions delete <id>
```

---

## 6. Windows 路径与权限问题

建议：

1. 使用 PowerShell 运行 `byoe`
2. 避免在受限系统目录执行
3. 尽量在项目根目录运行 `byoe init`

---

## 7. 浏览器端显示“服务断连”

### 排查

1. 确认 BYOE 进程仍在运行
2. 刷新状态或重新连接
3. 检查反向代理/防火墙是否拦截 SSE

---

## 8. 最小自检命令

```bash
byoe --version
byoe doctor
byoe models
byoe web --port 8080
```

如仍无法解决，请携带以下信息提交问题：

- BYOE 版本
- 操作系统
- 模型提供商与 base_url
- 复现步骤
- 关键报错日志
