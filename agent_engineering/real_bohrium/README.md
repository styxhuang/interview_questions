# 真实 Bohrium CLI 验证

真实平台联调是本题必做项，mock 只能用于快速回归，不能替代真实任务。

> Bohrium CLI 的软件包名是 `@dptech-corp/bohr-cli`，安装后的命令名是 `bohr`。

## 1. 注册与准备

1. 打开 [Bohrium 注册页](https://www.bohrium.com/login?pageType=register)创建账号并登录。新账号可能带有平台赠送的体验金，具体金额和适用范围以账户实际显示为准，不要假设一个固定额度。
2. 创建或加入一个可以提交计算任务的项目，记录 project ID。
3. 在可信终端安装 CLI：

   ```bash
   npm install -g @dptech-corp/bohr-cli@latest
   bohr version
   bohr doctor --offline
   ```

4. 在平台账号设置中生成自己的 AccessKey，只在可信终端完成认证：

   ```bash
   bohr auth login --ak '<your-access-key>'
   bohr auth status --verify
   ```

如果当前 CLI 版本提供浏览器 SSO，也可以直接运行 `bohr auth login`。不要把 AK 粘贴到开发智能体对话、截图、日志、Shell 脚本、`.env` 提交或 Git 历史中。输入 AK 的命令不要复制进报告；只记录“认证成功/失败”和 CLI 版本，不记录密钥值。

5. 在提交任何计算前查询可用余额和当前价格：

   ```bash
   bohr billing balance
   bohr billing pricing
   ```

   先确认体验金或其他可用余额足以覆盖本次最小任务。不得为完成面试题自行充值；余额不足、计价不明确或平台要求的费用超出体验金时，停止提交，保留脱敏证据并联系面试官。

## 2. 选择可用资源

候选人需要通过 CLI 查询当前账号可见的镜像和机型，选择成本最低、能够运行 shell 的 CPU 规格：

```bash
bohr image list --json
bohr machine list -c cpu --json
```

不要照抄一个未经账号验证的镜像或机型。将选定值、当前单价、预计最长运行时间和选择理由记录到 `workpack/EXPERIMENT_LOG.md`，但不要记录 AK。

## 3. 准备并提交最小任务

复制模板并替换 project ID、镜像、机型和唯一任务名：

```bash
cp real_bohrium/job.example.json real_bohrium/job.local.json
bohr job submit -i real_bohrium/job.local.json -p real_bohrium/input/
```

提交前再次确认平台显示的计费信息和自己的停止条件。只提交一次单节点、最低规格 CPU smoke job；模板已把最长运行时间限制为 2 分钟。禁止为了跑通测试申请 GPU 或高规格机器，禁止用真实提交做反复调试。第一次真实运行后应保存脱敏 replay，后续测试全部使用 replay。

提交后必须走完整闭环：

```bash
bohr job describe -j <JOB_ID> --json
bohr job log -j <JOB_ID> -o real_bohrium/results/logs/
bohr job download -j <JOB_ID> -o real_bohrium/results/output/
```

至少验证：最终状态、`result.json` 内容、下载文件校验值、本地 run 与真实 job ID 映射，以及失败时是否留下可诊断 trace。

## 4. 提交证据

在 `REAL_BOHRIUM_REPORT.md` 中记录：

- 注册、项目和认证是否完成（不写 AK）
- `bohr version`
- 执行时间、唯一 job name、job ID 和 project ID
- 使用的镜像与机型
- 提交前后的余额类别、当前单价和预计/实际费用（金额可以按公司要求脱敏，但必须能证明未超预算）
- submit、describe、log、download 的脱敏结果
- 结果文件 SHA-256
- 真实联调暴露的问题，以及它如何进入测试框架

提交前检查 Git 历史中没有任何 AK。真实任务产生的下载目录和 `job.local.json` 已被 `.gitignore` 排除。

参考：[Bohrium CLI 介绍](https://www.bohrium.com/bohr-cli/intro)、[计价说明](https://bohrium-doc.dp.tech/docs/bohrctl/pricing/)、[费用与体验金说明](https://bohrium-doc.dp.tech/docs/userguide/Billing)。
