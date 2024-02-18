## Подготовка
1. Необходимо создать индекс в [Amazon CloudSearch](https://docs.aws.amazon.com/cloudsearch/), файлы конфигурации находятся в директории `/cloudsearch`.
2. Так как CloudSearch не поддерживает настройки CORS, то ещё нужно создать [API Gateway](https://docs.aws.amazon.com/apigateway/) с `Access-Control-Allow-Origin: *`.
3. Установите пакеты, необходимые для работы [textract](https://textract.readthedocs.io/en/stable/installation.html), он используется для конвертации документов в текст.
4. Установите зависимости Python: `pip install -r requirements.txt`

## Запуск
Загрузка данных (при необходимости замените `v150` в ссылке на последнюю версию):
```
python3 sources/mosgorsud/main.py
```

Обновление индекса (замените `<id>` на реальное значение):
```
python3 sources/mosgorsud/export.py
find data/mosgorsud/export -name "*.json" -type f -exec aws cloudsearchdomain upload-documents --endpoint-url https://doc-court-cases-<id>.us-east-1.cloudsearch.amazonaws.com --content-type application/json --documents {} \;
rm data/mosgorsud/export/*.json
```

## Поиск
Форма для поиска обращается напрямую к индексу.
В текущий момент она доступна по адресу https://court.putnik.tech/.