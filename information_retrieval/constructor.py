import contextlib
from .inverted_index import InvertedIndexIterator, InvertedIndexWriter, InvertedIndexMapper
import pickle as pkl
import os
from .helper import IdMap
from typing import *
from hazm import *


class BSBIIndex:
    """
    Attributes
    ----------
    term_id_map IdMap: For mapping terms to termIDs
    doc_id_map(IdMap): For mapping relative paths of documents (eg path/to/docs/in/a/dir/) to docIDs
    data_dir(str): Path to data
    output_dir(str): Path to output index files
    index_name(str): Name assigned to index
    postings_encoding: Encoding used for storing the postings.
        The default (None) implies UncompressedPostings
    """

    def __init__(self, data_dir, output_dir, index_name="BSBI",
                 postings_encoding=None):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.index_name = index_name
        self.postings_encoding = postings_encoding

        # Stores names of intermediate indices
        self.intermediate_indices = []
        self.index()

    def save(self):
        """Dumps doc_id_map and term_id_map into output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'wb') as f:
            pkl.dump(self.term_id_map, f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'wb') as f:
            pkl.dump(self.doc_id_map, f)

    def load(self):
        """Loads doc_id_map and term_id_map from output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'rb') as f:
            self.term_id_map = pkl.load(f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'rb') as f:
            self.doc_id_map = pkl.load(f)

    def index(self):
        """Base indexing code

        This function loops through the data directories,
        calls parse_block to parse the documents
        calls invert_write, which inverts each block and writes to a new index
        then saves the id maps and calls merge on the intermediate indices
        """
        for block_dir_relative in sorted(next(os.walk(self.data_dir))[1]):
            td_pairs = self.parse_block(block_dir_relative)
            index_id = 'index_' + block_dir_relative
            self.intermediate_indices.append(index_id)
            with InvertedIndexWriter(index_id, directory=self.output_dir,
                                     postings_encoding=self.postings_encoding) as index:
                self.invert_write(td_pairs, index)
                td_pairs = None
        self.save()
        with InvertedIndexWriter(self.index_name, directory=self.output_dir,
                                 postings_encoding=self.postings_encoding) as merged_index:
            with contextlib.ExitStack() as stack:
                indices = [stack.enter_context(
                    InvertedIndexIterator(index_id,
                                          directory=self.output_dir,
                                          postings_encoding=self.postings_encoding))
                           for index_id in self.intermediate_indices]
                self.merge(indices, merged_index)

    def parse_block(self, block_dir_relative):
        """Parses a tokenized text file into termID-docID pairs

        Parameters
        ----------
        block_dir_relative : str
            Relative Path to the directory that contains the files for the block

        Returns
        -------
        List[Tuple[Int, Int]]
            Returns all the td_pairs extracted from the block

        Should use self.term_id_map and self.doc_id_map to get termIDs and docIDs.
        These persist across calls to parse_block
        """
        # Begin your code

        td_pairs = list()
        for filename in os.listdir(os.path.join(self.data_dir, block_dir_relative)):
            with open(os.path.join(self.data_dir, block_dir_relative, filename), 'r', encoding='utf8') as f:
                doc_id = self.doc_id_map._get_id(os.path.join(
                    self.data_dir, block_dir_relative, filename))
                tokens = word_tokenize(f.read())
                for token in tokens:
                    token_id = self.term_id_map._get_id(token)
                    td_pair = (token_id, doc_id)
                    td_pairs.append(td_pair)
        return td_pairs
        # End your code

    def invert_write(self, td_pairs, index):
        """Inverts td_pairs into postings_lists and writes them to the given index

        Parameters
        ----------
        td_pairs: List[Tuple[Int, Int]]
            List of termID-docID pairs
        index: InvertedIndexWriter
            Inverted index on disk corresponding to the block
        """
        # Begin your code
        d = dict()

        for pair in td_pairs:
            l = d.get(pair[0], [])
            l.append(pair[1])
            d[pair[0]] = l


        for term, postings_list in d.items():
            index.append(term, postings_list)
        # End your code

    def merge(self, indices, merged_index):
        """Merges multiple inverted indices into a single index

        Parameters
        ----------
        indices: List[InvertedIndexIterator]
            A list of InvertedIndexIterator objects, each representing an
            iterable inverted index for a block
        merged_index: InvertedIndexWriter
            An instance of InvertedIndexWriter object into which each merged
            postings list is written out one at a time
        """
        # Begin your code

        d = dict()
        # print(indices)
        for index in indices:
            # print(index)
            for term_id, postings_list in index:
                # print(term_id , postings_list , 'my print')
                # print(value)
                l: list = d.get(term_id, [])
                l.extend(postings_list)
                merged_index.append(term_id, l)
        # End your code

    def retrieve(self, query: AnyStr):
        """
        use InvertedIndexMapper here!
        Retrieves the documents corresponding to the conjunctive query

        Parameters
        ----------
        query: str
            Space separated list of query tokens

        Result
        ------
        List[str]
            Sorted list of documents which contains each of the query tokens.
            Should be empty if no documents are found.

        Should NOT throw errors for terms not in corpus
        """

        if len(self.term_id_map) == 0 or len(self.doc_id_map) == 0:
            self.load()

        # Begin your code
        with InvertedIndexMapper(self.index_name, directory=self.output_dir,
                                 postings_encoding=self.postings_encoding) as merged_index:
            tokens = word_tokenize(query)

            last_posting_list_doc_names: List[str] = None

            for token in tokens:
                posting_list = merged_index._get_postings_list(
                    self.term_id_map[token])
                posting_list_doc_names = sorted([self.doc_id_map[docid]
                                                 for docid in posting_list])

                last_posting_list_doc_names = sorted_intersect(
                    posting_list_doc_names, last_posting_list_doc_names)

            return last_posting_list_doc_names

        # End your code


def sorted_intersect(list1: List[Any], list2: List[Any]):
    """Intersects two (ascending) sorted lists and returns the sorted result


    Parameters
    ----------
    list1: List[Comparable]
    list2: List[Comparable]
        Sorted lists to be intersected

    Returns
    -------
    List[Comparable]
        Sorted intersection
    """
    # Begin your code
    if list2 is None:
        return list1
    return list(set(list1).intersection(set(list2)))
    # End your code
