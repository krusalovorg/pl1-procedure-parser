# <идентификатор>: PROCEDURE[(<список параметров>)][RETURNS(<атрибут>)];
# <список параметров> :: = <идентификатор> |<список параметров>,<идентификатор>
# <атрибут> :: = BIN   FIXED| FLOAT| CHARACTER ( <константа> ) 
# <идентификатор> - последовательность символов языка начинается с буквы, включает последовательность букв, цифр 
# <константа> - целое число без знака

# TEST: PROCEDURE(A, B) RETURNS(FLOAT);
# TEST: PROCEDURE RETURNS(BIN FIXED);
# TEST: PROCEDURE(A) RETURNS(CHARACTER(20));
# TEST: PROCEDURE(A, B);

PROGRAM_WORDS = [
    "PROCEDURE",
    "RETURNS",
    "FLOAT",
    "CHARACTER"
]

def skip_spaces(line: str, pos: int) -> int:
    while pos < len(line) and line[pos].isspace():
        pos += 1
    return pos

def expect(line: str, pos: int, char: str) -> int:
    pos = skip_spaces(line, pos)
    if pos >= len(line) or line[pos] != char:
        raise SyntaxError(
            f"Ожидался '{char}' на позиции {pos}"
        )

    return pos + 1

def parse_identifier(line: str, pos: int) -> tuple[str, int]:
    pos = skip_spaces(line, pos)
    start = pos
    if pos >= len(line) or not line[pos].isalpha():
        raise SyntaxError("Идентификатор должен начинаться с буквы")
    while pos < len(line) and line[pos].isalnum():
        pos += 1
    name = line[start:pos]
    if pos - (start + 1) > 7:
        raise ValueError("Семантическая ошибка: имя длиннее 8 символов")
    if name.upper() in PROGRAM_WORDS:
        raise ValueError("Семантическая ошибка: зарезервированное слово")
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
        raise SyntaxError(f"Ожидалось слово '{keyword}'")

    if end < len(line) and line[end].isalnum():
        raise SyntaxError(f"Некорректное ключевое слово на позиции {pos}")

    return end
TYPES = ["FLOAT"]

def parse_attribute(line: str, pos: int) -> tuple[str, int]:
    pos = skip_spaces(line, pos)

    for type_name in TYPES:
        if line[pos:pos + len(type_name)].upper() == type_name:
            pos = expect_keyword(line, pos, type_name)
            return type_name, pos

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
            raise SyntaxError(
                f"Ожидалась числовая константа на позиции {pos}"
            )
        number = int(line[start:pos])
        if not 1 <= number <= 256:
            raise ValueError(
                f"Семантическая ошибка: константа {number} вне диапазона 1–256"
            )
        pos = expect(line, pos, ")")
        return f"CHARACTER({number})", pos
    raise SyntaxError(f"Неизвестный тип на позиции {pos}")

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
        raise SyntaxError(f"Лишние символы на позиции {pos}")

    print("Имя:", name)
    print("Параметры:", arguments)
    print("Тип:", return_type)
    return {
        "name": name.upper(),
        "kind": "function" if return_type else "procedure",
        "type": return_type,
        "arguments": arguments
    }

def main(code: str):
    parse_line(code)
    print("\n")

if __name__ == "__main__":
    main("TEST: PROCEDURE(A, B) RETURNS(FLOAT);")
    # main("TEST PROCEDURE(A, B) RETURNS(FLOAT);")
    main("TEST: PROCEDURE RETURNS(BIN FIXED);")
    main("TEST: PROCEDURE(A) RETURNS(CHARACTER(20));")
    main("TEST: PROCEDURE(A, B);")
