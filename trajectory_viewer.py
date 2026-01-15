"""
Android World 轨迹可视化工具

使用 Streamlit 创建的交互式轨迹查看器，用于可视化和分析 Android World 任务执行轨迹。

运行方式：
    streamlit run trajectory_viewer.py
"""

import gzip
import io
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


# ============================================================================
# 数据加载函数
# ============================================================================

def load_trajectory_file(file_path: str) -> List[Dict[str, Any]]:
    """加载 .pkl.gz 格式的轨迹文件"""
    try:
        with gzip.open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data if isinstance(data, list) else [data]
    except Exception as e:
        st.error(f"加载文件失败: {e}")
        return []


def load_trajectory_from_bytes(file_bytes: bytes) -> List[Dict[str, Any]]:
    """从上传的文件字节加载轨迹数据"""
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(file_bytes)) as f:
            data = pickle.load(f)
        return data if isinstance(data, list) else [data]
    except Exception as e:
        st.error(f"解析文件失败: {e}")
        return []


def transpose_dol_to_lod(data: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """将字典-列表格式转换为列表-字典格式"""
    if not data:
        return []
    return [dict(zip(data.keys(), values)) for values in zip(*data.values())]


# ============================================================================
# UI 元素可视化
# ============================================================================

def draw_bbox_on_image(
    image: np.ndarray,
    ui_elements: List[Dict[str, Any]],
    selected_index: Optional[int] = None
) -> Image.Image:
    """在截图上绘制 UI 元素的边界框"""
    if image is None:
        return None

    # 转换为 PIL Image
    if isinstance(image, np.ndarray):
        pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
    else:
        pil_image = image

    draw = ImageDraw.Draw(pil_image)

    # 尝试加载字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font = ImageFont.load_default()

    for idx, elem in enumerate(ui_elements):
        # 获取边界框（优先使用像素坐标）
        bbox = elem.get('bbox_pixels') or elem.get('bbox')
        if not bbox:
            continue

        # 提取坐标
        if hasattr(bbox, 'x_min'):
            x_min, y_min = bbox.x_min, bbox.y_min
            x_max, y_max = bbox.x_max, bbox.y_max
        elif isinstance(bbox, dict):
            x_min = bbox.get('x_min', 0)
            y_min = bbox.get('y_min', 0)
            x_max = bbox.get('x_max', 0)
            y_max = bbox.get('y_max', 0)
        else:
            continue

        # 如果是归一化坐标，转换为像素坐标
        if x_max <= 1.0 and y_max <= 1.0:
            width, height = pil_image.size
            x_min, x_max = int(x_min * width), int(x_max * width)
            y_min, y_max = int(y_min * height), int(y_max * height)

        # 选择颜色（选中的元素用红色，其他用绿色）
        color = 'red' if idx == selected_index else 'green'
        width = 3 if idx == selected_index else 1

        # 绘制边界框
        draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=width)

        # 绘制索引标签
        label = f"{idx}"
        text_bbox = draw.textbbox((x_min, y_min - 15), label, font=font)
        draw.rectangle(text_bbox, fill=color)
        draw.text((x_min, y_min - 15), label, fill='white', font=font)

    return pil_image


def render_ui_element(elem: Dict[str, Any], index: int) -> str:
    """渲染单个 UI 元素的详细信息"""
    text = elem.get('text', '')
    content_desc = elem.get('content_description', '')
    class_name = elem.get('class_name', '')
    resource_id = elem.get('resource_id', '')

    # 构建显示文本
    parts = []
    if text:
        parts.append(f"📝 Text: `{text}`")
    if content_desc:
        parts.append(f"📄 Desc: `{content_desc}`")
    if class_name:
        parts.append(f"🏷️ Class: `{class_name}`")
    if resource_id:
        parts.append(f"🆔 ID: `{resource_id}`")

    # 添加交互属性
    attrs = []
    if elem.get('is_clickable'):
        attrs.append('✅ Clickable')
    if elem.get('is_editable'):
        attrs.append('✏️ Editable')
    if elem.get('is_scrollable'):
        attrs.append('📜 Scrollable')
    if elem.get('is_checkable'):
        attrs.append('☑️ Checkable')

    if attrs:
        parts.append(' | '.join(attrs))

    return '\n'.join(parts) if parts else f"Element {index}"


# ============================================================================
# 主界面
# ============================================================================

