"""Weltzeituhr (Alexanderplatz) data: post-1997 faces [HU], ring order, plus 1990 reconstruction variants."""
import unicodedata, re

FACES_1997 = [
 (1, "Amsterdam, Berlin, Brüssel, Budapest, Madrid, Paris, Prag, Stockholm, Warschau, Oslo, Kopenhagen, Wien, Bern, Pressburg, Belgrad, Rom, Tunis, Kinshasa"),
 (2, "Helsinki, Riga, Tallinn, Wilna, Minsk, Kiew, Bukarest, Sofia, Nikosia, Ankara, Istanbul, Athen, Tel Aviv, Jerusalem, Beirut, Damaskus, Kairo, Kapstadt"),
 (3, "Murmansk, St. Petersburg, Moskau, Teheran, Bagdad, Aden, Sanaa, Addis Abeba, Mogadischu, Daressalam, Antananarivo, Kuwait"),
 (4, "Nischnij Nowgorod, Wolgograd, Baku, Tiflis, Eriwan, Kabul, Mauritius"),
 (5, "Jekaterinburg, Aschgabat, Bischkek, Duschanbe, New Delhi, Karachi, Colombo"),
 (6, "Omsk, Almaty, Taschkent, Nowosibirsk, Rangun, Dhaka"),
 (7, "Krasnojarsk, Hanoi, Bangkok, Phnom Penh, Jakarta"),
 (8, "Irkutsk, Ulan-Bator, Peking, Shanghai, Manila, Perth, Hongkong, Kuala Lumpur, Singapur"),
 (9, "Jakutsk, Pjöngjang, Tokyo, Seoul, Chabarowsk, Wladiwostok, Sydney, Canberra, Melbourne"),
 (10, "Magadan, Sachalin"),
 (12, "Kamtschatka, Wellington"),
 (12.5, "Datumsgrenze"),
 (-11, "Kap Deschnew, Apia"),
 (-10, "Honolulu, Marquesas In."),
 (-9, "Nome, Fairbanks, Anchorage"),
 (-8, "Vancouver, Dawson, San Francisco, Los Angeles"),
 (-7, "Edmonton, Denver"),
 (-6, "New Orleans, Mexiko-Stadt, Guatemala-Stadt, Managua, Galápagos In."),
 (-5, "Montreal, Washington, New York, Havanna, Panama, Santafé de Bogotá, Quito, Lima"),
 (-4, "Halifax, Caracas, La Paz, Asunción, Santiago de Chile"),
 (-3, "Westgrönland, Brasilia, Rio de Janeiro, São Paulo, Montevideo, Buenos Aires"),
 (-2, "Ostgrönland"),
 (-1, "Azoren, Kap Verde"),
 (0, "Reykjavik, Dublin, London, Lissabon, Madeira, Bissau, Casablanca, Conakry, Dakar, Bamako, Accra"),
]
# nominal UTC offset of each face (face 10 holds +11 cities; 12.5 = date line face)
FACE_UTC = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0]
# alternative: strict face hour 1..24 / ring index
FACE_IDX = list(range(24))

def faces(version="1997"):
    F = [[c.strip() for c in s.split(",")] for _, s in FACES_1997]
    if version == "1997":
        return F
    if version.startswith("1990"):
        F = [list(f) for f in F]
        rm = {"Oslo", "Jerusalem", "Tel Aviv", "Kapstadt", "Seoul"}
        F = [[c for c in f if c not in rm] for f in F]
        ren = {"St. Petersburg": "Leningrad", "Almaty": "Alma Ata", "Pressburg": "Bratislava"}
        F = [[ren.get(c, c) for c in f] for f in F]
        # Kiew back on Moscow face (position: append after Moskau? unknown; variants)
        F[1].remove("Kiew")
        if version == "1990a":
            F[2].insert(F[2].index("Moskau") + 1, "Kiew")
        elif version == "1990b":
            F[2].insert(F[2].index("Moskau"), "Kiew")
        elif version == "1990c":
            F[2].append("Kiew")
        elif version == "1990d":
            F[2].insert(0, "Kiew")
        if "nodl" in version:
            pass
        return F
    raise ValueError(version)

def norm(name, mode="strip"):
    s = name.upper()
    if mode == "ue":
        s = s.replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub("[^A-Z]", "", s)

def cities(version="1997", dateline=True):
    """List of (name, face_ring_index, face_utc) in ring order."""
    out = []
    for fi, f in enumerate(faces(version)):
        for c in f:
            if c == "Datumsgrenze" and not dateline:
                continue
            out.append((c, fi, FACE_UTC[fi]))
    return out

VERSIONS = ["1997", "1990a", "1990b", "1990c", "1990d"]
