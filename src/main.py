# <идентификатор>: PROCEDURE[(<список параметров>)][RETURNS(<атрибут>)];
# <список параметров> :: = <идентификатор> |<список параметров>,<идентификатор>
# <атрибут> :: = BIN   FIXED| FLOAT| CHARACTER ( <константа> ) 
# <идентификатор> - последовательность символов языка начинается с буквы, включает последовательность букв, цифр 
# <константа> - целое число без знака

# TEST: PROCEDURE(A, B) RETURNS(FLOAT);
# TEST: PROCEDURE RETURNS(BIN FIXED);
# TEST: PROCEDURE(A) RETURNS(CHARACTER(20));
# TEST: PROCEDURE(A, B);

from string import ascii_letters, digits

PROGRAM_WORDS = [
    "PROCEDURE",
    "RETURNS",
    "FLOAT",
    "CHARACTER"
]

class ParserError(Exception):
    def __init__(self, kind: str, pos: int, message: str):
        self.kind = kind
        self.pos = pos
        self.message = message
        super().__init__(message)

def skip_spaces(line: str, pos: int) -> int:
    while pos < len(line) and line[pos].isspace():
        pos += 1
    return pos

def expect(line: str, pos: int, char: str) -> int:
    pos = skip_spaces(line, pos)
    if pos >= len(line) or line[pos] != char:
        raise ParserError(
            "Синтаксическая",
            pos,
            f"Ожидался символ '{char}'"
        )

    return pos + 1

def parse_identifier(line: str, pos: int) -> tuple[str, int]:
    pos = skip_spaces(line, pos)
    start = pos
    if pos >= len(line) or line[pos] not in ascii_letters:
        raise ParserError("Синтаксическая", pos, "Идентификатор должен начинаться с латинской буквы")
    while pos < len(line) and line[pos] in ascii_letters + digits:
        pos += 1
    name = line[start:pos]
    if len(name) > 8:
        raise ParserError("Семантическая", start + 8, "Имя длиннее 8 символов")
    if name.upper() in PROGRAM_WORDS:
        raise ParserError("Семантическая", start, "Зарезервированное слово")
    return name, pos

def parse_arguments(line: str, pos: int) -> tuple[list[str], int]:
    arguments = []
    pos = expect(line, pos, "(")
    while True:
        name, pos = parse_identifier(line, pos)
        arguments.append(name)
        pos = skip_spaces(line, pos)
        if pos < len(line) and line[pos] == ",":
            pos +=1
            continue
        pos = expect(line, pos, ")")
        break
    return arguments, pos

def expect_keyword(line: str, pos: int, keyword: str) -> int:
    pos = skip_spaces(line, pos)
    end = pos + len(keyword)

    if line[pos:end].upper() != keyword.upper():
        raise ParserError("Синтаксическая", pos, f"Ожидалось слово '{keyword}'")

    if end < len(line) and line[end].isalnum():
        raise ParserError("Синтаксическая", pos, "Некорректное ключевое слово")

    return end

def parse_attribute(line: str, pos: int) -> tuple[str, int]:
    pos = skip_spaces(line, pos)

    if line[pos:pos + 5].upper() == "FLOAT":
        pos = expect_keyword(line, pos, "FLOAT")
        return "FLOAT", pos

    if line[pos:pos + 3].upper() == "BIN":
        pos = expect_keyword(line, pos, "BIN")
        pos = expect_keyword(line, pos, "FIXED")
        return "BIN FIXED", pos

    if line[pos:pos + 9].upper() == "CHARACTER":
        pos = expect_keyword(line, pos, "CHARACTER")
        pos = expect(line, pos, "(")
        pos = skip_spaces(line, pos)

        start = pos

        while pos < len(line) and line[pos] in "0123456789":
            pos += 1

        if start == pos:
            raise ParserError(
                "Синтаксическая",
                pos,
                "Ожидалась числовая константа"
            )
        number = int(line[start:pos])
        if not 1 <= number <= 256:
            raise ParserError(
                "Семантическая",
                start,
                f"константа вне диапазона 1–256"
            )
        pos = expect(line, pos, ")")
        return f"CHARACTER({number})", pos
    raise ParserError(
        "Синтаксическая",
        pos,
        "Неизвестный тип данных"
    )

def parse_line(line: str):
    pos = 0

    name, pos = parse_identifier(line, pos)

    pos = expect(line, pos, ":")
    pos = expect_keyword(line, pos, "PROCEDURE")
    pos = skip_spaces(line, pos)

    arguments = []
    if pos < len(line) and line[pos] == "(":
        arguments, pos = parse_arguments(line, pos)
    
    pos = skip_spaces(line, pos)

    return_type = None
    if line[pos:pos + 7].upper() == "RETURNS":
        pos = expect_keyword(line, pos, "RETURNS")
        pos = expect(line, pos, "(")
        return_type, pos = parse_attribute(line, pos)
        pos = expect(line, pos, ")")

    pos = expect(line, pos, ";")
    pos = skip_spaces(line, pos)

    if pos != len(line):
        raise ParserError("Синтаксическая", pos, "Лишние символы")

    return {
        "name": name.upper(),
        "kind": "function" if return_type else "procedure",
        "type": return_type,
        "arguments": [argument.upper() for argument in arguments]
    }

def register_declaration(declarations_by_name: dict, declaration: dict) -> None:
    name = declaration["name"]
    records = declarations_by_name.setdefault(name, [])
    if declaration not in records:
        records.append(declaration)


def print_identifiers(declarations_by_name: dict) -> None:
    procedures = set()
    functions = {}
    parameters = {}

    for records in declarations_by_name.values():
        for data in records:
            name = data["name"]
            if data["kind"] == "procedure":
                procedures.add(name)
            else:
                functions.setdefault(name, set()).add(data["type"])

            for index, argument in enumerate(data["arguments"], start=1):
                parameters.setdefault(argument, set()).add(f"{name} №{index}")

    print("\n========== ПРОЦЕДУРЫ ==========")
    for name in sorted(procedures):
        print(f"  {name}")
    if not procedures:
        print("  —")

    print("\n========== ФУНКЦИИ ==========")
    for name, types in sorted(functions.items()):
        print(f"  {name:<12} | {', '.join(sorted(types))}")
    if not functions:
        print("  —")

    print("\n========== ПАРАМЕТРЫ ==========")
    for name, locations in sorted(parameters.items()):
        print(f"  {name:<12} | {', '.join(sorted(locations))}")
    if not parameters:
        print("  —")


def process_line(code: str, declarations_by_name: dict) -> bool:
    try:
        result = parse_line(code)
    except ParserError as error:
        print(code)
        print(" " * error.pos + "^")
        print(f"{error.kind} ошибка: {error.message}")
        return False

    register_declaration(declarations_by_name, result)
    print("Строка принадлежит языку.")
    return True


def main() -> None:
    declarations_by_name: dict[str, list[dict]] = {}

    print("Анализатор заголовков PL/1")
    print("Введите заголовок или 'exit' для завершения.\n")

    while True:
        try:
            code = input("PL/1> ")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            break

        if code.strip().lower() in {"exit", "quit", "выход"}:
            print("Работа завершена.")
            break
        if not code.strip():
            continue

        if not process_line(code, declarations_by_name):
            print()
            continue

        try:
            while True:
                answer = input("Показать накопленные списки? (y/n): ").strip().lower()
                if answer in {"y", "n"}:
                    break
                print("Пожалуйста, введите y или n.")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            break

        if answer == "y":
            print_identifiers(declarations_by_name)
        print()


if __name__ == "__main__":
    main()
