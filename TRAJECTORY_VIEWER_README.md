# Android World 轨迹查看器使用说明

## 简介

这是一个基于 Streamlit 的交互式可视化工具，用于查看和分析 Android World 任务执行轨迹。

## 功能特性

✨ **主要功能**：
- 📂 支持加载 `.pkl.gz` 格式的轨迹文件
- 📊 显示 Episode 元数据（任务目标、成功率、运行时间等）
- 🔍 逐步浏览任务执行的每一步
- 📸 可视化截图和 UI 元素边界框
- 🎯 查看每一步的动作详情和执行理由
- 🗂️ 浏览和搜索 UI 元素列表
- 💬 查看 LLM 的提示词和响应内容

## 安装依赖

```bash
pip install -r trajectory_viewer_requirements.txt
```

或者手动安装：

```bash
pip install streamlit numpy Pillow
```

## 运行方法

在项目根目录下运行：

```bash
streamlit run trajectory_viewer.py
```

程序将自动在浏览器中打开（默认地址：http://localhost:8501）

## 使用步骤

### 1. 加载轨迹文件

有两种方式加载轨迹文件：

**方式一：上传文件**
- 在左侧边栏选择"上传文件"
- 点击文件上传按钮，选择 `.pkl.gz` 文件

**方式二：本地路径**
- 在左侧边栏选择"本地路径"
- 输入完整的文件路径，例如：`/path/to/your/trajectory.pkl.gz`

### 2. 选择 Episode

如果轨迹文件包含多个 episode，在左侧边栏的下拉菜单中选择要查看的 episode。

### 3. 查看 Episode 元数据

页面顶部显示当前 episode 的元数据：
- **任务模板**：任务类型
- **实例 ID**：任务实例标识
- **成功率**：任务完成的成功程度（0-100%）
- **步骤数**：总共执行了多少步
- **运行时间**：任务执行耗时
- **代理名称**：执行任务的 Agent 名称
- **任务目标**：任务的具体目标描述

### 4. 浏览步骤详情

使用以下方式在步骤之间导航：
- **上一步/下一步按钮**：逐步浏览
- **滑块**：快速跳转到特定步骤

### 5. 查看步骤内容

每个步骤有四个标签页：

#### 📸 截图标签页
- 显示当前步骤的屏幕截图
- 支持多种截图类型（原始截图、带标注的截图等）
- 可选择显示 UI 元素的边界框，每个元素会用绿色框标注，并显示索引编号
- 点击元素时，可以在"UI 元素"标签页查看详细信息

#### 🎯 动作标签页
- 显示 Agent 执行的动作类型（点击、滑动、输入文本等）
- 显示动作参数（坐标、目标元素索引、输入文本等）
- 显示 Agent 选择该动作的理由
- 显示步骤执行的总结

#### 🗂️ UI 元素标签页
- 列出当前屏幕上的所有 UI 元素
- 支持搜索功能，可按文本、描述、ID 搜索
- 点击元素可查看详细属性：
  - 文本内容
  - 内容描述
  - 类名和资源 ID
  - 交互属性（可点击、可编辑、可滚动等）
  - 完整的原始数据

#### 💬 LLM 交互标签页
- 显示发送给 LLM 的提示词
- 显示 LLM 的原始响应
- 包括动作选择和步骤总结两个阶段的交互内容

## 数据格式说明

### Episode 数据结构

```python
{
    'task_template': str,        # 任务模板名称
    'instance_id': str,          # 实例 ID
    'goal': str,                 # 任务目标
    'is_successful': float,      # 成功率 (0.0-1.0)
    'episode_length': int,       # 步骤数
    'run_time': float,           # 运行时间（秒）
    'agent_name': str,           # Agent 名称
    'seed': int,                 # 随机种子
    'finish_dtime': datetime,    # 完成时间
    'episode_data': dict,        # 步骤数据（字典-列表格式）
}
```

### Step 数据结构

每个步骤可能包含以下字段（取决于 Agent 类型）：

```python
{
    # 观察数据
    'raw_screenshot': np.ndarray,              # 原始截图
    'before_screenshot': np.ndarray,           # 执行前截图
    'after_screenshot': np.ndarray,            # 执行后截图
    'before_screenshot_with_som': np.ndarray,  # 带标注的截图
    'ui_elements': list[dict],                 # UI 元素列表

    # 动作数据
    'action_prompt': str,                      # 动作选择提示词
    'action_output': str,                      # 动作输出
    'action_output_json': dict,                # 动作 JSON
    'action_reason': str,                      # 动作理由
    'action_raw_response': str,                # LLM 原始响应

    # 总结数据
    'summary_prompt': str,                     # 总结提示词
    'summary': str,                            # 步骤总结
    'summary_raw_response': str,               # 总结原始响应
}
```

### UI 元素数据结构

```python
{
    # 文本信息
    'text': str,                    # 显示文本
    'content_description': str,     # 内容描述
    'hint_text': str,              # 提示文本

    # 位置信息
    'bbox': dict,                  # 归一化边界框 (0-1)
    'bbox_pixels': dict,           # 像素边界框

    # 交互属性
    'is_clickable': bool,          # 可点击
    'is_editable': bool,           # 可编辑
    'is_scrollable': bool,         # 可滚动
    'is_checkable': bool,          # 可勾选

    # 标识信息
    'class_name': str,             # 类名
    'resource_id': str,            # 资源 ID
    'package_name': str,           # 包名
}
```

## 常见问题

### Q: 支持哪些文件格式？
A: 目前支持 Android World 标准的 `.pkl.gz` 格式（Gzip 压缩的 Pickle 文件）。

### Q: 为什么有些步骤没有截图？
A: 不同类型的 Agent 记录的数据不同。例如，RandomAgent 可能只记录基本信息，而 M3A 和 T3A Agent 会记录更详细的截图和交互数据。

### Q: UI 元素边界框显示不正确怎么办？
A: 确保轨迹数据中包含 `bbox` 或 `bbox_pixels` 字段。如果使用归一化坐标，程序会自动转换为像素坐标。

### Q: 如何快速找到特定的 UI 元素？
A: 在"UI 元素"标签页使用搜索功能，输入元素的文本、描述或资源 ID 进行过滤。

### Q: 程序运行缓慢怎么办？
A: 对于包含大量步骤或高分辨率截图的轨迹，加载可能较慢。建议：
   - 关闭不需要的边界框显示
   - 避免同时展开多个扩展面板
   - 考虑分批处理大型轨迹文件

## 技术栈

- **Streamlit**: 交互式 Web 应用框架
- **NumPy**: 数组处理
- **Pillow (PIL)**: 图像处理和标注

## 扩展和定制

### 自定义 UI 元素渲染

修改 `render_ui_element()` 函数以添加或修改显示的元素属性。

### 添加新的可视化功能

在相应的标签页添加新的可视化组件，例如：
- 动作轨迹图
- 成功率统计
- 时间线视图
- 比较多个 episode

### 导出功能

可以添加导出功能，例如：
- 导出特定步骤的截图
- 导出 LLM 交互记录
- 生成 PDF 报告

## 贡献

欢迎提出问题和改进建议！

## 许可证

与 Android World 项目保持一致。
