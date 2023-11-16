"""
Locality Sensitive Hash function implementation.

Motivation for this implementation is to develop a quick search "engine" for
the recipes and the ingredients.
"""

import hashlib
import unicodedata
import unidecode
import pytest


def normalize_str(word: str) -> str:
    """
    Normalizse a string to a lowercase ASCII-only (using unicode transformations) string

    Args:
        - word (str): the string to normalize

    Return:
        A normalize string (lowercase ASCII-only)
    """
    # Normalize the unicode string to the NFKC form (decompose and recompose
    # every char in mostly an unique form)
    un = unicodedata.normalize("NFKC", word)
    # Try to transliterate all unicode characters into an ascii-only form.
    ud = unidecode.unidecode(un)
    # Finally ignore all unicode and make every char lowercase.
    return ud.encode("ascii", "ignore").decode("ascii").lower()


def shringles(word: str, n: int) -> list[str]:
    """
    Produces the shringles set of a word.

    Args:
        - word (str): the given word
        - n (int): shringle length

    Return:
        List of distinct shringles (sorted in alphabetical order)

    Note: word SHOULD preferably be normalized beforehand.
    """
    if n <= 0:
        raise ValueError(f"got n: {n}, expected: n > 0")
    sh = set()
    for i in range(0, len(word) - n + 1):
        sh.add(word[i : i + n].lower())
    shl = list(sh)
    shl.sort()
    return shl


def minhash(wvec: list[int], permutations: list[list[int]]) -> list[int]:
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


def lsh(sig: list[int], b: int) -> list[(int, str)]:
    """
    Locality Sensitive Hash function.

    Args:
        - sig (list[int]): signature vector
        - b (int): number of bands

    Return:
        A list of tuples (band, digest) where band is the band number and digest
        is the corresponding hashed band.
    """
    hashes = []
    r = len(sig) // b
    # Implementation Note:
    # LSH splits the signature in multiple bands of same length (row). Each band get a unique hash.
    # The search is then done on the hashed bands and not the entire signature allowing to
    # perform a quick search on similarities of words.
    for i in range(b):
        end_slice = min(len(sig), (i + 1) * r)
        digest = hashlib.sha256(sig[i * r : end_slice]).hexdigest()
        hashes.append((i, digest))
    return hashes


def lsh_hash(
    word: str, k: int, b: int, permutations: list[list[int]], shringle_set: list[str]
) -> list[(int, str)]:
    """
    Locality Sensitive Hash function.

    Args:
        - word (str): the given word
        - k (int): shringle length
        - b (int): number of bands
        - permutations (list[list[int]]): key permutations to generate the dense vector
        - shringle_set (list[str]): set of shringles (each shringle is unique) and sorted
          in alphabetical order.
    Return:
        A list of tuples (band, digest) where band is the band number and digest is the
        corresponding hashed band.

    Important: k should be the same length used by the shringle_set. Shringles are always
    provided in lowercase.

    Note: word SHOULD preferably be normalized beforehand.
    """
    sh = shringles(word, k)
    # Preparing the word vector
    i, j = 0, 0
    wvec = [0 for _ in range(len(shringle_set))]
    while i < len(sh) and j < len(shringle_set):
        if sh[i] == shringle_set[j]:
            wvec[j] = 1
            i += 1
            j += 1
        elif sh[i] < shringle_set[j]:
            # In this case, the shringle sh[i] is not contained in the shringle_set (this can happen
            # for sake of performance). Therefore, we skip it.
            i += 1
        else:
            # In this case, the shringle shringle_set[j] is not part of the word. We can
            # safely skip it.
            j += 1
    sig = minhash(wvec, permutations)
    return lsh(sig, b)


def test_normalize():
    assert normalize_str("à la pêche aux moules") == "a la peche aux moules"
    assert normalize_str("peche") == "peche"
    assert normalize_str("Pêche") == "peche"
    assert normalize_str("Cœur") == "coeur"
    assert normalize_str("ひらがな") == "hiragana"
    assert normalize_str("平仮名") == "ping jia ming "


def test_shringles():
    assert shringles("peche", 2) == sorted(["pe", "ec", "ch", "he"])
    assert shringles("peche", 3) == sorted(["pec", "ech", "che"])
    assert shringles("a la peche", 2) == sorted(
        ["a ", " l", "la", " p", "pe", "ec", "ch", "he"]
    )
    assert shringles("", 2) == []


def test_negative_shringles():
    with pytest.raises(ValueError):
        shringles("", 0)
        shringles("", -1)
