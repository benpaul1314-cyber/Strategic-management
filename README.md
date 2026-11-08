# Strategic-management

# 研索 · 管理学期刊搜索

统一检索 Administrative Science Quarterly、Management Science、Organization Science、Strategic Management Journal 的 Crossref 公开元数据，支持关键词、年份、期刊选择、排序与分页，显示作者、摘要（若提供）与 DOI 原文链接。

## 启动

需要 Python 3.10+，无需安装第三方依赖。

```sh
cd /workspace/Strategic-management
python3 server.py
```

在本机部署时打开浏览器访问端口 8000。可用 `PORT=8080 python3 server.py` 更改端口。云环境需通过平台支持的访问方式连接；服务默认监听 0.0.0.0，请部署在可信网络中。

后端需允许 HTTPS 访问 `api.crossref.org`，保留代理与 TLS 验证。无需 API 密钥。受限网络请先在环境设置中允许该域名。

EBSCO 是单独的数据库入口，不纳入此工具的统一检索；页面提供原机构路径的高级检索链接，未保存会话参数。出版方与 EBSCO 全文可能需要机构登录。Crossref 的元数据覆盖、索引时效和摘要完整度由出版方决定；关键词为相关性检索，不保证支持数据库布尔语法。分页为每本期刊各取 10 条再合并排序，并非跨期刊全局排名。

## 验证

```sh
python3 -m unittest discover -s tests -v
curl --fail 'http://127.0.0.1:8000/api/search?q=strategy&journal=smj&from=2020&sort=newest'
```

单元测试使用确定性模拟元数据，验证筛选、故障处理和归一化；不代表外部 API 已连通。真实请求失败时，页面会显示错误，仍可通过期刊入口检索。

## 文献综述工作台

内置六组针对德国中小企业继任和估值的关键词，点击主题后可编辑。Crossref 搜索使用相关性匹配；单独生成的布尔检索式可复制到 EBSCO，不能作为本工具已执行严格 AND/OR 的证据。

搜索结果可收藏，文献库支持综述笔记、CSV 和 RIS 导出，检索记录可以恢复期刊、年份及关键词。收藏与记录存于当前浏览器 localStorage，不会跨设备同步，清除浏览器数据会丢失；请定期导出。CSV 包含标题、作者、年份、期刊、DOI、URL、摘要和笔记。RIS 中作者原始文本保留在备注，避免错误拆分姓名。

额外验证：`node --test tests/review.test.mjs`。

## Mac 快速启动

从 GitHub 点击 **Code → Download ZIP**，解压后双击 `启动研索.command`。需要 Python 3.10+。如果 macOS 提示无执行权限，在终端输入 `bash `（末尾有空格），把该文件拖入终端后按回车。启动后会自动打开浏览器；关闭终端会停止服务。若系统提示安装命令行工具，也可以从 python.org 安装 Python。
