import math
from .idf import Idf
import hazm
import os
class BM25Scorer:
    """ An abstract class for a scorer. 
        Implement query vector and doc vector.
        Needs to be extended by each specific implementation of scorers.
    """

    def __init__(self, idf: Idf, data_dir, query_weight_scheme=None, doc_weight_scheme=None):  # Modified
        self.idf: Idf = idf
        self.data_dir = data_dir
        self.avg_doc_len = 0
        self.default_query_weight_scheme = {"tf": 'b', "df": 't', "norm": None}  # boolean, idf, none
        self.default_doc_weight_scheme = {"tf": 'n', "df": 'n', "norm": None}  # natural, none

        self.query_weight_scheme = query_weight_scheme if query_weight_scheme is not None \
            else self.default_query_weight_scheme  # Modified (added)
        self.doc_weight_scheme = doc_weight_scheme if doc_weight_scheme is not None \
            else self.default_doc_weight_scheme  # Modified (added)

        
        for block_dir_relative in sorted(next(os.walk(self.data_dir))[1]):
            for filename in os.listdir(os.path.join(self.data_dir, block_dir_relative)):
                with open(os.path.join(self.data_dir, block_dir_relative, filename), 'r', encoding='utf8') as f:
                    self.avg_doc_len += self.get_len(self.get_doc_vector(f.read()))
        self.avg_doc_len /= idf.total_doc_num        
        # End your code

        
        
    def get_sim_score(self, q, d):
        """ Score each document for each query.
        Args:
            q (Query): the Query
            d (Document) :the Document

        Returns:
            pass now, will be implement in task 1, 2 and 3
        """

        ### Begin your code
        s = 0
        k1 = 2
        b = 0.75
        doc_vec = self.get_doc_vector(d)
        for term, qidf in self.get_query_vector(q).items():
            f = self.f(term, d)
            s = qidf *( f * (k1 + 1) / (f + k1 * (1 - b + b * self.get_len(doc_vec) / self.avg_doc_len)))
        return s
        # return self.idf(t) * baghali
        ### End your code

    def f(self, term, d):
        s = 0
        for w in hazm.word_tokenize(d):
            s += (w==term)
        return s or 1
    
    def get_len(self, doc_vec):
        return math.sqrt(sum([x*x for x in doc_vec.values()]))
    
    def get_query_vector(self, q):
        query_vec = {}
        ### Begin your code
        for t in hazm.word_tokenize(q):
            query_vec[t] = self.idf.get_idf(t)
        ### End your code
        return query_vec

    def get_doc_vector(self, d, doc_weight_scheme=None):
        doc_vec = {}

        ### Begin your code
        for t in hazm.word_tokenize(d):
            doc_vec[t] = self.idf.get_idf(t)
        
            
        ### End your code

        doc_vec = self.normalize_doc_vec(doc_vec)
        return doc_vec

    def normalize_doc_vec(self, doc_vec):
        ### Begin your code
        # print(doc_vec)
        l = self.get_len(doc_vec)
        return {x: v/l for x,v in doc_vec.items()}
        ### End your code
        # ...

# DATASET_PATH = './Dataset_IR/Train'
# OUTPUT_DIR = './results'
# if __name__ == '__main__':

#     BSBI_instance = BSBIIndex(data_dir=DATASET_PATH, output_dir=OUTPUT_DIR)
#     idf = Idf()
#     scorer = BM25Scorer()
#     d = "here is the document"
#     q = "here is the query"
#     score = scorer.get_sim_score(q, d)
#     print(score)
