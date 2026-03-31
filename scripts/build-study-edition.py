#!/usr/bin/env python3
"""
Build a study edition of the Einbürgerungskurs markdown file.

For each content page (5-56), inserts a study page with:
- Vocabulary tables (nouns, adjectives, verbs) matched from a pre-built dictionary
- Practice questions for the naturalisation interview
- Notes section for the student
"""

import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_FILE = os.path.join(BASE_DIR, "course-material", "einbuergerungskurs-2026.md")
OUTPUT_FILE = os.path.join(BASE_DIR, "course-material", "einbuergerungskurs-2026-study.md")

# Master vocabulary dictionary: (german, english, type)
# type: "n" = noun, "adj" = adjective, "v" = verb
VOCAB = [
    # Geography & Landscape (pages 5-6)
    ("Binnenland", "landlocked country", "n"),
    ("Grosslandschaft", "major landscape", "n"),
    ("Naturraum", "natural region", "n"),
    ("Gesamtfläche", "total area", "n"),
    ("Gebirge", "mountain range", "n"),
    ("Mittelland", "Central Plateau", "n"),
    ("Alpen", "Alps", "n"),
    ("Jura", "Jura", "n"),
    ("Fläche", "area", "n"),
    ("Landwirtschaft", "agriculture", "n"),
    ("Infrastruktur", "infrastructure", "n"),
    ("Bevölkerung", "population", "n"),
    ("Einwohner", "inhabitants", "n"),
    ("Ausländer", "foreigners", "n"),
    ("Agglomeration", "agglomeration", "n"),
    ("Wasserfall", "waterfall", "n"),
    ("Trinkwasser", "drinking water", "n"),
    ("See", "lake", "n"),
    ("Fluss", "river", "n"),
    ("Quelle", "source", "n"),
    ("Klima", "climate", "n"),
    ("Niederschlag", "precipitation", "n"),
    ("Nordwind", "north wind", "n"),
    ("Föhn", "Foehn", "n"),
    ("hügelig", "hilly", "adj"),
    ("fruchtbar", "fertile", "adj"),
    ("gemässigt", "temperate", "adj"),
    ("feucht", "humid", "adj"),
    ("mild", "mild", "adj"),
    ("erstrecken", "to stretch", "v"),
    ("umfassen", "to cover/encompass", "v"),
    ("einnehmen", "to occupy/take up", "v"),
    ("schützen", "to protect", "v"),
    ("leben", "to live", "v"),

    # Languages & Religion (pages 7-8)
    ("Landessprache", "national language", "n"),
    ("Amtssprache", "official language", "n"),
    ("Muttersprache", "mother tongue", "n"),
    ("Sprachgrenze", "language border", "n"),
    ("Röstigraben", "Röstigraben", "n"),
    ("Dialekt", "dialect", "n"),
    ("Religionsfreiheit", "freedom of religion", "n"),
    ("Konfession", "denomination", "n"),
    ("Feiertag", "public holiday", "n"),
    ("Kirchenglocke", "church bell", "n"),
    ("Zugnetz", "railway network", "n"),
    ("Flughafen", "airport", "n"),
    ("Tunnel", "tunnel", "n"),
    ("Ruhetag", "day of rest", "n"),
    ("mehrsprachig", "multilingual", "adj"),
    ("deutschsprachig", "German-speaking", "adj"),
    ("französischsprachig", "French-speaking", "adj"),
    ("katholisch", "Catholic", "adj"),
    ("protestantisch", "Protestant", "adj"),
    ("konfessionslos", "non-denominational", "adj"),
    ("christlich", "Christian", "adj"),
    ("sprechen", "to speak", "v"),
    ("verstehen", "to understand", "v"),
    ("zwingen", "to force", "v"),
    ("beitreten", "to join", "v"),
    ("schlagen", "to strike/ring", "v"),

    # Customs & Culture (pages 9-12)
    ("Brauch", "custom", "n"),
    ("Brauchtum", "customs/traditions", "n"),
    ("Fasnacht", "carnival", "n"),
    ("Sechseläuten", "Sechseläuten", "n"),
    ("Alpaufzug", "Alpine procession", "n"),
    ("Alpabzug", "descent from Alps", "n"),
    ("Winzerfest", "wine harvest festival", "n"),
    ("Weihnachtsmarkt", "Christmas market", "n"),
    ("Sportverein", "sports club", "n"),
    ("Schwingen", "Swiss wrestling", "n"),
    ("Hornussen", "Hornussen", "n"),
    ("Nationalgericht", "national dish", "n"),
    ("Nationalgetränk", "national beverage", "n"),
    ("Käsesorte", "type of cheese", "n"),
    ("Brotsorte", "type of bread", "n"),
    ("Museum", "museum", "n"),
    ("Bauweise", "building style", "n"),
    ("Architektur", "architecture", "n"),
    ("Schriftsteller", "writer", "n"),
    ("Künstler", "artist", "n"),
    ("lokal", "local", "adj"),
    ("beliebt", "popular", "adj"),
    ("bekannt", "well-known", "adj"),
    ("berühmt", "famous", "adj"),
    ("typisch", "typical", "adj"),
    ("historisch", "historical", "adj"),
    ("ländlich", "rural", "adj"),
    ("vertreiben", "to drive away", "v"),
    ("feiern", "to celebrate", "v"),
    ("erfinden", "to invent", "v"),
    ("erhalten", "to receive/preserve", "v"),

    # History (pages 13-14)
    ("Eidgenossenschaft", "Confederacy", "n"),
    ("Bundesbrief", "Federal Charter", "n"),
    ("Willensnation", "nation of will", "n"),
    ("Reformation", "Reformation", "n"),
    ("Religionskrieg", "religious war", "n"),
    ("Souveränität", "sovereignty", "n"),
    ("Republik", "republic", "n"),
    ("Freiheitsrecht", "right to freedom", "n"),
    ("Landesstreik", "general strike", "n"),
    ("Wirtschaftsraum", "economic area", "n"),
    ("Kaufkraft", "purchasing power", "n"),
    ("Erdölkrise", "oil crisis", "n"),
    ("Frauenstimmrecht", "women's suffrage", "n"),
    ("unabhängig", "independent", "adj"),
    ("neutral", "neutral", "adj"),
    ("zentralistisch", "centralist", "adj"),
    ("politisch", "political", "adj"),
    ("gemeinsam", "shared/common", "adj"),
    ("schliessen", "to conclude/form", "v"),
    ("besetzt", "to occupy", "v"),
    ("einführen", "to introduce", "v"),
    ("wachsen", "to grow", "v"),
    ("wandeln", "to transform", "v"),

    # Federalism (pages 15-16)
    ("Föderalismus", "federalism", "n"),
    ("Bundesstaat", "federal state", "n"),
    ("Kanton", "canton", "n"),
    ("Gemeinde", "municipality", "n"),
    ("Bund", "Confederation", "n"),
    ("Teilstaat", "member state", "n"),
    ("Bundesverfassung", "Federal Constitution", "n"),
    ("Verfassung", "constitution", "n"),
    ("Aussenpolitik", "foreign policy", "n"),
    ("Geldpolitik", "monetary policy", "n"),
    ("Finanzausgleich", "fiscal equalisation", "n"),
    ("Autonomie", "autonomy", "n"),
    ("Gemeindeordnung", "municipal regulations", "n"),
    ("Gemeindeversammlung", "municipal assembly", "n"),
    ("Stimmbürger", "eligible voter", "n"),
    ("Feuerwehr", "fire service", "n"),
    ("Abfallentsorgung", "waste disposal", "n"),
    ("Volksschule", "public school", "n"),
    ("Steuer", "tax", "n"),
    ("föderalistisch", "federalist", "adj"),
    ("eigenständig", "independent/autonomous", "adj"),
    ("kantonale", "cantonal", "adj"),
    ("obligatorisch", "compulsory", "adj"),
    ("aufteilen", "to divide/share", "v"),
    ("verankern", "to enshrine", "v"),
    ("übernehmen", "to take on", "v"),
    ("fusionieren", "to merge", "v"),
    ("bestimmen", "to determine", "v"),
    ("widersprechen", "to contradict", "v"),

    # Democracy (pages 17-18)
    ("Demokratie", "democracy", "n"),
    ("Entscheidungsgewalt", "decision-making power", "n"),
    ("Behörde", "authority", "n"),
    ("Gleichberechtigung", "equal rights", "n"),
    ("Diskriminierung", "discrimination", "n"),
    ("Stimmberechtigte", "eligible voters", "n"),
    ("Landsgemeinde", "Landsgemeinde", "n"),
    ("Gewaltenteilung", "separation of powers", "n"),
    ("Legislative", "legislature", "n"),
    ("Exekutive", "executive", "n"),
    ("Judikative", "judiciary", "n"),
    ("Machtmissbrauch", "abuse of power", "n"),
    ("direkt", "direct", "adj"),
    ("indirekt", "indirect", "adj"),
    ("halbdirekt", "semi-direct", "adj"),
    ("gleichberechtigt", "equal", "adj"),
    ("gegenseitig", "mutual", "adj"),
    ("entscheiden", "to decide", "v"),
    ("wählen", "to elect/vote", "v"),
    ("erlassen", "to enact", "v"),
    ("kontrollieren", "to oversee/check", "v"),
    ("abstimmen", "to vote", "v"),

    # Parliament (pages 19-20)
    ("Nationalrat", "National Council", "n"),
    ("Ständerat", "Council of States", "n"),
    ("Bundesversammlung", "Federal Assembly", "n"),
    ("Kammer", "chamber", "n"),
    ("Session", "session", "n"),
    ("Fraktion", "parliamentary group", "n"),
    ("Kommission", "committee", "n"),
    ("Parlamentsmitglied", "member of parliament", "n"),
    ("Gesetzesentwurf", "draft law", "n"),
    ("Motion", "motion", "n"),
    ("Postulat", "postulate", "n"),
    ("Interpellation", "interpellation", "n"),
    ("gleichberechtigt", "equal", "adj"),
    ("ständig", "standing/permanent", "adj"),
    ("getrennt", "separate", "adj"),
    ("verabschieden", "to pass/adopt", "v"),
    ("vorschlagen", "to propose", "v"),
    ("vertreten", "to represent", "v"),
    ("tagen", "to meet/sit", "v"),

    # Federal Council (pages 21-22)
    ("Bundesrat", "Federal Council", "n"),
    ("Konkordanzprinzip", "concordance principle", "n"),
    ("Kollegialitätsprinzip", "collegiality principle", "n"),
    ("Departement", "department", "n"),
    ("Bundeskanzler", "Federal Chancellor", "n"),
    ("Bundeskanzlei", "Federal Chancellery", "n"),
    ("Bundesgericht", "Federal Supreme Court", "n"),
    ("Regierungschef", "head of government", "n"),
    ("Bundesratspräsident", "President of the Confederation", "n"),
    ("Rechtsprechung", "jurisprudence", "n"),
    ("Menschenrechtsverletzung", "human rights violation", "n"),
    ("beratend", "advisory", "adj"),
    ("vereinigt", "united", "adj"),
    ("verbindlich", "binding", "adj"),
    ("umsetzen", "to implement", "v"),
    ("beurteilen", "to assess", "v"),
    ("vermitteln", "to mediate", "v"),
    ("koordinieren", "to coordinate", "v"),

    # Parties (pages 23-25)
    ("Partei", "party", "n"),
    ("Volkspartei", "People's Party", "n"),
    ("Wähleranteil", "voter share", "n"),
    ("Eigenverantwortung", "personal responsibility", "n"),
    ("Bürokratie", "bureaucracy", "n"),
    ("Wettbewerbsfähigkeit", "competitiveness", "n"),
    ("Umweltschutz", "environmental protection", "n"),
    ("Sozialwerk", "social welfare", "n"),
    ("Verband", "association", "n"),
    ("Dachverband", "umbrella organisation", "n"),
    ("Lobbying", "lobbying", "n"),
    ("Gewerkschaft", "trade union", "n"),
    ("Interessengruppe", "interest group", "n"),
    ("konservativ", "conservative", "adj"),
    ("liberal", "liberal", "adj"),
    ("progressiv", "progressive", "adj"),
    ("wirtschaftsliberal", "economically liberal", "adj"),
    ("gesellschaftsliberal", "socially liberal", "adj"),
    ("gründen", "to found", "v"),
    ("fördern", "to promote", "v"),
    ("lancieren", "to launch", "v"),
    ("finanzieren", "to finance", "v"),

    # Laws & Constitution (pages 26-28)
    ("Völkerrecht", "international law", "n"),
    ("Bundesgesetz", "federal law", "n"),
    ("Zivilgesetzbuch", "Civil Code", "n"),
    ("Obligationenrecht", "Code of Obligations", "n"),
    ("Strafgesetzbuch", "Criminal Code", "n"),
    ("Strassenverkehrsgesetz", "Road Traffic Act", "n"),
    ("Verordnung", "ordinance", "n"),
    ("Grundrecht", "fundamental right", "n"),
    ("Menschenrecht", "human right", "n"),
    ("Rechtsgleichheit", "equality before the law", "n"),
    ("Meinungsfreiheit", "freedom of expression", "n"),
    ("Versammlungsfreiheit", "freedom of assembly", "n"),
    ("Todesstrafe", "death penalty", "n"),
    ("Bilaterale Verträge", "bilateral agreements", "n"),
    ("Kinderarbeit", "child labour", "n"),
    ("Niederlassungsfreiheit", "freedom of establishment", "n"),
    ("Bürgerrecht", "citizenship", "n"),
    ("verhältnismässig", "proportionate", "adj"),
    ("verbindlich", "binding", "adj"),
    ("strafbar", "punishable", "adj"),
    ("gleichberechtigt", "equal", "adj"),
    ("regeln", "to regulate", "v"),
    ("beschränken", "to restrict", "v"),
    ("bestrafen", "to punish", "v"),
    ("diskriminieren", "to discriminate", "v"),

    # Voting rights (pages 29-33)
    ("Wahlrecht", "right to vote", "n"),
    ("Stimmrecht", "right to vote (referendums)", "n"),
    ("Majorzwahl", "majority vote", "n"),
    ("Proporzwahl", "proportional vote", "n"),
    ("Absolutes Mehr", "absolute majority", "n"),
    ("Relatives Mehr", "relative majority", "n"),
    ("Volksmehr", "popular majority", "n"),
    ("Ständemehr", "cantonal majority", "n"),
    ("Doppeltes Mehr", "double majority", "n"),
    ("Volksinitiative", "popular initiative", "n"),
    ("Referendum", "referendum", "n"),
    ("Gegenvorschlag", "counter-proposal", "n"),
    ("Petitionsrecht", "right of petition", "n"),
    ("Unterschrift", "signature", "n"),
    ("Abstimmung", "vote/referendum", "n"),
    ("Wahlempfehlung", "voting recommendation", "n"),
    ("Vorlage", "proposal", "n"),
    ("fakultativ", "optional", "adj"),
    ("obligatorisch", "mandatory", "adj"),
    ("dringlich", "urgent", "adj"),
    ("wahlberechtigt", "eligible to vote", "adj"),
    ("sammeln", "to collect", "v"),
    ("erzwingen", "to force", "v"),
    ("akzeptieren", "to accept", "v"),
    ("prüfen", "to review", "v"),

    # Duties (pages 34-35)
    ("Gehorsamspflicht", "duty of obedience", "n"),
    ("Militärdienstpflicht", "military service obligation", "n"),
    ("Zivilschutzpflicht", "civil protection duty", "n"),
    ("Schulpflicht", "compulsory schooling", "n"),
    ("Versicherungspflicht", "compulsory insurance", "n"),
    ("Steuerpflicht", "tax obligation", "n"),
    ("Rekrutenschule", "recruit school", "n"),
    ("Wiederholungskurs", "refresher course", "n"),
    ("Zivildienst", "civilian service", "n"),
    ("Milizarmee", "militia army", "n"),
    ("Mehrwertsteuer", "value-added tax", "n"),
    ("Einkommenssteuer", "income tax", "n"),
    ("Steuerwettbewerb", "tax competition", "n"),
    ("progressiv", "progressive", "adj"),
    ("verbindlich", "binding", "adj"),
    ("indirekt", "indirect", "adj"),
    ("leisten", "to perform/serve", "v"),
    ("erheben", "to levy", "v"),
    ("abziehen", "to deduct", "v"),
    ("befolgen", "to follow/obey", "v"),

    # Insurance (pages 36-39)
    ("Haftpflichtversicherung", "liability insurance", "n"),
    ("Sachversicherung", "property insurance", "n"),
    ("Hausratversicherung", "household insurance", "n"),
    ("Gebäudeversicherung", "building insurance", "n"),
    ("Rechtsschutzversicherung", "legal protection insurance", "n"),
    ("Krankenversicherung", "health insurance", "n"),
    ("Unfallversicherung", "accident insurance", "n"),
    ("Sozialversicherung", "social insurance", "n"),
    ("Altersvorsorge", "old-age provision", "n"),
    ("Pensionskasse", "pension fund", "n"),
    ("Grundversicherung", "basic insurance", "n"),
    ("Zusatzversicherung", "supplementary insurance", "n"),
    ("Franchise", "deductible", "n"),
    ("Selbstbehalt", "co-payment", "n"),
    ("Prämie", "premium", "n"),
    ("Prämienverbilligung", "premium reduction", "n"),
    ("Säule", "pillar", "n"),
    ("Existenzgrundbedarf", "basic subsistence needs", "n"),
    ("Altersrente", "old-age pension", "n"),
    ("Invalidenrente", "disability pension", "n"),
    ("Lebenserwartung", "life expectancy", "n"),
    ("Arbeitslosenversicherung", "unemployment insurance", "n"),
    ("Erwerbsersatz", "income replacement", "n"),
    ("Familienzulage", "family allowance", "n"),
    ("Mutterschaftsurlaub", "maternity leave", "n"),
    ("Vaterschaftsurlaub", "paternity leave", "n"),
    ("empfehlenswert", "recommended", "adj"),
    ("freiwillig", "voluntary", "adj"),
    ("versichern", "to insure", "v"),
    ("beantragen", "to apply for", "v"),
    ("einzahlen", "to pay in/deposit", "v"),
    ("auszahlen", "to pay out", "v"),
    ("decken", "to cover", "v"),

    # Health (pages 40-41)
    ("Gesundheitssystem", "health system", "n"),
    ("Prävention", "prevention", "n"),
    ("Apotheke", "pharmacy", "n"),
    ("Hausarzt", "family doctor", "n"),
    ("Facharzt", "specialist", "n"),
    ("Notaufnahme", "emergency department", "n"),
    ("Spital", "hospital", "n"),
    ("Spitex", "home nursing service", "n"),
    ("Zahnarzt", "dentist", "n"),
    ("Ambulanz", "ambulance", "n"),
    ("Ernährung", "nutrition", "n"),
    ("Impfprogramm", "vaccination programme", "n"),
    ("ambulant", "outpatient", "adj"),
    ("stationär", "inpatient", "adj"),
    ("lebensbedrohlich", "life-threatening", "adj"),
    ("kostenlos", "free of charge", "adj"),
    ("überweisen", "to refer", "v"),
    ("behandeln", "to treat", "v"),

    # Economy (pages 42-44)
    ("Wirtschaft", "economy", "n"),
    ("Wirtschaftssektor", "economic sector", "n"),
    ("Dienstleistungssektor", "service sector", "n"),
    ("Landwirtschaft", "agriculture", "n"),
    ("Industrie", "industry", "n"),
    ("Rohstoffhandel", "commodity trading", "n"),
    ("Pharmaindustrie", "pharmaceutical industry", "n"),
    ("Uhrenindustrie", "watch industry", "n"),
    ("Staatsverschuldung", "government debt", "n"),
    ("Arbeitslosenquote", "unemployment rate", "n"),
    ("Handelspartner", "trading partner", "n"),
    ("Strukturwandel", "structural change", "n"),
    ("Wettbewerbsfähigkeit", "competitiveness", "n"),
    ("Wirtschaftsraum", "economic region", "n"),
    ("Unternehmen", "company", "n"),
    ("Goldraffinierie", "gold refinery", "n"),
    ("innovativ", "innovative", "adj"),
    ("wettbewerbsfähig", "competitive", "adj"),
    ("exportieren", "to export", "v"),
    ("importieren", "to import", "v"),
    ("veredeln", "to refine", "v"),

    # Work (pages 45-46)
    ("Sozialpartnerschaft", "social partnership", "n"),
    ("Gesamtarbeitsvertrag", "collective labour agreement", "n"),
    ("Normalarbeitsvertrag", "standard employment contract", "n"),
    ("Einzelarbeitsvertrag", "individual employment contract", "n"),
    ("Arbeitszeugnis", "work reference", "n"),
    ("Bruttolohn", "gross salary", "n"),
    ("Nettolohn", "net salary", "n"),
    ("Kündigung", "termination", "n"),
    ("Arbeitgeber", "employer", "n"),
    ("Arbeitnehmer", "employee", "n"),
    ("Freiwilligenarbeit", "volunteer work", "n"),
    ("Höchstarbeitszeit", "maximum working time", "n"),
    ("allgemeingültig", "universally binding", "adj"),
    ("unbezahlt", "unpaid", "adj"),
    ("aushandeln", "to negotiate", "v"),
    ("kündigen", "to terminate", "v"),
    ("abziehen", "to deduct", "v"),
    ("melden", "to register", "v"),

    # Education (pages 47-48)
    ("Bildung", "education", "n"),
    ("Schulpflicht", "compulsory schooling", "n"),
    ("Kindergarten", "kindergarten", "n"),
    ("Primarschule", "primary school", "n"),
    ("Sekundarstufe", "secondary level", "n"),
    ("Gymnasium", "grammar school", "n"),
    ("Berufslehre", "vocational apprenticeship", "n"),
    ("Berufsmaturität", "vocational baccalaureate", "n"),
    ("Fachhochschule", "university of applied sciences", "n"),
    ("Universität", "university", "n"),
    ("Hochschule", "university/college", "n"),
    ("Lehrplan", "curriculum", "n"),
    ("Lehrling", "apprentice", "n"),
    ("Weiterbildung", "continuing education", "n"),
    ("Volkshochschule", "adult education centre", "n"),
    ("durchlässig", "permeable", "adj"),
    ("praxisorientiert", "practice-oriented", "adj"),
    ("ausbilden", "to train", "v"),
    ("studieren", "to study", "v"),
    ("einsteigen", "to enter/join", "v"),

    # Canton Zurich (pages 49-56)
    ("Bezirk", "district", "n"),
    ("Kantonsrat", "Cantonal Council", "n"),
    ("Regierungsrat", "Government Council", "n"),
    ("Direktion", "directorate", "n"),
    ("Staatskanzlei", "State Chancellery", "n"),
    ("Bildungsdirektion", "Education Directorate", "n"),
    ("Sicherheitsdirektion", "Security Directorate", "n"),
    ("Baudirektion", "Construction Directorate", "n"),
    ("Gesundheitsdirektion", "Health Directorate", "n"),
    ("Finanzdirektion", "Finance Directorate", "n"),
    ("Volkswirtschaftsdirektion", "Economic Affairs Directorate", "n"),
    ("Raumplanung", "spatial planning", "n"),
    ("Baubewilligung", "building permit", "n"),
    ("Sozialhilfe", "social welfare", "n"),
    ("Strafverfolgung", "criminal prosecution", "n"),
    ("Strafvollzug", "penal system", "n"),
    ("Kulturförderung", "cultural promotion", "n"),
    ("Gleichstellung", "equality", "n"),
    ("Integration", "integration", "n"),
    ("Stadtpräsident", "city president", "n"),
    ("Obergericht", "high court", "n"),
    ("Bezirksgericht", "district court", "n"),
    ("dezentralisiert", "decentralised", "adj"),
    ("bevölkerungsdicht", "densely populated", "adj"),
    ("zahlbar", "affordable", "adj"),
    ("organisieren", "to organise", "v"),
    ("verwalten", "to administer", "v"),
    ("pflegen", "to maintain", "v"),
]

