# Weather_vizualization

# Приложение для прогноза погоды на маршруте

Это веб-приложение на Python, созданное с использованием Dash, которое предоставляет прогноз погоды для заданного маршрута, включая промежуточные точки. Приложение интегрируется с OpenWeatherMap API для получения данных о погоде.

## Возможности

- **Прогноз погоды по маршруту**: Получите прогноз для начальной, конечной и промежуточных точек маршрута.
- **Интерактивная карта**: Визуализация маршрута на карте с отображением погодной информации для каждого пункта.
- **Настраиваемые параметры**: Выбор параметров прогноза, таких как температура, скорость ветра и осадки.
- **Выбор временного интервала**: Прогноз на 1, 3 или 5 дней.
- **Динамический ввод**: Возможность добавления промежуточных точек маршрута.

## Установка

### Требования

- Python 3.7 или выше
- Установленный пакетный менеджер pip

### Шаги установки

1. Клонируйте репозиторий или скачайте исходный код.
2. Установите зависимости:
   ```bash
   pip install -r requarement.txt 
    ```

Получите API-ключ OpenWeatherMap:
1. Зарегистрируйтесь на OpenWeatherMap.
2. Скопируйте ваш API-ключ и замените значение переменной API_KEY в коде приложения.
3. Запустите приложение.

Использование:
1. Откройте браузер и перейдите по адресу http://127.0.0.1:8050/.
2. Введите начальную и конечную точки маршрута.
3. При необходимости добавьте промежуточные точки маршрута.
4. Выберите параметры прогноза и временной интервал.
5. Нажмите "Получить прогноз", чтобы увидеть карту и графики прогноза.

Основные компоненты:

- Ввод маршрута:
  - Поля для начальной и конечной точек.
  - Возможность добавления промежуточных точек.

- Параметры прогноза:
  - Температура, скорость ветра, осадки.
  - Прогноз на 1, 3 или 5 дней.

- Карта и графики:
  - Карта маршрута с отображением погодных данных.
  - Графики изменения выбранных параметров по времени для каждого пункта маршрута.

Пример использования:
1. Введите "Москва" как начальную точку и "Санкт-Петербург" как конечную.
2. Добавьте промежуточную точку, например "Новгород".
3. Выберите параметры: температура и осадки.
4. Выберите интервал: 3 дня.
5. Нажмите "Получить прогноз", чтобы увидеть маршрут на карте и графики прогноза.

