# 模块二 步骤隔离规则

> 子Agent隔离，每个Agent只知当前步骤
>
> **加载时机**：编排器派发任务时，每条规则注入对应Agent

| ID | 条款 | 注给谁 |
|:---:|------|------|
| C22 | 步骤隔离：每个子Agent只做当前步骤，不知道下一步。整改后的任务作为新任务派发。 | 全体子Agent |
| C23 | 开发Agent只知本任务，不知道code-qa和func-qa存在。 | 开发Agent |
| C24 | code-qa Agent只知验收当前代码，不知道func-qa存在。 | code-qa |
| C25 | func-qa Agent（GLM-5V）只知验收，不知道前面步骤细节。 | func-qa |
