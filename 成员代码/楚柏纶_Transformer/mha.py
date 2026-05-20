# mha.py
import numpy as np
from layernorm import LayerNorm


class MultiHeadAttention:
    """基于 NumPy 实现的多头自注意力模块。"""

    def __init__(self, hidden_size, num_heads):
        assert hidden_size % num_heads == 0, "hidden_size 必须能够被 num_heads 整除"

        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads

        # 查询、键、值以及输出投影矩阵
        self.Wq = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Wk = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Wv = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Wo = np.random.randn(hidden_size, hidden_size) * 0.01

        self.ln = LayerNorm(hidden_size)

    def split_heads(self, x):
        """将隐藏维度拆分为多个注意力头。

        输入形状：[seq_len, hidden_size]
        输出形状：[seq_len, num_heads, head_dim]
        """
        seq_len = x.shape[0]
        return x.reshape(seq_len, self.num_heads, self.head_dim)

    def merge_heads(self, x):
        """将多个注意力头重新合并为隐藏维度。

        输入形状：[seq_len, num_heads, head_dim]
        输出形状：[seq_len, hidden_size]
        """
        seq_len = x.shape[0]
        return x.reshape(seq_len, self.num_heads * self.head_dim)

    def softmax(self, x):
        """在最后一个维度上计算 softmax，并通过减去最大值提升数值稳定性。"""
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)

    def __call__(self, x):
        """执行多头自注意力计算。

        输入形状：[seq_len, hidden_size]
        输出形状：[seq_len, hidden_size]
        """
        x_norm = self.ln(x)

        q = x_norm @ self.Wq
        k = x_norm @ self.Wk
        v = x_norm @ self.Wv

        q = self.split_heads(q)
        k = self.split_heads(k)
        v = self.split_heads(v)

        # attn_scores 形状：[seq_len, seq_len, num_heads]
        # 第一个 seq_len 表示查询位置，第二个 seq_len 表示被关注的位置
        attn_scores = np.einsum("ihd,jhd->ijh", q, k) / np.sqrt(self.head_dim)
        attn_weights = self.softmax(attn_scores)

        # 根据注意力权重对 value 进行加权求和
        attn_output = np.einsum("ijh,jhd->ihd", attn_weights, v)

        out = self.merge_heads(attn_output)
        out = out @ self.Wo

        return out
