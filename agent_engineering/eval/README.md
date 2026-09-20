# 候选人需要实现的评测框架

本目录只给出验收契约，不提供现成 runner、case 或 scorer。评测框架本身是本题交付物之一，场景也由候选人根据工程审计自行设计。

## 最低要求

评测框架需要满足以下条件。

1. 提供一条可重复执行的命令，例如 `make eval`。
2. 每个 case 独立运行，能够固定模型、参数、随机种子和代码版本。
3. 默认支持不消耗真实算力的 offline 模式，可使用 mock、FakeModel、replay 或等价方案。
4. 支持单独运行真实 Bohrium case；真实 case 不得在普通单元测试中自动提交付费任务。
5. case 输入、期望状态和评分规则使用结构化格式保存。
6. scorer 至少读取数据库、trace 和工具副作用，不能只比较最终自然语言答案，也不能只依赖 LLM-as-judge。
7. 输出机器可读的逐题结果和汇总指标。
8. baseline 与 improved 使用同一套 case、配置和评分规则。

## 场景要求

至少自行设计 8 个有区分度的 case，覆盖以下类型：

- 正常任务与输入校验
- 外部系统失败、超时或结果未知
- 重复请求、重试或并发副作用
- 安全、权限或人工批准
- 服务重启后的状态恢复
- 至少 1 个已真实执行过的 Bohrium CLI 场景

真实场景可以保存脱敏后的 replay fixture，供离线回归使用；最终报告仍须给出真实 job ID、执行时间、CLI 版本、最终状态和结果文件校验值，以证明它不是纯 mock。

## 建议输出

```text
eval/
├── README.md
├── cases/                  # 候选人设计
├── fixtures/               # 脱敏 replay 数据
├── runner.*                # 候选人实现
└── results/
    ├── baseline/
    │   ├── results.json
    │   └── metrics.json
    └── improved/
        ├── results.json
        └── metrics.json
```

不得为了提高分数修改 baseline gold、mock 行为或真实执行记录。需要调整评分规则时，应保留变更前后的版本并说明原因。
