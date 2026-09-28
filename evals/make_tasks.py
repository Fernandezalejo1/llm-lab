#!/usr/bin/env python3
"""Genera evals/tasks.jsonl con 50 tareas verificables.

Cada tarea tiene un test que se ejecuta de verdad (python/bash/sql)
o una respuesta exacta, igual que un eval de OpenAI con reward verificable.
Uso: python make_tasks.py   -> escribe tasks.jsonl
"""

import json

T = []  # tasks


def add(**kw):
    defaults = {"test_kind": "python", "timeout": 30}
    defaults.update(kw)
    T.append(defaults)


# ============================================================ python_core
add(id="py-001", category="python_core",
    prompt=("Escribí una función `fib(n)` que devuelva el n-ésimo número de "
            "Fibonacci (F(0)=0, F(1)=1). Si n es negativo, devolvé None. "
            "Respondé solo con el bloque ```python```."),
    test=("import solution\n"
          "assert solution.fib(0) == 0\n"
          "assert solution.fib(1) == 1\n"
          "assert solution.fib(10) == 55\n"
          "assert solution.fib(20) == 6765\n"
          "assert solution.fib(-3) is None\n"
          "print('OK')"))

add(id="py-002", category="python_core",
    prompt=("Escribí una función `is_palindrome(text)` que diga si un texto es "
            "palíndromo ignorando mayúsculas, espacios y signos de puntuación. "
            "Respondé solo con el bloque ```python```."),
    test=("import solution\n"
          "assert solution.is_palindrome('Anita lava la tina') is True\n"
          "assert solution.is_palindrome('reconocer') is True\n"
          "assert solution.is_palindrome('hola') is False\n"
          "assert solution.is_palindrome('') is True\n"
          "assert solution.is_palindrome('A man, a plan, a canal: Panama') is True\n"
          "print('OK')"))

add(id="py-003", category="python_core",
    prompt=("Escribí una función `reverse_words(s)` que invierta el orden de las "
            "palabras de un string manteniendo las palabras intactas y un único "
            "espacio entre ellas (sin espacios al inicio/fin). Respondé solo con "
            "el bloque ```python```."),
    test=("import solution\n"
          "assert solution.reverse_words('hola mundo') == 'mundo hola'\n"
          "assert solution.reverse_words('  uno  dos  tres ') == 'tres dos uno'\n"
          "assert solution.reverse_words('') == ''\n"
          "assert solution.reverse_words('sola') == 'sola'\n"
          "print('OK')"))

add(id="py-004", category="python_core",
    prompt=("Escribí una función `two_sum(nums, target)` que devuelva los índices "
            "de los dos números que suman `target` (existe siempre una única "
            "solución y no se usa el mismo elemento dos veces). Respondé solo con "
            "el bloque ```python```."),
    test=("import solution\n"
          "assert solution.two_sum([2, 7, 11, 15], 9) == [0, 1]\n"
          "assert solution.two_sum([3, 2, 4], 6) == [1, 2]\n"
          "assert solution.two_sum([3, 3], 6) == [0, 1]\n"
          "assert solution.two_sum([1, 5, -1, 2], 1) in ([2, 3], [3, 2])\n"
          "print('OK')"))

add(id="py-005", category="python_core",
    prompt=("Escribí una función `fizzbuzz(n)` que devuelva una lista de n "
            "elementos: 'Fizz' si el número (1-indexado) es múltiplo de 3, 'Buzz' "
            "si es múltiplo de 5, 'FizzBuzz' si es de ambos, y el número como "
            "string en otro caso. Respondé solo con el bloque ```python```."),
    test=("import solution\n"
          "assert solution.fizzbuzz(5) == ['1', '2', 'Fizz', '4', 'Buzz']\n"
          "assert solution.fizzbuzz(15)[14] == 'FizzBuzz'\n"
          "assert solution.fizzbuzz(3) == ['1', '2', 'Fizz']\n"
          "assert solution.fizzbuzz(0) == []\n"
          "print('OK')"))