QUESTIONS = {
    5: [
        ("Welche drei Grosslandschaften hat die Schweiz?", "What are the three major landscapes of Switzerland?"),
        ("Wie viel Prozent der Schweizer Fläche nehmen die Alpen ein?", "What percentage of Switzerland's area do the Alps cover?"),
        ("In welcher Grosslandschaft leben die meisten Menschen?", "In which major landscape do most people live?"),
    ],
    6: [
        ("Welcher See ist der grösste in der Schweiz?", "Which lake is the largest in Switzerland?"),
        ("Wie viele Einwohner hat die Schweiz?", "How many inhabitants does Switzerland have?"),
        ("Wie viel Prozent der Bevölkerung sind Ausländer?", "What percentage of the population are foreigners?"),
    ],
    7: [
        ("Welche vier Landessprachen hat die Schweiz?", "What four national languages does Switzerland have?"),
        ("Was ist der längste Eisenbahntunnel der Welt?", "What is the longest railway tunnel in the world?"),
        ("Was bedeutet der Röstigraben?", "What does the Röstigraben mean?"),
    ],
    8: [
        ("Seit wann gilt in der Schweiz Religionsfreiheit?", "Since when has freedom of religion applied in Switzerland?"),
        ("Welche sind die zwei grössten Konfessionen?", "What are the two largest denominations?"),
        ("Was bedeutet Mehrsprachigkeit in den Kantonen?", "What does multilingualism mean in the cantons?"),
    ],
    9: [
        ("Nennen Sie zwei nationale Sportarten der Schweiz.", "Name two national sports of Switzerland."),
        ("Was ist das Sechseläuten?", "What is the Sechseläuten?"),
        ("Was passiert beim Alpaufzug?", "What happens during the Alpaufzug?"),
    ],
    10: [
        ("Was gilt als Schweizer Nationalgericht?", "What is considered the Swiss national dish?"),
        ("Was ist Rivella?", "What is Rivella?"),
        ("Woher kommt das Fondue ursprünglich?", "Where does fondue originally come from?"),
    ],
    11: [
        ("Nennen Sie einen berühmten Schweizer Architekten.", "Name a famous Swiss architect."),
        ("Was ist das Ballenberg?", "What is the Ballenberg?"),
        ("Was ist typisch für die Bauweise im Tessin?", "What is typical for the building style in Ticino?"),
    ],
    12: [
        ("Wer schrieb die Heidi-Romane?", "Who wrote the Heidi novels?"),
        ("Nennen Sie einen berühmten Schweizer Künstler.", "Name a famous Swiss artist."),
        ("Wer gilt als Pionier der modernen Architektur?", "Who is considered a pioneer of modern architecture?"),
    ],
    13: [
        ("Was geschah 1291?", "What happened in 1291?"),
        ("Was ist der Bundesbrief?", "What is the Federal Charter?"),
        ("Warum nennt man die Schweiz eine Willensnation?", "Why is Switzerland called a 'nation of will'?"),
    ],
    14: [
        ("Wann wurde die Bundesverfassung geschrieben?", "When was the Federal Constitution written?"),
        ("Wann erhielten Frauen das Stimmrecht?", "When did women receive the right to vote?"),
        ("Wann trat die Schweiz der UNO bei?", "When did Switzerland join the UN?"),
    ],
    15: [
        ("Was bedeutet Föderalismus?", "What does federalism mean?"),
        ("Auf welchen drei Stufen ist die politische Macht verteilt?", "On which three levels is political power distributed?"),
        ("Welche Kantone zahlen in den Finanzausgleich?", "Which cantons pay into the fiscal equalisation?"),
    ],
    16: [
        ("Was sind typische Aufgaben der Gemeinde?", "What are typical tasks of the municipality?"),
        ("Was ist eine Gemeindeversammlung?", "What is a municipal assembly?"),
        ("Wie wird die Gemeinde finanziert?", "How is the municipality financed?"),
    ],
    17: [
        ("Was ist eine halbdirekte Demokratie?", "What is a semi-direct democracy?"),
        ("Was ist eine Landsgemeinde?", "What is a Landsgemeinde?"),
        ("Wer ist der Souverän in der Schweiz?", "Who is the sovereign in Switzerland?"),
    ],
    18: [
        ("Was bedeutet Gewaltenteilung?", "What does separation of powers mean?"),
        ("Nennen Sie die drei Gewalten.", "Name the three powers."),
        ("Was macht die Legislative?", "What does the legislature do?"),
    ],
    19: [
        ("Aus wie vielen Mitgliedern besteht der Nationalrat?", "How many members does the National Council have?"),
        ("Was ist eine Fraktion?", "What is a parliamentary group?"),
        ("Wie oft finden Sessionen statt?", "How often do sessions take place?"),
    ],
    20: [
        ("Was ist der Unterschied zwischen Nationalrat und Ständerat?", "What is the difference between the National Council and the Council of States?"),
        ("Was ist eine parlamentarische Motion?", "What is a parliamentary motion?"),
        ("Wie viele Sitze hat der Ständerat?", "How many seats does the Council of States have?"),
    ],
    21: [
        ("Aus wie vielen Mitgliedern besteht der Bundesrat?", "How many members does the Federal Council have?"),
        ("Was ist das Konkordanzprinzip?", "What is the concordance principle?"),
        ("Was ist die Zauberformel?", "What is the magic formula?"),
    ],
    22: [
        ("Was ist das Kollegialitätsprinzip?", "What is the collegiality principle?"),
        ("Gibt es in der Schweiz einen Regierungschef?", "Is there a head of government in Switzerland?"),
        ("Wo hat das Bundesgericht seinen Sitz?", "Where is the Federal Supreme Court based?"),
    ],
    23: [
        ("Welche politische Ausrichtung hat die SVP?", "What political orientation does the SVP have?"),
        ("Welche politische Ausrichtung hat die SP?", "What political orientation does the SP have?"),
        ("Was ist der Unterschied zwischen FDP und SP?", "What is the difference between FDP and SP?"),
    ],
    24: [
        ("Welche Parteien sind im Bundesrat vertreten?", "Which parties are represented in the Federal Council?"),
        ("Was sind die Ziele der Grünen Partei?", "What are the goals of the Green Party?"),
        ("Wann wurde die GLP gegründet?", "When was the GLP founded?"),
    ],
    25: [
        ("Was ist ein Verband?", "What is an association?"),
        ("Nennen Sie einen einflussreichen Arbeitgeberverband.", "Name an influential employer association."),
        ("Was machen Verbände durch Lobbying?", "What do associations do through lobbying?"),
    ],
    26: [
        ("Was ist die Bundesverfassung?", "What is the Federal Constitution?"),
        ("Was regelt das ZGB?", "What does the ZGB regulate?"),
        ("Was ist der Unterschied zwischen Gesetz und Verordnung?", "What is the difference between a law and an ordinance?"),
    ],
    27: [
        ("Was sind die Bilateralen Verträge?", "What are the Bilateral Agreements?"),
        ("Nennen Sie drei Grundrechte.", "Name three fundamental rights."),
        ("Was bedeutet Religionsfreiheit?", "What does freedom of religion mean?"),
    ],
    28: [
        ("Welche politischen Rechte haben nur Schweizer Bürger?", "Which political rights do only Swiss citizens have?"),
        ("Was bedeutet Meinungsfreiheit?", "What does freedom of expression mean?"),
        ("Seit wann dürfen gleichgeschlechtliche Paare heiraten?", "Since when can same-sex couples marry?"),
    ],
    29: [
        ("Was ist der Unterschied zwischen aktivem und passivem Wahlrecht?", "What is the difference between active and passive voting rights?"),
        ("Was ist eine Majorzwahl?", "What is a majority vote?"),
        ("Was bedeutet absolutes Mehr?", "What does absolute majority mean?"),
    ],
    30: [
        ("Was ist eine Proporzwahl?", "What is a proportional vote?"),
        ("Was ist das Volksmehr?", "What is the popular majority?"),
        ("Was ist das Ständemehr?", "What is the cantonal majority?"),
    ],
    31: [
        ("Was ist das Doppelte Mehr?", "What is the double majority?"),
        ("Wie viele Unterschriften braucht eine Volksinitiative?", "How many signatures does a popular initiative need?"),
        ("In welcher Frist müssen die Unterschriften gesammelt werden?", "Within what timeframe must signatures be collected?"),
    ],
    32: [
        ("Was ist ein Referendum?", "What is a referendum?"),
        ("Was ist der Unterschied zwischen obligatorischem und fakultativem Referendum?", "What is the difference between a mandatory and optional referendum?"),
        ("Wie viele Unterschriften braucht ein fakultatives Referendum?", "How many signatures does an optional referendum need?"),
    ],
    33: [
        ("Was ist das Petitionsrecht?", "What is the right of petition?"),
        ("Wer darf eine Petition einreichen?", "Who may submit a petition?"),
        ("Muss die Behörde auf eine Petition antworten?", "Must the authorities respond to a petition?"),
    ],
    34: [
        ("Wie lange dauert die Militärdienstpflicht?", "How long does military service obligation last?"),
        ("Was ist der Zivildienst?", "What is civilian service?"),
        ("Wie lange dauert die obligatorische Schulpflicht?", "How long does compulsory schooling last?"),
    ],
    35: [
        ("Was sind direkte und indirekte Steuern?", "What are direct and indirect taxes?"),
        ("Was bedeutet progressive Besteuerung?", "What does progressive taxation mean?"),
        ("Was ist der Steuerwettbewerb?", "What is tax competition?"),
    ],
    36: [
        ("Welche Versicherung ist für Motorfahrzeuge obligatorisch?", "Which insurance is compulsory for motor vehicles?"),
        ("Ist die private Haftpflichtversicherung obligatorisch?", "Is private liability insurance compulsory?"),
        ("Was ist eine Gebäudeversicherung?", "What is building insurance?"),
    ],
    37: [
        ("In welche 5 Bereiche sind die Sozialversicherungen eingeteilt?", "Into which 5 areas is social insurance divided?"),
        ("Wie werden die Sozialversicherungen finanziert?", "How is social insurance financed?"),
        ("Was ist die Altersvorsorge?", "What is old-age provision?"),
    ],
    38: [
        ("Was ist das 3-Säulen-Prinzip?", "What is the 3-pillar principle?"),
        ("Was ist die AHV?", "What is the AHV?"),
        ("Ab welchem Alter erhält man die AHV-Rente?", "At what age does one receive the AHV pension?"),
    ],
    39: [
        ("Was ist die zweite Säule?", "What is the second pillar?"),
        ("Was ist die dritte Säule?", "What is the third pillar?"),
        ("Was bedeutet 'Eingliederung vor Rente'?", "What does 'integration before pension' mean?"),
    ],
    40: [
        ("Was ist der Unterschied zwischen BU und NBU?", "What is the difference between occupational and non-occupational accidents?"),
        ("Ist die Krankenversicherung in der Schweiz obligatorisch?", "Is health insurance compulsory in Switzerland?"),
        ("Was ist die Franchise?", "What is the deductible/franchise?"),
    ],
    41: [
        ("Was ist die Spitex?", "What is Spitex?"),
        ("Welche Nummer wählt man bei einem Notfall?", "What number do you call in an emergency?"),
        ("Ist der Zahnarzt in der Grundversicherung?", "Is the dentist included in basic insurance?"),
    ],
    42: [
        ("Was ist das grösste Unternehmen der Schweiz nach Angestellten?", "What is the largest Swiss company by employees?"),
        ("In welchem Wirtschaftssektor arbeiten die meisten Schweizer?", "In which economic sector do most Swiss work?"),
        ("Was sind die 3 Wirtschaftssektoren?", "What are the 3 economic sectors?"),
    ],
    43: [
        ("Wie viel Prozent des Goldes wird in der Schweiz veredelt?", "What percentage of gold is refined in Switzerland?"),
        ("Wie viele Banken gibt es in der Schweiz?", "How many banks are there in Switzerland?"),
        ("Was ist die FINMA?", "What is FINMA?"),
    ],
    44: [
        ("In wie viele Wirtschaftsräume ist die Schweiz eingeteilt?", "Into how many economic regions is Switzerland divided?"),
        ("Wo sind die Löhne am höchsten?", "Where are wages highest?"),
        ("Was ist eine Sozialpartnerschaft?", "What is a social partnership?"),
    ],
    45: [
        ("Was ist ein GAV?", "What is a collective labour agreement (GAV)?"),
        ("Welche Abzüge werden vom Bruttolohn gemacht?", "What deductions are made from gross salary?"),
        ("Was passiert, wenn man arbeitslos wird?", "What happens when you become unemployed?"),
    ],
    46: [
        ("Was ist ein Arbeitszeugnis?", "What is a work reference?"),
        ("Was ist das RAV?", "What is the RAV?"),
        ("Was zählt als Freiwilligenarbeit?", "What counts as volunteer work?"),
    ],
    47: [
        ("Wie lange dauert die obligatorische Schulzeit?", "How long does compulsory schooling last?"),
        ("Was ist eine Berufslehre?", "What is a vocational apprenticeship?"),
        ("Was ist die Berufsmaturität?", "What is the vocational baccalaureate?"),
    ],
    48: [
        ("Was ist die ETH?", "What is the ETH?"),
        ("Wie viele Universitäten hat die Schweiz?", "How many universities does Switzerland have?"),
        ("Was ist das Besondere am Schweizer Bildungssystem?", "What is special about the Swiss education system?"),
    ],
    49: [
        ("An welche Kantone grenzt der Kanton Zürich?", "Which cantons border the Canton of Zurich?"),
        ("Was ist der grösste See im Kanton Zürich?", "What is the largest lake in the Canton of Zurich?"),
        ("Wie heisst der höchste Berg im Kanton Zürich?", "What is the highest mountain in the Canton of Zurich?"),
    ],
    50: [
        ("Wie heisst die Legislative des Kantons Zürich?", "What is the legislature of the Canton of Zurich called?"),
        ("Wie viele Bezirke hat der Kanton Zürich?", "How many districts does the Canton of Zurich have?"),
        ("Wie viele Einwohner hat der Kanton Zürich?", "How many inhabitants does the Canton of Zurich have?"),
    ],
    51: [
        ("Wie viele Direktionen hat der Regierungsrat?", "How many directorates does the Government Council have?"),
        ("Wer leitet die Bildungsdirektion?", "Who heads the Education Directorate?"),
        ("Was macht die Sicherheitsdirektion?", "What does the Security Directorate do?"),
    ],
    52: [
        ("Was macht die Baudirektion?", "What does the Construction Directorate do?"),
        ("Was macht die Finanzdirektion?", "What does the Finance Directorate do?"),
        ("Was macht die Volkswirtschaftsdirektion?", "What does the Economic Affairs Directorate do?"),
    ],
    53: [
        ("Wie viele Gemeinden hat der Kanton Zürich?", "How many municipalities does the Canton of Zurich have?"),
        ("Was hat der Gemeinderat im Kanton Zürich für zwei Bedeutungen?", "What two meanings does Gemeinderat have in the Canton of Zurich?"),
        ("Was sind Aufgaben der Gemeinden?", "What are tasks of the municipalities?"),
    ],
    54: [
        ("Was ist die Gemeindeordnung?", "What is the municipal regulations?"),
        ("Wer wählt den Gemeinderat?", "Who elects the municipal council?"),
        ("Welche Aufgabe hat der Stadtpräsident?", "What is the role of the city president?"),
    ],
    55: [
        ("Was ist die Kunsthalle Zürich?", "What is the Kunsthalle Zurich?"),
        ("Was ist das Zürcher Filmfestival?", "What is the Zurich Film Festival?"),
        ("Welche kulturellen Institutionen kennen Sie in Zürich?", "What cultural institutions do you know in Zurich?"),
    ],
    56: [
        ("Wie ist das Schweizer Bildungssystem aufgebaut?", "How is the Swiss education system structured?"),
        ("Was ist die Sekundarstufe II?", "What is the upper secondary level?"),
        ("Was ist eine Fachhochschule?", "What is a university of applied sciences?"),
    ],
}


