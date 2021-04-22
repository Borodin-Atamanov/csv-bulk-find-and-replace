Bulk find and replace in CSV files

© Copyright 2021 Slava Borodin-Atamanov

The program reads all cells from the "input.csv", searches for a line from the first column from the "findreplace.csv", replaces it with a string from the second column of the "findreplace.csv" file.

Run the program
`python csv-bulk-find-and-replace.py`

The input.csv and findreplace.csv examples will be created

Put your source text to input.csv

Save the "what-to-find", "what to replace" pairs to the "findreplace.csv"
In the first column - what-to-find, in the second column what-to-replace.

The program will create a configuration in the config.ini file in the "output-csv-bulk-find-and-replace" directory


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
