# Academic Hygiene

**VeriLoop 项目级长期硬约束**
**VeriLoop Project-Level Hard Constraint**

Status: APPROVED
Applies from: H1-01B — Rules Lock
Gate type: BLOCKING
Owner: lingfeng-an
Last reviewed: 2026-10-07

---

## 0. 文件性质

本文件不是普通文档。

它是 VeriLoop 项目级的 **Gate**：任何阶段产出在进入下一阶段之前，
必须先通过本文件定义的 Hygiene Check。检查不通过，不得推进。

本文件适用于 H1-01B 及之后的所有阶段，并追溯适用于 H1-01A 已产出的
v0.1 基线（v0.1 已通过检查，作为参考样本保留）。

本文件一旦批准，修改需走与实验协议同级的 Owner 批准流程。

---

## 1. 目的

VeriLoop 是一个公开研究项目。项目文件、Git 历史、提交信息、tag、
文档、数据集和代码注释，都构成研究成果的一部分，会被审稿人、复现者、
合作方和公众阅读。

本文件的目的是：

1. 清除与科研内容无关的**工具痕迹**和**环境痕迹**。
2. 保证项目在任何机器上 clone 后都**可复现、专业、整洁**。
3. 防止 AI 辅助工具的输出意外泄漏到研究材料中，干扰读者对研究
   过程和作者身份的判断。

**明确边界：**

- 本文件**不是**为了伪造“人类独立完成”。
- 本文件**不要求**隐藏 AI 作为研发助手的使用事实。
- 本文件**只要求**清除与科研内容无关的工具名称、路径和执行痕迹。
- AI 在 VeriLoop 中的角色是**外部研发助手**，不是研究项目的组成部分。

科研贡献的披露、作者署名、致谢和 AI 使用声明，另行由 Owner 决定，
不在本文件管辖范围内。

---

## 2. 适用范围

适用于 VeriLoop 项目内的所有内容，包括但不限于：

- 文件内容（Markdown、代码、注释、测试、配置）
- 文件名与目录名
- Git 元数据（commit author、committer、tag tagger、remote URL）
- commit message 与 tag message
- README、docs/、experiments/、data/、results/
- Issue、PR、Release 描述（若未来使用）
- 项目内引用的外部链接与截图

不适用于：

- 本地 shell 历史
- AI 工具自身的输出窗口
- Owner 与 AI 之间的私有对话
- 临时草稿文件（但不得进入项目目录）
- Owner 本地维护的外部执行配置（见 §6.3）

---

## 3. 禁止内容

以下内容不得出现在 §2 定义的适用范围内：

### 3.1 AI 工具痕迹

- 任何 AI 助手产品的名称、logo、水印、脚注
- AI 工具生成的提示词、会话记录、日志、截图
- AI 工具的默认署名、模板化输出特征
- 未披露的 AI 生成署名（commit author、tag tagger 等）

### 3.2 个人环境痕迹

- 个人机器绝对路径模式，例如：
  - POSIX 风格的用户主目录前缀（如 `/Users/<name>/...`、`/home/<name>/...`）
  - Windows 风格的用户主目录前缀（如 `C:\Users\<name>\...`）
  - 展开式用户主目录前缀（如 `~/...` 指向具体用户目录时）
- 项目文件不得记录具体用户名、具体主机名、具体主目录路径。
- 主机名、本地用户名、临时目录、缓存路径。
- 特定 IDE、编辑器、操作系统特有的隐藏文件
  （`.DS_Store`、`Thumbs.db`、`*.swp`、`*~`）。

**说明：** 在规则说明、示例或命令用法中作为模式列举出现的
`/Users/...`、`~/...` 等写法，不视为违规；只有当它们指向一个
具体、可识别的个人环境时，才视为违规。

### 3.3 未披露的自动化痕迹

- 自动生成且未标注来源的批量文件
- 未说明用途的脚本、中间产物、缓存文件
- 与科研内容无关的调试输出

**例外说明：**

本文件 §3.1、§3.2、§3.3 在**本文件自身**中的列举，仅作为规则范围
的说明，不构成对上述工具的使用或依赖。本文件不包含任何具体的
AI 工具名称、具体路径或具体主机名。

---

## 4. 允许内容

以下内容允许出现在项目内：

- 项目自定义的匿名身份
  （例如：`lingfeng-an <lingfeng-an@users.noreply.github.com>`）
