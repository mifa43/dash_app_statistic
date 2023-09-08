import pandas as pd
from pathlib import Path
import os
class LocateAndLoadData:
    """### Klasa koja ce da locira svaku excel datoteku iz zadatog direktorijuma i kreira objekat DataFrame
        :param|protected_all
        - `self.__path_to_data: str` -> putanja do direktorijuma sa podatcima
        - `self.__located_data: list` -> lista ge se smesta locirana .xlsx datoteka
        - `self.pandas_dataframe: list` -> ucitavamo pronadjene datoteke | pubilc
    """

    def __init__(self) -> None:
        
        self.__path_to_data: str = "./hr_statistic/app"

        self.__located_data: list = []

        option: str = None

        self.df = None

        # self.pandas_dataframe: list = []

    def locate_data(self):
        """### Pronalazimo sve datoteke sa *.xlsx u datom direktorijumu"""

        cwd = os.getcwd()  
        print("TRENUTNI FOLDER")

        folder = Path(self.__path_to_data)

        if folder.exists() and folder.is_dir():

            is_file_excel = folder.glob("*.xlsx")
            
            for file in is_file_excel:

                self.__located_data.append(file)

    def load_data(self, option: str = None):
        """### Ucitavanje datoteka i vracanje DataFrame objekta
            :param
            - `option: str = None` -> Prima kao parametar kom ili telem
        """

        # Prolazimo kroz alociranu datoteke
        for data in self.__located_data:

            # Ako je opcija = Komercijala otvaramo datoteku za kom, moze da bude i Telemarketing
            if (option is None or option.lower() in str(data).lower()) and data.exists():
                
                print(f"Opening the file: {data}")
                
                self.df = pd.read_excel(data, 1)
                if self.df is None:

                    raise TypeError("NEMA DF JER JE NONE")
                else:
                
                    return self.df
        
        print("File not found or an unexpected error occurred!")
class CleanData(LocateAndLoadData):
    """### Ciscenje podataka iz tabela ako je citava kolona NaN brisi prazna polja
    :param
        - `self.clean_data: list` -> lista ociscenih pandas DataFrame
    """

    def __init__(self) -> None:

        super().__init__()

    def clean(self):
        """### Metoda koja radi iteraciju kroz alocirane excel datoteke  i izbacuje prazna polja"""
        # Prljavi podatci i varijacije
        name_variant = {"Lepša": ["Lepša", "lepša ", " lepša", "lePŠA", "Lepša  ", "lepša  "],
                        "Lepša ZTP": ["lepša ZTP", "Lepša ztp "],
                        "Nemanja": ["Nemanja ", "nemanja", "nemanja ", "Nemanja "],
                        "Nemanja Božinovski": ["Nemanja B", "Nemanja B ", "Nemanja B.", "nemanja b", "nemanja B"],
                        "Goran": ["Goran ", "goran"],
                        "Mara": ["MARA", "mara"],
                        "Ana": ["ANA", "ana"],
                        "Sale": ["Sale", "sale"],
                        "Milica": ["MIlica", "MILICA", "milica"],
                        "Tijana Ž.": ["Tijana", "tijana"],
                        "Peđa": ["peđa", "Peđa"]
                        }

        # Izvlacimo imena rukovodilaca
        get_keys = list(name_variant.keys())
            
        # Kolika je duzina liste sa imenima rukovodilaca
        for key in range(len(get_keys)):

            # Prolazimo kroz sve ne ispravne varijacije u name_variant
            for name in name_variant[get_keys[key]]:
                
                # Konvertujemo ime rukovodilca u text i izbacujemo razmake i sve varijacije stavljamo u mala slova i dodajemo vrednost keya
                self.df.loc[self.df["Rukovodilac"].str.strip().str.lower() == name.lower(), "Rukovodilac"] = get_keys[key]

        self.df.loc[:, "Datum zakazivanja"] = pd.to_datetime(self.df["Datum zakazivanja"], format="%d %B, %Y")
        
        self.df["Datum obuke"] = pd.to_datetime(self.df["Datum obuke"], format="%d %B, %Y")

        self.df = self.df.dropna(thresh=4)  

        return self.df

