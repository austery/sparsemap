# Prompt 测试指南

## 程序工作流程

```
用户输入文本
    ↓
build_prompt() 构建完整 prompt
    ↓
发送给 LLM (Gemini 或 DeepSeek)
    ↓
LLM 生成 JSON 响应
    ↓
extract_json() 提取 JSON
    ↓
repair_json() 修复格式问题
    ↓
Graph.model_validate() 解析验证
    ↓
返回知识图谱给前端展示
```

**你的理解完全正确！** ✅

## 在 Google AI Studio 测试

### 1. 访问 AI Studio
https://aistudio.google.com/

### 2. 完整的 Prompt 结构

#### System Instruction (Gemini 专用)
```
你是一位知识架构专家，擅长将复杂课程内容解构为清晰的逻辑骨架。
返回纯 JSON，不要包含 markdown 代码块。
```

#### User Prompt (主要内容)
```
你是一位资深的教学专家和知识架构师。请分析以下课程内容，提取逻辑骨架和知识依赖关系。

要求：
1. **识别主线逻辑**：课程的核心思想、步骤流程、关键主张（type: "main"）
2. **识别支线知识**：达成主线目标所需的技术工具、背景概念（type: "dependency"）
3. **最佳实践校验**：结合行业最佳实践，若文本遗漏关键步骤，请补充节点并标记 type 为 "suggested_best_practice"
4. **解释关系**：为每个依赖关系说明"为什么需要这个工具/概念"，节点提供 reason 字段

返回严格的 JSON 格式：
{
  "nodes": [
    {
      "id": "n1",
      "label": "节点名称",
      "type": "main" | "dependency" | "suggested_best_practice",
      "priority": "critical" | "optional",
      "reason": "节点出现的原因",
      "source": "text1",
      "description": "节点描述"
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "type": "depends_on" | "references" | "implements",
      "reason": "为什么需要这个依赖"
    }
  ],
  "summary": "整体课程逻辑的简要总结"
}

内容：

=== 来源 text1 ===
Robert C. "Uncle Bob" Martin is a software craftsman, and one of the leading names in contemporary software development. His books and videos are immensely popular.

In this unique live training session, Uncle Bob will use his signature presentation style to explain the benefits of the SOLID approach to application development. Crafted and defined through decades of first-hand design experience, SOLID has five principles that, when followed, make software designs easier to understand, more flexible, and less problematic to maintain.

[你的完整文本...]
```

### 3. 配置参数
- **Model**: `gemini-2.0-flash-exp`
- **Temperature**: `0.2`
- **Max output tokens**: `4000`

### 4. 期望输出
```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "SOLID Principles",
      "type": "main",
      "priority": "critical",
      "reason": "课程核心主题",
      "source": "text1",
      "description": "面向对象设计的五大原则"
    },
    {
      "id": "n2", 
      "label": "Clean Code",
      "type": "dependency",
      "priority": "critical",
      "reason": "SOLID 的基础",
      "source": "text1",
      "description": "编写可读性高的代码"
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "type": "depends_on",
      "reason": "SOLID 原则需要 Clean Code 作为基础"
    }
  ],
  "summary": "Uncle Bob 讲解 SOLID 设计原则及其在软件开发中的应用"
}
```

## 代码位置

### Prompt 构建
**文件**: `src/sparsemap/services/llm.py`
**函数**: `build_prompt(contents: List[dict]) -> str`

### DeepSeek System Prompt
**文件**: `src/sparsemap/services/providers/deepseek.py`
**位置**: `generate_graph()` 方法的 `system_content` 变量

### Gemini System Prompt
**文件**: `src/sparsemap/services/providers/gemini.py`
**位置**: `generate_graph()` 方法的 `system_instruction` 变量

## 快速测试命令

```bash
# 生成完整 prompt
cd /Users/leipeng/Documents/Projects/sparsemap
uv run python -c "
import sys
sys.path.insert(0, 'src')
from sparsemap.services.llm import build_prompt
contents = [{'source': 'text1', 'text': '你的测试文本'}]
print(build_prompt(contents))
"
```

## 调试技巧

1. **在 AI Studio 测试** - 快速验证 prompt 质量
2. **查看日志** - 检查 token 使用和响应长度
3. **调整 temperature** - 0.2 (确定) vs 0.5 (创造)
4. **增加 max_tokens** - 如果输出被截断

## 相关配置文件
- `.env` - LLM provider 和 API key
- `src/sparsemap/core/config.py` - 默认参数