add(id="py-006", category="python_core",
    prompt=("Escribí una función `flatten(lst)` que aplane completamente una "
            "lista de listas anidadas arbitrariamente y devuelva una lista de un "
            "solo nivel. Respondé solo con el bloque ```python```."),
    test=("import solution\n"
          "assert solution.flatten([1, [2, [3, [4]]], 5]) == [1, 2, 3, 4, 5]\n"
          "assert solution.flatten([]) == []\n"
          "assert solution.flatten([[[1]]]) == [1]\n"
          "assert solution.flatten([1, [], [2, 3]]) == [1, 2, 3]\n"
          "print('OK')"))

add(id="py-007", category="python_core",
    prompt=("Escribí una función `char_count(text)` que devuelva un dict con la "
            "frecuencia de cada carácter alfabético del texto, ignorando "
            "mayúsculas (cuenta todo en minúscula) y espacios. Respondé solo con "
            "el bloque ```python```."),
    test=("import solution\n"
          "assert solution.char_count('Hola Mundo') == {'h':1,'o':2,'l':1,'a':1,'m':1,'u':1,'n':1,'d':1}\n"
          "assert solution.char_count('') == {}\n"
          "assert solution.char_count('aaBB') == {'a':2,'b':2}\n"
          "print('OK')"))

add(id="py-008", category="python_core",
    prompt=("Escribí una función `longest_common_prefix(strings)` que devuelva el "
            "prefijo común más largo de una lista de strings ('' si no hay). "
            "Respondé solo con el bloque ```python```."),
    test=("import solution\n"
          "assert solution.longest_common_prefix(['flower','flow','flight']) == 'fl'\n"
          "assert solution.longest_common_prefix(['dog','racecar','car']) == ''\n"
          "assert solution.longest_common_prefix(['same','same']) == 'same'\n"
          "assert solution.longest_common_prefix([]) == ''\n"
          "print('OK')"))

add(id="py-009", category="python_core",
    prompt=("Escribí una función `is_balanced(s)` que diga si un string de "
            "paréntesis/llaves/corchetes está balanceado (cada apertura tiene su "
            "cierre en el orden correcto). Respondé solo con el bloque "
            "```python```."),
    test=("import solution\n"
          "assert solution.is_balanced('()') is True\n"
          "assert solution.is_balanced('()[]{}') is True\n"
          "assert solution.is_balanced('(]') is False\n"
          "assert solution.is_balanced('([)]') is False\n"
          "assert solution.is_balanced('{[]}') is True\n"
          "assert solution.is_balanced('') is True\n"
          "print('OK')"))

add(id="py-010", category="python_core",
    prompt=("Escribí una función `roman_to_int(s)` que convierta un número romano "
            "válido (I, V, X, L, C, D, M) a entero. Respondé solo con el bloque "
            "```python```."),
    test=("import solution\n"
          "assert solution.roman_to_int('III') == 3\n"
          "assert solution.roman_to_int('IV') == 4\n"
          "assert solution.roman_to_int('IX') == 9\n"
          "assert solution.roman_to_int('LVIII') == 58\n"
          "assert solution.roman_to_int('MCMXCIV') == 1994\n"
          "print('OK')"))

# ============================================================ algorithms
add(id="al-001", category="algorithms",
    prompt=("Escribí una función `binary_search(nums, target)` para una lista "
            "ordenada; devolvé el índice del target o -1 si no está. Respondé solo "
            "con el bloque ```python```."),
    test=("import solution\n"
          "assert solution.binary_search([1,3,5,7,9], 5) == 2\n"
          "assert solution.binary_search([1,3,5,7,9], 4) == -1\n"
          "assert solution.binary_search([], 1) == -1\n"
          "assert solution.binary_search([2], 2) == 0\n"
          "assert solution.binary_search([1,2,3,4,5], 1) == 0\n"
          "print('OK')"))

add(id="al-002", category="algorithms",
    prompt=("Escribí una función `merge_sorted(a, b)` que combine dos listas ya "
            "ordenadas en una sola ordenada. Respondé solo con el bloque "
            "```python```."),
    test=("import solution\n"
          "assert solution.merge_sorted([1,3,5], [2,4]) == [1,2,3,4,5]\n"
          "assert solution.merge_sorted([], []) == []\n"
          "assert solution.merge_sorted([1], [2]) == [1,2]\n"
          "assert solution.merge_sorted([1,1,1], [1]) == [1,1,1,1]\n"
          "print('OK')"))

