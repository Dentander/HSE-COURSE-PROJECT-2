import asyncio
import aiohttp

BASE = "http://localhost:8000/api/v1/course/admin"

COURSE = [
  {
    "id": "topic-1",
    "title": "Деревня Переменных",
    "items": [
      {
        "type": "lesson",
        "id": "variables-intro",
        "title": "Что такое переменная",
        "theoryBlocks": [
          {"type": "title", "content": "Переменные в C#"},
          {"type": "text", "content": "Переменная — это именованная область памяти, где хранится значение. Представь коробку с подписью: в коробке лежит что-то, а подпись говорит что именно."},
          {"type": "code", "content": 'int age = 18;\nstring name = "Ilya";\nbool isStudent = true;'},
          {"type": "text", "content": "Слева — тип данных, потом имя переменной, потом значение через знак =."}
        ]
      },
      {
        "type": "lesson",
        "id": "data-types",
        "title": "Основные типы данных",
        "theoryBlocks": [
          {"type": "title", "content": "Типы данных"},
          {"type": "text", "content": "Каждая переменная имеет тип — он говорит компилятору, что именно хранится в памяти."},
          {"type": "subtitle", "content": "Числа"},
          {"type": "code", "content": "int count = 10;       // целое число\ndouble price = 9.99;  // дробное число"},
          {"type": "subtitle", "content": "Текст и логика"},
          {"type": "code", "content": 'string title = "C# Study";\nbool isActive = false;'},
          {"type": "text", "content": "Использование правильного типа важно: если хранить деньги в int, дробная часть будет потеряна."}
        ]
      },
      {
        "type": "task",
        "id": "task-types",
        "title": "Задание: типы данных",
        "taskType": "single-choice",
        "npcText": "Рыцарь! Мне нужно хранить цену товара — 49.99. Какой тип выбрать?",
        "question": "Какой тип данных подходит для хранения дробных чисел?",
        "answers": ["int", "bool", "double", "string"],
        "correctIndex": 2,
        "rewardXp": 10
      },
      {
        "type": "lesson",
        "id": "constants",
        "title": "Константы",
        "theoryBlocks": [
          {"type": "title", "content": "Константы"},
          {"type": "text", "content": "Константа — это переменная, значение которой нельзя изменить после объявления. Используй ключевое слово const."},
          {"type": "code", "content": 'const double Pi = 3.14159;\nconst string AppName = "C# Study";'},
          {"type": "text", "content": "Если попытаться изменить константу — компилятор выдаст ошибку. Это защищает важные значения от случайного изменения."}
        ]
      },
      {
        "type": "lesson",
        "id": "type-conversion",
        "title": "Приведение типов",
        "theoryBlocks": [
          {"type": "title", "content": "Приведение типов"},
          {"type": "text", "content": "Иногда нужно преобразовать один тип в другой. Есть явное и неявное приведение."},
          {"type": "code", "content": "int a = 10;\ndouble b = a;        // неявное: int → double\n\ndouble x = 9.7;\nint y = (int)x;      // явное: double → int, дробь теряется"},
          {"type": "text", "content": "Явное приведение пишется в скобках перед значением. Будь осторожен — данные могут теряться."}
        ]
      },
      {
        "type": "task",
        "id": "task-conversion",
        "title": "Задание: приведение типов",
        "taskType": "fill-in-blank",
        "npcText": "Рыцарь! Мне нужно явно привести double к int, но я забыл синтаксис!",
        "codeTemplate": "double x = 9.7;\nint y = ___(x);",
        "blank": "(int)",
        "rewardXp": 15
      },
      {
        "type": "task",
        "id": "task-variables-match",
        "title": "Задание: сопоставь типы",
        "taskType": "match-pairs",
        "npcText": "Рыцарь! Помоги разложить типы по полкам!",
        "pairs": [
          {"left": "int", "right": "42"},
          {"left": "double", "right": "3.14"},
          {"left": "string", "right": '"hello"'},
          {"left": "bool", "right": "true"}
        ],
        "rewardXp": 15
      }
    ]
  },
  {
    "id": "topic-2",
    "title": "Замок Условий",
    "items": [
      {
        "type": "lesson",
        "id": "if-else",
        "title": "Оператор if/else",
        "theoryBlocks": [
          {"type": "title", "content": "Условный оператор if/else"},
          {"type": "text", "content": "Оператор if позволяет выполнить разный код в зависимости от условия."},
          {"type": "code", "content": 'int age = 20;\n\nif (age >= 18) {\n    Console.WriteLine("Доступ разрешён");\n} else {\n    Console.WriteLine("Доступ закрыт");\n}'}
        ]
      },
      {
        "type": "lesson",
        "id": "logical-operators",
        "title": "Логические операторы",
        "theoryBlocks": [
          {"type": "title", "content": "Логические операторы"},
          {"type": "text", "content": "Логические операторы позволяют объединять несколько условий в одно."},
          {"type": "code", "content": "bool a = true;\nbool b = false;\n\nConsole.WriteLine(a && b); // И: false\nConsole.WriteLine(a || b); // ИЛИ: true\nConsole.WriteLine(!a);     // НЕ: false"},
          {"type": "text", "content": "&& — оба должны быть true. || — достаточно одного true. ! — инвертирует значение."}
        ]
      },
      {
        "type": "task",
        "id": "task-if-fill",
        "title": "Задание: дополни условие",
        "taskType": "fill-in-blank",
        "npcText": "Стражник кричит: мой код пускает всех подряд! Вставь пропущенное слово!",
        "codeTemplate": '___ (age >= 18) {\n    Console.WriteLine("Добро пожаловать");\n}',
        "blank": "if",
        "rewardXp": 10
      },
      {
        "type": "lesson",
        "id": "switch",
        "title": "Оператор switch",
        "theoryBlocks": [
          {"type": "title", "content": "Оператор switch"},
          {"type": "text", "content": "Switch удобен когда нужно сравнить переменную с несколькими конкретными значениями."},
          {"type": "code", "content": 'string day = "Monday";\n\nswitch (day) {\n    case "Monday":\n        Console.WriteLine("Понедельник");\n        break;\n    case "Friday":\n        Console.WriteLine("Пятница");\n        break;\n    default:\n        Console.WriteLine("Другой день");\n        break;\n}'}
        ]
      },
      {
        "type": "lesson",
        "id": "ternary",
        "title": "Тернарный оператор",
        "theoryBlocks": [
          {"type": "title", "content": "Тернарный оператор"},
          {"type": "text", "content": "Тернарный оператор — это краткая форма if/else для простых условий."},
          {"type": "code", "content": 'int age = 20;\nstring result = age >= 18 ? "Взрослый" : "Ребёнок";\nConsole.WriteLine(result);'},
          {"type": "text", "content": "Синтаксис: условие ? значение_если_true : значение_если_false"}
        ]
      },
      {
        "type": "task",
        "id": "task-conditions-order",
        "title": "Задание: собери условие",
        "taskType": "code-order",
        "npcText": "Маг перепутал строки заклинания! Расставь их правильно!",
        "description": "Расставь строки так, чтобы программа проверяла доступ по возрасту",
        "codeLines": [
          "int age = 20;",
          "if (age >= 18) {",
          '    Console.WriteLine("Доступ разрешён");',
          "}"
        ],
        "correctOrder": [0, 1, 2, 3],
        "rewardXp": 20
      },
      {
        "type": "task",
        "id": "task-conditions-bug",
        "title": "Задание: найди баг",
        "taskType": "find-the-bug",
        "npcText": "Рыцарь! Моя программа падает — найди ошибку в коде!",
        "codeLines": [
          "int x = 10;",
          "if (x = 10) {",
          '    Console.WriteLine("Равно 10");',
          "}"
        ],
        "bugLineIndex": 1,
        "explanation": "Использован = вместо ==. Одно равно — это присваивание, два — сравнение.",
        "rewardXp": 20
      }
    ]
  },
  {
    "id": "topic-3",
    "title": "Лабиринт Циклов",
    "items": [
      {
        "type": "lesson",
        "id": "for-loop",
        "title": "Цикл for",
        "theoryBlocks": [
          {"type": "title", "content": "Цикл for"},
          {"type": "text", "content": "Цикл for используется когда заранее известно, сколько раз нужно повторить действие."},
          {"type": "code", "content": "for (int i = 0; i < 5; i++) {\n    Console.WriteLine(i);\n}"},
          {"type": "text", "content": "int i = 0 — начало. i < 5 — условие продолжения. i++ — шаг (увеличение на 1)."}
        ]
      },
      {
        "type": "lesson",
        "id": "while-loop",
        "title": "Цикл while",
        "theoryBlocks": [
          {"type": "title", "content": "Цикл while"},
          {"type": "text", "content": "While выполняется пока условие истинно. Удобен когда количество итераций заранее неизвестно."},
          {"type": "code", "content": "int count = 0;\n\nwhile (count < 3) {\n    Console.WriteLine(count);\n    count++;\n}"},
          {"type": "text", "content": "Важно не забыть изменять переменную внутри цикла — иначе получишь бесконечный цикл."}
        ]
      },
      {
        "type": "task",
        "id": "task-for-order",
        "title": "Задание: собери цикл",
        "taskType": "code-order",
        "npcText": "Фермер перепутал строки урожайного заклинания! Помоги собрать цикл!",
        "description": "Расставь строки чтобы получился правильный цикл for",
        "codeLines": [
          "for (int i = 0; i < 5; i++)",
          "{",
          "    Console.WriteLine(i);",
          "}"
        ],
        "correctOrder": [0, 1, 2, 3],
        "rewardXp": 20
      },
      {
        "type": "lesson",
        "id": "foreach-loop",
        "title": "Цикл foreach",
        "theoryBlocks": [
          {"type": "title", "content": "Цикл foreach"},
          {"type": "text", "content": "Foreach удобен для перебора элементов коллекции — не нужно следить за индексом."},
          {"type": "code", "content": 'string[] names = { "Alice", "Bob", "Charlie" };\n\nforeach (string name in names) {\n    Console.WriteLine(name);\n}'}
        ]
      },
      {
        "type": "lesson",
        "id": "break-continue",
        "title": "break и continue",
        "theoryBlocks": [
          {"type": "title", "content": "break и continue"},
          {"type": "text", "content": "break — прерывает цикл полностью. continue — пропускает текущую итерацию и идёт к следующей."},
          {"type": "code", "content": "for (int i = 0; i < 10; i++) {\n    if (i == 3) continue; // пропустить 3\n    if (i == 7) break;    // остановиться на 7\n    Console.WriteLine(i);\n}"}
        ]
      },
      {
        "type": "task",
        "id": "task-loops-choice",
        "title": "Задание: выбери цикл",
        "taskType": "single-choice",
        "npcText": "Нужно перебрать всех жителей деревни. Какой цикл удобнее всего?",
        "question": "Какой цикл лучше всего подходит для перебора элементов массива?",
        "answers": ["for", "while", "foreach", "do-while"],
        "correctIndex": 2,
        "rewardXp": 10
      },
      {
        "type": "task",
        "id": "task-loops-bug",
        "title": "Задание: найди баг",
        "taskType": "find-the-bug",
        "npcText": "Лабиринт не заканчивается — цикл бесконечный! Найди ошибку!",
        "codeLines": [
          "int i = 0;",
          "while (i < 5) {",
          "    Console.WriteLine(i);",
          "}"
        ],
        "bugLineIndex": 3,
        "explanation": "Нет i++ внутри цикла. Переменная i никогда не меняется, цикл бесконечен.",
        "rewardXp": 20
      }
    ]
  },
  {
    "id": "topic-4",
    "title": "Башня Методов",
    "items": [
      {
        "type": "lesson",
        "id": "methods-intro",
        "title": "Объявление методов",
        "theoryBlocks": [
          {"type": "title", "content": "Методы в C#"},
          {"type": "text", "content": "Метод — это именованный блок кода. Пишешь один раз, вызываешь сколько угодно раз."},
          {"type": "code", "content": 'void SayHello() {\n    Console.WriteLine("Hello!");\n}\n\nSayHello(); // вызов'},
          {"type": "text", "content": "void означает что метод ничего не возвращает. SayHello — имя метода."}
        ]
      },
      {
        "type": "lesson",
        "id": "method-params",
        "title": "Параметры методов",
        "theoryBlocks": [
          {"type": "title", "content": "Параметры"},
          {"type": "text", "content": "Параметры позволяют передавать данные в метод."},
          {"type": "code", "content": 'void Greet(string name) {\n    Console.WriteLine("Привет, " + name + "!");\n}\n\nGreet("Ilya");   // Привет, Ilya!\nGreet("Alice");  // Привет, Alice!'}
        ]
      },
      {
        "type": "task",
        "id": "task-methods-bug",
        "title": "Задание: найди баг",
        "taskType": "find-the-bug",
        "npcText": "Маг кричит: моё заклинание не работает! Найди ошибку!",
        "codeLines": [
          "void SayHello()",
          "{",
          '    Console.WriteLine("Hello")',
          "}"
        ],
        "bugLineIndex": 2,
        "explanation": "Пропущена точка с запятой в конце строки с Console.WriteLine.",
        "rewardXp": 20
      },
      {
        "type": "lesson",
        "id": "return-values",
        "title": "Возвращаемые значения",
        "theoryBlocks": [
          {"type": "title", "content": "Возвращаемые значения"},
          {"type": "text", "content": "Метод может вернуть результат. Вместо void пишем тип возвращаемого значения и используем return."},
          {"type": "code", "content": "int Add(int a, int b) {\n    return a + b;\n}\n\nint result = Add(3, 5);\nConsole.WriteLine(result); // 8"}
        ]
      },
      {
        "type": "lesson",
        "id": "method-overload",
        "title": "Перегрузка методов",
        "theoryBlocks": [
          {"type": "title", "content": "Перегрузка методов"},
          {"type": "text", "content": "В C# можно создать несколько методов с одинаковым именем, но разными параметрами."},
          {"type": "code", "content": "int Add(int a, int b) {\n    return a + b;\n}\n\ndouble Add(double a, double b) {\n    return a + b;\n}\n\nConsole.WriteLine(Add(2, 3));       // 5\nConsole.WriteLine(Add(1.5, 2.5));   // 4.0"},
          {"type": "text", "content": "Компилятор сам выберет нужную версию метода в зависимости от типа аргументов."}
        ]
      },
      {
        "type": "task",
        "id": "task-methods-choice",
        "title": "Задание: тип метода",
        "taskType": "single-choice",
        "npcText": "Башенный страж спрашивает: что написать вместо void, если метод должен вернуть число?",
        "question": "Какой тип возврата указать для метода, который возвращает целое число?",
        "answers": ["void", "return", "int", "number"],
        "correctIndex": 2,
        "rewardXp": 10
      },
      {
        "type": "task",
        "id": "task-methods-match",
        "title": "Задание: сопоставь понятия",
        "taskType": "match-pairs",
        "npcText": "Помоги магу разложить свитки по полкам!",
        "pairs": [
          {"left": "void", "right": "Метод ничего не возвращает"},
          {"left": "return", "right": "Возврат значения из метода"},
          {"left": "параметр", "right": "Данные, передаваемые в метод"},
          {"left": "перегрузка", "right": "Методы с одним именем, но разными параметрами"}
        ],
        "rewardXp": 20
      }
    ]
  },
  {
    "id": "topic-5",
    "title": "Рынок Массивов",
    "items": [
      {
        "type": "lesson",
        "id": "arrays-intro",
        "title": "Массивы",
        "theoryBlocks": [
          {"type": "title", "content": "Массивы в C#"},
          {"type": "text", "content": "Массив хранит несколько значений одного типа под одним именем. Элементы нумеруются с нуля."},
          {"type": "code", "content": "int[] numbers = { 10, 20, 30, 40, 50 };\n\nConsole.WriteLine(numbers[0]); // 10\nConsole.WriteLine(numbers[4]); // 50\nConsole.WriteLine(numbers.Length); // 5"}
        ]
      },
      {
        "type": "lesson",
        "id": "arrays-loops",
        "title": "Перебор массива",
        "theoryBlocks": [
          {"type": "title", "content": "Перебор массива"},
          {"type": "text", "content": "Массивы удобно перебирать циклами."},
          {"type": "code", "content": "int[] scores = { 5, 3, 8, 1, 9 };\n\n// через for:\nfor (int i = 0; i < scores.Length; i++) {\n    Console.WriteLine(scores[i]);\n}\n\n// через foreach:\nforeach (int score in scores) {\n    Console.WriteLine(score);\n}"}
        ]
      },
      {
        "type": "task",
        "id": "task-arrays-order",
        "title": "Задание: собери перебор",
        "taskType": "code-order",
        "npcText": "Торговец перепутал все ценники! Расставь код правильно!",
        "description": "Собери цикл перебора массива в правильном порядке",
        "codeLines": [
          'string[] items = { "меч", "щит", "зелье" };',
          "foreach (string item in items)",
          "{",
          "    Console.WriteLine(item);",
          "}"
        ],
        "correctOrder": [0, 1, 2, 3, 4],
        "rewardXp": 20
      },
      {
        "type": "lesson",
        "id": "lists",
        "title": "Списки List",
        "theoryBlocks": [
          {"type": "title", "content": "List в C#"},
          {"type": "text", "content": "List — это динамический массив. В отличие от обычного массива, его размер можно менять."},
          {"type": "code", "content": "List<string> names = new List<string>();\n\nnames.Add(\"Alice\");\nnames.Add(\"Bob\");\nnames.Remove(\"Alice\");\n\nConsole.WriteLine(names.Count); // 1"}
        ]
      },
      {
        "type": "lesson",
        "id": "multidimensional",
        "title": "Многомерные массивы",
        "theoryBlocks": [
          {"type": "title", "content": "Многомерные массивы"},
          {"type": "text", "content": "Двумерный массив — это таблица из строк и столбцов."},
          {"type": "code", "content": "int[,] grid = {\n    { 1, 2, 3 },\n    { 4, 5, 6 }\n};\n\nConsole.WriteLine(grid[0, 0]); // 1\nConsole.WriteLine(grid[1, 2]); // 6"}
        ]
      },
      {
        "type": "task",
        "id": "task-arrays-match",
        "title": "Задание: сопоставь операции",
        "taskType": "match-pairs",
        "npcText": "Помоги торговцу разобрать товар по полкам!",
        "pairs": [
          {"left": "numbers[0]", "right": "Первый элемент массива"},
          {"left": ".Length", "right": "Количество элементов"},
          {"left": ".Add()", "right": "Добавить элемент в List"},
          {"left": ".Remove()", "right": "Удалить элемент из List"}
        ],
        "rewardXp": 20
      },
      {
        "type": "task",
        "id": "task-arrays-bug",
        "title": "Задание: найди баг",
        "taskType": "find-the-bug",
        "npcText": "Программа торговца падает с ошибкой! Найди где!",
        "codeLines": [
          'int[] prices = { 10, 20, 30 };',
          "Console.WriteLine(prices[3]);"
        ],
        "bugLineIndex": 1,
        "explanation": "Индекс 3 выходит за пределы массива. У массива из 3 элементов индексы: 0, 1, 2.",
        "rewardXp": 20
      }
    ]
  }
]


