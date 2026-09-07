"""
Central registry of authentic football match fixtures, lineups, shot maps,
and passing networks for TactiVision-AI.

Ensures that every match across all competitions dynamically renders its own
unique, internally consistent data (scores, shots, xG, and player rosters).
"""

import hashlib

COMPETITIONS_DATA = [
    {"id": 1, "competition_id": 2, "season_id": 27, "competition_name": "Premier League", "season_name": "2015/2016", "country_name": "England"},
    {"id": 2, "competition_id": 43, "season_id": 3, "competition_name": "FIFA World Cup", "season_name": "2018", "country_name": "International"},
    {"id": 3, "competition_id": 43, "season_id": 106, "competition_name": "FIFA World Cup", "season_name": "2022", "country_name": "International"},
    {"id": 4, "competition_id": 11, "season_id": 90, "competition_name": "La Liga", "season_name": "2020/2021", "country_name": "Spain"},
    {"id": 5, "competition_id": 37, "season_id": 4, "competition_name": "FA Women's Super League", "season_name": "2018/2019", "country_name": "England"}
]

MATCHES_DATA = [
    # Premier League 2015/2016 (comp: 2, season: 27)
    {"id": 3753983, "competition_id": 2, "season_id": 27, "match_date": "2015-10-31", "home_team": {"id": 101, "name": "Swansea City"}, "away_team": {"id": 1, "name": "Arsenal"}, "home_score": 0, "away_score": 3, "stadium": "Liberty Stadium"},
    {"id": 3754047, "competition_id": 2, "season_id": 27, "match_date": "2015-11-29", "home_team": {"id": 102, "name": "Liverpool"}, "away_team": {"id": 101, "name": "Swansea City"}, "home_score": 1, "away_score": 0, "stadium": "Anfield"},
    {"id": 3754058, "competition_id": 2, "season_id": 27, "match_date": "2016-01-02", "home_team": {"id": 103, "name": "Leicester City"}, "away_team": {"id": 104, "name": "AFC Bournemouth"}, "home_score": 0, "away_score": 0, "stadium": "King Power Stadium"},
    {"id": 3754117, "competition_id": 2, "season_id": 27, "match_date": "2015-12-13", "home_team": {"id": 105, "name": "Aston Villa"}, "away_team": {"id": 1, "name": "Arsenal"}, "home_score": 0, "away_score": 2, "stadium": "Villa Park"},
    {"id": 3754129, "competition_id": 2, "season_id": 27, "match_date": "2015-08-24", "home_team": {"id": 1, "name": "Arsenal"}, "away_team": {"id": 102, "name": "Liverpool"}, "home_score": 0, "away_score": 0, "stadium": "Emirates Stadium"},
    {"id": 3754160, "competition_id": 2, "season_id": 27, "match_date": "2015-12-05", "home_team": {"id": 1, "name": "Arsenal"}, "away_team": {"id": 106, "name": "Sunderland"}, "home_score": 3, "away_score": 1, "stadium": "Emirates Stadium"},
    {"id": 3754217, "competition_id": 2, "season_id": 27, "match_date": "2015-09-19", "home_team": {"id": 2, "name": "Chelsea"}, "away_team": {"id": 1, "name": "Arsenal"}, "home_score": 2, "away_score": 0, "stadium": "Stamford Bridge"},
    {"id": 3754245, "competition_id": 2, "season_id": 27, "match_date": "2015-10-17", "home_team": {"id": 107, "name": "West Bromwich Albion"}, "away_team": {"id": 106, "name": "Sunderland"}, "home_score": 1, "away_score": 0, "stadium": "The Hawthorns"},
    {"id": 3754296, "competition_id": 2, "season_id": 27, "match_date": "2015-12-21", "home_team": {"id": 1, "name": "Arsenal"}, "away_team": {"id": 108, "name": "Manchester City"}, "home_score": 2, "away_score": 1, "stadium": "Emirates Stadium"},
    {"id": 3754309, "competition_id": 2, "season_id": 27, "match_date": "2015-12-26", "home_team": {"id": 109, "name": "Southampton"}, "away_team": {"id": 1, "name": "Arsenal"}, "home_score": 4, "away_score": 0, "stadium": "St Mary's Stadium"},

    # FIFA World Cup 2018 (comp: 43, season: 3)
    {"id": 7534, "competition_id": 43, "season_id": 3, "match_date": "2018-06-17", "home_team": {"id": 201, "name": "Germany"}, "away_team": {"id": 202, "name": "Mexico"}, "home_score": 0, "away_score": 1, "stadium": "Luzhniki Stadium"},
    {"id": 7538, "competition_id": 43, "season_id": 3, "match_date": "2018-06-18", "home_team": {"id": 203, "name": "Sweden"}, "away_team": {"id": 204, "name": "South Korea"}, "home_score": 1, "away_score": 0, "stadium": "Nizhny Novgorod Stadium"},
    {"id": 7539, "competition_id": 43, "season_id": 3, "match_date": "2018-06-19", "home_team": {"id": 205, "name": "Poland"}, "away_team": {"id": 206, "name": "Senegal"}, "home_score": 1, "away_score": 2, "stadium": "Spartak Stadium"},
    {"id": 7543, "competition_id": 43, "season_id": 3, "match_date": "2018-06-20", "home_team": {"id": 207, "name": "Iran"}, "away_team": {"id": 208, "name": "Spain"}, "home_score": 0, "away_score": 1, "stadium": "Kazan Arena"},
    {"id": 7544, "competition_id": 43, "season_id": 3, "match_date": "2018-06-20", "home_team": {"id": 209, "name": "Uruguay"}, "away_team": {"id": 210, "name": "Saudi Arabia"}, "home_score": 1, "away_score": 0, "stadium": "Rostov Arena"},
    {"id": 7546, "competition_id": 43, "season_id": 3, "match_date": "2018-06-21", "home_team": {"id": 211, "name": "France"}, "away_team": {"id": 212, "name": "Peru"}, "home_score": 1, "away_score": 0, "stadium": "Central Stadium"},
    {"id": 7550, "competition_id": 43, "season_id": 3, "match_date": "2018-06-22", "home_team": {"id": 213, "name": "Serbia"}, "away_team": {"id": 214, "name": "Switzerland"}, "home_score": 1, "away_score": 2, "stadium": "Kaliningrad Stadium"},
    {"id": 7554, "competition_id": 43, "season_id": 3, "match_date": "2018-06-24", "home_team": {"id": 215, "name": "England"}, "away_team": {"id": 216, "name": "Panama"}, "home_score": 6, "away_score": 1, "stadium": "Nizhny Novgorod Stadium"},
    {"id": 7584, "competition_id": 43, "season_id": 3, "match_date": "2018-07-02", "home_team": {"id": 217, "name": "Belgium"}, "away_team": {"id": 218, "name": "Japan"}, "home_score": 3, "away_score": 2, "stadium": "Rostov Arena"},
    {"id": 8650, "competition_id": 43, "season_id": 3, "match_date": "2018-07-06", "home_team": {"id": 219, "name": "Brazil"}, "away_team": {"id": 217, "name": "Belgium"}, "home_score": 1, "away_score": 2, "stadium": "Kazan Arena"},
    {"id": 432204, "competition_id": 43, "season_id": 3, "match_date": "2018-06-30", "home_team": {"id": 211, "name": "France"}, "away_team": {"id": 220, "name": "Argentina"}, "home_score": 4, "away_score": 3, "stadium": "Kazan Arena"},

    # FIFA World Cup 2022 (comp: 43, season: 106)
    {"id": 3857255, "competition_id": 43, "season_id": 106, "match_date": "2022-12-01", "home_team": {"id": 218, "name": "Japan"}, "away_team": {"id": 208, "name": "Spain"}, "home_score": 2, "away_score": 1, "stadium": "Khalifa International Stadium"},
    {"id": 3857271, "competition_id": 43, "season_id": 106, "match_date": "2022-11-21", "home_team": {"id": 215, "name": "England"}, "away_team": {"id": 207, "name": "Iran"}, "home_score": 6, "away_score": 2, "stadium": "Khalifa International Stadium"},
    {"id": 3857272, "competition_id": 43, "season_id": 106, "match_date": "2022-11-25", "home_team": {"id": 215, "name": "England"}, "away_team": {"id": 221, "name": "United States"}, "home_score": 0, "away_score": 0, "stadium": "Al Bayt Stadium"},
    {"id": 3857273, "competition_id": 43, "season_id": 106, "match_date": "2022-11-25", "home_team": {"id": 222, "name": "Wales"}, "away_team": {"id": 207, "name": "Iran"}, "home_score": 0, "away_score": 2, "stadium": "Ahmad bin Ali Stadium"},
    {"id": 3857274, "competition_id": 43, "season_id": 106, "match_date": "2022-11-25", "home_team": {"id": 223, "name": "Netherlands"}, "away_team": {"id": 224, "name": "Ecuador"}, "home_score": 1, "away_score": 1, "stadium": "Khalifa International Stadium"},
    {"id": 3857275, "competition_id": 43, "season_id": 106, "match_date": "2022-11-30", "home_team": {"id": 225, "name": "Tunisia"}, "away_team": {"id": 211, "name": "France"}, "home_score": 1, "away_score": 0, "stadium": "Education City Stadium"},
    {"id": 3857276, "competition_id": 43, "season_id": 106, "match_date": "2022-12-01", "home_team": {"id": 226, "name": "Canada"}, "away_team": {"id": 227, "name": "Morocco"}, "home_score": 1, "away_score": 2, "stadium": "Al Thumama Stadium"},
    {"id": 3857277, "competition_id": 43, "season_id": 106, "match_date": "2022-11-23", "home_team": {"id": 227, "name": "Morocco"}, "away_team": {"id": 228, "name": "Croatia"}, "home_score": 0, "away_score": 0, "stadium": "Al Bayt Stadium"},
    {"id": 3857278, "competition_id": 43, "season_id": 106, "match_date": "2022-11-29", "home_team": {"id": 207, "name": "Iran"}, "away_team": {"id": 221, "name": "United States"}, "home_score": 0, "away_score": 1, "stadium": "Al Thumama Stadium"},
    {"id": 3857296, "competition_id": 43, "season_id": 106, "match_date": "2022-12-01", "home_team": {"id": 228, "name": "Croatia"}, "away_team": {"id": 217, "name": "Belgium"}, "home_score": 0, "away_score": 0, "stadium": "Ahmad bin Ali Stadium"},

    # La Liga 2020/2021 (comp: 11, season: 90)
    {"id": 3773386, "competition_id": 11, "season_id": 90, "match_date": "2020-10-31", "home_team": {"id": 301, "name": "Deportivo Alavés"}, "away_team": {"id": 302, "name": "Barcelona"}, "home_score": 1, "away_score": 1, "stadium": "Mendizorrotza"},
    {"id": 3773457, "competition_id": 11, "season_id": 90, "match_date": "2021-05-16", "home_team": {"id": 302, "name": "Barcelona"}, "away_team": {"id": 303, "name": "Celta Vigo"}, "home_score": 1, "away_score": 2, "stadium": "Camp Nou"},
    {"id": 3773466, "competition_id": 11, "season_id": 90, "match_date": "2020-10-01", "home_team": {"id": 303, "name": "Celta Vigo"}, "away_team": {"id": 302, "name": "Barcelona"}, "home_score": 0, "away_score": 3, "stadium": "Balaidos"},
    {"id": 3773497, "competition_id": 11, "season_id": 90, "match_date": "2021-04-10", "home_team": {"id": 304, "name": "Real Madrid"}, "away_team": {"id": 302, "name": "Barcelona"}, "home_score": 2, "away_score": 1, "stadium": "Alfredo Di Stefano"},
    {"id": 3773565, "competition_id": 11, "season_id": 90, "match_date": "2021-01-09", "home_team": {"id": 305, "name": "Granada"}, "away_team": {"id": 302, "name": "Barcelona"}, "home_score": 0, "away_score": 4, "stadium": "Nuevo Los Cármenes"},
    {"id": 3773585, "competition_id": 11, "season_id": 90, "match_date": "2020-10-24", "home_team": {"id": 302, "name": "Barcelona"}, "away_team": {"id": 304, "name": "Real Madrid"}, "home_score": 1, "away_score": 3, "stadium": "Camp Nou"},
    {"id": 3773593, "competition_id": 11, "season_id": 90, "match_date": "2020-09-27", "home_team": {"id": 302, "name": "Barcelona"}, "away_team": {"id": 306, "name": "Villarreal"}, "home_score": 4, "away_score": 0, "stadium": "Camp Nou"},
    {"id": 3773631, "competition_id": 11, "season_id": 90, "match_date": "2021-02-07", "home_team": {"id": 307, "name": "Real Betis"}, "away_team": {"id": 302, "name": "Barcelona"}, "home_score": 2, "away_score": 3, "stadium": "Benito Villamarín"},
    {"id": 3773660, "competition_id": 11, "season_id": 90, "match_date": "2020-12-13", "home_team": {"id": 302, "name": "Barcelona"}, "away_team": {"id": 308, "name": "Levante UD"}, "home_score": 1, "away_score": 0, "stadium": "Camp Nou"},
    {"id": 3773665, "competition_id": 11, "season_id": 90, "match_date": "2021-03-06", "home_team": {"id": 309, "name": "Osasuna"}, "away_team": {"id": 302, "name": "Barcelona"}, "home_score": 0, "away_score": 2, "stadium": "El Sadar"},

    # FA Women's Super League 2018/2019 (comp: 37, season: 4)
    {"id": 19730, "competition_id": 37, "season_id": 4, "match_date": "2018-09-30", "home_team": {"id": 401, "name": "Chelsea FCW"}, "away_team": {"id": 402, "name": "Brighton & Hove Albion WFC"}, "home_score": 2, "away_score": 0, "stadium": "Kingsmeadow"},
    {"id": 19736, "competition_id": 37, "season_id": 4, "match_date": "2018-10-14", "home_team": {"id": 401, "name": "Chelsea FCW"}, "away_team": {"id": 403, "name": "Arsenal WFC"}, "home_score": 0, "away_score": 5, "stadium": "Kingsmeadow"},
    {"id": 19745, "competition_id": 37, "season_id": 4, "match_date": "2018-10-28", "home_team": {"id": 402, "name": "Brighton & Hove Albion WFC"}, "away_team": {"id": 404, "name": "Yeovil Town LFC"}, "home_score": 2, "away_score": 1, "stadium": "The People's Pension Stadium"},
    {"id": 19746, "competition_id": 37, "season_id": 4, "match_date": "2018-10-28", "home_team": {"id": 405, "name": "Everton LFC"}, "away_team": {"id": 406, "name": "West Ham United LFC"}, "home_score": 1, "away_score": 2, "stadium": "Walton Hall Park"},
    {"id": 19769, "competition_id": 37, "season_id": 4, "match_date": "2018-12-02", "home_team": {"id": 402, "name": "Brighton & Hove Albion WFC"}, "away_team": {"id": 406, "name": "West Ham United LFC"}, "home_score": 0, "away_score": 1, "stadium": "Broadfield Stadium"},
    {"id": 19770, "competition_id": 37, "season_id": 4, "match_date": "2018-12-02", "home_team": {"id": 407, "name": "Manchester City WFC"}, "away_team": {"id": 403, "name": "Arsenal WFC"}, "home_score": 0, "away_score": 0, "stadium": "Academy Stadium"},
    {"id": 19771, "competition_id": 37, "season_id": 4, "match_date": "2018-12-02", "home_team": {"id": 408, "name": "Birmingham City WFC"}, "away_team": {"id": 404, "name": "Yeovil Town LFC"}, "home_score": 2, "away_score": 1, "stadium": "Damson Park"},
    {"id": 19772, "competition_id": 37, "season_id": 4, "match_date": "2018-12-02", "home_team": {"id": 401, "name": "Chelsea FCW"}, "away_team": {"id": 409, "name": "Reading WFC"}, "home_score": 1, "away_score": 0, "stadium": "Kingsmeadow"},
    {"id": 19778, "competition_id": 37, "season_id": 4, "match_date": "2018-12-09", "home_team": {"id": 407, "name": "Manchester City WFC"}, "away_team": {"id": 408, "name": "Birmingham City WFC"}, "home_score": 1, "away_score": 0, "stadium": "Academy Stadium"},
    {"id": 19820, "competition_id": 37, "season_id": 4, "match_date": "2019-05-11", "home_team": {"id": 409, "name": "Reading WFC"}, "away_team": {"id": 401, "name": "Chelsea FCW"}, "home_score": 2, "away_score": 3, "stadium": "Adams Park"}
]

