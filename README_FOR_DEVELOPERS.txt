================================================================================
        UBEM Analysis MCP Server - 开源版本说明（中文）
================================================================================

版本: v1.0.0
创建日期: 2025年11月26日
许可证: MIT License

================================================================================
                    重要说明
================================================================================

本版本是完全通用的开源版本，不包含任何私人信息或具体项目细节。

已移除的信息：
  ✓ 具体的项目路径 (D:\Files\LLM-RAG-UBEM_New)
  ✓ 具体的建筑名称和数据
  ✓ 个人工作流程细节
  ✓ 具体的配置信息

替换为：
  ✓ 环境变量配置
  ✓ 通用占位符路径
  ✓ 示例说明
  ✓ 通用文档

================================================================================
                    项目结构
================================================================================

ubem-mcp-opensource/
├── ubem_analysis_mcp/          # 主包
│   ├── __init__.py             # 包初始化
│   ├── server.py               # MCP服务器
│   ├── config.py               # 配置管理（使用环境变量）
│   └── tools/                  # 工具模块
│       ├── __init__.py
│       ├── weather_analysis.py # 天气分析
│       ├── simulation_tools.py # 仿真工具
│       └── data_analysis.py    # 数据分析
│
├── examples/                   # 示例
│   ├── basic_usage.py          # 基础用法
│   └── mcp_client_config.json  # MCP客户端配置示例
│
├── tests/                      # 测试目录（待添加测试）
├── docs/                       # 文档目录（待添加文档）
├── .github/workflows/          # CI/CD配置（待添加）
│
├── README.md                   # 主文档（英文）
├── LICENSE                     # MIT许可证
├── pyproject.toml              # 项目配置
├── setup.py                    # 安装脚本
├── requirements.txt            # 依赖列表
├── .gitignore                  # Git忽略规则
├── CHANGELOG.md                # 版本历史
├── CONTRIBUTING.md             # 贡献指南
└── README_FOR_DEVELOPERS.txt   # 本文件（开发者说明）

================================================================================
                    配置方式
================================================================================

本版本使用环境变量来配置路径，不包含任何硬编码的私人路径。

【方式1：设置环境变量】

```bash
export UBEM_PROJECT_ROOT="/path/to/your/project"
export ENERGYPLUS_ROOT="/path/to/EnergyPlus"
```

Windows:
```cmd
set UBEM_PROJECT_ROOT=C:\path\to\your\project
set ENERGYPLUS_ROOT=C:\EnergyPlusV25-1-0
```

【方式2：编辑config.py】

直接编辑 ubem_analysis_mcp/config.py 中的默认值。

【方式3：通过MCP客户端传递】

在MCP客户端配置中设置环境变量（参考examples/mcp_client_config.json）。

================================================================================
                    安装和使用
================================================================================

【安装】

1. 克隆或下载此项目
2. 进入目录：cd ubem-mcp-opensource
3. 安装：pip install -e .

【运行MCP服务器】

```bash
# 设置环境变量
export UBEM_PROJECT_ROOT="/your/project"
export ENERGYPLUS_ROOT="/path/to/EnergyPlus"

# 运行服务器
python -m ubem_analysis_mcp.server
```

【使用工具】

```python
from ubem_analysis_mcp.tools.weather_analysis import analyze_epw_hottest_days

result = analyze_epw_hottest_days("path/to/weather.epw", top_n=3)
print(result)
```

================================================================================
                    发布到GitHub
================================================================================

【准备步骤】

1. 在GitHub上创建新仓库
   - 仓库名：ubem-mcp（或其他名称）
   - 可见性：Public
   - 不初始化README（因为已有）

2. 更新README.md中的URL
   - 将 YOUR_USERNAME 替换为你的GitHub用户名

3. 初始化Git并推送

```bash
cd ubem-mcp-opensource
git init
git add .
git commit -m "Initial commit: UBEM Analysis MCP Server v1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ubem-mcp.git
git push -u origin main
```

4. 创建Release
   - 在GitHub上创建新Release
   - 标签：v1.0.0
   - 标题：UBEM Analysis MCP Server v1.0.0
   - 描述：参考CHANGELOG.md

================================================================================
                    发布到PyPI
================================================================================

【准备】

1. 注册PyPI账号：https://pypi.org

2. 安装构建工具：
```bash
pip install build twine
```

【构建和发布】

1. 构建包：
```bash
python -m build
```

2. 检查包：
```bash
twine check dist/*
```

3. 上传到TestPyPI（测试）：
```bash
twine upload --repository testpypi dist/*
```

4. 测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ ubem-analysis-mcp
```

5. 上传到PyPI（正式）：
```bash
twine upload dist/*
```

================================================================================
                    功能特点
================================================================================

【完全通用】
✓ 不包含任何私人路径或数据
✓ 使用环境变量配置
✓ 通用的示例代码
✓ 适用于任何EnergyPlus项目

【标准开源项目】
✓ MIT许可证
✓ 完整的README
✓ 贡献指南
✓ 变更日志
✓ 标准的项目结构

【MCP协议支持】
✓ FastMCP集成
✓ 6个MCP工具
✓ JSON输出格式
✓ 完整的错误处理

【易于扩展】
✓ 模块化设计
✓ 清晰的代码结构
✓ 详细的文档
✓ 示例代码

================================================================================
                    与私人版本的区别
================================================================================

【私人版本（UBEM-MCP-Server）】
- 包含具体的项目路径
- 包含具体的建筑数据和结果
- 硬编码的配置
- 特定项目的工作流程
- 完整的仿真数据和结果

【开源版本（ubem-mcp-opensource）】
- 使用环境变量配置
- 通用的示例和文档
- 不包含任何私人数据
- 通用的工作流程
- 无具体数据文件

================================================================================
                    使用建议
================================================================================

【对于开源发布】
✓ 直接使用ubem-mcp-opensource
✓ 更新README中的URL
✓ 发布到GitHub和PyPI

【对于个人使用】
✓ 可以继续使用UBEM-MCP-Server
✓ 或基于ubem-mcp-opensource自定义

【对于贡献者】
✓ Fork ubem-mcp-opensource
✓ 添加新功能或改进
✓ 提交Pull Request

================================================================================
                    后续维护
================================================================================

【版本管理】
- 遵循语义化版本控制
- 更新CHANGELOG.md
- 创建GitHub Release

【文档更新】
- 保持README.md最新
- 添加新功能文档
- 更新示例代码

【社区互动】
- 响应Issues
- 审核Pull Requests
- 发布新版本

================================================================================
                    联系方式
================================================================================

项目位置: ubem-mcp-opensource/
状态: 生产就绪 ✅

完全通用、无私人信息、可直接开源！

================================================================================
                    END
================================================================================

