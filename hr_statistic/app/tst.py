# Globalna lista rečnika
globalna_lista = []

# Funkcija za dodavanje rečnika sa ključem "A" u listu
def a():
    global globalna_lista
    for item in globalna_lista:
        if "A" in item:
            item.pop("A")
            return
    globalna_lista.append({"A": [1, 2, 3]})

# Funkcija za dodavanje rečnika sa ključem "B" u listu
def b():
    global globalna_lista
    for item in globalna_lista:
        if "B" in item:
            item.pop("B")
            return
    globalna_lista.append({"B": [1, 2, 3]})

# Funkcija za proveru da li postoje ključevi "A" i "B" u rečnicima u listi
def c():
    global globalna_lista
    has_A = any("A" in item for item in globalna_lista)
    has_B = any("B" in item for item in globalna_lista)

    if has_A and has_B:
        print("Lista sadrži i ključ 'A' i ključ 'B'.")
    elif has_A:
        print("Lista sadrži samo ključ 'A'.")
    elif has_B:
        print("Lista sadrži samo ključ 'B'.")
    else:
        print("Lista ne sadrži ni ključ 'A' ni ključ 'B'.")

# Testiranje funkcija
a()
a()
b()
c()
# import pandas as pd

# def format_str(data):
#     element_list = []

#     for sublist in data:
#         text = """
# | Rukovodilac | Broj ponavljanja |
# | ----------- | ----------- |
# """
#         for key, value in sublist.items():
#             text += f"| {key} | {value} |\n"
        
#         element_list.append(text)
    
#     return element_list

# data = [
#     {'Mara': 2, 'Lepša': 1, 'Ana': 1},
#     {'Voja': 4, 'Gogi': 1},
#     {'Mara': 7, 'Lepša': 2, 'Ana': 4, 'Voja': 11, 'Gogi': 6}, 
#     {'Mara': 2}
# ]

# dt = format_str(data)
# l = []
# for table in dt:
#     text_format = {
#         'Razlog': {'value': f"{table}", 'type': 'markdown'}
#     }
#     l.append(text_format)

# print(l)


# def format_str(data):

#     element_list = []

#     markdown_table = ""
#     text_format = ""

#     for list_len in range(len(data)):

#         markdown_table += f"""
# | Rukovodilac | Broj ponavljanja |
# | ----------- | ----------- |
# """

#         for key, value in data[list_len].items():

#             markdown_table += f"| {key}   | {value} |"
#             markdown_table += "\n"
#         # print(markdown_table)
#         text_format = {
#                 'Razlog': {'value': f"{markdown_table}", 'type': 'markdown'}
#             }

#         element_list.append(text_format)
        
#     return element_list

# # markdown_table = format_str(data)
# # print(markdown_table)