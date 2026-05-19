# Transformer 实现项目

## 项目简介
Transformer是一种基于自注意力机制的神经网络架构，专门用于处理和生成自然语言等序列数据。它完全放弃了传统的循环处理方式，通过并行计算大幅提升了模型训练效率，是当前绝大多数大型语言模型的核心基础。
本项目是一个基于 NumPy 实现的轻量级 Transformer (Causal LM) 模型。包含了从基础的 LayerNorm、Multi-Head Attention 到完整的 Transformer Block 和推理逻辑的完整实现。

## 核心功能说明

### 1. 模型架构 (model.py)
*   **CausalLM**: 核心模型类，集成了词嵌入层 (Embeddings)、多个 Transformer Block 以及最后的输出头 (Head)。
*   支持前向传播 (forward) 和文本生成 (generate)。

### 2. 多头注意力机制 (mha.py)
*   **MultiHeadAttention**: 实现了分头、缩放点积注意力和线性映射。
*   通过矩阵运算实现高效的自注意力计算。

### 3. 前馈网络 (ffn.py)
*   **FeedForward**: 包含两层线性变换和 ReLU 激活函数。
*   引入了 Dropout 逻辑以增强模型鲁棒性。

### 4. 层归一化 (layernorm.py)
*   **LayerNorm**: 对输入进行均值和方差归一化，并带有可学习的缩放 (gamma) 和偏移 (beta) 参数。

### 5. Transformer 模块 (transformer_block.py)
*   **TransformerBlock**: 封装了多头注意力 (MHA) 和前馈网络 (FFN)，并实现了残差连接 (Residual Connections)。

### 6. 配置与分词 (config.py & tokenizer.py)
*   **CausalLMConfig**: 统一管理模型的超参数（层数、头数、隐藏层维度等）。
*   **CausalLMTokenizer**: 提供简单的字符级分词功能，支持 `encode` 和 `decode`。

---

## 截图展示

![截图](./screenshot_test.png)