async def post(session, url, data):
    async with session.post(url, json=data) as r:
        text = await r.text()
        if r.status not in (200, 201):
            print(f"  ERR {r.status}: {url} → {text[:120]}")
        return r.status


async def cleanup(session):
    print("Очищаю БД...")
    for topic in COURSE:
        async with session.delete(f"{BASE}/topics/{topic['id']}") as r:
            if r.status not in (200, 204, 404):
                print(f"  Warn: delete topic {topic['id']} → {r.status}")
    print("Очистка завершена.")


async def seed():
    async with aiohttp.ClientSession() as session:
        await cleanup(session)
        for ti, topic in enumerate(COURSE):
            print(f"\nТема {ti+1}: {topic['title']}")
            await post(session, f"{BASE}/topics", {
                "id": topic["id"], "title": topic["title"], "order": ti
            })

            for ii, item in enumerate(topic["items"]):
                await post(session, f"{BASE}/items", {
                    "id": item["id"],
                    "topicId": topic["id"],
                    "type": item["type"],
                    "title": item["title"],
                    "order": ii
                })
                print(f"  {item['type']}: {item['title']}")

                if item["type"] == "lesson":
                    for bi, block in enumerate(item.get("theoryBlocks", [])):
                        await post(session, f"{BASE}/theory-blocks", {
                            "itemId": item["id"],
                            "type": block["type"],
                            "content": block.get("content", ""),
                            "order": bi,
                            "src": block.get("src"),
                            "alt": block.get("alt")
                        })

                elif item["type"] == "task":
                    tt = item["taskType"]
                    base_payload = {
                        "itemId": item["id"],
                        "npcText": item.get("npcText", ""),
                        "rewardXp": item.get("rewardXp", 0)
                    }

                    if tt == "single-choice":
                        await post(session, f"{BASE}/tasks/single-choice", base_payload | {
                            "question": item["question"],
                            "answers": item["answers"],
                            "correctIndex": item["correctIndex"]
                        })

                    elif tt == "fill-in-blank":
                        await post(session, f"{BASE}/tasks/fill-in-blank", base_payload | {
                            "codeTemplate": item["codeTemplate"],
                            "blank": item["blank"]
                        })

                    elif tt == "find-the-bug":
                        await post(session, f"{BASE}/tasks/find-the-bug", base_payload | {
                            "bugLineIndex": item["bugLineIndex"],
                            "explanation": item.get("explanation", ""),
                            "codeLines": item["codeLines"]
                        })

                    elif tt == "code-order":
                        await post(session, f"{BASE}/tasks/code-order", base_payload | {
                            "description": item.get("description", ""),
                            "codeLines": item["codeLines"],
                            "correctOrder": item.get("correctOrder")
                        })

                    elif tt == "match-pairs":
                        pairs = [
                            {"left": p["left"], "right": p["right"], "order": pi}
                            for pi, p in enumerate(item["pairs"])
                        ]
                        await post(session, f"{BASE}/tasks/match-pairs", base_payload | {
                            "pairs": pairs
                        })

        print("\nГотово!")


asyncio.run(seed())
