# Locality Sensitive Hash function implementation.
#
# Motivation for this implementation is to develop a quick search "engine" for 
# the recipes and the ingredients.

def shringles(word: str, n: int):
    """
    Produces the shringles set of a word.

    Args: 
        - word (str): the given word
        - n (int): shringle length

    Return:
        List of distinct shringles (order is not guaranteed)
    """
    sh = set()
    for i in range(0, len(word)-3):
        sh.add(word[i:i+3])
    return list(sh)


def minhash(wvec: list[int], permutations: list[list[int]]):
    """
    Minhash the word vector (wvec) based on the key permutations.

    Args:
        - wvec (list[int]): word vector (based on the shringles)
        - permutations (list[list[int]]): key permutations to generate the dense vector

    Return:
        A signature vector (list[int]) produced by the word shringles and the key permutations.
    """
    sig = [0 for _ in range(len(permutations))]
    for k in range(len(permutations)):
        for l in range(len(wvec)):
            if wvec[permutations[k][l]] != 0:
                sig[k] = l
                break
    return sig
        