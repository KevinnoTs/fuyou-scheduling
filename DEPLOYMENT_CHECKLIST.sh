#!/bin/bash
# Fuyou Scheduling 部署验证清单

echo "🔍 Fuyou Scheduling 部署验证清单"
echo "=================================="

# 检查基础环境
echo "📦 基础环境检查："
echo "✅ Python版本: $(python3 --version)"
echo "✅ Git版本: $(git --version)"
echo "✅ Nginx状态: $(systemctl is-active nginx)"
echo "✅ 防火墙状态: $(sudo ufw status | head -1)"

# 检查项目文件
echo ""
echo "📁 项目文件检查："
cd /var/www/fuyou_scheduling 2>/dev/null || echo "❌ 项目目录不存在"
if [ -d "/var/www/fuyou_scheduling" ]; then
    echo "✅ 项目目录存在"
    echo "✅ requirements.txt: $([ -f "requirements.txt" ] && echo "存在" || echo "缺失")"
    echo "✅ 虚拟环境: $([ -d "venv" ] && echo "存在" || echo "缺失")"
    echo "✅ 应用文件: $([ -f "run.py" ] && echo "存在" || echo "缺失")"
fi

# 检查服务状态
echo ""
echo "🚀 服务状态检查："
echo "✅ Fuyou服务: $(systemctl is-active fuyou_scheduling 2>/dev/null || echo "未启动")"
echo "✅ 端口监听: $(sudo ss -tlnp | grep :8000 > /dev/null && echo "8000端口正常" || echo "8000端口未监听")"
echo "✅ Nginx代理: $(sudo ss -tlnp | grep :80 > /dev/null && echo "80端口正常" || echo "80端口未监听")"

# 网络测试
echo ""
echo "🌐 网络访问测试："
IP=$(hostname -I | awk '{print $1}')
echo "✅ 服务器IP: $IP"
echo "🔗 应用访问: http://$IP"
echo "🔗 Nginx访问: http://$IP (如果配置了Nginx)"

# 数据库检查
echo ""
echo "💾 数据库检查："
if [ -f "/var/www/fuyou_scheduling/instance/fuyou.db" ]; then
    echo "✅ 数据库文件存在"
    echo "📊 数据库大小: $(du -h /var/www/fuyou_scheduling/instance/fuyou.db | cut -f1)"
else
    echo "❌ 数据库文件不存在"
fi

echo ""
echo "📋 下一步操作建议："
echo "1. 如果所有项目都显示 ✅，说明部署成功"
echo "2. 访问 http://$IP 测试应用"
echo "3. 如果有问题，检查日志: sudo journalctl -u fuyou_scheduling -f"
echo "4. 查看Nginx日志: sudo tail -f /var/log/nginx/error.log"

echo ""
echo "🎉 部署验证完成！"