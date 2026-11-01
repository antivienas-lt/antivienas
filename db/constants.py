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
    Cities.ANYKSCIAI:     (55.525723527887415, 25.10446509244491),
    Cities.AKMENE:        (56.2455, 22.7471),
    Cities.BIRZAI:        (56.2018, 24.7560),
    Cities.BIRSTONAS:     (54.60394535908352, 24.030442059919665),
    Cities.DRUSKININKAI:  (54.017586496680124, 23.974704677893786),
    Cities.ELEKTRENAI:    (54.78613234398312, 24.67127886538682),
    Cities.GARGZDAI:      (55.7128, 21.4033),
    Cities.IGNALINA:      (55.34282627783333, 26.164754399698182),
    Cities.JONAVA:        (55.0801, 24.2754),
    Cities.JONISKIS:      (56.23994049985425, 23.616494688561193),
    Cities.JURBARKAS:     (55.07778560073498, 22.77001889011421),
    Cities.KAUNAS:        (54.8985, 23.9036),
    Cities.KAISIADORYS:   (54.86090204480071, 24.452692031138678),
    Cities.KALVARIJA:     (54.41434513260041, 23.22653860313126),
    Cities.KAZLU_RUDA:    (54.752038026474935, 23.500285065825224),
    Cities.KEDAINIAI:     (55.2878, 23.9727),
    Cities.KELME:          (55.63152466815741, 22.93577683960334),
    Cities.KLAIPEDA:       (55.7068, 21.1391),
    Cities.KREKENAVA:      (55.5426593511247, 24.096291850366704),
    Cities.KRETINGA:       (55.8888, 21.2445),
    Cities.KUPISKIS:       (55.838711041357676, 24.974759663804324),
    Cities.KURSENAI:       (56.00515686738964, 22.931967562624088),
    Cities.LAZDIJAI:       (54.23586240728849, 23.51370096194022),
    Cities.LENTVARIS:      (54.644160887580036, 25.046993453671146),
    Cities.MARIJAMPOLE:    (54.55605797482049, 23.34695938386662),
    Cities.MAZEIKIAI:      (56.31060762357684, 22.348322092231854),
    Cities.MOLETAI:        (55.23135969312823, 25.419154850246528),
    Cities.NAUJOJI_AKMENE: (56.32178230786933, 22.88088892445522),
    Cities.NEMENCINE:      (54.84619330394806, 25.46551658414111),
    Cities.NERINGA:        (55.30416908688435, 21.006856977194133),
    Cities.PABRADE:        (54.98374663531067, 25.76499190027572),
    Cities.PAGEGIAI:       (55.134485812061875, 21.908990067128006),
    Cities.PAKRUOJIS:      (55.97697555819686, 23.846886161331383),
    Cities.PALANGA:        (55.91867925932411, 21.058251234920455),
    Cities.PASVALYS:       (56.06233160496893, 24.398705412555575),
    Cities.PLUNGE:         (55.91124427409058, 21.847635970867888),
    Cities.PRIENAI:        (54.63547127733858, 23.94632998033674),
    Cities.RADVILISKIS:    (55.814962533235324, 23.547186923802705),
    Cities.RASEINIAI:      (55.378900763725774, 23.114255024976206),
    Cities.RIETAVAS:       (55.723709218125805, 21.925329615365033),
    Cities.ROKISKIS:       (55.9600, 25.5900),
    Cities.SAKIAI:         (54.956609524188735, 23.045088632599956),
    Cities.SALCININKAI:    (54.3070887494949, 25.384754232273472),
    Cities.SILALE:         (55.489781611356534, 22.18762331044145),
    Cities.SILUTE:         (55.340987766348675, 21.461748279131044),
    Cities.SIRVINTOS:      (55.04702573656087, 24.94924306869507),
    Cities.SKUODAS:        (56.269291828346724, 21.525782356966744),
    Cities.SVENCIONYS:     (55.13397062313255, 26.158960190791785),
    Cities.SIAULIAI:       (55.9333, 23.3167),
    Cities.TAURAGE:        (55.2522, 22.2897),
    Cities.TELSIAI:        (55.9831, 22.2343),
    Cities.TRAKAI:         (54.638572025842706, 24.933565794573987),
    Cities.UKMERGE:        (55.24893787834831, 24.7653551104304),
    Cities.UTENA:          (55.5000, 25.6000),
    Cities.VARENA:         (54.21174437192398, 24.569429679334725),
    Cities.VIEVIS:         (54.76977772920762, 24.81282928139044),
    Cities.VILKAVISKIS:    (54.650303506769646, 23.03371733342979),
    Cities.VILNIUS:        (54.6892, 25.2798),
    Cities.VISAGINAS:      (55.5968, 26.4398),
    Cities.ZARASAI:        (55.73174476474307, 26.24560212707552),
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


PLATFORM_FEE_RATE = 1.20