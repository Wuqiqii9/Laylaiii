# 阿里云函数计算部署说明

用于把 Layla 钉钉日报从 GitHub Actions 定时任务迁移到阿里云函数计算，解决 GitHub schedule 延迟导致早上收不到的问题。

## 创建函数

1. 打开阿里云控制台，进入“函数计算 FC”。
2. 创建服务，例如：`layla-dingtalk-bot`。
3. 创建函数，选择：
   - 运行时：Python 3.10 或 Python 3.11
   - 创建方式：从零开始 / 上传代码包
   - 代码包：上传 `laylaii-dingtalk-bot-fc.zip`
   - 请求处理程序：`fc_handler.handler`
   - 内存：512 MB
   - 超时时间：180 秒

## 环境变量

在函数配置里添加这些环境变量：

```text
AIHUBMIX_API_KEY=你的 AIHubMix API Key
AIHUBMIX_BASE_URL=你的 AIHubMix Base URL
AIHUBMIX_MODEL=你的模型名称
DINGTALK_WEBHOOK=新钉钉群机器人的 Webhook
DINGTALK_SECRET=新钉钉群机器人的加签 Secret
SERPER_API_KEY=你的 Serper API Key
```

如果暂时没有 `SERPER_API_KEY`，可以不填；日报会跳过实时搜索，并标注最新事实待验证。

## 定时触发器

创建定时触发器：

- 触发器类型：定时触发器
- 触发方式：Cron 表达式
- 时区：Asia/Shanghai，如果控制台提供时区选择
- 时间：每天北京时间 08:30

如果控制台使用 UTC Cron，则填写：

```text
0 30 0 * * *
```

含义：UTC 00:30，即北京时间 08:30。

如果控制台使用北京时间 Cron，则填写：

```text
0 30 8 * * *
```

## 验证

部署完成后，在函数控制台点“测试函数”。

预期结果：

- 函数执行成功。
- 新钉钉群收到一条 Layla 日报。

验证成功后，可以回到 GitHub Actions 删除或停用 `schedule`，只保留手动触发作为备用。
