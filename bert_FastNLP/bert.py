import torch
import torch.nn as nn

import backbone

from utils import GeLU
from fastNLP.modules.other_modules import LayerNormalization


class BertSC(backbone.Bert):
    """
    BERT Sequence Classification Model: Bert based classification model for sequence
    """
    def __init__(self, vocab_size, hidden=768, n_layers=12, attn_heads=12, dropout=0.1, num_labels=2):
        """
        :param vocab_size: vocab_size of total words
        :param hidden: BERT model hidden size
        :param n_layers: numbers of Transformer blocks(layers)
        :param attn_heads: number of attention heads
        :param dropout: dropout rate
        :param num_labels: number of output labels
        """
        super(BertSC, self).__init__(vocab_size, hidden, n_layers, attn_heads, dropout)
        self.sc_num_labels = num_labels
        self.sc_dropout = nn.Dropout(dropout)
        self.sc_classifier = nn.Linear(hidden, num_labels)

    def forward(self, x, segment_info=None,, labels=None):
        _, pool_output = self.bert_forward(x, segment_info, all_output=False)
        
        pool_output = self.sc_dropout(pool_output)
        logits = self.sc_classifier(pool_output)

        return logits


class BertMLM(backbone.Bert):
    """
    BERT Mask Language Model: Bert based model for novel task of mask language model.
    """

    def __init__(self, vocab_size, hidden=768, n_layers=12, attn_heads=12, dropout=0.1):
        """
        :param vocab_size: vocab_size of total words
        :param hidden: BERT model hidden size
        :param n_layers: numbers of Transformer blocks(layers)
        :param attn_heads: number of attention heads
        :param dropout: dropout rate
        """

        super(BertMLM, self).__init__(vocab_size, hidden, n_layers, attn_heads, dropout)

        self.mlm_dense = nn.Linear(hidden, hidden)
        self.mlm_gelu = GeLU()
        self.mlm_LayerNorm = LayerNormalization(hidden)

        # The output weights are the same as the input embeddings, but there is
        # an output-only bias for each token.
        self.mlm_decoder = nn.Linear(
            self.embedding.token.embed.weight.size(1),
            self.embedding.token.embed.weight.size(0),
        )

    def forward(self, x, segment_info):
        # backbone bert
        output_layer, _ = self.bert_forward(x, segment_info, all_output=False)

        # mlm decoder
        output = self.mlm_dense(output_layer)
        output = self.mlm_gelu(output)
        output = self.mlm_LayerNorm(output)
        output = self.mlm_decoder(output)

        # output
        return output