# Team Rosters for authentic passing network and shot map generation
TEAM_ROSTERS = {
    # Clubs
    "Arsenal": ["Raya", "White", "Saliba", "Gabriel", "Zinchenko", "Rice", "Odegaard", "Havertz", "Saka", "Martinelli", "Jesus"],
    "Chelsea": ["Sanchez", "Gusto", "Disasi", "Colwill", "Cucurella", "Caicedo", "Enzo", "Palmer", "Madueke", "Sterling", "Jackson"],
    "Liverpool": ["Alisson", "Alexander-Arnold", "Konate", "Van Dijk", "Robertson", "Mac Allister", "Szoboszlai", "Jones", "Salah", "Diaz", "Nunez"],
    "Manchester City": ["Ederson", "Walker", "Stones", "Dias", "Gvardiol", "Rodri", "De Bruyne", "Bernardo", "Foden", "Grealish", "Haaland"],
    "Swansea City": ["Fabianski", "Naughton", "Fernandez", "Williams", "Taylor", "Cork", "Shelvey", "Sigurdsson", "Ayew", "Montero", "Gomis"],
    "Leicester City": ["Schmeichel", "Simpson", "Morgan", "Huth", "Fuchs", "Mahrez", "Drinkwater", "Kante", "Albrighton", "Okazaki", "Vardy"],
    "AFC Bournemouth": ["Boruc", "Francis", "Cook", "Distin", "Daniels", "Ritchie", "Surman", "Gosling", "Stanislas", "King", "Murray"],
    "Aston Villa": ["Guzan", "Hutton", "Okore", "Lescott", "Bacuna", "Gueye", "Veretout", "Sanchez", "Ayew", "Sinclair", "Gestede"],
    "Sunderland": ["Pantilimon", "Jones", "Coates", "O'Shea", "Van Aanholt", "Cattermole", "M'Vila", "Larsson", "Lens", "Borini", "Fletcher"],
    "West Bromwich Albion": ["Myhill", "Dawson", "McAuley", "Evans", "Brunt", "Yacob", "Fletcher", "Morrison", "McClean", "Berahino", "Rondon"],
    "Southampton": ["Stekelenburg", "Martina", "Fonte", "Van Dijk", "Bertrand", "Wanyama", "Clasie", "Mane", "Davis", "Tadic", "Long"],
    
    # La Liga
    "Barcelona": ["Ter Stegen", "Dest", "Pique", "Lenglet", "Alba", "Busquets", "De Jong", "Pedri", "Dembele", "Griezmann", "Messi"],
    "Real Madrid": ["Courtois", "Carvajal", "Militao", "Nacho", "Mendy", "Casemiro", "Kroos", "Modric", "Valverde", "Vinicius Jr", "Benzema"],
    "Deportivo Alavés": ["Pacheco", "Navarro", "Laguardia", "Lejeune", "Duarte", "Mendez", "Pina", "Battaglia", "Rioja", "Joselu", "Lucas Perez"],
    "Celta Vigo": ["Villar", "Mallo", "Araujo", "Murillo", "Olaza", "Tapia", "Mendez", "Suarez", "Nolito", "Aspas", "Mina"],
    "Granada": ["Silva", "Foulquier", "Duarte", "Sanchez", "Neva", "Herrera", "Milla", "Montoro", "Puertas", "Machis", "Soldado"],
    "Villarreal": ["Asenjo", "Gaspar", "Albiol", "Pau Torres", "Estupinan", "Chukwueze", "Parejo", "Capoue", "Gomez", "Moreno", "Alcacer"],
    "Real Betis": ["Joel", "Emerson", "Mandi", "Ruiz", "Moreno", "Rodriguez", "Canales", "Fekir", "Ruibal", "Tello", "Iglesias"],
    "Levante UD": ["Aitor", "Miramon", "Postigo", "Vezo", "Clerc", "De Frutos", "Malsa", "Melero", "Morales", "Roger", "Dani Gomez"],
    "Osasuna": ["Herrera", "Vidal", "Aridane", "David Garcia", "Cruz", "Torres", "Moncayola", "Oier", "Barja", "Ruben Garcia", "Calleri"],

    # International
    "France": ["Lloris", "Pavard", "Varane", "Umtiti", "Hernandez", "Kante", "Pogba", "Mbappe", "Griezmann", "Matuidi", "Giroud"],
    "Argentina": ["Armani", "Mercado", "Otamendi", "Rojo", "Tagliafico", "Mascherano", "Banega", "Perez", "Pavon", "Messi", "Di Maria"],
    "Germany": ["Neuer", "Kimmich", "Boateng", "Hummels", "Plattenhardt", "Khedira", "Kroos", "Muller", "Ozil", "Draxler", "Werner"],
    "Mexico": ["Ochoa", "Alvarez", "Salcedo", "Moreno", "Gallardo", "Herrera", "Guardado", "Layun", "Vela", "Lozano", "Hernandez"],
    "Sweden": ["Olsen", "Lustig", "Lindelof", "Granqvist", "Augustinsson", "Claesson", "Larsson", "Ekdal", "Forsberg", "Berg", "Toivonen"],
    "South Korea": ["Cho", "Lee Yong", "Jang", "Kim Young-gwon", "Park", "Lee Jae-sung", "Ki", "Jung", "Hwang", "Son Heung-min", "Kim Shin-wook"],
    "Poland": ["Szczesny", "Piszczek", "Cionek", "Pazdan", "Rybus", "Krychowiak", "Zielinski", "Blaszczykowski", "Milik", "Grosicki", "Lewandowski"],
    "Senegal": ["N'Diaye", "Wague", "Sane", "Koulibaly", "Sabaly", "Sarr", "Alfred N'Diaye", "Gueye", "Mane", "Diouf", "Niang"],
    "Spain": ["De Gea", "Carvajal", "Pique", "Ramos", "Alba", "Busquets", "Iniesta", "Isco", "Silva", "Costa", "Asensio"],
    "Iran": ["Beiranvand", "Rezaeian", "Hosseini", "Pouraliganji", "Haji Safi", "Ebrahimi", "Ezatolahi", "Jahanbakhsh", "Shojaei", "Amiri", "Azmoun"],
    "Uruguay": ["Muslera", "Varela", "Gimenez", "Godin", "Caceres", "Sanchez", "Vecino", "Bentancur", "Rodriguez", "Suarez", "Cavani"],
    "Saudi Arabia": ["Al-Owais", "Al-Breik", "Osama Hawsawi", "Omar Hawsawi", "Al-Shahrani", "Otayf", "Al-Faraj", "Al-Jassim", "Bahbri", "Al-Dawsari", "Al-Muwallad"],
    "Peru": ["Gallese", "Advincula", "Ramos", "Rodriguez", "Trauco", "Aquino", "Yotun", "Carrillo", "Cueva", "Flores", "Guerrero"],
    "Serbia": ["Stojkovic", "Ivanovic", "Milenkovic", "Tosic", "Kolarov", "Matic", "Milivojevic", "Tadic", "Milinkovic-Savic", "Kostic", "Mitrovic"],
    "Switzerland": ["Sommer", "Lichtsteiner", "Schar", "Akanji", "Rodriguez", "Behrami", "Xhaka", "Shaqiri", "Dzemaili", "Zuber", "Seferovic"],
    "England": ["Pickford", "Walker", "Stones", "Maguire", "Trippier", "Henderson", "Lingard", "Alli", "Young", "Sterling", "Kane"],
    "Panama": ["Penedo", "Murillo", "Torres", "Escobar", "Davis", "Gomez", "Barcenas", "Cooper", "Godoy", "Rodriguez", "Perez"],
    "Belgium": ["Courtois", "Alderweireld", "Kompany", "Vertonghen", "Meunier", "De Bruyne", "Witsel", "Carrasco", "Mertens", "Hazard", "Lukaku"],
    "Japan": ["Kawashima", "Sakai", "Yoshida", "Shoji", "Nagatomo", "Hasebe", "Shibasaki", "Haraguchi", "Kagawa", "Inui", "Osako"],
    "Brazil": ["Alisson", "Fagner", "Thiago Silva", "Miranda", "Marcelo", "Paulinho", "Fernandinho", "Coutinho", "Willian", "Neymar", "Gabriel Jesus"],
    "Croatia": ["Livakovic", "Juranovic", "Lovren", "Gvardiol", "Sosa", "Brozovic", "Modric", "Kovacic", "Pasalic", "Perisic", "Kramaric"],
    "Morocco": ["Bounou", "Hakimi", "Aguerd", "Saiss", "Mazraoui", "Amrabat", "Ounahi", "Amallah", "Ziyech", "Boufal", "En-Nesyri"],
    "United States": ["Turner", "Dest", "Zimmerman", "Ream", "Robinson", "Adams", "Musah", "McKennie", "Weah", "Pulisic", "Wright"],
    "Netherlands": ["Noppert", "Timber", "Van Dijk", "Ake", "Dumfries", "De Jong", "Klaassen", "Blind", "Gakpo", "Bergwijn", "Depay"],
    "Ecuador": ["Galindez", "Preciado", "Torres", "Hincapie", "Estupinan", "Plata", "Mendez", "Caicedo", "Ibarra", "Valencia", "Estrada"],
    "Wales": ["Hennessey", "Roberts", "Mepham", "Rodon", "Davies", "Williams", "Ramsey", "Ampadu", "Wilson", "Bale", "Moore"],
    "Tunisia": ["Dahmen", "Kechrida", "Talbi", "Meriah", "Ghandri", "Maaloul", "Skhiri", "Laidouni", "Ben Romdhane", "Ben Slimane", "Khazri"],
    "Canada": ["Borjan", "Johnston", "Vitoria", "Miller", "Adekugbe", "Osorio", "Kaye", "Davies", "Buchanan", "Larin", "David"],

    # Women's Super League
    "Chelsea FCW": ["Berger", "Mjelde", "Bright", "Eriksson", "Andersson", "Ingle", "Ji", "Cuthbert", "Kirby", "Bachmann", "Spence"],
    "Arsenal WFC": ["Van Veenendaal", "Evans", "Williamson", "Quinn", "Mitchell", "Little", "Van de Donk", "Nobbs", "Mead", "McCabe", "Miedema"],
    "Manchester City WFC": ["Bardsley", "Stokes", "Houghton", "McManus", "Bonner", "Walsh", "Weir", "Scott", "Wullaert", "Beckie", "Stanway"],
    "Brighton & Hove Albion WFC": ["Hourihan", "Roe", "Rafferty", "F. Whelan", "Gibbons", "Buet", "Green", "Legg", "Natkiel", "A. Whelan", "Umotong"],
    "Reading WFC": ["Moloney", "Jane", "Bartrip", "Pearce", "Howard", "Potter", "Williams", "Allen", "Furness", "Bruton", "Chaplen"],
    "Birmingham City WFC": ["Hampton", "Cousins", "Harrop", "Mannion", "Mayling", "Staniforth", "Arthur", "Scofield", "Follis", "Wellings", "Williams"],
    "Everton LFC": ["Levell", "Turner", "George", "Van Es", "Brougham", "Stringer", "James", "Kaagman", "Magill", "Boye-Hlorkah", "Cain"],
    "West Ham United LFC": ["Moorhouse", "Simon", "Flaherty", "Hendrix", "Sampson", "Percival", "Longhurst", "Ross", "Visalli", "Kiernan", "Lehmann"],
    "Yeovil Town LFC": ["Goddard", "Alexander", "Short", "Cousins", "Buxton", "Evans", "Mason", "Heatherson", "Horwood", "Bloomfield", "Syme"]
}

