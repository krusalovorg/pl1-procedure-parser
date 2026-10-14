from main import process_line, print_identifiers
import sys

valid_lines = [
    "ABCD10: PROCEDURE;",
    "ABCD20: PROCEDURE(A);",
    "PRIMER: PROCEDURE(A, B, CD, DEF);",
    "PRIMER1: PROCEDURE(A, B) RETURNS(FLOAT);",
    "PRIMER2: PROCEDURE RETURNS(BIN FIXED);",
    "PRIMER3: PROCEDURE(A, B) RETURNS(CHARACTER(20));",
    "TEST:PROCEDURE(A,B)RETURNS(FLOAT);",
    "test: procedure(a, b) returns(float);",
    "TEST   :   PROCEDURE   ( A , B )   ;",
    "A: PROCEDURE RETURNS(CHARACTER(1));",
    "A: PROCEDURE RETURNS(CHARACTER(256));",
    "ABCD1234: PROCEDURE;",
    "SUM: PROCEDURE(A, B, A);",
    "TEST: PROCEDURE(A, B);",
    "TEST: PROCEDURE RETURNS(BIN FIXED);",
    "TEST: PROCEDURE(A, B);",
]

# синтаксис
invalid_syntax = [
    "TEST PROCEDURE(A, B);",                  # Нет двоеточия
    "TEST: PROCEDURE(A, B)",                  # Нет ;
    "TEST: PROCEDUR(A);",                    # Опечатка в ключевом слове
    "TEST: PROCEDUREABC;",                   # Лишние буквы
    "TEST: PROCEDURE();",                    # Пустой список
    "TEST: PROCEDURE(A,);",                  # Лишняя запятая
    "TEST: PROCEDURE(,A);",                  # Нет первого параметра
    "TEST: PROCEDURE(A B);",                 # Нет запятой
    "TEST: PROCEDURE(A, B;",                 # Нет )
    "TEST: PROCEDURE(A, B));",               # Лишняя )
    "TEST: PROCEDURE RETURNS(FLOAT;",        # Нет ) у RETURNS
    "TEST: PROCEDURE RETURNS(INT);",         # Несуществующий тип
    "TEST: PROCEDURE RETURNS(CHARACTER);",   # Нет числовой константы
    "TEST: PROCEDURE RETURNS(BIN);",         # Нет FIXED
    "TEST: PROCEDURE RETURNS(CHARACTER());", # Пустая константа
    "TEST: PROCEDURE RETURNS(CHARACTER(-5));",
    "TEST: PROCEDURE RETURNS(CHARACTER(2.5));",
    "TEST: PROCEDURE; ABC",                  # Лишний текст после ;
    "TEST: PROCEDURE; ABC: PROCEDURE;",      # Два заголовка подряд
    "TEST: PROCEDURE(A_B);",                 # Недопустимый символ
    "123TEST: PROCEDURE;",                   # Имя начинается с цифры
    "ТЕСТ: PROCEDURE;",                      # Кириллица
    "TEST: PROCEDURE(AБ);",                  # Кириллица внутри имени
    "TEST: PROCEDURE(A) RETURNS(FLOAT) RETURNS(FLOAT);",
    "TEST: PROCEDURE RETURNS(CHARACTER(20);",
]

# семантика
invalid_semantic = [
    "ABCDEFGHI: PROCEDURE;",                 # Имя длиннее 8 символов
    "TEST: PROCEDURE(ABCDEFGHI);",
    "FLOAT: PROCEDURE;",                     # Зарезервированное слово
    "TEST: PROCEDURE(RETURNS);",
    "TEST: PROCEDURE RETURNS(CHARACTER(0));",
    "TEST: PROCEDURE RETURNS(CHARACTER(257));",
    "TEST: PROCEDURE RETURNS(CHARACTER(999));",
]


def run_cases(title: str, lines: list[str], expected: bool, registry: dict) -> tuple[int, int]:
    print(f"\n{'=' * 18} {title} {'=' * 18}")
    passed = 0

    for number, line in enumerate(lines, start=1):
        print(f"\n{number:02}. {line}")
        actual = process_line(line, registry)
        success = actual == expected
        print("[OK] Ожидаемый результат" if success else "[FAIL] Неожиданный результат")
        passed += success

    return passed, len(lines)


if __name__ == "__main__":
    declarations_by_name = {}

    results = [
        run_cases("ПРАВИЛЬНЫЕ", valid_lines, True, declarations_by_name),
        run_cases("СИНТАКСИЧЕСКИЕ ОШИБКИ", invalid_syntax, False, declarations_by_name),
        run_cases("СЕМАНТИЧЕСКИЕ ОШИБКИ", invalid_semantic, False, declarations_by_name),
    ]

    passed = sum(count for count, _ in results)
    total = sum(count for _, count in results)
    print(f"\nИТОГО: {passed}/{total} проверок прошли")

    print_identifiers(declarations_by_name)
    if passed != total:
        sys.exit(1)