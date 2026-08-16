from pathlib import Path

path = Path("hxsemantics.ado")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one match, got {count}: {old[:120]}")
    text = text.replace(old, new, 1)


replace_once("*! hxsemantics 1.4.1  12aug2026", "*! hxsemantics 1.4.2  16aug2026")
replace_once(
    " streg stcrreg dsregress poivregress ",
    " streg stcrreg arima arch ucm dfuller pperron corrgram pergram var svar vec varsoc vargranger varstable spregress spivregress spxtregress dsregress poivregress ",
)

marker = '        else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd\' ") {\n'
if text.count(marker) != 1:
    raise SystemExit(f"expected one mixed-family marker, got {text.count(marker)}")

block = '''        else if "`cmd'" == "arima" {
            local expr_label "结果变量 + 外生变量（可选）+ ARIMA 阶数 / AR-MA 设定"
            local example1 "arima y, arima(1,0,1)"
            local explain1 "估计 ARIMA(1,0,1)；阶数是模型核心设定。"
            local example2 "arima y x1 x2, arima(1,0,0)"
            local explain2 "在 AR(1) 动态回归中加入 x1、x2 外生解释变量。"
        }
        else if "`cmd'" == "arch" {
            local expr_label "结果变量 + 均值方程变量（可选）+ arch()/garch() 等波动设定"
            local example1 "arch y, arch(1) garch(1)"
            local explain1 "估计标准 GARCH(1,1) 波动模型。"
            local example2 "arch y x1, arch(1) garch(1)"
            local explain2 "在均值方程加入 x1，同时估计 GARCH(1,1)。"
        }
        else if "`cmd'" == "ucm" {
            local expr_label "结果变量 + 外生变量（可选）+ seasonal()/cycle() 等成分"
            local example1 "ucm y, seasonal(12) cycle(1)"
            local explain1 "按 12 期季节项和一阶周期成分拟合不可观测成分模型。"
            local example2 "help ucm"
            local explain2 "趋势、季节和周期成分取决于研究设计；运行前核对当前 Stata 版本支持的成分。"
        }
        else if "`cmd'" == "dfuller" {
            local expr_label "待检验序列 + lags() / trend 等 ADF 设定"
            local example1 "dfuller y, lags(1)"
            local explain1 "对 y 进行带 1 阶增广项的 Dickey–Fuller 单位根检验。"
            local example2 "dfuller y, lags(1) trend"
            local explain2 "在检验回归中加入确定性时间趋势。"
        }
        else if "`cmd'" == "pperron" {
            local expr_label "待检验序列 + Newey–West 滞后 / trend 等设定"
            local example1 "pperron y"
            local explain1 "对 y 进行 Phillips–Perron 单位根检验。"
            local example2 "pperron y, trend"
            local explain2 "在检验回归中加入确定性时间趋势。"
        }
        else if "`cmd'" == "corrgram" {
            local expr_label "待诊断序列 + lags() 等相关图设定"
            local example1 "corrgram y, lags(12)"
            local explain1 "查看 y 到 12 阶的自相关、偏自相关和 Q 统计量。"
        }
        else if "`cmd'" == "pergram" {
            local expr_label "待分析序列 + periodogram options"
            local example1 "pergram y"
            local explain1 "绘制 y 的 periodogram，用于查看周期频率结构。"
        }
        else if "`cmd'" == "var" {
            local expr_label "系统内生变量 + lags() 等 VAR 设定"
            local example1 "var y1 y2, lags(1/2)"
            local explain1 "把 y1、y2 都作为内生变量估计 1 至 2 阶 VAR。"
        }
        else if "`cmd'" == "svar" {
            local expr_label "系统变量 + lags() + A/B 识别矩阵（aeq()/beq()）"
            local example1 "help svar"
            local explain1 "SVAR 需要由识别假设定义 A/B 矩阵；先核对官方示例再填写。"
            local example2 "svar y1 y2, lags(1/2) aeq(A) beq(B)"
            local explain2 "使用事先定义的 A、B 识别矩阵估计结构 VAR。"
        }
        else if "`cmd'" == "vec" {
            local expr_label "系统变量 + rank() + lags() 等协整/VEC 设定"
            local example1 "vec y1 y2, rank(1) lags(2)"
            local explain1 "在协整秩为 1、VAR 阶数为 2 的设定下估计 VEC 模型。"
        }
        else if "`cmd'" == "varsoc" {
            local expr_label "系统变量 + maxlag() 等阶数选择设定"
            local example1 "varsoc y1 y2, maxlag(4)"
            local explain1 "比较 y1、y2 的候选滞后阶数，最大检查 4 阶。"
        }
        else if "`cmd'" == "vargranger" {
            local expr_label "VAR/VEC 估计后的 Granger 因果检验 options（通常可留空）"
            local example1 "vargranger"
            local explain1 "对上一项 VAR/VEC 结果执行 Granger 因果检验。"
            local example2 "help vargranger"
            local explain2 "需要更细的限制或显示设置时核对当前 Stata 版本的 options。"
        }
        else if "`cmd'" == "varstable" {
            local expr_label "VAR/SVAR 估计后的稳定性检验 options（通常可留空）"
            local example1 "varstable"
            local explain1 "检查上一项 VAR/SVAR 的特征根稳定性条件。"
            local example2 "help varstable"
            local explain2 "图形或其他稳定性设置按当前 Stata 版本核对。"
        }
        else if "`cmd'" == "spregress" {
            local expr_label "Y + X + 估计方法 + dvarlag()/ivarlag()/errorlag()"
            local example1 "spregress y x, gs2sls dvarlag(W)"
            local explain1 "使用预先创建的 W 对因变量加入空间滞后，并用 GS2SLS 估计。"
            local example2 "spregress y x, ml dvarlag(W)"
            local explain2 "使用 ML 估计因变量空间滞后模型。"
        }
        else if "`cmd'" == "spivregress" {
            local expr_label "Y + 外生 X + (内生变量 = 工具变量) + 空间权重设定"
            local example1 "spivregress y x1 (x2 = z), dvarlag(W) errorlag(M)"
            local explain1 "同时保留 IV 方程、因变量空间滞后和空间误差；W/M 需事先创建。"
            local example2 "help spivregress"
            local explain2 "ivarlag() 等更复杂空间结构按研究设定继续补充。"
        }
        else if "`cmd'" == "spxtregress" {
            local expr_label "Y + X + FE/RE + dvarlag()/ivarlag()/errorlag()"
            local example1 "spxtregress y x, fe dvarlag(W) errorlag(M)"
            local explain1 "在已声明的空间面板数据上估计固定效应空间自回归模型。"
            local example2 "spxtregress y x, re dvarlag(W) errorlag(M)"
            local explain2 "随机效应空间面板模型使用同样的空间权重结构。"
        }
'''

text = text.replace(marker, block + marker, 1)
path.write_text(text, encoding="utf-8", newline="\n")