def main():
    st.set_page_config(
        page_title="Android World 轨迹查看器",
        page_icon="📱",
        layout="wide"
    )

    st.title("📱 Android World 轨迹查看器")
    st.markdown("---")

    # 侧边栏：文件加载
    with st.sidebar:
        st.header("📂 加载轨迹文件")

        # 选择加载方式
        load_method = st.radio(
            "选择加载方式：",
            ["上传文件", "本地路径"]
        )

        episodes = []

        if load_method == "上传文件":
            uploaded_file = st.file_uploader(
                "上传 .pkl.gz 文件",
                type=['gz', 'pkl'],
                help="选择 Android World 保存的轨迹文件"
            )
            if uploaded_file:
                episodes = load_trajectory_from_bytes(uploaded_file.read())
        else:
            file_path = st.text_input(
                "输入文件路径：",
                placeholder="/path/to/trajectory.pkl.gz"
            )
            if file_path and Path(file_path).exists():
                episodes = load_trajectory_file(file_path)
            elif file_path:
                st.error("文件不存在")

        if not episodes:
            st.info("👆 请加载一个轨迹文件")
            st.stop()

        st.success(f"✅ 成功加载 {len(episodes)} 个 episode(s)")

        # Episode 选择
        st.markdown("---")
        st.header("📊 选择 Episode")
        episode_idx = st.selectbox(
            "Episode 编号：",
            range(len(episodes)),
            format_func=lambda x: f"Episode {x}"
        )

    # 获取当前 episode
    episode = episodes[episode_idx]

    # 显示 Episode 元数据
    st.header(f"📋 Episode {episode_idx} 元数据")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("任务模板", episode.get('task_template', 'N/A'))
        st.metric("实例 ID", episode.get('instance_id', 'N/A'))

    with col2:
        is_successful = episode.get('is_successful', 0)
        success_color = "🟢" if is_successful > 0.5 else "🔴"
        st.metric(f"{success_color} 成功率", f"{is_successful:.2%}")
        st.metric("步骤数", episode.get('episode_length', 0))

    with col3:
        run_time = episode.get('run_time', 0)
        st.metric("运行时间", f"{run_time:.2f}s")
        st.metric("代理名称", episode.get('agent_name', 'N/A'))

    with col4:
        st.metric("随机种子", episode.get('seed', 'N/A'))
        finish_time = episode.get('finish_dtime', 'N/A')
        if finish_time != 'N/A':
            finish_time = str(finish_time)[:19]  # 截断时间戳
        st.metric("完成时间", finish_time)

    # 显示任务目标
    goal = episode.get('goal', 'N/A')
    st.info(f"🎯 **任务目标**: {goal}")

    # 异常信息（如果有）
    exception_info = episode.get('exception_info')
    if exception_info:
        st.error(f"⚠️ **异常信息**: {exception_info}")

    st.markdown("---")

    # 获取步骤数据
    episode_data = episode.get('episode_data', {})
    if not episode_data:
        st.warning("此 episode 没有步骤数据")
        st.stop()

    # 转换为列表-字典格式
    steps = transpose_dol_to_lod(episode_data)
    total_steps = len(steps)

    if total_steps == 0:
        st.warning("此 episode 没有步骤数据")
        st.stop()

    # 步骤导航
    st.header(f"🔍 步骤详情 (共 {total_steps} 步)")

    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.button("⬅️ 上一步", disabled=st.session_state.get('step_idx', 0) == 0):
            st.session_state.step_idx = max(0, st.session_state.get('step_idx', 0) - 1)

    with col2:
        step_idx = st.slider(
            "选择步骤：",
            0, total_steps - 1,
            st.session_state.get('step_idx', 0),
            key='step_slider'
        )
        st.session_state.step_idx = step_idx

    with col3:
        if st.button("下一步 ➡️", disabled=st.session_state.get('step_idx', 0) >= total_steps - 1):
            st.session_state.step_idx = min(total_steps - 1, st.session_state.get('step_idx', 0) + 1)

    # 获取当前步骤
    current_step = steps[step_idx]

    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["📸 截图", "🎯 动作", "🗂️ UI 元素", "💬 LLM 交互"])

    # Tab 1: 截图
    with tab1:
        st.subheader("截图")

        # 尝试多个可能的截图字段
        screenshot_keys = [
            'raw_screenshot',
            'before_screenshot_with_som',
            'after_screenshot_with_som',
            'before_screenshot',
            'after_screenshot'
        ]

        screenshots_found = {}
        for key in screenshot_keys:
            if key in current_step and current_step[key] is not None:
                screenshots_found[key] = current_step[key]

        if screenshots_found:
            # 创建列显示多个截图
            cols = st.columns(len(screenshots_found))
            for idx, (key, screenshot) in enumerate(screenshots_found.items()):
                with cols[idx]:
                    st.markdown(f"**{key.replace('_', ' ').title()}**")

                    # 获取对应的 UI 元素
                    ui_elements = None
                    if 'before' in key:
                        ui_elements = current_step.get('before_ui_elements') or current_step.get('ui_elements', [])
                    elif 'after' in key:
                        ui_elements = current_step.get('after_ui_elements', [])
                    else:
                        ui_elements = current_step.get('ui_elements', [])

                    # 绘制边界框
                    if ui_elements and st.checkbox(f"显示 UI 边界框 ({key})", key=f"bbox_{idx}"):
                        annotated_img = draw_bbox_on_image(screenshot, ui_elements)
                        st.image(annotated_img, use_container_width=True)
                    else:
                        st.image(screenshot, use_container_width=True)
        else:
            st.info("此步骤没有截图数据")

    # Tab 2: 动作
    with tab2:
        st.subheader("执行的动作")

        # 检查动作输出
        action_output = current_step.get('action_output_json') or current_step.get('action_output')

        if action_output:
            # 解析动作
            if isinstance(action_output, dict):
                action_data = action_output
            elif isinstance(action_output, str):
                try:
                    import json
                    action_data = json.loads(action_output)
                except:
                    action_data = {'raw': action_output}
            else:
                action_data = {'raw': str(action_output)}

            # 显示动作类型
            action_type = action_data.get('action_type', 'Unknown')
            st.markdown(f"### 🎯 动作类型: `{action_type}`")

            # 显示动作参数
            col1, col2 = st.columns(2)

            with col1:
                if 'index' in action_data and action_data['index'] is not None:
                    st.metric("目标元素索引", action_data['index'])
                if 'x' in action_data and action_data['x'] is not None:
                    st.metric("X 坐标", action_data['x'])
                if 'text' in action_data and action_data['text']:
                    st.text_input("输入文本", action_data['text'], disabled=True)

            with col2:
                if 'y' in action_data and action_data['y'] is not None:
                    st.metric("Y 坐标", action_data['y'])
                if 'direction' in action_data and action_data['direction']:
                    st.metric("滚动方向", action_data['direction'])
                if 'app_name' in action_data and action_data['app_name']:
                    st.metric("应用名称", action_data['app_name'])

            # 显示完整动作 JSON
            with st.expander("📄 查看完整动作 JSON"):
                st.json(action_data)
        else:
            st.info("此步骤没有动作数据")

        # 显示动作理由（如果有）
        action_reason = current_step.get('action_reason')
        if action_reason:
            st.markdown("### 💭 动作理由")
            st.markdown(f"> {action_reason}")

        # 显示步骤总结（如果有）
        summary = current_step.get('summary')
        if summary:
            st.markdown("### 📝 步骤总结")
            st.markdown(f"> {summary}")

    # Tab 3: UI 元素
    with tab3:
        st.subheader("UI 元素列表")

        # 获取 UI 元素
        ui_elements_keys = ['before_ui_elements', 'after_ui_elements', 'ui_elements', 'before_element_list', 'after_element_list']
        ui_data = {}

        for key in ui_elements_keys:
            if key in current_step and current_step[key]:
                ui_data[key] = current_step[key]

        if ui_data:
            # 选择要显示的 UI 元素集
            selected_ui_key = st.selectbox(
                "选择 UI 元素集：",
                list(ui_data.keys()),
                format_func=lambda x: x.replace('_', ' ').title()
            )

            ui_elements = ui_data[selected_ui_key]
            st.info(f"共 {len(ui_elements)} 个 UI 元素")

            # 搜索过滤
            search_term = st.text_input("🔍 搜索 UI 元素（文本、描述、ID）：")

            # 过滤元素
            filtered_elements = []
            for idx, elem in enumerate(ui_elements):
                if search_term:
                    text = str(elem.get('text', '')).lower()
                    desc = str(elem.get('content_description', '')).lower()
                    res_id = str(elem.get('resource_id', '')).lower()
                    if search_term.lower() not in text + desc + res_id:
                        continue
                filtered_elements.append((idx, elem))

            # 显示过滤后的元素
            st.info(f"显示 {len(filtered_elements)} 个元素")

            for idx, elem in filtered_elements:
                with st.expander(f"**[{idx}]** {elem.get('text', elem.get('content_description', elem.get('class_name', 'Element')))}"):
                    st.markdown(render_ui_element(elem, idx))

                    # 显示完整元素数据
                    with st.expander("🔍 查看完整数据"):
                        st.json({k: str(v) if not isinstance(v, (dict, list, int, float, bool, type(None))) else v
                                for k, v in elem.items()})
        else:
            st.info("此步骤没有 UI 元素数据")

    # Tab 4: LLM 交互
    with tab4:
        st.subheader("LLM 提示词和响应")

        # 动作提示词
        action_prompt = current_step.get('action_prompt')
        if action_prompt:
            with st.expander("🤖 动作选择提示词", expanded=True):
                st.code(action_prompt, language="text")

        # 动作原始响应
        action_raw_response = current_step.get('action_raw_response')
        if action_raw_response:
            with st.expander("💬 动作选择响应"):
                st.code(action_raw_response, language="text")

        # 总结提示词
        summary_prompt = current_step.get('summary_prompt')
        if summary_prompt:
            with st.expander("📋 总结提示词"):
                st.code(summary_prompt, language="text")

        # 总结原始响应
        summary_raw_response = current_step.get('summary_raw_response')
        if summary_raw_response:
            with st.expander("📝 总结响应"):
                st.code(summary_raw_response, language="text")

        if not any([action_prompt, action_raw_response, summary_prompt, summary_raw_response]):
            st.info("此步骤没有 LLM 交互数据")


if __name__ == "__main__":
    main()
