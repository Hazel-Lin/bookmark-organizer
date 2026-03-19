做了个新开源小工具：`bookmark-organizer`。

它不是单纯“整理 Chrome 书签”的脚本，而是一个给 agent 用的 CLI。

核心流程只有 4 步：

- `scan`：先发现有哪些书签文件夹可整理
- `analyze`：把目标文件夹展平
- `plan`：先生成分类计划 JSON
- `apply`：确认后再写回，并自动备份

我这次最想验证的点不是书签本身，而是：

能不能把“本地半结构化数据的安全修改”做成一个 agent 可直接调用的协议。

因为很多自动化真正危险的地方，不是“不会改”，而是“改了之后你不知道有没有弄丢东西”。

所以这个项目默认先出 plan，再 apply。

下一步准备补：

- Edge / Brave 支持
- 重复书签检测
- 死链检查
- runtime API fallback

如果你也在做 agent-native CLI，应该会懂这种工具的价值。