- 通用工具链名称
  （Python、uv、pytest、ruff、Git、GitHub 等）
- 公开可复现的相对路径
  （`src/`、`tests/`、`docs/`、`data/`、`results/`）
- 明确披露的第三方依赖及其 License
- 明确披露的公开数据来源
- Owner 批准的 AI 使用声明（若未来需要）

---

## 5. Hygiene Gate

Academic Hygiene 是**项目级 Gate**，不是普通文档。

流程如下：

```
任何研发阶段
    ↓
产出写入项目
    ↓
Academic Hygiene Check（§6）
    ↓
PASS ─────────────→ 进入下一阶段
    ↓
   FAIL
    ↓
  STOP
    ↓
  修复
    ↓
  重检
```

**硬性规则：**

1. 检查不通过，不得进入下一阶段。
2. 不得以“先记录、后清理”的方式绕过 Gate。
3. 不得在 Gate 未通过时执行 git commit 或 git push。
4. 修复后必须重跑全部六项检查，不能只重跑失败项。

---

## 6. Hygiene Check 六项清单

每次阶段提交前，执行以下六项。任意一项不通过 → 停止。

### 6.1 文件内容扫描

扫描项目内所有文本文件，查找 AI 工具名称、路径、环境痕迹。

**执行配置说明：**

`$HYGIENE_DENYLIST` 是一个由 Owner 在**本机环境中**维护的
denylist 文件路径。它**不属于 VeriLoop 项目**，也不进入 Git。
项目文件本身不记录该路径的实际值。

检查程序仅通过环境变量引用：

```bash
export HYGIENE_DENYLIST="<local denylist path>"
```

命令示例：

```bash
grep -riE -f "$HYGIENE_DENYLIST" . \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude-dir=node_modules \
  --exclude-dir=.pytest_cache \
  --exclude-dir=.ruff_cache
```

**边界示意：**

```
VeriLoop 项目（进入 Git）
    └── docs/ACADEMIC_HYGIENE.md      ← 规则本体，不含具体名称/路径
    └── ...                            ← 其他项目文件

Owner 本机环境（不进入 Git）
    └── $HYGIENE_DENYLIST              ← 具体 AI 名称、主机名、路径模式
```

项目与执行配置严格分离：项目只描述规则，不携带规则参数。

### 6.2 路径与隐藏文件扫描

```bash
grep -rnE '/Users/|C:\\\\Users\\\\|~/' . \
  --exclude-dir=.git --exclude-dir=.venv

find . -name '.DS_Store' -o -name 'Thumbs.db' \
  -o -name '*.swp' -o -name '*~' \
  -not -path './.git/*'
```

### 6.3 外部 denylist

具体 AI 工具名称、主机名、路径模式由 Owner 在**项目外部**维护，
不进入 Git。项目文件不得记录该文件的实际路径。

检查时通过环境变量引用：

```bash
export HYGIENE_DENYLIST="<local denylist path>"
```

**理由：** 若把具体产品名或路径写入项目文件，等于用规则自身污染项目。
denylist 外置可保证项目干净，同时规则可执行。

### 6.4 Git 元数据扫描

```bash
git log --format='%an <%ae> | %cn <%ce>'
git tag -n
git remote -v
```

确认：author、committer、tagger、remote URL 均不含禁止内容。

### 6.5 文件名扫描

```bash
find . -not -path './.git/*' -not -path './.venv/*' \
  | grep -iE -f "$HYGIENE_DENYLIST"
```

### 6.6 关键文档复核

逐份复核以下文件，确认无禁止内容：

- `README.md`
- `docs/` 下所有文件
- `experiments/` 下所有 README 与 config
- `data/` 下所有数据文件与说明
- `results/` 下所有结果文件
- 所有 `*.py` 文件的注释与 docstring

### 6.7 Self-Reference Boundary

`docs/ACADEMIC_HYGIENE.md` 本身包含用于说明规则的路径模式与禁止
类别示例。这些示例**不构成违规**，因为它们是规则声明的一部分，
不指向任何具体个人环境。

检查器对本文件执行以下区分：

1. **规则示例区**：文件内用于说明禁止类别的模式列举（如
   `/Users/<name>/...`、`~/...`、AI 工具类别的抽象描述）不触发
   违规。
2. **具体泄漏区**：文件内若出现**具体用户名、具体主机名、具体
   主目录路径、具体 AI 工具产品名**，则视为违规。
