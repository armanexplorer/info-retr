from ranking.scorer import BM25Scorer
from ranking.idf import Idf
from information_retrieval.constructor import BSBIIndex
from information_retrieval.inverted_index import InvertedIndex
import os


DATASET_PATH = './Dataset_IR/Train'
OUTPUT_DIR = './results'
INDEX_NAME = "BSBI"
if __name__ == '__main__':
    BSBI_instance = BSBIIndex(data_dir=DATASET_PATH,
                              output_dir=OUTPUT_DIR, index_name=INDEX_NAME)

    merge_index = InvertedIndex(INDEX_NAME, directory=OUTPUT_DIR,
                                ).__enter__()

    query = input('search >>  ')

    # result = BSBI_instance.retrieve(query)

    idf = Idf(total_doc_num=len(BSBI_instance.doc_id_map),
              term_id_map=BSBI_instance.term_id_map, posting_dict=merge_index.postings_dict)

    result = dict()
    scorer = BM25Scorer(idf=idf, data_dir=DATASET_PATH)
    for block_dir_relative in sorted(next(os.walk(DATASET_PATH))[1]):
        for filename in os.listdir(os.path.join(DATASET_PATH, block_dir_relative)):
            with open(os.path.join(DATASET_PATH, block_dir_relative, filename), 'r', encoding='utf8') as f:
                s = scorer.get_sim_score(query, f.read())
                result[os.path.join(DATASET_PATH, block_dir_relative, filename)] = s
    
    # print()
    for k,v in dict(sorted(result.items(), reverse=True, key=lambda item: item[1])).items():
        print(f"{k}: {v}" )
    # print(sorted(result, key=result.get))
