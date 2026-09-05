from django.db import models
from datetime import date

class Cities(models.TextChoices):
  ALYTUS =          "alytus", "Alytus"
  ANYKSCIAI =       "anyksciai", "Anykščiai"
  AKMENE =          "akmene", "Akmenė"
  BIRZAI =          "birzai", "Biržai"
  BIRSTONAS =       "birstonas", "Birštonas"
  DRUSKININKAI =    "druskininkai", "Druskininkai"
  ELEKTRENAI =      "elektrenai", "Elektrėnai"
  GARGZDAI =        "gargzdai", "Gargždai"
  IGNALINA =        "ignalina", "Ignalina"
  JONAVA =          "jonava", "Jonava"
  JONISKIS =        "joniskis", "Joniškis"
  JURBARKAS =       "jurbarkas", "Jurbarkas"
  KAUNAS =          "kaunas", "Kaunas"
  KAISIADORYS =     "kaisiadorys", "Kaišiadorys"
  KALVARIJA =       "kalvarija", "Kalvarija"
  KAZLU_RUDA =      "kazlu_ruda", "Kazlų Rūda"
  KEDAINIAI =       "kedainiai", "Kėdainiai"
  KELME =           "kelme", "Kelmė"
  KLAIPEDA =        "klaipeda", "Klaipėda"
  KREKENAVA =       "krekenava", "Krekenava"
  KRETINGA =        "kretinga", "Kretinga"
  KUPISKIS =        "kupiskis", "Kupiškis"
  KURSENAI =        "kursenai", "Kuršėnai"
  LAZDIJAI =        "lazdijai", "Lazdijai"
  LENTVARIS =       "lentvaris", "Lentvaris"
  MARIJAMPOLE =     "marijampole", "Marijampolė"
  MAZEIKIAI =       "mazeikiai", "Mažeikiai"
  MOLETAI =         "moletai", "Molėtai"
  NAUJOJI_AKMENE =  "naujoji_akmene", "Naujoji Akmenė"
  NEMENCINE =       "nemencine", "Nemenčinė"
  NERINGA =         "neringa", "Neringa"
  PABRADE =         "pabrade", "Pabradė"
  PAGEGIAI =        "pagegiai", "Pagėgiai"
  PAKRUOJIS =       "pakruojis", "Pakruojis"
  PALANGA =         "palanga", "Palanga"
  PASVALYS =        "pasvalys", "Pasvalys"
  PLUNGE =          "plunge", "Plungė"
  PRIENAI =         "prienai", "Prienai"
  RADVILISKIS =     "radviliskis", "Radviliškis"
  RASEINIAI =       "raseiniai", "Raseiniai"
  RIETAVAS =        "rietavas", "Rietavas"
  ROKISKIS =        "rokiskis", "Rokiškis"
  SAKIAI =          "sakiai", "Šakiai"
  SALCININKAI =     "salcininkai", "Šalčininkai"
  SILALE =          "silale", "Šilalė"
  SILUTE =          "silute", "Šilutė"
  SIRVINTOS =       "sirvintos", "Širvintos"
  SKUODAS =         "skuodas", "Skuodas"
  SVENCIONYS =      "svencionys", "Švenčionys"
  SIAULIAI =        "siauliai", "Šiauliai"
  TAURAGE =         "taurage", "Tauragė"
  TELSIAI =         "telsiai", "Telšiai"
  TRAKAI =          "trakai", "Trakai"
  UKMERGE =         "ukmerge", "Ukmergė"
  UTENA =           "utena", "Utena"
  VARENA =          "varena", "Varėna"
  VIEVIS =          "vievis", "Vievis"
  VILKAVISKIS =     "vilkaviskis", "Vilkaviškis"
  VILNIUS =         "vilnius", "Vilnius"
  VISAGINAS =       "visaginas", "Visaginas"
  ZARASAI =         "zarasai", "Zarasai"

