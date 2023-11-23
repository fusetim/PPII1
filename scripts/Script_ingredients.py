import psycopg

conn = psycopg.connect("postgresql://ppii1@localhost:5432/ppii1")

conn.autocommit = True
cursor = conn.cursor()


sql = '''create temporary table t (code varchar(10) PRIMARY KEY,x2 varchar(200),x3 varchar(200),x4 varchar(200), name text,x6 varchar(200),x7 varchar(200),x8 varchar(200),x9 varchar(200),x10 varchar(200),x11 varchar(200),x12 varchar(200),x13 varchar(200),co2 float,x15 varchar(200), x16 varchar(200),x17 varchar(200),x18 varchar(200),x19 varchar(200),x20 varchar(200),x21 varchar(200),x22 varchar(200),x23 varchar(200),x24 varchar(200),x25 varchar(200),x26 varchar(200),x27 varchar(200),x28 varchar(200),x29 varchar(200))'''

cursor.execute(sql)


sql2 = '''
copy t (code ,x2 ,x3 ,x4, name  ,x6 ,x7 ,x8 ,x9 ,x10 ,x11 ,x12 ,x13, co2  ,x15 ,x16 ,x17 ,x18 ,x19 ,x20 ,x21 ,x22 ,x23 ,x24 ,x25 ,x26 ,x27 ,x28, x29 )
from stdin
DELIMITER ','
CSV HEADER;
'''

with open('agribalyse-31-synthese.csv', 'r') as f:
    with cursor.copy(sql2) as copy:
        for line in f:
            copy.write(line)

sql3 = '''drop table if exists ingredients'''

cursor.execute(sql3)


sql4 = '''create table ingredients (code varchar(10) PRIMARY KEY, name text, co2 float)'''

cursor.execute(sql4)


sql5 = '''insert into ingredients (code , name , co2 )
select code, name, co2
from t
'''

cursor.execute(sql5)


sql6 = '''drop table t'''

cursor.execute(sql6)


conn.commit()
conn.close()