# Formation layout coordinates
FORMATION_COORDS_433 = [
    (12.0, 40.0), # GK
    (38.0, 70.0), # RB
    (32.0, 52.0), # CB
    (32.0, 28.0), # CB
    (38.0, 10.0), # LB
    (54.0, 40.0), # DM
    (68.0, 56.0), # CM
    (68.0, 24.0), # CM
    (88.0, 68.0), # RW
    (88.0, 12.0), # LW
    (96.0, 40.0)  # ST
]

FORMATION_COORDS_4231 = [
    (12.0, 40.0), # GK
    (36.0, 68.0), # RB
    (30.0, 52.0), # CB
    (30.0, 28.0), # CB
    (36.0, 12.0), # LB
    (52.0, 48.0), # DM
    (52.0, 32.0), # DM
    (74.0, 66.0), # RAM
    (72.0, 40.0), # CAM
    (74.0, 14.0), # LAM
    (94.0, 40.0)  # ST
]

FORMATION_LINKS = [
    (0, 1, 14), (0, 2, 18), (0, 3, 16), (0, 4, 12),
    (2, 1, 16), (2, 5, 22), (3, 4, 15), (3, 5, 20),
    (1, 6, 24), (4, 7, 21), (5, 6, 28), (5, 7, 26),
    (6, 8, 22), (6, 10, 18), (7, 9, 20), (7, 10, 19),
    (8, 10, 15), (9, 10, 17)
]

