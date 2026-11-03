# Codex Game Studios

[English](README.en.md) · [完整技能和角色目录](docs/CATALOG.md) · [迁移说明](docs/MIGRATION.md)

把 [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) 转换为本地 Codex 游戏开发工作室，并打包成可安装、卸载的插件，支持 Codex 桌面端和 CLI。

保留 **74 个工作流、49 个角色、35 个辅助文件（含 Shell、AWK、Godot 脚本）、14 组领域规则**，覆盖 Godot、Unity、Unreal。插件另加一个 `$studio-setup` 安装后引导技能。这里是工作室模板和工具集；具体游戏内容由你在工作区中创建。

## 原生安装插件（推荐）

需要 Python 3.11+、Git、本地 Codex 客户端。Windows 安装 Git for Windows；辅助脚本使用它附带的 Git Bash。无需额外 Python 包，无需为插件单独提供 API Key。

### 方式一：上传插件压缩包

在 Codex 桌面端选择 **添加 → 上传插件压缩包**，直接选择：

```text
dist/codex-game-studios-0.2.0.zip
```

无需解压，也无需运行 `install.ps1`。按客户端提示完成导入和安装，然后在游戏工作区的新聊天中运行 `$studio-setup`。

这是单插件标准包：ZIP 根目录包含 `plugin.json`、`.codex-plugin/plugin.json`、`skills/`、`hooks/`、`assets/`、`scripts/` 和集中资源 `framework/`。75 个技能入口、49 个角色和所有迁移工作流都随包提供。

### 方式二：添加插件市场

下载并解压 `dist/codex-game-studios-marketplace-0.2.0.zip`。打开 **添加 → 添加插件市场**，按对话框的三个字段填写；“来源”是文本输入框，可以直接粘贴本地文件夹的绝对路径。

**当前电脑可直接使用的填写值：**

| 字段 | 填写内容 |
| --- | --- |
| 来源 | `E:\Users\LENOVO\Documents\ChatGPT\Codex-Game-Studios\dist\codex-game-studios-marketplace` |
| Git 引用 | 留空，本地文件夹不使用 Git 引用 |
| 稀疏路径 | 留空，本地文件夹不使用稀疏检出 |

点击“添加市场”，再从市场中安装 **Codex Game Studios**。如果把市场 ZIP 解压到其他位置，把“来源”替换成实际解压目录的绝对路径；该目录应直接包含 `.agents/plugins/marketplace.json`，不要填写 ZIP 路径、JSON 文件路径或插件子目录。

源码构建后的市场目录也可直接使用：`dist/codex-game-studios-marketplace/`。它只包含市场清单和插件，不含根级 `.codex/hooks.json`，因此添加市场本身不会把它变成游戏工作区。

**通过 GitHub 安装（无需下载 ZIP）：**

| 字段 | 填写规则 |
| --- | --- |
| 来源 | `wyx135230/Codex-Game-Studios` 或 `https://github.com/wyx135230/Codex-Game-Studios.git` |
| Git 引用 | `main`；也可留空使用默认分支 |
| 稀疏路径 | 小仓库建议留空，完整检出；需要稀疏检出时，按下方两行填写 |

```text
.agents/plugins
plugins/codex-game-studios
```

稀疏路径必须同时包含市场清单目录和它引用的插件目录，不能只填截图中的 `plugins/codex` 占位示例。截图里的“主分支”和“plugins/codex”是输入提示，不要求填写。

对应的 Git CLI 注册命令：

```powershell
codex plugin marketplace add wyx135230/Codex-Game-Studios --ref main --sparse .agents/plugins --sparse plugins/codex-game-studios
```

CLI 也支持注册同一目录：

```powershell
codex plugin marketplace add "E:\Users\LENOVO\Documents\ChatGPT\Codex-Game-Studios\dist\codex-game-studios-marketplace"
```

然后在 `/plugins` 中选择市场并安装。**市场 ZIP 用于解压后添加市场；单插件 ZIP 用于上传，两个文件不要混用。**

钩子须按客户端提示审核、信任。首次运行 `$studio-setup` 只绑定游戏工作区；不复制技能库、角色或通用脚本。插件包含本地脚本，需在支持本地执行的 Codex 桌面/CLI 环境使用。截图中的私有安装入口与公共插件目录投稿是不同流程；官方当前不接受含生命周期钩子的公共目录投稿。

