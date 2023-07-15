import py_opengauss

# 如果你没有 gauss 用户，请登录 omm 用户创建一个

"""
[omm@bogon ~]$ gsql -d postgres -p 15400
openGauss=# CREATE USER gauss WITH PASSWORD "2023@gauss";
CREATE ROLE
"""

db = py_opengauss.open("pq://gauss:2023@gauss@127.0.0.1:15400/postgres")
# 注意，表重复创建（同名）会报错
db.execute(
    "CREATE TABLE emp (emp_first_name text, emp_last_name text, emp_salary numeric)"
)
make_emp = db.prepare("INSERT INTO emp VALUES ($1, $2, $3)")
make_emp("John", "Doe", "75322")
emp = db.prepare("SELECT * FROM emp;")
for row in emp():
    print(row)
