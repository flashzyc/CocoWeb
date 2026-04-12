# tokenizer.py
class CausalLMTokenizer:
    def __init__(self, vocab=None):
        if vocab is None:
            # 简单示例词表
            self.vocab = {chr(i+97): i for i in range(26)}
            self.vocab['<unk>'] = 26
            self.inv_vocab = {v: k for k, v in self.vocab.items()}
        else:
            self.vocab = vocab
            self.inv_vocab = {v: k for k, v in vocab.items()}

    def encode(self, text):
        return [self.vocab.get(char, self.vocab['<unk>']) for char in text]

    def decode(self, token_ids):
        return ''.join([self.inv_vocab.get(i, '<unk>') for i in token_ids])