安装和市场格式依据 [官方插件打包说明](https://developers.openai.com/plugins/build/plugins)；图标和字段要求见 [官方格式参考](https://developers.openai.com/plugins/deploy/submission#icons-and-screenshots)。本地校验和 CLI 市场测试不等于已完成桌面上传界面的实际点击验收。

### 可选：源码仓库的兼容安装脚本

如果使用源码仓库，仍可在仓库根目录运行以下脚本。**原生安装不需要这些脚本，标准 ZIP 不包含它们。**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

若尚未构建，脚本会先生成插件。

安装脚本把插件放在 `~/.codex/plugins/local-source/codex-game-studios`，向 `~/.agents/plugins/marketplace.json` 添加独立条目，并向 Codex 用户配置添加带标记的启用段。它保留其他插件、模型和认证设置。重复安装会报告 `already-installed`。

脚本会打开插件详情链接。重启桌面端后，在 **Plugins → Local Game Studios → Codex Game Studios** 查看插件；已有个人市场时显示其原名称。根据客户端提示完成安装和钩子信任审核，然后新建聊天，在游戏工作区运行：

```text
$studio-setup
```

插件钩子必须经过 Codex 的信任审核才能运行；这是客户端要求，脚本不会绕过。安装本身不修改游戏工作区。首次引导只创建必要配置和简短指令入口，已有配置会保留，已有指令只追加带标记的插件入口。

**macOS / Linux / 不打开桌面链接：**从源码仓库运行：

```bash
python3 scripts/plugin_manager.py install
```

Python 命令会输出安装路径和桌面详情链接；也可从 CLI 的 `/plugins` 中选择本地市场。不同 CLI 版本支持的插件子命令不同，本机 0.125 只有 `plugin marketplace`，因此安装脚本不依赖新版 `codex plugin add`。

## 卸载、禁用和升级

通过“上传插件压缩包”或“添加插件市场”安装的插件，直接在 Codex 插件详情页选择禁用或卸载；不需要运行卸载脚本。更新时上传新版单插件 ZIP，或更新市场源后使用客户端更新操作。

以下脚本只用于旧的源码兼容安装方式：

Windows 在源码仓库根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\uninstall.ps1
```

其他平台运行 `python3 scripts/plugin_manager.py uninstall`。卸载移除该安装器拥有的插件源、市场条目和配置段，然后重启 Codex。**游戏工作区、设计文档、代码、会话记录都保留。** Codex 自身管理的已安装缓存若仍显示，可在插件详情页点卸载；安装器不递归删除 Codex 的共享缓存。

也可直接在桌面端插件详情页禁用或卸载。通过本安装器安装的本地源可再用卸载脚本清理。升级流程：卸载旧版、解压新版、安装新版；在新版插件中运行 `$studio-setup` 刷新资源绑定；项目产物和已有配置不会被覆盖。旧版框架副本可按下节预览清理。

可用 `python scripts/plugin_manager.py status` 检查本地源状态。`--home <目录>` 支持隔离安装测试；它指定包含 `.codex` 和 `.agents` 的用户主目录。若安装器的配置段被手工修改，卸载会停止并说明原因，避免删除修改后的设置。

## 0.2.0：插件资源与项目数据分离

安装包的 `skills/` 直接包含 74 个完整工作流及参考文件，另有 `$studio-setup`；`framework/` 保存规则、49 个角色说明、模板和辅助资源。技能入口不再转交到项目中的另一套技能。

新项目运行 `$studio-setup` 时只新增：

```text
AGENTS.md                    # 简短插件入口，不是整套工作室指令
project.yaml                 # 当前游戏配置
.studio/installation.json    # 插件版本、资源位置与文件归属记录
```

若已有 `AGENTS.override.md`，入口写入该文件；否则写入 `AGENTS.md`。保留现有内容，只追加或更新 `codex-game-studios` 标记区。已有 `project.yaml` 不覆盖。不会生成 `STUDIO.md`、`.agents/skills/`、项目 `.codex/`、通用 `scripts/`、README、许可证或 GitHub 配置副本，也不创建技能目录链接。

设计、代码、资产、引擎参考、测试与 `production/` 记录由对应工作流按需创建。项目特定的旧配置镜像与角色记忆按需放在 `.studio/technical-preferences.md` 和 `.studio/agent-memory/`。钩子运行时可能生成会话记录，这是项目数据，不是重复安装框架。

角色说明由插件提供；客户端不能直接使用命名角色时，把完整角色说明与元数据交给通用子代理。不为每个项目再生成 49 个原生代理配置；没有子代理工具时按运行协议披露顺序执行的限制。

旧版项目升级后先运行 `$studio-setup`。清理旧副本先预览，再执行（`<插件根目录>` 换成当前安装位置）：

```powershell
python "<插件根目录>/scripts/plugin_workspace.py" cleanup --root "<游戏目录>"
python "<插件根目录>/scripts/plugin_workspace.py" cleanup --root "<游戏目录>" --apply
```

只删除旧安装记录中哈希仍一致的技能、框架配置、工作室测试、通用运行脚本和旧 `STUDIO.md`。修改过的文件、角色记忆与游戏设计、代码、测试、会话产物均保留；未列为可清理类别的旧 README 等文件也保留。没有安装记录时不猜测归属，不整目录删除。

卸载后游戏产物仍保留，但插件工作流不再可用；简短指令入口会提示重新安装和绑定。插件缓存位置变更时，首次技能绑定或受信任的插件钩子会刷新记录。

## 直接使用项目模板

也可以在 Codex 桌面端打开本仓库，或在本仓库目录运行 `codex`，无需安装插件：

```powershell
python scripts/studio.py doctor
```

随后在聊天中输入 `$start`。根 `AGENTS.md` 是入口；技能位于 `.agents/skills/`，原生角色位于 `.codex/agents/`。默认 `.codex/config.toml` 使用已在本机 CLI 0.125 验证的角色注册格式；`.codex/config.modern.toml` 提供新版独立代理配置示例。不要把新版配置盲目覆盖到旧版 CLI。

插件与直接模板二选一即可。插件直接读取安装包中的完整工作流和只读资源，不向游戏项目复制技能库，也不重复注册项目钩子。源码模板模式仍保留仓库内的技能和原生角色配置，供维护或直接使用。

## 从想法到发布

| 目标 | 技能示例 |
| --- | --- |
| 新项目 / 接管已有项目 | `$start`、`$onboard`、`$adopt`、`$reverse-document` |
| 引擎和版本 | `$setup-engine`：Godot 4、Unity、Unreal 5 与各自语言、测试根目录 |
| 概念和设计 | `$brainstorm`、`$quick-design`、`$design-system`、`$art-bible`、`$ux-design` |
| 系统和架构 | `$map-systems`、`$create-architecture`、`$architecture-decision`、`$architecture-review` |
| 拆分与开发 | `$create-epics`、`$create-stories`、`$story-readiness`、`$dev-story`、`$story-done` |
| 跨专业协作 | `$team-combat`、`$team-ui`、`$team-level`、`$team-narrative`、其余 team 工作流 |
| 测试和审查 | `$test-setup`、`$smoke-check`、`$regression-suite`、`$code-review`、`$gate-check` |
| 生产和发布 | `$sprint-plan`、`$milestone-review`、`$release-checklist`、`$launch-checklist`、`$hotfix` |
| 工作室维护 | `$settings`、`$skill-test`、`$skill-improve`、`$help` |

完整 74 个技能和 49 个角色见 [目录](docs/CATALOG.md)。原文中的 `/dev-story` 等写法是历史工作流名称，Codex 中使用 `$dev-story` 或自然语言请求，不表示新增了原生斜杠命令。

例如：`$dev-story production/epics/epic-01/story-01.md`。角色保留总监 → 负责人 → 专家的分工与升级路径。客户端支持子代理时按工作流委派；不支持命名代理时，将完整角色说明传给通用代理；不支持子代理时顺序执行并明确报告，不能声称完成了独立审查。

## 配置、规则和会话

`project.yaml` 保存引擎、阶段和团队工作流配置；`project.local.yaml` 保存个人覆盖。原项目的配置优先级、阶段镜像、rigor 展开、自动化模式和系统级覆盖保持原逻辑，通过 `.codex/hooks/yaml-helper.sh resolve_config` 解析。

```text
$settings modes.rigor=standard
$settings --local modes.automation=guided
```

所有角色默认继承当前 Codex 模型。原 `sonnet/opus/haiku` 元数据保存在 `.codex/compat/` 用于审计，不会假装映射为某个 OpenAI 模型。原工具白名单、回合预算、角色记忆通过运行协议和任务说明处理；不宣称它们是客户端强制隔离。

插件模式由项目 `AGENTS.md`（或已有 `AGENTS.override.md`）的简短入口读取 `.studio/installation.json`，定位安装包的 `framework/PLUGIN_RUNTIME.md`；规则从插件 `framework/.codex/rules/` 读取。源码模板模式仍使用 `.codex/docs/runtime.md` 与 `.codex/rules/index.md`。Codex 不自动执行 `@` 导入、Claude 风格的路径规则和技能 Shell 注入，因此这些行为已改成显式读取和命令执行。

会话恢复读取 `production/session-state/active.md`。原有提交检查、注册表保护、写入保护、资产检查、阅读限制、子代理日志和产物检查均通过适配器保留。`apply_patch` 的新增、更新、删除、移动和多文件操作转换为逐文件校验。

客户端无法运行钩子时，显式执行生命周期命令。以下示例为源码模板模式；插件模式将 `scripts/studio.py` 换为当前插件根目录下的绝对路径，并从游戏工作区运行：

```powershell
python scripts/studio.py hook SessionStart
python scripts/studio.py hook PreCompact
python scripts/studio.py hook Stop
python scripts/studio.py status
```

工具检查可使用 `hook PreToolUse --payload payload.json` 和 `hook PostToolUse --payload payload.json`，JSON 示例见 [迁移说明](docs/MIGRATION.md)。钩子是辅助保护；通过 Shell、外部编辑器或特殊工具进行的文件操作仍需按工作流显式校验。

## 验证与开发

以下命令用于源码仓库根目录；插件绑定的游戏工作区通过安装包内的 `scripts/studio.py doctor` 检查环境；框架测试留在源码仓库，不复制进游戏项目。

```powershell
python -m unittest discover -s tests -v
python scripts/studio.py doctor
python scripts/verify.py
python scripts/build_plugin.py
python scripts/validate_distribution.py
```

Windows 的完整校验需要允许 Git Bash 正常启动；可通过 `STUDIO_BASH` 指定可执行文件。报告保存在 `docs/verification.json`。`scripts/probe_codex.py` 使用临时配置检查 CLI 解析，不修改个人配置。

分发包校验使用开发依赖 PyYAML（`python -m pip install PyYAML`）；插件运行时仍只需 Python 标准库。构建会同时生成单插件上传 ZIP、独立市场目录、市场 ZIP 和各自的 SHA-256 校验文件。

验证范围包括文件迁移覆盖、角色和技能格式、补丁转换、拒绝与告警传递、安装卸载隔离测试、所有 Shell 脚本语法和代表性辅助脚本。**未执行模型驱动的全部工作流，也未运行三种游戏引擎构建或真实桌面 UI 点击测试。** 这些需要目标客户端、账号和所选引擎，不能用静态通过替代。

常见问题：技能未出现时重启客户端并核对插件启用状态；钩子未运行时检查信任审核；Windows 缺 Bash 时安装 Git for Windows；遇到已有全局配置解析错误时修正错误所指配置，插件不会改写用户模型或服务等级。

## 来源和许可

来源为用户提供的 `Claude-Code-Game-Studios` 模板（638 个文件，版本标识 1.2.0）。[逐文件清单](docs/migration-manifest.json) 保存源路径、目标路径和源 SHA-256。原 README、变更日志和升级历史在 `docs/upstream/`；它们是历史参考，Codex 操作以本文和运行协议为准。保留原 [MIT 许可证](LICENSE)。

插件格式和安装方法依据 [OpenAI 插件文档](https://developers.openai.com/plugins/build/plugins)、[技能文档](https://developers.openai.com/codex/skills)、[代理文档](https://developers.openai.com/codex/subagents) 和 [钩子文档](https://learn.chatgpt.com/docs/hooks)。这是本地插件，不包含云托管服务，也未发布到公共插件目录。
