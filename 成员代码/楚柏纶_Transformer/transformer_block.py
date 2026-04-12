# transformer_block.py
from .mha import MultiHeadAttention
from .ffn import FeedForward

class TransformerBlock:
    def __init__(self, hidden_size, num_heads, dropout=0.1):
        self.mha = MultiHeadAttention(hidden_size, num_heads)
        self.ffn = FeedForward(hidden_size, dropout)

    def __call__(self, x):
        # 残差连接
        x = x + self.mha(x)
        x = x + self.ffn(x)
        return x
