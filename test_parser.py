#!/usr/bin/env python3
import subprocess
import tempfile
import os


def run_test(name, input_text, expected_contains=None, should_fail=False):
    """Запускает тест"""
    try:
        result = subprocess.run(
            ['python3', 'config_parser.py'],
            input=input_text,
            text=True,
            capture_output=True
        )

        if should_fail:
            if result.returncode == 0:
                print(f"{name}: должен был завершиться ошибкой, но завершился успешно")
                return False
            else:
                print(f"{name}: корректно завершился с ошибкой")
                return True
        else:
            if result.returncode != 0:
                print(f"{name}: завершился с ошибкой")
                print(f"   Ошибка: {result.stderr.strip()}")
                return False

            if expected_contains:
                if expected_contains not in result.stdout:
                    print(f"{name}: не найден '{expected_contains}' в выводе")
                    return False

            print(f"{name}: пройден")
            return True
    except Exception as e:
        print(f"{name}: исключение: {e}")
        return False


def test_all():
    print("Запуск тестов...\n")
    passed = 0
    total = 0

    # Тест 1: Простой словарь с числами
    total += 1
    input1 = """{
  port -> 8080.
  active -> 1.
}"""
    if run_test("Тест 1: Простой словарь", input1, "<name>port</name>"):
        passed += 1

    # Тест 2: Константы
    total += 1
    input2 = """var port 8080;
{
  server_port -> ?[port].
  count -> 5.
}"""
    if run_test("Тест 2: Константы", input2, "<value>8080</value>"):
        passed += 1

    # Тест 3: Вложенные словари
    total += 1
    input3 = """{
  database -> {
    port -> 5432.
    timeout -> 30.
  }.
}"""
    if run_test("Тест 3: Вложенные словари", input3, "<dictionary>"):
        passed += 1

    # Тест 4: Числа с точкой
    total += 1
    input4 = """{
  pi -> 3.14.
  score -> 95.5.
}"""
    if run_test("Тест 4: Числа с точкой", input4, "type=\"float\""):
        passed += 1

    # Тест 5: Целые числа
    # Тест 5: Целые числа
    total += 1
    input5 = """{
  x -> 100.
  y -> 200.
}"""
    # Ищем сами значения чисел без атрибута type="int"
    if run_test("Тест 5: Целые числа", input5, "<value>100</value>"):
        passed += 1

    # Тест 6: Синтаксическая ошибка
    total += 1
    input6 = """{
  name -> 100
  port -> 8080.
}"""
    if run_test("Тест 6: Синтаксическая ошибка", input6, should_fail=True):
        passed += 1

    # Тест 7: Неизвестная константа
    total += 1
    input7 = """{
  value -> ?[unknown].
}"""
    if run_test("Тест 7: Неизвестная константа", input7, should_fail=True):
        passed += 1

    # Тест 8: Множественные словари и константы
    total += 1
    input8 = """var timeout 30;
var retries 3;

{
  server -> {
    timeout -> ?[timeout].
    port -> 8080.
  }.
}
{
  client -> {
    retries -> ?[retries].
  }.
}"""
    if run_test("Тест 8: Множественные словари", input8, "<name>client</name>"):
        passed += 1

    # Тест 9: Сложный вложенный словарь
    total += 1
    input9 = """{
  config -> {
    a -> 1.
    b -> {
      c -> 2.5.
      d -> {
        e -> 3.
      }.
    }.
  }.
}"""
    if run_test("Тест 9: Сложный вложенный словарь", input9, "2.5"):
        passed += 1

    # Тест 10: Константа как словарь
    total += 1
    input10 = """var db_config {
  host -> "localhost".
  port -> 5432.
};
{
  database -> ?[db_config].
  app -> {
    name -> "test".
  }.
}"""
    if run_test("Тест 10: Константа-словарь", input10, should_fail=True):  # У нас нет строк
        passed += 1

    print(f"\nРезультат: {passed}/{total} тестов пройдено")

    # Быстрые примеры для проверки
    print("\n--- Быстрая проверка вручную ---")

    print("\nПример:")
    print('echo \'var max 100; { value -> ?[max]. }\' | python3 config_parser.py')


if __name__ == "__main__":
    test_all()