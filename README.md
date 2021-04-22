Bulk find and replace in CSV files

© Copyright 2021 Slava Borodin-Atamanov

Программа читает все ячейки из файла input.csv, ищет строку из первой колонки файла findreplace.csv, заменяет на строку из второй колонки файла findreplace.csv

Запустите программу
python csv-bulk-find-and-replace.py

Создадутся примеры input.csv и findreplace.csv

Поместите исходный текст в input.csv

Сохраните пары "что-найти", "на что заменить" в файл findreplace.csv
В первой колонке - что нужно найти, во второй колонке - на что заменить.

Программа создаст конфигурацию в файле config.ini в директории output-csv-bulk-find-and-replace



Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
