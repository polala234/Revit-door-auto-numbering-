from pyrevit import revit, DB, script, forms
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
from System import String
from datetime import datetime
import sys
from collections import defaultdict
import string
import csv
import os

doc = revit.doc

# Definicja nazw parametrow
PARAM_DOOR_NUM_NEW = "MED_Door Number"
PARAM_ROOM_TO = "MED_Door To"

# Wewnetrzna lista do zbierania danych do eksportu
export_data = []

# Naglowki dla pliku CSV
CSV_HEADERS = ["Door ID", "Room To Value", "Old Door Number", "New Door Number"]

# Funkcja pomocnicza do generowania sekwencji alfabetycznej (A, B, C, ..., AA, AB, ...)
def get_alphabet_sequence(count):
    letters = []
    for i in range(1, count + 1):
        s = ''
        n = i
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            s = string.ascii_uppercase[remainder] + s
        letters.append(s)
    return letters

## 1. Pobranie i Grupowanie Elementow Drzwi
collector = FilteredElementCollector(doc)
doors = collector.OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

if not doors:
    forms.alert('Nie znaleziono elementow Drzwi do przetworzenia.', title='Przetwarzanie Drzwi')
    sys.exit()

# Grupowanie drzwi po wartosci parametru 'MED_Door To'
door_groups = defaultdict(list)
for door in doors:
    try:
        room_to_param = door.LookupParameter(PARAM_ROOM_TO)
        # Uzyj ID elementu jako klucza, jesli parametr docelowy jest pusty
        room_to_value = room_to_param.AsString() if room_to_param and room_to_param.AsString() else "BRAK_POKOJU"

        if room_to_param is None:
            # Jesli parametr docelowy w ogole nie istnieje, pomin element
            continue

        door_groups[room_to_value].append(door)

    except Exception as e:
        script.get_output().print_html('Blad odczytu parametru **{}** dla elementu ID: {}: {}'.format(PARAM_ROOM_TO, door.Id, e))


## 2. Numerowanie Drzwi i Zbieranie Danych Logu
with forms.revit.Transaction('Nadanie numerow drzwi'):

    for room_key, group_of_doors in door_groups.items():

        group_count = len(group_of_doors)
        alphabet_seq = get_alphabet_sequence(group_count)

        for i, door in enumerate(group_of_doors):

            # Nowy numer drzwi: [Room To Value].[Letter]
            new_door_number = "{}.{}".format(room_key, alphabet_seq[i])

            # --- Zbieranie starego numeru ---
            old_door_num_param = door.LookupParameter(PARAM_DOOR_NUM_NEW)
            old_door_number = old_door_num_param.AsString() if old_door_num_param and old_door_num_param.AsString() else "BRAK_STAREGO_NUMERU"

            # --- Zapis nowego numeru do Revita ---
            try:
                param_new = door.LookupParameter(PARAM_DOOR_NUM_NEW)
                if param_new:
                    param_new.Set(new_door_number)
                else:
                    script.get_output().print_html('Brak parametru docelowego **{}** dla elementu ID: {}'.format(PARAM_DOOR_NUM_NEW, door.Id))
            except Exception as e:
                script.get_output().print_html('Blad ustawienia parametru **{}** dla elementu ID: {}: {}'.format(PARAM_DOOR_NUM_NEW, door.Id, e))

            # --- Zbieranie danych do eksportu ---
            export_data.append({
                "Door ID": door.Id.ToString(), # Konwersja ID na string
                "Room To Value": room_key,
                "Old Door Number": old_door_number,
                "New Door Number": new_door_number
            })

## 3. Eksport danych do pliku CSV

if export_data:

    # Generowanie domyslnej nazwy pliku z data/czasem
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = 'Door_Number_Change_Log_{}.csv'.format(now_str)

    # Otwarcie okna dialogowego zapisu
    output_file = forms.save_file(
        title='Zapisz Log Zmian Numeracji Drzwi',
        default_name=default_filename,
        file_ext='csv'
    )

    if output_file:
        try:
            with open(output_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS, delimiter=';')
                writer.writeheader()
                writer.writerows(export_data)

            forms.alert('Eksport logu zmian zakonczony pomyslnie!', title='Eksport Gotowy')

        except Exception as e:
            forms.alert('Blad podczas eksportu danych do pliku CSV: {}'.format(e), title='Blad Eksportu')

    else:
        forms.alert('Anulowano zapis pliku CSV.', title='Anulowano')