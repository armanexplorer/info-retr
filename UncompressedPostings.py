import array
class UncompressedPostings:

    staticmethod
    def encode(postings_list):
        return array.array('L', postings_list).tobytes()

    @staticmethod
    def decode(encoded_postings_list):
        decoded_postings_list = array.array('L')
        decoded_postings_list.frombytes(encoded_postings_list) 
        return decoded_postings_list.tolist()

x = UncompressedPostings.encode([1,2,3])
print(x)
print(UncompressedPostings.decode(x))