# config.py
class CausalLMConfig:
    def __init__(self, vocab_size=30522, hidden_size=768, num_layers=12, num_heads=12, max_position_embeddings=512, dropout=0.1):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.max_position_embeddings = max_position_embeddings
        self.dropout = dropout

    def to_dict(self):
        return self.__dict__