3. 检查 `ACADEMIC_HYGIENE.md` 时，`$HYGIENE_DENYLIST` 中的
   **具体 AI 工具名称**仍然适用；**路径模式**对该文件的规则
   示例段不适用。

实际操作：

- 对 `ACADEMIC_HYGIENE.md` 单独执行一次人工复核，由 Owner 确认
  其中出现的一切路径与名称均属规则说明，而非实际泄漏。
- 其余项目文件仍按 §6.1–§6.6 全量执行自动检查。

**理由：** 规则文件天然包含规则所禁止模式的示例。若不区分
“示例”与“泄漏”，检查器会把自己的规则判为违规，形成自检悖论。

---

## 7. 违规处理

### 7.1 发现违规时

1. **立即停止**当前阶段。
2. **不得**继续写入新内容。
3. **不得**提交或推送。
4. 记录违规项：文件路径、行号、违规类型。
5. 报告 Owner。

### 7.2 修复方式

按违规内容的所处位置分层处理：

**A. 未提交文件**

直接修改。

**B. 已提交但未推送**

用 `git commit --amend` 或 `git rebase` 修复历史。

**C. 已推送但未发布**

按 Owner 指示处理。默认优先采用新增修复 commit，不重写历史。

**D. 已公开发布（含已公开 tag）**

**默认不得重写历史。**

VeriLoop 的公开 commit 和 tag 是研究记录的一部分。若发现公开历史中
存在 Hygiene 违规：

1. 优先采用**新增修复 commit**，并在 commit message 中说明修复内容。
2. 只有 Owner **明确批准**时，才允许对公开历史做 force push 或
   历史重写。
3. 历史重写后必须在 `docs/` 中记录：原 commit、新 commit、重写理由、
   批准日期。

### 7.3 修复后

重跑 §6 全部六项，全部通过才能继续。

---

## 8. 与各阶段的关系

| 阶段 | 与本文件的关系 |
|---|---|
| H1-01A — Build | v0.1 已通过检查，作为参考样本 |
| H1-01B — Rules Lock | 本文件在本阶段建立；所有 H1-01B 文档受本文件约束 |
| H1-01C — Run | 正式运行前必须通过 Hygiene Check |
| H1-01D — Results | 结果文件、分析文档、报告受本文件约束 |
| H2-01 / H3-01 | 同样受本文件约束 |
| 公开发布（GitHub / arXiv / 会议） | 发布前必须通过完整 Hygiene Check |

---

## 9. 元信息

- 版本：v1.0
- 状态：APPROVED
- 生效日期：2026-10-07
- 生效条件：Owner 已在 §10.1 登记 Approval Record
- 修改流程：与实验协议同级，需 Owner 批准
- 引用方式：所有 H1-01B 及后续文档在开头引用本文件

---

## 10. Owner Approval Record

本文件在以下条件全部满足后生效：

- [x] Owner 逐条审阅 §1–§8
- [x] Owner 确认 §3 禁止清单完整
- [x] Owner 确认 §6 检查清单可执行
- [x] Owner 确认 §7 违规处理规则合理
- [x] Owner 在下方 Approval Record 中登记

### 10.1 Approval Record

```
Owner:           lingfeng-an
Approval date:   2026-10-07
Version:         v1.0
Approval status: APPROVED
Notes:           Technical gate passed. All §6.1–§6.7 checks PASS with
                 denylist configured externally. §6.3 verified.
```

登记后，本文件的 Git commit 历史即为审批记录的一部分。
未登记的版本状态保持 DRAFT，不生效。

### 10.2 Review Triggers（事件触发复审）

本文件不设置固定复审周期。以下事件发生时，必须重新审查本文件：

- Hygiene 规则本身发生修改
- 新增项目阶段（如 H1-01C、H1-01D、H2-01）
- 新增发布渠道（如 arXiv、会议、镜像仓库）
- 新增数据来源或实验材料类型
- Git 身份或发布策略发生变化
- 发现新的 Hygiene 违规类别
- Owner 明确要求复审

复审记录追加在 §11。

---

## 11. 复审记录

| 日期 | 版本 | 触发事件 | 变更摘要 | Owner 批准 |
|---|---|---|---|---|
| (待填) | (待填) | (待填) | (待填) | (待填) |

---

**End of Academic Hygiene**
