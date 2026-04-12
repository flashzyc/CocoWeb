# test_causal_lm.py
import torch
from config import CausalLMConfig
from tokenizer import CausalLMTokenizer
from model import CausalLM

def test_zero_input():
    config = CausalLMConfig(vocab_size=10, hidden_size=8, num_layers=2, num_heads=2, max_position_embeddings=16)
    model = CausalLM(config)
    # 用torch替换np的权重
    model.embeddings = torch.nn.Parameter(torch.randn(config.vocab_size, config.hidden_size) * 0.01)
    model.head = torch.nn.Parameter(torch.randn(config.hidden_size, config.vocab_size) * 0.01)
    # 输入全0
    input_ids = [0, 0, 0, 0]
    # 用torch tensor
    x = model.embeddings[input_ids].detach().numpy()
    for block in model.blocks:
        x = block(x)
    x = model.ln_f(x)
    logits = x @ model.head.detach().numpy()
    print("logits shape:", logits.shape)
    print("logits:", logits)
    assert logits.shape == (len(input_ids), config.vocab_size)
    print("Test passed!")

if __name__ == "__main__":
    test_zero_input()