add(id="al-003", category="algorithms",
    prompt=("Escribí una función `max_subarray(nums)` que devuelva la suma máxima "
            "de un subarreglo contiguo (algoritmo de Kadane). Respondé solo con el "
            "bloque ```python```."),
    test=("import solution\n"
          "assert solution.max_subarray([-2,1,-3,4,-1,2,1,-5,4]) == 6\n"
          "assert solution.max_subarray([1]) == 1\n"
          "assert solution.max_subarray([-1,-2]) == -1\n"
          "assert solution.max_subarray([5,-2,3]) == 6\n"
          "print('OK')"))

add(id="al-004", category="algorithms",
    prompt=("Definí una clase `Node` (con atributos value y next) y una función "
            "`has_cycle(head)` que detecte si una lista enlazada tiene un ciclo. "
            "Respondé solo con el bloque ```python```."),
    test=("import solution\n"
          "n1 = solution.Node(1); n2 = solution.Node(2); n3 = solution.Node(3)\n"
          "n1.next = n2; n2.next = n3\n"
          "assert solution.has_cycle(n1) is False\n"
          "n3.next = n1\n"
          "assert solution.has_cycle(n1) is True\n"
          "assert solution.has_cycle(None) is False\n"
          "n = solution.Node(5)\n"
          "assert solution.has_cycle(n) is False\n"
          "print('OK')"))

add(id="al-005", category="algorithms",
    prompt=("Escribí una función `kth_smallest(nums, k)` que devuelva el k-ésimo "
            "elemento más pequeño (k es 1-indexado). Respondé solo con el bloque "
            "```python```."),
    test=("import solution\n"
          "assert solution.kth_smallest([3,1,4,2], 2) == 2\n"
          "assert solution.kth_smallest([7], 1) == 7\n"
          "assert solution.kth_smallest([5,5,5,1], 3) == 5\n"
          "assert solution.kth_smallest([-3,-1,-2], 1) == -3\n"
          "print('OK')"))

add(id="al-006", category="algorithms",
    prompt=("Escribí una función `group_anagrams(words)` que agrupe palabras que "
            "son anagramas entre sí y devuelva una lista de listas. Respondé solo "
            "con el bloque ```python```."),
    test=("import solution\n"
          "got = sorted(sorted(g) for g in solution.group_anagrams(['ana','naa','hola','loha','aab']))\n"
          "assert got == sorted([['aab'], ['ana','naa'], ['hola','loha']]), got\n"
          "got2 = sorted(sorted(g) for g in solution.group_anagrams(['abc','cba','bca']))\n"
          "assert got2 == [['abc','bca','cba']], got2\n"
          "print('OK')"))

add(id="al-007", category="algorithms",
    prompt=("Escribí una función `edit_distance(a, b)` que calcule la distancia de "
            "Levenshtein entre dos strings. Respondé solo con el bloque "
            "```python```."),
    test=("import solution\n"
          "assert solution.edit_distance('kitten', 'sitting') == 3\n"
          "assert solution.edit_distance('', 'abc') == 3\n"
          "assert solution.edit_distance('abc', 'abc') == 0\n"
          "assert solution.edit_distance('horse', 'ros') == 3\n"
          "print('OK')"))

add(id="al-008", category="algorithms",
    prompt=("Escribí una función `contains_permutation(s1, s2)` que devuelva True "
            "si `s2` contiene alguna permutación de `s1` como subcadena contigua. "
            "Respondé solo con el bloque ```python```."),
    test=("import solution\n"
          "assert solution.contains_permutation('ab', 'eidbaooo') is True\n"
          "assert solution.contains_permutation('ab', 'eidboaoo') is False\n"
          "assert solution.contains_permutation('a', 'a') is True\n"
          "assert solution.contains_permutation('abc', 'ab') is False\n"
          "print('OK')"))

add(id="al-009", category="algorithms",
    prompt=("Escribí una clase `LRUCache(capacity)` con `get(key)` (devuelve -1 si "
            "no existe) y `put(key, value)`, expulsando el menos recientemente "
            "usado cuando excede la capacidad. Respondé solo con el bloque "
            "```python```."),
    test=("import solution\n"
          "c = solution.LRUCache(2)\n"
          "c.put(1, 1); c.put(2, 2)\n"
          "assert c.get(1) == 1\n"
          "c.put(3, 3)\n"
          "assert c.get(2) == -1\n"
          "c.put(4, 4)\n"
          "assert c.get(1) == -1\n"
          "assert c.get(3) == 3\n"
          "assert c.get(4) == 4\n"
          "print('OK')"))