class Analytic(CleanData):

    def __init__(self) -> None:

        super().__init__()

    def filter_by_date(self, rukovodilac: str, start_date: str, end_date: str):
        """### Pretrazuje po zadatom kriterijumu i vraca dataframe
        :param
        - `rukovodilac: str` -> Ime rukovodilca 
        - `start_date: str` -> Datum od: pocetak range-a
        - `end_date: str` -> Datum do: kraj range-a

        :return
        - `DataFrame` -> Daje pandas df za zadate kriterijume
        """
        # Formatiranje datuma
        start_date = pd.to_datetime(start_date, format="%d-%m-%Y")
        end_date = pd.to_datetime(end_date, format="%d-%m-%Y")

        self.df.loc[:, "Datum zakazivanja"] = pd.to_datetime(self.df["Datum zakazivanja"], format="%d %B, %Y")
        
        # Kriterijum pretrage
        new_df = self.df.loc[(self.df["Rukovodilac"] == rukovodilac) & (self.df["Datum zakazivanja"] >= start_date) & (self.df["Datum zakazivanja"] < end_date) & (self.df["Pojavio se"].str.lower() == "da")]
        
        # Grupisanje podataka po "Datum zakazivanja" i brojanje za svaki dan u range
        counts_by_day = new_df.groupby("Datum zakazivanja")["Datum zakazivanja"].count()

        # Preimenovanje kolona

        return counts_by_day
    
    def pie_data(self, start_date: str, end_date: str):
        # Formatiranje datuma
        start_date = pd.to_datetime(start_date, format="%d-%m-%Y")
        end_date = pd.to_datetime(end_date, format="%d-%m-%Y")

        # Izvlačenje svih imena rukovodilaca
        rukovodilci = self.df["Rukovodilac"].unique()

        self.df.loc[:, "Datum zakazivanja"] = pd.to_datetime(self.df["Datum zakazivanja"], format="%d %B, %Y")

        # Inicijalizacija praznog rečnika za čuvanje rezultata za svakog rukovodioca
        rezultati = {}
        rezultati_acepted = {}
        rezultati_obuka = {}
        rezultati_declined = {}

        for rukovodilac in rukovodilci:
            # Kriterijum pretrage za svakog rukovodioca
            new_df = self.df.loc[
                (self.df["Rukovodilac"] == rukovodilac) & 
                (self.df["Datum zakazivanja"] >= start_date) & 
                (self.df["Datum zakazivanja"] < end_date) & 
                (self.df["Pojavio se"].str.lower() == "da")
                ]
            
            new_df_accepted = self.df.loc[
                (self.df["Rukovodilac"] == rukovodilac) & 
                (self.df["Datum zakazivanja"] >= start_date) & 
                (self.df["Datum zakazivanja"] < end_date) & 
                (self.df["Pojavio se"].str.lower() == "da") & 
                (self.df["Status"].str.lower() == "da")
                ]
            
            new_df_traning = self.df.loc[
                (self.df["Rukovodilac"] == rukovodilac) & 
                (self.df["Datum zakazivanja"] >= start_date) & 
                (self.df["Datum zakazivanja"] < end_date) & 
                (self.df["Pojavio se"].str.lower() == "da") & 
                (self.df["Status"].str.lower() == "da") & 
                (self.df["Datum obuke"].notna())
                ]
            
            new_df_traning_declined = self.df.loc[
                (self.df["Rukovodilac"] == rukovodilac) & 
                (self.df["Datum zakazivanja"] >= start_date) & 
                (self.df["Datum zakazivanja"] < end_date) & 
                (self.df["Pojavio se"].str.lower() == "da") & 
                (self.df["Status"].str.lower() == "da") & 
                (self.df["Datum obuke"].isnull() | (self.df["Datum obuke"] == pd.NaT))
                ]
        
            
            # Brojanje intervjua za svakog rukovodioca
            ukupan_broj_intervjua = len(new_df)

            ukupan_broj_primljenih = len(new_df_accepted)
            
            ukupan_broj_obuka = len(new_df_traning)

            ukupan_broj_declined = len(new_df_traning_declined)

            if ukupan_broj_intervjua > 0 and ukupan_broj_primljenih > 0 and ukupan_broj_obuka > 0 and ukupan_broj_declined > 0:
                
                rezultati[rukovodilac] = ukupan_broj_intervjua

                rezultati_acepted[rukovodilac] = ukupan_broj_primljenih

                rezultati_obuka[rukovodilac] = ukupan_broj_obuka

                rezultati_declined[rukovodilac] = ukupan_broj_declined

        return rezultati, rezultati_acepted, rezultati_obuka, rezultati_declined
    
        
# l = Analytic()

# l.locate_data()

# l.load_data("Telemarketing")

# ch = l.clean()

# ch = l.pie_data("01-01-2023", "30-09-2023")

# num = 0
# for k,v in zip(ch[2].keys(), ch[2].values()):
#     x = v
#     num = num + x
# print(num)
# for key in ch:
#     if ch[key] > 0:
#         print(f"{key}:{ch[key]}")
# key = list(ch.keys())
# value = list(ch.values())
# print(key, value)
# ch = l.filter_by_date("Nemanja Božinovski", "01-01-2023", "30-09-2023")

# # # rukovodilac = ch["Rukovodilac"].drop_duplicates()
# result = []
# for idx, val in zip(ch.index, ch.values):
#     result.append([idx, val])
# # Kreirajte DataFrame
# df = pd.DataFrame(result, columns=["Datum zakazivanja", "Broj intervjua"])

# # Pretvorite kolonu "Datum" u tip podataka za datume
# df["Datum zakazivanja"] = pd.to_datetime(df["Datum zakazivanja"])

# # Prikazivanje DataFrame-a
# print(df["Broj intervjua"].sum())