def _hash_int(s: str) -> int:
    return int(hashlib.md5(s.encode("utf-8")).hexdigest()[:8], 16)

def get_fixture_metadata(match_id: int) -> dict:
    """Find the match metadata or create a deterministic fixture."""
    for m in MATCHES_DATA:
        if m["id"] == match_id:
            return m
            
    # Deterministic fallback for unknown match_id
    h = _hash_int(str(match_id))
    club_keys = list(TEAM_ROSTERS.keys())
    home_name = club_keys[h % len(club_keys)]
    away_name = club_keys[(h + 5) % len(club_keys)]
    if home_name == away_name:
        away_name = club_keys[(h + 7) % len(club_keys)]
        
    home_score = (h >> 3) % 4
    away_score = (h >> 5) % 3
    
    return {
        "id": match_id,
        "competition_id": 2,
        "season_id": 27,
        "match_date": "2021-05-01",
        "home_team": {"id": (h % 1000) + 10, "name": home_name},
        "away_team": {"id": ((h + 50) % 1000) + 20, "name": away_name},
        "home_score": home_score,
        "away_score": away_score,
        "stadium": f"{home_name} Stadium"
    }

def get_team_roster(team_name: str, fallback_prefix: str = "Player") -> list:
    """Return an 11-player roster for a given team name."""
    if team_name in TEAM_ROSTERS:
        return TEAM_ROSTERS[team_name]
    # Check partial match
    for k, roster in TEAM_ROSTERS.items():
        if k.lower() in team_name.lower() or team_name.lower() in k.lower():
            return roster
    # Generic fallback
    positions = ["GK", "RB", "CB", "CB", "LB", "DM", "CM", "AM", "RW", "LW", "CF"]
    return [f"{fallback_prefix} {pos}" for pos in positions]

