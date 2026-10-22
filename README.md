# bili-api-client

免登录调用 Bilibili 搜索与评论接口的轻量客户端：单个 Python 文件，**只用标准库**，无第三方依赖。

## 为什么需要这些设置

B 站的 Web 接口对请求来源与请求头较敏感：从非常规网络直连、或带过于简单的 UA 的脚本，通常会吃 `412 Precondition Failed`。本脚本把实测可用的设置打包在一起：

1. **代理**：从 `https_proxy` / `HTTPS_PROXY` 环境变量读取（无代理需求时可直连，视网络而定）
2. **常见浏览器 UA**：Chrome 桌面端 UA
3. **完整请求头**：`Accept` / `Referer` / `Accept-Language`
4. **buvid3 cookie**：首次请求时经 `x/frontend/finger/spi` 接口获取，并在进程内缓存复用

## 用法

```bash
# 搜索视频（按发布时间排序）：关键词 [页码] [每页条数]
python3 bili_api.py search "Python 教程" 1 20

# 拉取评论：视频 aid [页码] [每页条数]（sort=2 按热度；<aid> 替换为目标视频的 aid）
python3 bili_api.py replies <aid> 1 20
```

也可以作为模块导入：

```python
from bili_api import bili_search, bili_replies
```

## 已知限制

- `x/web-interface/view`（视频详情）接口在部分网络环境下仍可能返回 412；本脚本覆盖的 search 与 reply 接口正常
- 接口为 B 站未公开的 Web 接口，参数与返回结构可能随官方调整而变化

## 免责声明

- 本工具仅供个人学习与研究，使用者应遵守 B 站用户协议并控制请求频率
- 经接口获取的内容版权归原作者所有，请勿未经授权公开或再分发

## License

MIT