add(id="al-010", category="algorithms",
    prompt=("Escribí una función `rotate_matrix(matrix)` que rote una matriz "
            "cuadrada 90° en sentido horario y devuelva la NUEVA matriz sin "
            "modificar la original. Respondé solo con el bloque ```python```."),
    test=("import solution\n"
          "m = [[1,2,3],[4,5,6],[7,8,9]]\n"
          "r = solution.rotate_matrix(m)\n"
          "assert r == [[7,4,1],[8,5,2],[9,6,3]], r\n"
          "assert m == [[1,2,3],[4,5,6],[7,8,9]]\n"
          "assert solution.rotate_matrix([[1]]) == [[1]]\n"
          "print('OK')"))

# ============================================================ debugging
add(id="db-001", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef sum_to(n):\n    return sum(range(1, n))\n```\n"
            "Corregí el error para que `sum_to(n)` devuelva 1+2+...+n. Devolvé el "
            "código corregido completo en un bloque ```python```."),
    test=("import solution\n"
          "assert solution.sum_to(5) == 15\n"
          "assert solution.sum_to(1) == 1\n"
          "assert solution.sum_to(10) == 55\n"
          "assert solution.sum_to(0) == 0\n"
          "print('OK')"))

add(id="db-002", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef smallest(nums):\n    m = nums[0]\n    for x in nums[1:]:\n        if x > m:\n            m = x\n    return m\n```\n"
            "Corregí el error para que devuelva el número más pequeño. Devolvé el "
            "código corregido completo en un bloque ```python```."),
    test=("import solution\n"
          "assert solution.smallest([3,1,2]) == 1\n"
          "assert solution.smallest([-5,0,5]) == -5\n"
          "assert solution.smallest([7]) == 7\n"
          "print('OK')"))

add(id="db-003", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef add_item(item, items=[]):\n    items.append(item)\n    return items\n```\n"
            "Corregí el error para que cada llamada sin lista use una lista nueva "
            "(sin el estado mutable compartido). Devolvé el código corregido "
            "completo en un bloque ```python```."),
    test=("import solution\n"
          "a = solution.add_item(1)\n"
          "b = solution.add_item(2)\n"
          "assert a == [1] and b == [2], (a, b)\n"
          "assert solution.add_item(3, [0]) == [0, 3]\n"
          "print('OK')"))

add(id="db-004", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef average(nums):\n    return sum(nums) // len(nums)\n```\n"
            "Corregí el error para que devuelva el promedio real (con decimales). "
            "Devolvé el código corregido completo en un bloque ```python```."),
    test=("import solution\n"
          "assert solution.average([1, 2]) == 1.5\n"
          "assert solution.average([1, 2, 3]) == 2.0\n"
          "assert solution.average([5]) == 5.0\n"
          "print('OK')"))

add(id="db-005", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef find_index(nums, target):\n    for i, n in enumerate(nums):\n        if n == target:\n            return i\n```\n"
            "Corregí el error para que devuelva -1 si el target no está. Devolvé "
            "el código corregido completo en un bloque ```python```."),
    test=("import solution\n"
          "assert solution.find_index([1,2,3], 2) == 1\n"
          "assert solution.find_index([1,2,3], 9) == -1\n"
          "assert solution.find_index([], 5) == -1\n"
          "print('OK')"))

add(id="db-006", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef evens_up_to(n):\n    out = []\n    for i in range(n + 1):\n        if i % 2 != 0:\n            out.append(i)\n    return out\n```\n"
            "Corregí el error para que devuelva los números PARES hasta n inclusive. "
            "Devolvé el código corregido completo en un bloque ```python```."),
    test=("import solution\n"
          "assert solution.evens_up_to(5) == [0, 2, 4]\n"
          "assert solution.evens_up_to(0) == [0]\n"
          "assert solution.evens_up_to(10) == [0, 2, 4, 6, 8, 10]\n"
          "print('OK')"))

