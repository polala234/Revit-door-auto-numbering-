# Revit Door Auto Numbering (pyRevit)

Skrypt do automatycznego numerowania drzwi w Autodesk Revit na podstawie parametru `Door To`.

## Opis

Skrypt pobiera wszystkie drzwi w modelu, grupuje je według wartości parametru docelowego pomieszczenia i nadaje im nowe numery w formacie:
`[Room To].[Litera]` (np. 101.A, 101.B).

Dodatkowo zapisuje log zmian do pliku CSV (stary numer, nowy numer, ID drzwi, wartość Room To).

## Technologie

* Python (pyRevit)
* Revit API

## Działanie

1. Pobranie wszystkich drzwi w modelu
2. Grupowanie po parametrze `Door To`
3. Generowanie sekwencji liter (A, B, C, …, AA, AB…)
4. Nadanie nowego numeru drzwi
5. Eksport logu zmian do CSV

## Zastosowanie

Automatyzacja numeracji drzwi w projektach BIM oraz ograniczenie błędów wynikających z ręcznego nadawania numerów.