def get_german_lines(content):
    """Extract only the German text lines from page content (skip English, headings, images, comments)."""
    german_lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        # Skip English translation lines (start with * but not **)
        if stripped.startswith('*') and not stripped.startswith('**'):
            continue
        # Skip lines starting with *** (italic-wrapped bold English)
        if stripped.startswith('***'):
            continue
        # Skip heading lines
        if stripped.startswith('#'):
            continue
        # Skip image lines
        if stripped.startswith('!['):
            continue
        # Skip HTML comments
        if stripped.startswith('<!--'):
            continue
        # Skip horizontal rules
        if stripped == '---':
            continue
        # Skip blockquote lines (from study pages if re-processing)
        if stripped.startswith('>'):
            continue
        german_lines.append(stripped)
    return ' '.join(german_lines)


def find_matching_vocab(page_content, max_per_type=10):
    """Find vocab words from VOCAB that appear in the page's German text."""
    german_text = get_german_lines(page_content)
    german_text_lower = german_text.lower()

    nouns = []
    adjectives = []
    verbs = []

    # Track already-added German terms to avoid duplicates
    seen = set()

    for de, en, word_type in VOCAB:
        if de in seen:
            continue
        # Case-insensitive substring match
        if de.lower() in german_text_lower:
            seen.add(de)
            if word_type == "n" and len(nouns) < max_per_type:
                nouns.append((de, en))
            elif word_type == "adj" and len(adjectives) < max_per_type:
                adjectives.append((de, en))
            elif word_type == "v" and len(verbs) < max_per_type:
                verbs.append((de, en))

    return nouns, adjectives, verbs