add(id="db-007", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef remove_dup(nums):\n    return list(set(nums))\n```\n"
            "Corregí el error para que elimine duplicados CONSERVANDO el orden "
            "original de los elementos. Devolvé el código corregido completo en un "
            "bloque ```python```."),
    test=("import solution\n"
          "assert solution.remove_dup([1,2,1,3,2]) == [1,2,3]\n"
          "assert solution.remove_dup([4,4,4]) == [4]\n"
          "assert solution.remove_dup([]) == []\n"
          "print('OK')"))

add(id="db-008", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef double_first(nums):\n    nums[0] = nums[0] * 2\n    return nums\n```\n"
            "Corregí el error para que devuelva una NUEVA lista con el primer "
            "elemento duplicado, sin modificar la lista original. Devolvé el "
            "código corregido completo en un bloque ```python```."),
    test=("import solution\n"
          "lst = [1, 2, 3]\n"
          "out = solution.double_first(lst)\n"
          "assert out == [2, 2, 3], out\n"
          "assert lst == [1, 2, 3]\n"
          "print('OK')"))

add(id="db-009", category="debugging", timeout=20,
    prompt=("Este código tiene un bug (se cuelga): \n```python\ndef count_up_to(n):\n    out = []\n    i = 0\n    while i < n:\n        out.append(i)\n    return out\n```\n"
            "Corregí el error para que devuelva [0, 1, ..., n-1] sin loop infinito. "
            "Devolvé el código corregido completo en un bloque ```python```."),
    test=("import solution\n"
          "assert solution.count_up_to(3) == [0, 1, 2]\n"
          "assert solution.count_up_to(0) == []\n"
          "assert solution.count_up_to(5) == [0, 1, 2, 3, 4]\n"
          "print('OK')"))

add(id="db-010", category="debugging",
    prompt=("Este código tiene un bug: \n```python\ndef max_in(nums):\n    for n in nums:\n        return n\n```\n"
            "Corregí el error para que devuelva el valor máximo de la lista. "
            "Devolvé el código corregido completo en un bloque ```python```."),
    test=("import solution\n"
          "assert solution.max_in([1,5,3]) == 5\n"
          "assert solution.max_in([-1,-5]) == -1\n"
          "assert solution.max_in([7]) == 7\n"
          "print('OK')"))

# ============================================================ sql
add(id="sq-001", category="sql", test_kind="sql",
    schema=("CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);\n"
            "CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL);\n"
            "INSERT INTO customers VALUES (1,'Ana'),(2,'Luis'),(3,'Cata');\n"
            "INSERT INTO orders VALUES (1,1,100),(2,1,50),(3,2,75);"),
    expected=[["Ana", 2], ["Luis", 1], ["Cata", 0]],
    prompt=("Tenés estas tablas:\n```sql\n"
            "CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);\n"
            "CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL);\n```\n"
            "Escribí un SELECT que devuelva pares (name, cantidad de pedidos) de "
            "TODOS los clientes, incluidos los que no tienen pedidos (con 0). "
            "Respondé solo con el SELECT, sin explicaciones."))

add(id="sq-002", category="sql", test_kind="sql",
    schema=("CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT);\n"
            "CREATE TABLE sales(id INTEGER PRIMARY KEY, product_id INTEGER, amount REAL);\n"
            "INSERT INTO products VALUES (1,'Camisa'),(2,'Pantalon'),(3,'Zapatos');\n"
            "INSERT INTO sales VALUES (1,1,100),(2,1,50),(3,2,200),(4,3,75),(5,2,25);"),
    expected=[["Pantalon", 225.0], ["Camisa", 150.0], ["Zapatos", 75.0]],
    prompt=("Tenés estas tablas:\n```sql\n"
            "CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT);\n"
            "CREATE TABLE sales(id INTEGER PRIMARY KEY, product_id INTEGER, amount REAL);\n```\n"
            "Escribí un SELECT que devuelva (name, total vendido) de cada producto, "
            "ordenado de mayor total a menor. Respondé solo con el SELECT."))

