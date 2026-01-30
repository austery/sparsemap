# LLM Provider 配置指南

SparseMap 支持多个 LLM 提供商，您可以根据需求自由切换。

## 支持的提供商

### 1. **Gemini** (Google)
- ✅ 最新模型，JSON 输出质量好
- ✅ 免费额度充足
- ✅ 响应速度快

### 2. **DeepSeek** (OpenAI-compatible)
- ✅ 性价比高
- ✅ 中文支持好
- ✅ 兼容 OpenAI API

## 配置方法

### 使用 Gemini

在 `.env` 文件中设置：

```env
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.0-flash-exp
```

**获取 API Key**: https://aistudio.google.com/app/apikey

**可用模型**:
- `gemini-2.0-flash-exp` - 最新实验版（推荐）
- `gemini-1.5-flash` - 稳定快速版
- `gemini-1.5-pro` - 高级推理版

### 使用 DeepSeek

在 `.env` 文件中设置：

```env
LLM_PROVIDER=deepseek
LLM_API_KEY=your_deepseek_api_key
LLM_BASE_URL=https://space.ai-builders.com/backend/v1
LLM_MODEL=deepseek
```

**获取 API Key**: https://space.ai-builders.com/

## 切换提供商

只需修改 `.env` 文件中的 `LLM_PROVIDER` 参数，无需修改代码：

```bash
# 当前使用 Gemini
LLM_PROVIDER=gemini

# 切换到 DeepSeek
LLM_PROVIDER=deepseek
```

重启应用即可生效。

## 高级配置

可选参数（在 `.env` 中覆盖默认值）：

```env
LLM_TEMPERATURE=0.2      # 0.0-1.0，越低越确定
LLM_MAX_TOKENS=2000      # 最大输出 tokens
LLM_MAX_RETRIES=2        # 失败重试次数
```

## 添加新的提供商

如需支持其他 LLM，可参考 `src/sparsemap/services/providers/` 下的实现：

1. 继承 `LLMProvider` 抽象类
2. 实现 `generate_graph()` 和 `generate_raw()` 方法
3. 在 `llm.py` 的 `_get_provider()` 中注册

示例：参考 `gemini.py` 和 `deepseek.py` 的实现。
