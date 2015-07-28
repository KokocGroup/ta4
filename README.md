ta4 ![build-status](https://travis-ci.org/KokocGroup/text-analyze4.svg)
===========

Пакет позволяет находит вхождения слов в текст в нужных словоформах.

# Установка
```
pip install ta4
```

# Development

Для пробной установки пакета выполнить
```
python -c "import setuptools; execfile('setup.py')" develop
```

Для тестов используется py.test, соответственно для запуска тестов, выполняем:
```
py.test
```


# Публикация изменений

Если вы хотите выкатить изменения в PyPI, то вы можите воспользоваться fab-командами, в зависимости от семантики ваших изменений:
```
fab [major|minor|patch]
```