add(id="sq-003", category="sql", test_kind="sql",
    schema=("CREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT);\n"
            "INSERT INTO users VALUES (1,'a@x.com'),(2,'b@x.com'),(3,'a@x.com'),(4,'c@x.com');"),
    expected=[["a@x.com"]],
    prompt=("Tenés esta tabla:\n```sql\nCREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT);\n```\n"
            "Escribí un SELECT que devuelva los emails que aparecen más de una vez. "
            "Respondé solo con el SELECT."))

add(id="sq-004", category="sql", test_kind="sql",
    schema=("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);\n"
            "CREATE TABLE scores(user_id INTEGER, score REAL);\n"
            "INSERT INTO users VALUES (1,'Ana'),(2,'Luis');\n"
            "INSERT INTO scores VALUES (1,8),(1,6),(2,10),(2,4);"),
    expected=[["Ana", 7.0], ["Luis", 7.0]],
    prompt=("Tenés estas tablas:\n```sql\n"
            "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);\n"
            "CREATE TABLE scores(user_id INTEGER, score REAL);\n```\n"
            "Escribí un SELECT que devuelva (name, promedio de scores) para cada "
            "usuario. Respondé solo con el SELECT."))

add(id="sq-005", category="sql", test_kind="sql",
    schema=("CREATE TABLE dept(id INTEGER PRIMARY KEY, name TEXT);\n"
            "CREATE TABLE emp(id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER, salary REAL);\n"
            "INSERT INTO dept VALUES (1,'Ventas'),(2,'IT');\n"
            "INSERT INTO emp VALUES (1,'Ana',1,5000),(2,'Luis',1,6000),(3,'Cata',2,7000),(4,'Leo',2,6500);"),
    expected=[["Ventas", "Luis"], ["IT", "Cata"]],
    prompt=("Tenés estas tablas:\n```sql\n"
            "CREATE TABLE dept(id INTEGER PRIMARY KEY, name TEXT);\n"
            "CREATE TABLE emp(id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER, salary REAL);\n```\n"
            "Escribí un SELECT que devuelva (departamento, nombre del empleado con "
            "el mayor salario) por departamento. Respondé solo con el SELECT."))

# ============================================================ reasoning
add(id="rs-001", category="reasoning", test_kind="answer", answer="4",
    prompt=("Un auto A sale a 60 km/h. Dos horas después, un auto B sale del mismo "
            "punto a 90 km/h por la misma ruta. ¿Cuántas horas después de la "
            "salida de B lo alcanza? Respondé únicamente con el número."))

add(id="rs-002", category="reasoning", test_kind="answer", answer="medico",
    prompt=("Ana, Bruno y Caro tienen profesiones distintas: médico, ingeniero y "
            "abogado. Ana no es abogada. Bruno no es médico. Caro es ingeniera. "
            "¿Cuál es la profesión de Ana? Respondé únicamente con la palabra."))

add(id="rs-003", category="reasoning", test_kind="answer", answer="2",
    prompt=("Tenés 8 monedas idénticas, pero una es más pesada. Tenés una balanza "
            "de dos platillos. ¿Cuál es el número MÍNIMO de pesajes que garantiza "
            "encontrar la moneda más pesada? Respondé únicamente con el número."))

add(id="rs-004", category="reasoning", test_kind="answer", answer="35",
    prompt=("Dentro de 5 años, la edad de Ana será el doble de la edad de su hijo. "
            "Hoy, las edades de Ana y su hijo suman 50. ¿Cuál es la edad actual de "
            "Ana? Respondé únicamente con el número."))

add(id="rs-005", category="reasoning", test_kind="answer", answer="42",
    prompt=("¿Cuál es el siguiente número de la secuencia: 2, 6, 12, 20, 30, ...? "
            "Respondé únicamente con el número."))

add(id="rs-006", category="reasoning", test_kind="answer", answer="1/6",
    prompt=("Se lanzan dos dados justos de 6 caras. ¿Cuál es la probabilidad de que "
            "la suma sea 7? Respondé únicamente con la fracción simplificada."))

add(id="rs-007", category="reasoning", test_kind="answer", answer="3",
    prompt=("Una receta usa 3/4 de taza de harina para 12 galletas. ¿Cuántas tazas "
            "de harina se necesitan para 48 galletas? Respondé únicamente con el "
            "número."))

