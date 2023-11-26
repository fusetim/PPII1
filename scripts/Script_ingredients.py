import psycopg
import csv
import unicodedata
from unidecode import unidecode


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
    ud = unidecode(un)
    # Finally ignore all unicode and make every char lowercase.
    return ud.encode("ascii", "ignore").decode("ascii").lower()


conn = psycopg.connect("postgresql://ppii1@localhost:5432/ppii1")

conn.autocommit = True
cursor = conn.cursor()


sql = """create temporary table t (code varchar(10) PRIMARY KEY, name text, normalized_name text, co2 float)"""

cursor.execute(sql)


sql2 = """
copy t (code, name, normalized_name, co2)
from stdin;
"""

with open("/home/fusetim/Téléchargements/agribalyse-31-synthese.csv", "r") as f:
    data = csv.reader(f, delimiter=",")
    with cursor.copy(sql2) as copy:
        skip_header = data.__next__()
        for row in data:
            copy.write_row((row[0], row[4], normalize_str(row[4]), row[13]))

sql3 = """drop table if exists ingredients"""

cursor.execute(sql3)


sql4 = """create table ingredients (code varchar(10) PRIMARY KEY, name text, normalized_name text, co2 float)"""

cursor.execute(sql4)


sql5 = """insert into ingredients (code , name, normalized_name, co2 )
select code, name, name, co2
from t
"""

cursor.execute(sql5)


sql6 = """drop table t"""

cursor.execute(sql6)

conn.commit()
conn.close()
