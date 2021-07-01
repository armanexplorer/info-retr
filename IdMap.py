class IdMap:
    def __init__(self) -> None:
        self.str_to_id = {}
        self.id_to_str = []

    def __len__(self):
        return len(self.id_to_str)

    def _get_str(self, i):
        return self.id_to_str[i]

    def _get_id(self, s):
        if s in self.str_to_id.keys():
            return self.str_to_id[s]
        else:
            max_id = len(self.id_to_str)-1
            self.id_to_str.append(s)
            self.str_to_id[s] = max_id+1
            return self.str_to_id[s]

    def __getitem__(self, key):
        if type(key) is int:
            return self._get_str(key)
        elif type(key) is str:
            return self._get_id(key)
        else:
            raise TypeError

idmap = IdMap()

print(idmap._get_id('hi'))
print(idmap._get_id('hi'))
print(idmap._get_id('bye'))
print(idmap.__getitem__(1))
