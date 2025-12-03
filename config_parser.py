#!/usr/bin/env python3
import sys


class ConfigParser:
    def __init__(self):
        self.constants = {}
        self.pos = 0
        self.line = 1
        self.input = ""
        self.result = []

    def parse(self, text):
        self.input = text
        self.pos = 0
        self.result = ['<?xml version="1.0"?>', '<config>']

        while self.pos < len(self.input):
            self.skip_whitespace()
            if self.pos >= len(self.input):
                break

            if self.peek(3) == 'var':
                self.parse_constant()
            elif self.current() == '{':
                self.parse_dict()
            else:
                self.error(f"Неожиданный символ '{self.current()}'")

        self.result.append('</config>')
        return '\n'.join(self.result)

    def parse_constant(self):
        self.consume('var')
        self.skip_whitespace()
        name = self.parse_name()
        self.skip_whitespace()
        value = self.parse_value()
        self.skip_whitespace()
        self.consume(';')
        self.constants[name] = value

    def parse_dict(self):
        self.consume('{')
        self.result.append('  <dictionary>')
        self.skip_whitespace()

        while self.pos < len(self.input) and self.current() != '}':
            name = self.parse_name()
            self.skip_whitespace()
            self.consume('->')
            self.skip_whitespace()
            value = self.parse_value()
            self.skip_whitespace()

            # Точка - это разделитель пар, а не часть числа
            if self.current() == '.':
                self.consume('.')
                self.skip_whitespace()
            else:
                self.error(f"Ожидается '.', получено '{self.current()}'")

            self.result.append(f'    <pair>')
            self.result.append(f'      <name>{name}</name>')
            self.result.append(f'      <value>{self.value_to_xml(value)}</value>')
            self.result.append(f'    </pair>')

        self.consume('}')
        self.result.append('  </dictionary>')

    def parse_value(self):
        if self.current() == '{':
            return self.parse_dict_value()
        elif self.current() == '?':
            return self.parse_eval()
        else:
            return self.parse_number()

    def parse_dict_value(self):
        self.consume('{')
        result = {}
        self.skip_whitespace()

        while self.pos < len(self.input) and self.current() != '}':
            key = self.parse_name()
            self.skip_whitespace()
            self.consume('->')
            self.skip_whitespace()
            value = self.parse_value()
            self.skip_whitespace()

            if self.current() == '.':
                self.consume('.')
                self.skip_whitespace()
            else:
                self.error(f"Ожидается '.', получено '{self.current()}'")

            result[key] = value

        self.consume('}')
        return result

    def parse_eval(self):
        self.consume('?')
        self.consume('[')
        name = self.parse_name()
        self.consume(']')

        if name not in self.constants:
            self.error(f"Неизвестная константа '{name}'")

        return self.constants[name]

    def parse_number(self):
        start = self.pos
        has_dot = False

        # Читаем первую цифру
        if not self.current().isdigit():
            self.error(f"Ожидается число, получено '{self.current()}'")

        while self.pos < len(self.input):
            c = self.current()
            if c.isdigit():
                self.advance()
            elif c == '.':
                # Проверяем следующий символ
                next_pos = self.pos + 1
                if next_pos < len(self.input) and self.input[next_pos].isdigit():
                    # Это десятичная точка в числе
                    has_dot = True
                    self.advance()
                else:
                    # Это конец числа, точка как разделитель
                    break
            else:
                break

        num_str = self.input[start:self.pos]
        try:
            if has_dot:
                return float(num_str)
            return int(num_str)
        except ValueError:
            self.error(f"Неверное число: {num_str}")

    def parse_name(self):
        start = self.pos
        if not self.current().isalpha():
            self.error("Имя должно начинаться с буквы")

        self.advance()
        while self.pos < len(self.input):
            c = self.current()
            if c.isalnum() or c == '_':
                self.advance()
            else:
                break

        return self.input[start:self.pos]

    def value_to_xml(self, value):
        if isinstance(value, dict):
            return f'<dictionary>...</dictionary>'
        elif isinstance(value, float):
            return f'<value type="float">{value}</value>'
        else:
            return f'<value type="int">{value}</value>'

    def current(self):
        if self.pos < len(self.input):
            return self.input[self.pos]
        return ''

    def peek(self, n):
        if self.pos + n <= len(self.input):
            return self.input[self.pos:self.pos + n]
        return ''

    def advance(self):
        if self.current() == '\n':
            self.line += 1
        self.pos += 1

    def skip_whitespace(self):
        while self.pos < len(self.input) and self.input[self.pos].isspace():
            self.advance()

    def consume(self, expected):
        for char in expected:
            if self.pos >= len(self.input) or self.input[self.pos] != char:
                self.error(
                    f"Ожидается '{expected}', получено '{self.current() if self.pos < len(self.input) else 'EOF'}'")
            self.advance()

    def error(self, msg):
        sys.stderr.write(f"Ошибка в строке {self.line}: {msg}\n")
        sys.exit(1)


def main():
    text = sys.stdin.read()
    parser = ConfigParser()
    xml = parser.parse(text)
    sys.stdout.write(xml)


if __name__ == "__main__":
    main()