def build_study_page(page_num, page_content):
    """Build a study page section for a given page number."""
    nouns, adjectives, verbs = find_matching_vocab(page_content)
    questions = QUESTIONS.get(page_num, [])

    sections = []

    sections.append("---")
    sections.append("")
    sections.append(f"> ### \U0001f4dd Lernseite / Study Page \u2014 Seite {page_num}")

    # Combined vocabulary table: Nomen | Adjektive | Verben side by side with Notes column
    if nouns or adjectives or verbs:
        sections.append("")
        sections.append("> #### Wortschatz / Vocabulary")
        sections.append("> ")
        sections.append("> | Nomen / Nouns | Adjektive / Adjectives | Verben / Verbs | Notizen / Notes |")
        sections.append("> |---|---|---|---|")

        max_rows = max(len(nouns), len(adjectives), len(verbs))
        for i in range(max_rows):
            n_de = nouns[i][0] if i < len(nouns) else ""
            n_en = nouns[i][1] if i < len(nouns) else ""
            a_de = adjectives[i][0] if i < len(adjectives) else ""
            a_en = adjectives[i][1] if i < len(adjectives) else ""
            v_de = verbs[i][0] if i < len(verbs) else ""
            v_en = verbs[i][1] if i < len(verbs) else ""

            noun_cell = f"**{n_de}** – {n_en}" if n_de else ""
            adj_cell = f"**{a_de}** – {a_en}" if a_de else ""
            verb_cell = f"**{v_de}** – {v_en}" if v_de else ""

            sections.append(f"> | {noun_cell} | {adj_cell} | {verb_cell} | |")

    # Questions
    if questions:
        sections.append("")
        sections.append("> #### M\u00f6gliche Pr\u00fcfungsfragen / Possible Interview Questions")
        sections.append("> ")
        for i, (de, en) in enumerate(questions, 1):
            sections.append(f"> **{i}. {de}**")
            sections.append(f"> *{en}*")
            if i < len(questions):
                sections.append("> ")

    # Notes
    sections.append("")
    sections.append("> #### Notizen / Notes")
    sections.append("> ")
    for i in range(5):
        sections.append("> _______________________________________________")
        if i < 4:
            sections.append("> ")

    sections.append("")
    sections.append("---")

    return '\n'.join(sections)