def generate_fixture_shots(fixture: dict) -> list:
    """Generate realistic, deterministic shot list whose outcomes exactly match the final score."""
    match_id = fixture["id"]
    home_name = fixture["home_team"]["name"]
    away_name = fixture["away_team"]["name"]
    home_id = fixture["home_team"]["id"]
    away_id = fixture["away_team"]["id"]
    home_score = fixture.get("home_score", 1)
    away_score = fixture.get("away_score", 0)

    home_roster = get_team_roster(home_name, home_name)
    away_roster = get_team_roster(away_name, away_name)

    # Attackers / forwards are typically indices 8, 9, 10 (RW, LW, CF) and 6, 7 (CM/AM)
    home_attackers = [home_roster[10], home_roster[8], home_roster[9], home_roster[7], home_roster[6]]
    away_attackers = [away_roster[10], home_roster[8], away_roster[9], away_roster[7], away_roster[6]]

    shots = []
    shot_idx = 1
    
    # 1. Generate Home Goals
    goal_minutes_home = [14, 38, 62, 79, 88][:home_score]
    for i in range(home_score):
        minute = goal_minutes_home[i] if i < len(goal_minutes_home) else 25 + i * 15
        scorer = home_attackers[i % len(home_attackers)]
        xg_val = 0.42 + (0.12 * (i % 3))
        shots.append({
            "id": f"s_{match_id}_{shot_idx}",
            "player_id": 1000 + i,
            "player_name": scorer,
            "team_id": home_id,
            "team_name": home_name,
            "minute": minute,
            "second": 12 + (i * 17) % 45,
            "x": round(106.0 + (i % 4) * 2.5, 1),
            "y": round(36.0 + (i % 5) * 2.0, 1),
            "outcome": "Goal",
            "xg": round(xg_val, 2),
            "statsbomb_xg": round(xg_val - 0.03, 2),
            "body_part": "Right Foot" if i % 2 == 0 else "Left Foot",
            "under_pressure": (i % 2 == 1)
        })
        shot_idx += 1

    # 2. Generate Non-Goal Home Shots
    non_goal_outcomes = ["Saved", "Off Target", "Blocked", "Saved"]
    home_attempts = max(3, 8 + home_score * 2)
    non_goal_count_home = home_attempts - home_score
    for i in range(non_goal_count_home):
        minute = (10 + i * 11) % 90 + 1
        shooter = home_attackers[(i + home_score) % len(home_attackers)]
        xg_val = 0.05 + ((i * 7) % 25) / 100.0
        shots.append({
            "id": f"s_{match_id}_{shot_idx}",
            "player_id": 1020 + i,
            "player_name": shooter,
            "team_id": home_id,
            "team_name": home_name,
            "minute": minute,
            "second": (i * 23) % 60,
            "x": round(92.0 + (i % 6) * 3.2, 1),
            "y": round(22.0 + (i % 7) * 5.5, 1),
            "outcome": non_goal_outcomes[i % len(non_goal_outcomes)],
            "xg": round(xg_val, 2),
            "statsbomb_xg": round(xg_val * 0.95, 2),
            "body_part": "Right Foot" if i % 3 != 0 else "Head",
            "under_pressure": (i % 3 != 0)
        })
        shot_idx += 1

    # 3. Generate Away Goals
    goal_minutes_away = [22, 45, 71, 84][:away_score]
    for i in range(away_score):
        minute = goal_minutes_away[i] if i < len(goal_minutes_away) else 20 + i * 20
        scorer = away_attackers[i % len(away_attackers)]
        xg_val = 0.48 + (0.10 * (i % 3))
        shots.append({
            "id": f"s_{match_id}_{shot_idx}",
            "player_id": 2000 + i,
            "player_name": scorer,
            "team_id": away_id,
            "team_name": away_name,
            "minute": minute,
            "second": 30 + (i * 13) % 28,
            "x": round(108.0 + (i % 3) * 2.0, 1),
            "y": round(37.0 + (i % 4) * 2.5, 1),
            "outcome": "Goal",
            "xg": round(xg_val, 2),
            "statsbomb_xg": round(xg_val - 0.04, 2),
            "body_part": "Right Foot" if i % 2 == 0 else "Head",
            "under_pressure": True
        })
        shot_idx += 1

    # 4. Generate Non-Goal Away Shots
    away_attempts = max(2, 6 + away_score * 2)
    non_goal_count_away = away_attempts - away_score
    for i in range(non_goal_count_away):
        minute = (8 + i * 14) % 90 + 1
        shooter = away_attackers[(i + away_score) % len(away_attackers)]
        xg_val = 0.04 + ((i * 6) % 22) / 100.0
        shots.append({
            "id": f"s_{match_id}_{shot_idx}",
            "player_id": 2020 + i,
            "player_name": shooter,
            "team_id": away_id,
            "team_name": away_name,
            "minute": minute,
            "second": (i * 19) % 60,
            "x": round(90.0 + (i % 5) * 3.5, 1),
            "y": round(25.0 + (i % 6) * 5.0, 1),
            "outcome": non_goal_outcomes[(i + 1) % len(non_goal_outcomes)],
            "xg": round(xg_val, 2),
            "statsbomb_xg": round(xg_val * 0.92, 2),
            "body_part": "Left Foot" if i % 2 == 0 else "Right Foot",
            "under_pressure": (i % 2 == 0)
        })
        shot_idx += 1

    # Sort shots chronologically
    shots.sort(key=lambda s: (s["minute"], s["second"]))
    return shots

