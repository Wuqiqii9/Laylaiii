# Layla 中东 AI 角色互动情报机器人

每天早上 08:30（北京时间）自动生成并推送一份钉钉群日报。

这不是普通新闻机器人，而是给 Layla 项目使用的产品情报助手。它会持续关注中东 AI 角色互动产品、沙特/海湾市场、阿语本地化、方言与人设匹配，以及可以落到产品迭代里的功能灵感。

## 关注内容

- 竞品：PolyBuzz、CrushOn.AI、Character.AI、Talkie、Chai、Replika、Janitor AI、Emochi、Linky
- 市场：沙特阿拉伯优先，兼顾埃及、阿联酋、泛海湾阿语用户
- 语言：Hejazi、Najdi、Khaleeji、Egyptian、MSA、Arabic-English code-switching
- 产品：角色创建、角色推荐、关系进阶、语音、记忆、多人场景、酒馆/lounge/private room 玩法
- 风险：沙特文化边界、内容尺度、性别表达、宗教语境、方言错位

## 文件结构

```text
laylaii-dingtalk-bot/
├── main.py
├── requirements.txt
├── README.md
├── config/
│   └── topics.json
├── prompts/
│   └── daily_report.md
└── .github/
    └── workflows/
        └── daily_report.yml
```

## 必须配置的 GitHub Secrets

进入仓库页面：

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

添加：

| Secret 名称 | 说明 |
| --- | --- |
| `DINGTALK_WEBHOOK` | 钉钉群机器人 Webhook URL |
| `DINGTALK_SECRET` | 钉钉群机器人加签 Secret |
| `AIHUBMIX_API_KEY` | AIHubMix API Key |

建议添加：

| Secret 名称 | 说明 |
| --- | --- |
| `AIHUBMIX_BASE_URL` | AIHubMix API 地址，默认 `https://aihubmix.com/v1` |
| `AIHUBMIX_MODEL` | 模型名，默认 `gpt-4o-mini` |
| `SERPER_API_KEY` | 用于搜索实时资料。没有它也能跑，但最新事实会标注“待验证”。 |

## 定时运行

GitHub Actions 使用 UTC 时间。

```yaml
cron: "30 0 * * *"
```

这等于北京时间每天 08:30。

## 手动测试

在 GitHub 仓库页面：

```text
Actions -> Layla 每日情报日报 -> Run workflow
```

运行后等待 1-2 分钟，查看钉钉群是否收到消息。

## 本地测试

只生成内容、不推送钉钉：

```bash
DRY_RUN=true AIHUBMIX_API_KEY=你的key python main.py
```

完整推送需要再配置：

```bash
DINGTALK_WEBHOOK=你的webhook
DINGTALK_SECRET=你的secret
```

## 后续扩展

- 增加 App Store / Google Play 评论抓取
- 增加 Reddit、TikTok、X 趋势关键词监控
- 每日阿语表达沉淀到语言资产库
- 每周一自动生成周报
- 接入内部用户反馈和产品数据
