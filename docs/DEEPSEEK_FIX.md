# DeepSeek JSON 解析问题修复

## 问题现象
```
DeepSeek response invalid on attempt 1: Unterminated string starting at: line 225 column 14
DeepSeek response invalid on attempt 2: Expecting ',' delimiter: line 213 column 36
```

## 根本原因
DeepSeek 生成的 JSON 包含未转义的特殊字符（引号、换行符等），导致解析失败。

## 解决方案

### 1. 参照 linklog 成功经验
通过对比 linklog 项目（已验证正常运行），发现关键差异：

| 配置项 | SparseMap (失败) | linklog (成功) |
|--------|------------------|----------------|
| Temperature | 0.2 | 0.3 |
| System Prompt | 简化版本 | 包含完整 JSON 示例 |
| JSON Schema | 在 user prompt | 在 system prompt |

### 2. 应用的修复

#### A. 更新 System Prompt
```python
# 完全复制 linklog 的成功 prompt
system_content = """你是一位知识架构专家...

**重要：JSON 格式要求**
1. 所有字符串中的特殊字符必须正确转义
2. 字符串中的双引号必须转义为 \\"
...

返回格式：
{
  "nodes": [...],
  "edges": [...],
  "summary": "..."
}"""
```

#### B. 调整温度参数
```python
temperature=0.3  # 与 linklog 保持一致
```

#### C. 增强 JSON 修复逻辑
添加 `repair_json()` 函数：
- 移除尾随逗号
- 提取 JSON 代码块
- 正则表达式提取
- 多层次修复尝试

### 3. 测试验证
```bash
# 重启应用测试
uv run sparsemap
```

## 经验教训

1. **Temperature 很重要**：0.2 vs 0.3 影响生成质量
2. **Prompt 结构**：JSON schema 应该在 system prompt 中明确
3. **已验证的配置优先**：复用成功项目的配置比自己调试更可靠
4. **渐进式修复**：基础修复 → 正则提取 → 降级方案

## 相关文件
- `src/sparsemap/services/providers/deepseek.py` - DeepSeek provider
- `src/sparsemap/services/llm_utils.py` - JSON 修复工具
- `/Users/leipeng/Documents/Projects/linklog/server.py` - 参考实现