add(id="rs-008", category="reasoning", test_kind="answer", answer="si",
    prompt=("Luisa tiene que estudiar 45 minutos, comer 30 minutos y jugar 60 "
            "minutos. Si empieza a las 14:30 y debe terminar todo antes de las "
            "17:00, ¿le alcanza el tiempo? Respondé únicamente con 'si' o 'no'."))

add(id="rs-009", category="reasoning", test_kind="answer", answer="80",
    prompt=("Un producto cuesta $80. Su precio sube 25% y después baja 20%. ¿Cuál "
            "es el precio final? Respondé únicamente con el número."))

add(id="rs-010", category="reasoning", test_kind="answer", answer="400",
    prompt=("Dos trenes salen del mismo punto en la misma dirección: A a 80 km/h y "
            "B a 100 km/h. B sale 1 hora después que A. ¿A qué distancia (en km) "
            "del punto de partida alcanza B a A? Respondé únicamente con el "
            "número."))

# ============================================================ bash
add(id="sh-001", category="bash", test_kind="bash",
    prompt=("Escribí un script bash que reciba la ruta de un archivo como primer "
            "argumento y muestre en pantalla SOLO el número de líneas del archivo. "
            "Respondé solo con el bloque ```bash```."),
    test=("printf 'a\\nb\\nc\\nd\\ne\\n' > data.txt\n"
          "bash solution.sh data.txt > out.txt\n"
          "[ \"$(cat out.txt | tr -d ' \\n')\" = \"5\" ] || { echo FAIL; exit 1; }\n"
          "echo PASS0"))

add(id="sh-002", category="bash", test_kind="bash",
    prompt=("Escribí un script bash que lea números (uno por línea) desde la "
            "entrada estándar y muestre SOLO la suma total. Respondé solo con el "
            "bloque ```bash```."),
    test=("printf '1\\n2\\n3\\n4\\n' | bash solution.sh > out.txt\n"
          "[ \"$(cat out.txt | tr -d ' \\n')\" = \"10\" ] || { echo FAIL; exit 1; }\n"
          "echo PASS0"))

add(id="sh-003", category="bash", test_kind="bash",
    prompt=("Escribí un script bash que, en el directorio actual, renombre todos "
            "los archivos con extensión .txt a .bak. Respondé solo con el bloque "
            "```bash```."),
    test=("touch a.txt b.txt\n"
          "bash solution.sh\n"
          "[ -f a.bak ] && [ -f b.bak ] && [ ! -f a.txt ] && [ ! -f b.txt ] || { echo FAIL; exit 1; }\n"
          "echo PASS0"))

add(id="sh-004", category="bash", test_kind="bash",
    prompt=("Escribí un script bash que reciba la ruta de un archivo como primer "
            "argumento y muestre sus líneas únicas ORDENADAS (sin duplicados). "
            "Respondé solo con el bloque ```bash```."),
    test=("printf 'b\\na\\nb\\nc\\na\\n' > data.txt\n"
          "bash solution.sh data.txt > out.txt\n"
          "[ \"$(cat out.txt | tr -d '\\n')\" = \"abc\" ] || { echo FAIL; exit 1; }\n"
          "echo PASS0"))

add(id="sh-005", category="bash", test_kind="bash",
    prompt=("Escribí un script bash que reciba la ruta de un archivo de texto como "
            "primer argumento y muestre todos los números que contiene el texto, "
            "uno por línea, en orden de aparición. Respondé solo con el bloque "
            "```bash```."),
    test=("printf 'abc 12 def 34 xyz 500\\n' > data.txt\n"
          "bash solution.sh data.txt > out.txt\n"
          "[ \"$(cat out.txt | tr -d '\\n')\" = \"1234500\" ] || { echo FAIL; exit 1; }\n"
          "echo PASS0"))


def main():
    assert len(T) == 50, f"se definieron {len(T)} tareas, esperaba 50"
    ids = [t["id"] for t in T]
    assert len(set(ids)) == len(ids), "ids duplicados"
    with open("tasks.jsonl", "w", encoding="utf-8") as f:
        for t in T:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    from collections import Counter
    print(f"Generadas {len(T)} tareas:", dict(Counter(t['category'] for t in T)))


if __name__ == "__main__":
    main()