def add_paragraph_spacing(text):
    """Add extra blank lines between paragraphs for readability.

    Ensures 2 blank lines between a German paragraph and its English translation,
    and 2 blank lines before each new heading.
    Does not add extra spacing inside list items or between consecutive list items.
    """
    lines = text.split('\n')
    result = []

    for i, line in enumerate(lines):
        result.append(line)

        if i < len(lines) - 1:
            current_stripped = line.strip()
            next_stripped = lines[i + 1].strip() if i + 1 < len(lines) else ''

            if current_stripped and not next_stripped:
                # Find the next non-empty line after the blank
                j = i + 2
                while j < len(lines) and not lines[j].strip():
                    j += 1

                if j < len(lines):
                    next_content = lines[j].strip()
                    blank_count = j - i - 1

                    # Add extra blank line before headings (ensure 2 blanks)
                    if next_content.startswith('#') and blank_count < 2:
                        result.append('')

                    # Between German text and English translation (line starting with *)
                    elif (not current_stripped.startswith('-')
                          and not current_stripped.startswith('*')
                          and not current_stripped.startswith('#')
                          and not current_stripped.startswith('!')
                          and not current_stripped.startswith('<!--')
                          and not current_stripped.startswith('---')
                          and next_content.startswith('*')
                          and not next_content.startswith('**')
                          and blank_count < 2):
                        result.append('')

                    # Between English translation block and next German text
                    elif (current_stripped.startswith('*')
                          and not current_stripped.startswith('**')
                          and not current_stripped.startswith('*-')
                          and not next_content.startswith('*')
                          and not next_content.startswith('#')
                          and not next_content.startswith('<!--')
                          and not next_content.startswith('---')
                          and not next_content.startswith('!')
                          and next_content
                          and blank_count < 2):
                        result.append('')

    return '\n'.join(result)


