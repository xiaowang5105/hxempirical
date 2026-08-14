# hxempirical 安装

## 推荐：通用一行安装

在 **Stata 17 或更高版本**的命令窗口直接运行：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

安装完成后运行：

```stata
hxempirical
```

这个安装器不依赖 `net install` 的 PLUS 目录写权限。它会：

1. 先检查 Stata 的用户级 `PERSONAL` ado 目录是否可写；
2. 从 `hxempirical.pkg` 自动读取当前发布文件清单；
3. 优先从 GitHub Pages 下载，每个文件失败时自动改用 GitHub Raw；
4. 先把全部文件下载到 Stata 临时目录，全部成功后才覆盖正式安装；
5. 将正式文件安装到当前用户的 `PERSONAL` ado 目录，因此 Windows/macOS 上通常不需要管理员权限；
6. 检查 `hxempirical.ado` 和 `hxworkbench.jar` 是否实际写入成功。

## GitHub Pages 无法访问时

使用 Raw 入口启动同一个安装器：

```stata
do "https://raw.githubusercontent.com/xiaowang5105/hxempirical/main/hxinstall.do"
```

安装器启动后仍会在两个下载源之间自动回退。

## 传统安装方式

Stata 标准包管理方式仍然可用：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace force
```

`net install` 默认把社区下载内容写入 Stata 的 `PLUS` 目录。如果某台学校、实验室或共享电脑的 PLUS 目录没有当前用户写权限，可能出现 `r(603)`。这种情况下优先使用上面的 `hxinstall.do` 通用安装器。

## 更新

重新运行通用一行安装即可覆盖到当前发布版本：

```stata
do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
```

如果当前会话已经打开 Java 工作台，建议先关闭工作台；如遇到 JAR 文件占用问题，关闭并重新打开 Stata 后，再运行安装器。
