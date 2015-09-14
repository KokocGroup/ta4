ta4 [![Travis](https://travis-ci.org/KokocGroup/ta4.svg?branch=master)](https://travis-ci.org/KokocGroup/ta4) [![Coverage Status](https://coveralls.io/repos/KokocGroup/ta4/badge.svg?branch=master&service=github)](https://coveralls.io/github/KokocGroup/ta4?branch=master)
===========

Пакет позволяет находит вхождения слов в текст в нужных словоформах.

# Установка
```
pip install ta4
```

# Development

Для пробной установки пакета выполнить
```
pip install -e .
```

Для тестов используется py.test, соответственно для запуска тестов, выполняем(предварительно делаем установку, см. предыдущий пункт:
```
py.test
```


# Публикация изменений

Если вы хотите выкатить изменения в PyPI, то вы можите воспользоваться fab-командами, в зависимости от семантики ваших изменений:
```
fab [major|minor|patch]
```
