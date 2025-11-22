# 霞鹜新晰黑字体设置指南

## 字体介绍

霞鹜新晰黑 (LXGWNeoXiHei) 是一款优秀的开源中文字体，具有以下特点：
- 清晰易读，适合屏幕显示
- 支持简体中文、繁体中文、英文、数字
- 开源免费，可商用
- 字重完整，包含常规和粗体

## 项目地址

https://github.com/lxgw/LxgwNeoXiHei

## 下载步骤

### 方法1: GitHub下载
1. 访问项目地址：https://github.com/lxgw/LxgwNeoXiHei
2. 进入 Releases 页面
3. 下载最新版本的字体文件
4. 推荐下载以下文件：
   - `LXGWWenKai-Regular.ttf` (常规字体)
   - `LXGWWenKai-Bold.ttf` (粗体)

### 方法2: CDN下载（推荐）
可以直接下载以下链接的字体文件：
- 常规字体：https://cdn.jsdelivr.net/gh/lxgw/LxgwNeoXiHei/dist/LXGWWenKai-Regular.ttf
- 粗体字体：https://cdn.jsdelivr.net/gh/lxgw/LxgwNeoXiHei/dist/LXGWWenKai-Bold.ttf

### 方法3: 使用提供的脚本
```bash
# 下载字体文件
cd static/fonts/

# 下载常规字体
curl -o LXGWWenKai-Regular.ttf https://cdn.jsdelivr.net/gh/lxgw/LxgwNeoXiHei/dist/LXGWWenKai-Regular.ttf

# 下载粗体字体
curl -o LXGWWenKai-Bold.ttf https://cdn.jsdelivr.net/gh/lxgw/LxgwNeoXiHei/dist/LXGWWenKai-Bold.ttf
```

## 文件放置位置

下载完成后，请将字体文件放置在以下目录：
```
static/fonts/
├── font-setup.css          # 字体配置文件（已存在）
├── LXGWWenKai-Regular.ttf  # 常规字体（需要下载）
├── LXGWWenKai-Bold.ttf     # 粗体字体（需要下载）
└── README.md               # 本说明文件
```

## 配置说明

字体配置已在 `font-setup.css` 中完成，包括：

### 1. 字体声明
- 常规字体：`LXGWNeoXiHei` (normal weight)
- 粗体字体：`LXGWNeoXiHei` (bold weight)

### 2. 全局应用
- 所有文本元素都使用霞鹜新晰黑
- 包含降级字体方案，确保兼容性

### 3. 特殊优化
- 表单元素、按钮、卡片等组件的字体优化
- 移动端和高分辨率屏幕适配
- 字体加载动画效果

## 验证方法

下载字体文件后，可以通过以下方式验证：

### 1. 浏览器开发者工具
1. 打开网站
2. 按F12打开开发者工具
3. 查看网络面板，确认字体文件加载成功
4. 查看计算样式，确认使用的是 LXGWNeoXiHei 字体

### 2. 视觉检查
- 检查中文字符显示是否清晰
- 确认字体风格统一
- 对比使用前后的显示效果

## 故障排除

### 字体未加载
1. 确认字体文件路径正确
2. 检查字体文件是否损坏
3. 确认浏览器支持字体格式

### 显示异常
1. 清除浏览器缓存
2. 检查CSS文件是否正确引入
3. 确认字体文件权限正确

### 性能问题
1. 字体文件较大，考虑使用 woff2 格式
2. 设置 `font-display: swap` 优化加载体验
3. 使用CDN加速字体下载

## 字体文件信息

- **文件名**: LXGWWenKai-Regular.ttf
- **文件大小**: 约 4-6MB
- **支持格式**: TTF, WOFF2
- **字符集**: 简体中文、繁体中文、英文、数字、符号
- **授权**: SIL Open Font License 1.1

## 备用方案

如果无法下载霞鹜新晰黑，系统会自动降级使用以下字体：
1. Noto Sans SC (Google 字体)
2. Microsoft YaHei (Windows 系统字体)
3. PingFang SC (macOS 系统字体)
4. 其他系统默认中文字体

## 联系方式

如有字体相关的问题，请：
1. 查看霞鹜新晰黑项目文档
2. 提交 GitHub Issue
3. 联系项目维护者

---

**注意**: 请确保遵守字体许可证条款，霞鹜新晰黑使用 SIL Open Font License 1.1，可以自由使用和分发。