CITY_COORDINATES = {
    Cities.ALYTUS:        (54.3963, 24.0459),
    Cities.ANYKSCIAI:     (55.5300, 25.1017),
    Cities.AKMENE:        (56.2455, 22.7471),
    Cities.BIRZAI:        (56.2018, 24.7560),
    Cities.BIRSTONAS:     (54.56697, 24.00931),
    Cities.DRUSKININKAI:  (53.9934, 24.0342),
    Cities.ELEKTRENAI:    (54.7654, 24.7741),
    Cities.GARGZDAI:      (55.7128, 21.4033),
    Cities.IGNALINA:      (55.3490, 26.1550),
    Cities.JONAVA:        (55.0801, 24.2754),
    Cities.JONISKIS:      (56.2167, 23.8667),
    Cities.JURBARKAS:     (55.0772, 22.9753),
    Cities.KAUNAS:        (54.8985, 23.9036),
    Cities.KAISIADORYS:   (55.2667, 24.1167),
    Cities.KALVARIJA:     (54.5833, 23.0167),
    Cities.KAZLU_RUDA:    (54.8833, 23.0500),
    Cities.KEDAINIAI:     (55.2878, 23.9727),
    Cities.KELME:          (55.7000, 22.9333),
    Cities.KLAIPEDA:       (55.7068, 21.1391),
    Cities.KREKENAVA:      (55.6000, 23.9000),
    Cities.KRETINGA:       (55.8888, 21.2445),
    Cities.KUPISKIS:       (55.9667, 24.9667),
    Cities.KURSENAI:       (55.9333, 22.5333),
    Cities.LAZDIJAI:       (54.2167, 23.4167),
    Cities.LENTVARIS:      (54.7000, 25.2000),
    Cities.MARIJAMPOLE:    (54.5667, 23.3500),
    Cities.MAZEIKIAI:      (56.3167, 22.3333),
    Cities.MOLETAI:        (55.2500, 25.5000),
    Cities.NAUJOJI_AKMENE: (56.3000, 22.3167),
    Cities.NEMENCINE:      (54.9833, 24.1833),
    Cities.NERINGA:        (55.3200, 21.0600),
    Cities.PABRADE:        (54.9167, 24.9500),
    Cities.PAGEGIAI:       (55.0833, 21.9833),
    Cities.PAKRUOJIS:      (55.9833, 23.9667),
    Cities.PALANGA:        (55.9203, 21.0710),
    Cities.PASVALYS:       (56.0833, 24.3500),
    Cities.PLUNGE:         (55.9077, 21.8456),
    Cities.PRIENAI:        (54.6500, 24.3000),
    Cities.RADVILISKIS:    (55.7333, 23.7667),
    Cities.RASEINIAI:      (55.3333, 22.2167),
    Cities.RIETAVAS:       (55.5667, 21.8500),
    Cities.ROKISKIS:       (55.9600, 25.5900),
    Cities.SAKIAI:         (55.0833, 23.0333),
    Cities.SALCININKAI:    (54.1500, 25.3167),
    Cities.SILALE:         (55.3667, 22.9000),
    Cities.SILUTE:         (55.3453, 21.4733),
    Cities.SIRVINTOS:      (55.04702573656087, 24.94924306869507),
    Cities.SKUODAS:        (56.2667, 21.5167),
    Cities.SVENCIONYS:     (55.1167, 26.3667),
    Cities.SIAULIAI:       (55.9333, 23.3167),
    Cities.TAURAGE:        (55.2522, 22.2897),
    Cities.TELSIAI:        (55.9831, 22.2343),
    Cities.TRAKAI:         (54.6333, 24.9333),
    Cities.UKMERGE:        (55.24893787834831, 24.7653551104304),
    Cities.UTENA:          (55.5000, 25.6000),
    Cities.VARENA:         (54.2167, 24.5667),
    Cities.VIEVIS:         (54.7500, 25.2833),
    Cities.VILKAVISKIS:    (54.6333, 23.0333),
    Cities.VILNIUS:        (54.6892, 25.2798),
    Cities.VISAGINAS:      (55.5968, 26.4398),
    Cities.ZARASAI:        (55.7333, 26.2500),
}

class Genders(models.TextChoices):
  VYRAS =   "vyras", "Vyras"
  MOTERIS = "moteris", "Moteris"

YEARS = range(date.today().year, 1900, -1)  # e.g., 2025 → 1901
DAYS = range(1, 32)

class Months(models.IntegerChoices):
    JANUARY =     1, 'Sausis'
    FEBRUARY =    2, 'Vasaris'
    MARCH =       3, 'Kovas'
    APRIL =       4, 'Balandis'
    MAY =         5, 'Gegužė'
    JUNE =        6, 'Birželis'
    JULY =        7, 'Liepa'
    AUGUST =      8, 'Rugpjūtis'
    SEPTEMBER =   9, 'Rugsėjis'
    OCTOBER =     10, 'Spalis'
    NOVEMBER =    11, 'Lapkritis'
    DECEMBER =    12, 'Gruodis'
  
class Hours(models.IntegerChoices):
    H00 = 0, "00:00"
    H01 = 1, "01:00"
    H02 = 2, "02:00"
    H03 = 3, "03:00"
    H04 = 4, "04:00"
    H05 = 5, "05:00"
    H06 = 6, "06:00"
    H07 = 7, "07:00"
    H08 = 8, "08:00"
    H09 = 9, "09:00"
    H10 = 10, "10:00"
    H11 = 11, "11:00"
    H12 = 12, "12:00"
    H13 = 13, "13:00"
    H14 = 14, "14:00"
    H15 = 15, "15:00"
    H16 = 16, "16:00"
    H17 = 17, "17:00"
    H18 = 18, "18:00"
    H19 = 19, "19:00"
    H20 = 20, "20:00"
    H21 = 21, "21:00"
    H22 = 22, "22:00"
    H23 = 23, "23:00"
    H24 = 24, "24:00"

class MeetingStatusEnum(models.IntegerChoices):
    CREATED     = 1, "Created"   # When user creates meeting request
    CONFIRMED   = 2, "Confirmed" # After friend confirms meeting request
    COMPLETED   = 3, "Completed" # After confirmation code is succesfully entered by friend
    FAILED      = 4, "Failed"    # When meeting code doesn't get entered after a certain period
    DECLINED    = 5, "Declined"  # When created meeting is declined by friend
    EXPIRED     = 6, "Expired"   # When created meeting is unconfirmed and reaches deadline

class BanReasonEnum(models.IntegerChoices):
   UNPAID_MEETING = 1, "Unpaid meeting"
   BAD_BEHAVIOR = 2, "Bad behavior"
   BAD_PROFILE = 3, "Bad profile"