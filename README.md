# AstrBot Meme Deploy
📄 配套文章：[AstrBot 表情包排障实录](https://blog.csdn.net/FunkNJazz/article/details/169456616)

> 给 AstrBot 的 meme_manager 插件批量部署表情包，并解决「装了却不发图」的三处配置问题。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.29-green)](https://astrbot.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 这是什么

AstrBot 的 meme_manager 插件支持从官方源安装表情包，但在网络受限环境下经常失败；即使安装成功，也可能因为配置问题导致机器人**永远不发图**。

这个仓库提供：

1. **按文件并发下载脚本** —— 绕开整包下载，支持断点续传与完整性校验
2. **一键诊断脚本** —— 直接调插件 API，确认包是否真的加载
3. **配置排查文档** —— 三处隐藏配置的定位过程

## 功能特性

- 🚀 多线程并发下载（默认 10 路），单文件失败不影响整体
- 🧩 先写 `.part` 再原子替换，中断不留半截文件
- ✅ GIF 尾部字节校验，过滤截断文件
- 🔁 多镜像轮转 + 自动重试
- 🔍 一键查询插件已加载的表情包状态

## 快速开始

### 1. 下载表情包文件

```bash
python3 scripts/fetch_memes.py \
  --list memes.txt \
  --base https://raw.githubusercontent.com/DarlingDowlin/astrbot-meme-deploy/v1.0.0 \
  --dest ./packs/blue-fat-fish/memes \
  --workers 10
```

`memes.txt` 每行一个相对路径，例如：

```
memes/happy/0101_smile.gif
memes/sleep/0117_sleep.gif
```

### 2. 检查插件是否真的加载了包

```bash
python3 scripts/check_packs.py \
  --host http://127.0.0.1:6185 \
  --user admin \
  --password '***'
```

输出示例：

```json
{
  "id": "blue-fat-fish-meme-pack",
  "image_count": 157,
  "category_count": 15,
  "is_default": true
}
```

## 关键配置（不发图的三个原因）

配置路径：`data/config/meme_manager_config.json`

```jsonc
{
  "generation": {
    "prompt": {
      "category_example_enabled": true,   // ① 让模型学会输出 &&分类&& 标记
      "reply_example_enabled": true
    },
    "message": {
      "send_image_as_base64": true        // ② 跨系统场景必须用 base64 传图
    },
    "emotion": {
      "probability": 100                  // ③ 默认 35，会被随机丢掉 65%
    }
  }
}
```

改完**必须重启** AstrBot 服务。

详细定位过程见 [docs/troubleshooting.md](docs/troubleshooting.md)。

## 目录结构

```
.
├── README.md
├── LICENSE
├── .gitignore
├── scripts/
│   ├── fetch_memes.py     # 并发下载 + 校验
│   └── check_packs.py     # 插件状态诊断
└── docs/
    └── troubleshooting.md # 三处配置排查记录
```

## 环境

- Python 3.10+
- AstrBot 4.29+ / meme_manager 5.2.9+
- Linux / WSL2 / macOS

## 常见问题

**Q: 下载很慢怎么办？**
A: 换 `--base` 为可用的镜像前缀，或降低 `--workers` 避免被限流。

**Q: 文件下载了但插件不认？**
A: 检查目录结构是否与 `manifest.json` 中的 `memes/<分类>/` 一致。

**Q: 显示了包但机器人不发图？**
A: 九成是上面三处配置之一，按文档逐个排查。

## License

MIT