def main():
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by page markers, keeping the markers
    # <!-- Page X --> marks the END of page X's content.
    # So content for page X is in parts[idx-1] (the part BEFORE the marker).
    parts = re.split(r'(<!-- Page \d+ -->)', content)

    # Build a mapping: page_num -> content (the part BEFORE the marker)
    page_contents = {}
    for idx, part in enumerate(parts):
        m = re.match(r'<!-- Page (\d+) -->', part.strip())
        if m:
            page_num = int(m.group(1))
            if idx > 0:
                page_contents[page_num] = parts[idx - 1]

    # Build output: reassemble with study pages inserted AFTER each page marker
    output = []

    for idx, part in enumerate(parts):
        m = re.match(r'<!-- Page (\d+) -->', part.strip())
        if m:
            page_num = int(m.group(1))
            output.append(part)

            # Insert study page after the marker for pages 5-56
            # Use the content BEFORE this marker (the actual page content)
            if 5 <= page_num <= 56 and page_num in page_contents:
                study = build_study_page(page_num, page_contents[page_num])
                output.append('\n\n' + study + '\n')
        else:
            # Add paragraph spacing to content
            spaced = add_paragraph_spacing(part)
            output.append(spaced)

    result = ''.join(output)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Study edition written to: {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE)} bytes")


if __name__ == '__main__':
    main()
