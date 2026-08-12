# hxempirical

Stata 实证工作台（HX Empirical Workbench）。

当前发布版本：0.9.7。

## 一行安装

在 Stata 命令窗口运行：

```stata
net install hxempirical, from("https://xiaowang5105.github.io/hxempirical/") replace
```

安装完成后即可启动。

## 启动

```stata
hxempirical
```

## 更新或重新安装

再次运行上面的安装命令即可覆盖更新。若当前 Stata 会话已经运行过 `hxempirical`，并出现 Java/JAR 文件正在使用或 `r(602)` 等提示，请关闭 Stata，重新打开后先执行安装命令。

## 系统要求

支持 Stata 17 及以上版本。
