
from information_retrieval.helper import IdMap
import pickle as pkl
import os
import math


class Idf:
    """Build idf dictionary and return idf of a term, whether in or not in built dictionary.
        Recall from PA1 that postings_dict maps termID to a 3 tuple of
        (start_position_in_index_file, number_of_postings_in_list, length_in_bytes_of_postings_list)

        Remember that it's possible for a term to not appear in the collection corpus.
        Thus to guard against such a case, we will apply Laplace add-one smoothing.

        Note: We expect you to store the idf as {term: idf} and handle term which is not in posting_list

        Hint: For term not in built dictionary, we should return math.log10(total_doc_num / 1.0).
    """

    def __init__(self, total_doc_num, term_id_map, posting_dict):
        """Build an idf dictionary"""
        self.total_doc_num = total_doc_num
        self.total_term_num = len(term_id_map)
        self.postings_dict = posting_dict
        self.term_id_map: IdMap = term_id_map

    def get_idf(self, term=None):
        """Return idf of return idf of a term, whether in or not in built dictionary.
        Args:
            term(str) : term to return its idf
        Return(float):
            idf of the term
        """

        if term not in self.term_id_map.str_to_id.keys():
            return math.log10(self.total_doc_num / 1.0)

        nq = self.postings_dict[self.term_id_map[term]][1]
        return math.log10((self.total_doc_num - nq+0.5) / (nq + 0.5) + 1)

