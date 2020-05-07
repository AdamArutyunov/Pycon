from data import db_session
from data.models.test import Test
from data.models.problem import Problem
from data.models.contest import Contest
import datetime

db_session.global_init("data/database/main.db")
session = db_session.create_session()

problem = Problem()
problem.name = "Вася и анальный граф"
problem.situation = 'Вася так долго ходил по графу, что пропустил, когда огромное ребро проникло ему прямо в анальное отверстие. Теперь Вася — вершина графа. Васе повезло, что граф оказался ненаправленным, и стрелка графа не воткнулась прямо ему в жопу. Однако, граф взвешенный. Помогите Васе найти ближайший выход к заданной вершине, где его уже ждут проктологи.'
problem.input_data = 'В первой строке находится единственное число N — количество вершин графа. В следующих N строках задана матрица смежности, где -1 означает отсутствие ребра между вершинами, а любое другое число определяет длину ребра. На главной диагонали матрицы стоят нули.<br>В последней сроке заданы два числа M и K — номера вершин с Васей и проктологами соответственно.'
problem.output_data = 'Выведите минимальную длину пути, который нужно преодолеть Васе, чтобы наложить швы на анус. Если такого пути не существует, выведите -1.'
problem.solution = 'print(-1)'
problem.time_limit = 2
problem.memory_limit = 64
test1 = Test()
test1.number = 1
test1.input_data = '''5
0 -1 4 -1 2
-1 0 -1 -1 1
4 -1 0 2 -1
-1 -1 2 0 3
2 1 -1 3 0
1 4'''
test1.output_data = '5'
test1.example = True
test1.problem = problem

test2 = Test()
test2.input_data = '''4
0 -1 -1 -1
-1 0 1 2
-1 1 0 3
-1 2 3 0
1 4'''
test2.output_data = '-1'
test2.number = 2
test2.example = True
test2.problem = problem

session.add(test1)
session.add(test2)
session.add(problem)
session.commit()


problem = Problem()
problem.name = "Тестовая задача"
problem.situation = '123'
problem.time_limit = 4
problem.memory_limit = 64
session.add(problem)
session.commit()

problem = Problem()
problem.name = "Тестовая задача 2"
problem.situation = '456'
problem.time_limit = 4
problem.memory_limit = 64
session.add(problem)
session.commit()


contest = Contest()
contest.name = 'Тестовый контест'
for problem in session.query(Problem).all():
    contest.problems.append(problem)

contest.start_date = datetime.datetime.now() + datetime.timedelta(minutes=30)
contest.duration = datetime.timedelta(hours=3)
session.add(contest)
session.commit()

