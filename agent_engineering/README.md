# Bohrium Agent 工程化面试题

这是一个可直接运行的智能体工程化面试 starter repo。候选人需要在现有原型上完成工程化改造，而不是从零搭一个普通 CRUD 服务。

原型覆盖以下链路：

```text
FastAPI -> Agent Harness -> Model -> Skills/Tools -> mock/real bohr CLI
                         \-> SQLite/MySQL + run trace
```

当前 starter 可以启动，并能通过 mock CLI 完成最简单的提交与查询。它不是参考答案；候选人需要用证据识别问题、建立自己的评测框架、改进运行时，并完成一次真实 Bohrium CLI 任务闭环。

建议第一步把 [`INITIAL_PROMPT.md`](INITIAL_PROMPT.md) 交给你使用的开发智能体。Prompt 会先建立项目地图、基线和 `workpack/` 题包记录，再进入修改。

## 5 分钟启动

环境要求：Python 3.9+。默认使用 SQLite，因此不需要先安装 MySQL。

```bash
cd agent_engineering
make install
make init-db
make run
```

服务启动后：

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/v1/runs \
  -H 'content-type: application/json' \
  -d '{"message":"提交任务 image=python:3.11 command=python_main.py cpu=2 memory_gb=4 scenario=happy","client_request_id":"demo-001"}'
```

`POST /v1/runs` 返回 `run_id` 后，可查询运行轨迹：

```bash
curl http://127.0.0.1:8000/v1/runs/<run_id>
```

## MySQL 模式

本地快速开发默认使用 SQLite；用 Docker Compose 可以验证 MySQL 8：

```bash
docker compose up --build
```

Compose 会把 API 暴露在 `localhost:8000`，MySQL 暴露在 `localhost:3307`。应用通过 `DATABASE_URL` 切换数据库，因此也可连接已有 MySQL：

```bash
DATABASE_URL='mysql+pymysql://user:password@127.0.0.1:3306/bohrium_agent' make run
```

## 基础测试

```bash
make test
```

基础测试只证明 starter 能安装和运行，不代表系统工程质量达标。

## 候选人自建评测框架

仓库不提供现成 eval runner、case 或 scorer。候选人需要按照 [`eval/README.md`](eval/README.md) 自行设计测试框架和至少 8 个场景，先保存 baseline，再在完全相同的条件下生成 improved 结果。

评测必须检查数据库、trace、工具参数和外部副作用，不能只判断最终回答是否相似。

## 真实 Bohrium 场景

真实平台联调为必做项。候选人需要从[注册页](https://www.bohrium.com/login?pageType=register)创建 Bohrium 账号、创建或加入项目、取得自己的 AccessKey、安装 `bohr` CLI，并完成一次最低成本的真实 CPU 任务：提交、查询、日志、下载和结果校验。详见 [`real_bohrium/README.md`](real_bohrium/README.md)。

AccessKey 只允许保存在可信终端或 CLI 的本地凭据存储中，禁止写入代码、Prompt、日志、截图、fixture、报告或 Git 历史。

新账号可能带有平台赠送的体验金，具体金额和适用范围以账号实际页面为准。提交前必须先用 `bohr billing balance` 查询余额、用 `bohr billing pricing` 核对当前价格；只允许提交一次最小 CPU smoke job，后续回归使用脱敏 replay。不得为完成本题自行充值，若体验金不足应保留证据并联系面试官。

## 目录结构

```text
app/              FastAPI 入口和请求模型
agent/            model、harness、skill loader
skills/           三个示例 Agent Skill
tools/            Bohrium 工具适配层
mock_boh_cli/     可确定复现超时、OOM、注入等场景的本地 CLI
db/               SQLAlchemy 模型和 repository
eval/             候选人需要实现的评测框架契约
real_bohrium/     真实 bohr CLI 联调说明与最小输入
workpack/         项目地图、基线、问题与实验记录规范
tests/            基础单元/集成测试
INITIAL_PROMPT.md 开发智能体初始化 Prompt
```

完整任务要求见 [`面试者版_波尔计算智能体工程化.md`](面试者版_波尔计算智能体工程化.md)。
