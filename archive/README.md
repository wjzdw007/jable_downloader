# 归档文件说明

本目录包含开发和测试过程中产生的临时文件，已移动到这里进行归档。

## 目录结构

### tests/
测试文件，用于验证各种功能和场景：
- `test_browser_simulation.py` - 浏览器模拟测试
- `test_functionality.py` - 功能测试
- `test_headers.py` - HTTP 头部测试
- `test_headless_vs_headed.py` - 有头/无头模式对比测试
- `test_network.py` - 网络测试
- `test_playwright_debug.py` - Playwright 调试测试
- `test_playwright.py` - Playwright 基础测试
- `test_real_crawling.py` - 真实爬取测试
- `test_real_site.py` - 真实站点测试
- `test_subscription.py` - 订阅功能测试
- `test_video_download_dry_run.py` - 视频下载演练测试

### debug_tools/
调试和诊断工具：
- `check_proxy.py` - 代理检查工具
- `compare_real_browser.py` - 浏览器行为对比工具
- `debug_model_page.py` - 演员页面调试工具
- `debug_video_url.py` - 视频 URL 调试工具
- `detect_browser_version.py` - 浏览器版本检测工具
- `diagnose_venv.sh` - 虚拟环境诊断脚本
- `fix_permissions.sh` - 权限修复脚本
- `install.sh` - 安装脚本
- `run_with_display.sh` - 显示运行脚本

### docs/
开发过程中的分析文档：
- `404_ERROR_ANALYSIS.md` - 404 错误分析
- `CODE_REVIEW.md` - 代码审查文档
- `DEBUG_IMPROVEMENTS.md` - 调试改进说明
- `IMPROVEMENTS.md` - 改进建议

## 说明

这些文件在精简模式优化过程中已不再需要，但保留用于：
1. 参考之前的测试方法
2. 了解开发和调试历史
3. 需要时可以恢复使用

如果需要清理磁盘空间，可以安全删除整个 `archive/` 目录。

---

归档时间: 2025-10-23
