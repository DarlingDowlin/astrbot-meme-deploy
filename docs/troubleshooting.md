# 三处隐藏配置排查记录

## 症状

插件面板显示安装成功，包里 157 张图，已设为默认包，但机器人回复永远只有文字。

## 排查步骤

### 第一步：确认包真的加载了

不要相信界面。直接调插件 API：

```bash
TOKEN=*** -s -X POST http://127.0.0.1:6185/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"***"}' | jq -r .data.token)

curl -s -H "Authorization: Bearer ***" \
  http://127.0.0.1:6185/api/plug/meme_manager/packs
```

如果返回 `image_count: 157` 且 `is_default: true`，说明**安装没问题**，问题在发送链路。

### 第二步：看运行时日志

```
[meme_manager] 去重后的最终表情列表: []
```

空列表 = 模型没有输出 `&&分类键&&` 标记。

### 第三步：打开教学示例

```json
{ "generation": { "prompt": {
    "category_example_enabled": true,
    "reply_example_enabled": true
} } }
```

重启后日志变为：

```
[meme_manager] 去重后的最终表情列表: ['sleep']
```

### 第四步：解决跨系统路径

机器人跑在 WSL，协议端跑在 Windows。插件默认传本地路径：

```
/home/user/data/packs/memes/sleep/0117.gif
```

Windows 读不到 → 图片被静默丢弃（不报错）。

**改法：**

```json
{ "generation": { "message": { "send_image_as_base64": true } } }
```

### 第五步：关掉随机丢图

```json
{ "generation": { "emotion": { "probability": 100 } } }
```

默认 35，意味着 65% 的图会被随机丢弃。

## 经验

1. 界面上"成功"≠ 运行时真的加载了
2. 静默失败最危险：不报错不代表没问题
3. 默认关闭的功能往往是"看起来坏了"的真凶
4. 跨系统调用时，路径格式按调用方规则写
