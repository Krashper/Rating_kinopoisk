# Название проекта

Модель предсказания рейтинга фильмов (Kinopoisk API)

## Описание

В данном проекте была реализована модель регрессии для предсказания рейтинга фильмов. 
Лучший показатель, замеченный во время обучения модели (RMSE=0.60). Данные были получены через Kinopoisk API. 
В качестве модели был выбран Random Forest Regressor с подобранными параметрами.
*Проведена иммитация реального потокового получения данных с сайта

## Список используемых технологий

1. Airflow - автоматизация рабочих процессов, планирование и мониторинг
2. MiniO - облачное хранение моделей
3. Scikit-learn - создание и обучение модели регрессии
4. Pandas, numpy, json - обработка данных
5. Docker - контейнеризация проекта

## Задачи в DAGs

### DAG 1: Сreate_movie_dataset

DAG используется для получения данных с API, первичной обработки и сохранения в базу данных (ETL процесс).
#### Задачи:

1. **Task 1: Start_dag**
   - Проверка на возможность получения новых данных с API (в бесплатной версии есть ограничения)

2. **Task 2: Get_json**
   - Получение json файла с информацией о фильмах

3. **Task 3: Get_data_from_json**
   - Получение нужных данных из json файла

4. **Task 4: Create_movies_table**
   - Создание таблицы в базе данных (если она не была создана)

5. **Task 5: Insert_data_to_db**
   - Сохранение данных о фильмах в базе данных

### DAG 2: Model_training

DAG используется для обучения и тестирования модели машинного обучения.

#### Задачи:

1. **Task 1: Create_bucket**
   - Создание S3-bucket в MiniO (если он не был создан)

2. **Task 2: Get_data**
   - Получение данных о фильмах с базы данных

3. **Task 3: Preprocess_data**
   - Предобработка данных (преобразование признаков, нормализация, сжатие признаков, обработка пропущенных значений)

4. **Task 4: Train_model**
   - Обучение модели Random Forest Regressor c подбором параметров через GridSearch, тестирование модели

## Способ запуска через Docker

### Требования

Перед запуском проекта убедитесь, что у вас установлены следующие компоненты:

- Docker
- Docker Compose

### Инструкции по запуску

1. **Клонирование репозитория:**

   ```bash
   git clone https://github.com/your/repository.git
   cd repository
   
2. **Настройка окружения:**

   Создайте файл .env и заполните переменные на основе .env.example

3. **Запуск контейнера**

   ```bash
   docker-compose up -d

4. **Остановка контейнера**

   ```bash
   docker-compose down
