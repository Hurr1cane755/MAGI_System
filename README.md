# MAGI-Link

> *"MAGI 系统表决完毕。"*

受《新世纪福音战士》MAGI 超级计算机启发的多智能体决策系统。将你的问题提交给三个承载赤木直子博士人格的 AI 单元，由它们独立分析、各自表决，一票否决制决出最终裁决。

---

## 系统架构

MAGI 由三个完全平等的单元组成，各自承载赤木直子博士不同侧面的人格：

| 单元 | 人格 | 分析视角 |
|------|------|----------|
| **MELCHIOR-1** | 科学家 | 逻辑推断、数据评估、最优解 |
| **BALTHASAR-2** | 母亲 | 保护、长远影响、道德责任 |
| **CASPER-3** | 女人 | 直觉、情感、内心真实 |

三个单元**完全并行**运行，互不知晓对方的分析结果。

```
MELCHIOR·1 ──→ 通过/拒绝 ──┐
BALTHASAR·2 ──→ 通过/拒绝 ──┼──→ 一票否决制 ──→ 承認 / 否决
CASPER·3 ──→ 通过/拒绝 ────┘
```

**裁决规则：三票全部通过 → 承認；任意一票拒绝 → 否决。**

---

## 功能

- **Web 界面**：橙黑配色的 EVA 风格 UI，三面板实时展示各单元分析
- **CLI 模式**：终端运行，带 NERV 风格 ASCII banner 和进度动画
- **Mock 模式**：无需 API Key 即可运行，自动返回示例回复
- **Vercel 部署**：前后端一体，开箱即用

---

## 快速开始

### 环境要求

- Python 3.11+
- Google Gemini API Key（[Google AI Studio](https://aistudio.google.com/) 免费获取）

### 安装

```bash
git clone https://github.com/Hurr1cane755/MAGI_System.git
cd MAGI_System
pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
# 编辑 .env，填入你的 GOOGLE_API_KEY
```

### 本地运行

**Web 模式**（启动 API 服务器）：

```bash
uvicorn api.index:app --reload
```

然后用浏览器打开 `public/index.html`，或直接访问 `http://localhost:8000`。

**CLI 模式**：

```bash
python main.py
# 或直接传入问题
python main.py "我应该换工作吗？"
```

### Mock 模式

不设置 `GOOGLE_API_KEY` 时自动启用 Mock 模式，返回预设示例回复，适合本地调试 UI。

---

## 部署到 Vercel

1. Fork 本仓库
2. 在 Vercel 导入项目
3. 在项目设置中添加环境变量 `GOOGLE_API_KEY`
4. 部署完成

---

## 项目结构

```
MAGI-Link/
├── api/
│   └── index.py        # FastAPI 后端，三 agent 并行调用与裁决逻辑
├── magi/
│   ├── base_agent.py   # Agent 基类
│   ├── melchior.py     # MELCHIOR-1（科学家）
│   ├── balthasar.py    # BALTHASAR-2（母亲）
│   └── caspar.py       # CASPER-3（女人）
├── public/
│   ├── index.html      # EVA 风格 Web 前端
│   ├── document.js     # 前端交互逻辑
│   └── document.css    # 样式
├── main.py             # CLI 入口
├── config.py           # 环境变量配置
├── vercel.json         # Vercel 部署配置
└── requirements.txt
```

---

## API

### `POST /api/analyze`

```json
{
  "question": "我应该辞职吗？"
}
```

返回：

```json
{
  "melchior": "通过\n【假说与依据】...",
  "balthasar": "拒绝\n【守护对象分析】...",
  "casper": "通过\n【直觉感受】...",
  "melchior_vote": "通过",
  "balthasar_vote": "拒绝",
  "casper_vote": "通过",
  "verdict": "否定"
}
```

### `GET /api/health`

返回系统状态及 API Key 配置情况。

---

## 免责声明

本项目为个人娱乐项目，纯属致敬《新世纪福音战士》原作，与任何真实组织或技术无关。

MAGI 系统的所有输出内容**仅供娱乐**，不构成任何形式的建议——无论是医疗、法律、财务、职业还是人生决策。请勿将 AI 的表决结果作为真实决策的依据。

> 赤木直子博士的人格或许住在这里，但她不为你的人生负责。

---

## License

MIT