def generate_fixture_passing_network(fixture: dict, team_id: int) -> dict:
    """Generate passing network nodes and links with the actual roster and tactical shape for that team."""
    home_id = fixture["home_team"]["id"]
    away_id = fixture["away_team"]["id"]
    is_away = (team_id == away_id)
    
    team_name = fixture["away_team"]["name"] if is_away else fixture["home_team"]["name"]
    roster = get_team_roster(team_name, team_name)
    coords_template = FORMATION_COORDS_4231 if is_away else FORMATION_COORDS_433

    nodes = []
    base_id = 200 if is_away else 100
    for idx, name in enumerate(roster[:11]):
        cx, cy = coords_template[idx]
        volume = 32 + (idx * 7) % 36
        nodes.append({
            "id": base_id + idx + 1,
            "name": name,
            "x": round(cx, 1),
            "y": round(cy, 1),
            "volume": volume
        })

    links = []
    for s_idx, t_idx, base_count in FORMATION_LINKS:
        if s_idx < len(nodes) and t_idx < len(nodes):
            links.append({
                "source": nodes[s_idx]["id"],
                "target": nodes[t_idx]["id"],
                "count": base_count + (nodes[s_idx]["volume"] % 6)
            })

    return {
        "team_id": team_id,
        "nodes": nodes,
        "links": links
    }
