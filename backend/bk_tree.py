

# Damerau–Levenshtein distance
def dl_distance(alphabet: str, word1: str, word2: str):
    """
    Returns the Damerau–Levenshtein distance between two strings.

    Args:
        alphabet (str): The alphabet of the strings.
        word1 (str): The first string.
        word2 (str): The second string.

    Returns:
        int: The Damerau–Levenshtein distance between the two strings.
    """
    dword1 = [0 for _ in range(len(alphabet))]

    mapping = dict()
    for i in range(len(alphabet)):
        mapping[alphabet[i]] = i

    distances = [[0 for _ in range(len(word2) + 2)] for _ in range(len(word1) + 2)]
    maxdist = len(word1) + len(word2)
    distances[0][0] = maxdist
    for i in range(1, len(word1) + 2):
        distances[i][0] = maxdist
        distances[i][1] = i - 1
    for j in range(1, len(word2) + 2):
        distances[0][j] = maxdist
        distances[1][j] = j - 1

    for i in range(2, len(word1) + 2):
        dword2 = 1
        for j in range(2, len(word2) + 2):
            k = dword1[mapping[word2[j - 2]]]
            l = dword2
            if word1[i - 2] == word2[j - 2]:
                cost = 0
                dword2 = j - 1
            else:
                cost = 1
            distances[i][j] = min(
                distances[i - 1][j - 1] + cost,
                distances[i][j - 1] + 1,
                distances[i - 1][j] + 1,
                distances[k - 1][l - 1] + (i - k - 1) + 1 + (j - l - 1),
            )
        dword1[mapping[word1[i - 2]]] = i
    return distances[len(word1) + 1][len(word2) + 1]


def test_dl_distance():
    """
    Test very simple cases of the Damerau–Levenshtein distance.
    """
    assert dl_distance("abc", "abc", "abc") == 0
    assert dl_distance("abc", "acb", "abc") == 2
    assert dl_distance("abc", "aba", "abc") == 1
    assert dl_distance("abc", "aba", "aca") == 1
    assert dl_distance("abc", "abc", "aaa") == 2


# BK-tree

class BKNode(object):
    """
    A node in a BK-tree.
    """
    word = None
    value = None
    children = dict()

    def __init__(self, word: str, value: any = None):
        """
        Initializes a BK-tree node.

        Args:
            word (str): The word of the node.
            value (any, optional): The value of the node. Defaults to None.
        """
        self.word = word
        self.value = value
    
    def insert(self, alphabet: str, word: str, value: any = None):
        """
        Inserts a word into the BK-tree.

        Args:
            alphabet (str): The alphabet of the words.
            word (str): The word to insert.
            value (any, optional): The value of the word. Defaults to None.
        """
        dist = dl_distance(alphabet, self.word, word)
        self.value = value
        if dist not in self.children:
            self.children[dist] = BKNode(word, value)
        else:
            self.children[dist].insert(alphabet, word, value)

    def get_value(self) -> any:
        """
        Returns the value of the node.

        Returns:
            any: The value of the node.
        """
        return self.value

    def get_children(self):
        """
        Returns the children of the node.

        Returns:
            list[(int, BKNode)]: The children of the node.
        """
        return self.children.items()
        

class BKTree(object):
    root = None
    alphabet = None

    def __init__(self, alphabet: str):
        """
        Initializes a BK-tree.

        Args:
            alphabet (str): The alphabet of the words.
        """
        self.alphabet = alphabet

    def insert(self, word: str, value: any = None):
        """
        Inserts a word into the BK-tree.

        Args:
            word (str): The word to insert.
            value (any, optional): The value of the word. Defaults to None.
        """
        if self.root is None:
            if value is None:
                value = word
            self.root = BKNode(word, value)
        else:
            u = self.root
            while u is not None:
                dist = dl_distance(self.alphabet, u.word, word)
                if dist == 0:
                    u.value = value
                    return
                elif dist not in u.children:
                    u.children[dist] = BKNode(word, value)
                    return
                else:
                    u = u.children[dist]

    def search(self, word: str, k: int = 5) -> list:
        """
        Searches for words in the BK-tree.

        Args:
            word (str): The word to search for.
            k (int, optional): The k most similar. Defaults to 5.

        Returns:
            list: A list of the values of similar words.
        """
        if self.root is None:
            return []
        else:
            S = [self.root]
            best_distance = dl_distance(self.alphabet, self.root.word, word)
            best_values = []
            while len(S) != 0:
                node = S.pop()
                dist =  dl_distance(self.alphabet, node, word)
                if dist <= best_distance:
                    best_distance = dist
                    best_values.append(node.get_value())
                    if len(best_values) > k:
                        best_values.pop(0)
                    for (d,c) in node.get_children():
                        if abs(d-dist) <= best_distance:
                            S.append(c)
            return best_values


def test_bk_tree():
    t = BKTree("baoekptrnsc")
    t.insert("book")
    t.insert("books")
    t.insert("boo")
    t.insert("cook")
    #t.insert("boon")
    #t.insert("cake")
    #t.insert("cape")
    #t.insert("cart")
    #assert t.search("book") == ["book"]
    #assert t.search("books") == ["book", "books"]