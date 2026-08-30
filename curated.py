# -*- coding: utf-8 -*-
"""Events that no open API carries.

Linked Events covers what the city runs and Helsinki Festival publishes its own
programme, but between them they miss whatever a private organiser puts on. On
a Sunday that means Helsinki Design Week's own programme, the summer stages
closing for the year, the neighbourhood flea markets, and the evening gigs --
none of which the city's API carries.

Where only a start time was published, a conventional length is used for the
end: three hours for a market, four for an evening gig, two for a talk. Those
ends are a shape for the timeline, not a promise, and the note says so where it
matters.

Fields: (start, end, name_en, name_fi, venue_query, price, rank, tags, note)
  rank  3 unmissable, 2 strong, 1 good if you are passing, 0 the rest
  tags  'out' outdoors · 'free' · 'soldout' · 'late' · 'k18'
"""

DAY = '2026-08-30'

CURATED = [
 # ---- markets, and the design week that is on its last day ----
 ('09:00','15:00','Aleksis Kivi Street Flea Market','Aleksis Kiven kadun kirppis',
  'Dallapénpuisto','free',1,['out','free'],
  'The Vallila street flea market, in the park by Dallapénpuisto. Free, outdoors, and the '
  'rain is forecast to be at its heaviest right through it.'),
 ('11:00','16:00','Konepaja Block Flea Market','Konepajan korttelikirppis',
  'Konepaja','free',1,['out','free'],
  'The Konepaja block sells its cupboards out onto the old railway yard. Free.'),
 ('11:00','18:00','Design Market','Design Market','Kaapelitehdas','free',3,['free'],
  'The Nordics\' biggest design warehouse sale, and the day Helsinki Design Week opens: '
  'furniture, homeware, fashion and accessories sold in Merikaapelihalli by the people who '
  'made them. Free, indoors, and the last of two days -- which on a wet Sunday makes it the '
  'easiest good decision of the day.'),
 ('11:00','18:00',"Children's Design Week",'Lasten Design Week','Kaapelitehdas','free',1,['free'],
  'Hands-on workshops for children in Turbiinisali, in the same building as the Design '
  'Market and on the same two days.'),
 ('17:00','20:00','Helsinki Indie','Helsinki Indie','Oodi','free',1,['free'],
  'Free programme and a flea market inside the central library.'),

 # ---- music ----
 ('15:00','17:00','Kun Ilta Tummentuu','Kun Ilta Tummentuu','Aino Acktén huvila','',1,[],
  'An afternoon concert in the villa at Tullisaari.'),
 ('15:00','20:00','Kiska Kii Festival','Kiska Kii -festivaali','Käpylän lippakioski','free',1,
  ['out','free'],
  'A small free festival around the Käpylä kiosk. Outdoors, so the forecast matters.'),
 ('15:00','20:00','Storyville Country Festival: closing day',
  'Storyville Country Festival: päätöspäivä','Storyville','',1,[],
  'The country festival plays out its last day at Storyville.'),
 ('19:00','23:00','On The Rocks 25 Years: Yona + Kanerva','On The Rocks 25 vuotta: Yona + Kanerva',
  'On The Rocks','',2,['late'],
  'The club turns twenty-five and puts Yona and Kanerva on for it.'),
 ('19:00','23:00','Rico Ace (UK)','Rico Ace (UK)','Kuudes Linja','',1,['late'],''),
 ('19:00','23:00','Siltanen summer gigs and club','Siltasen kesäkeikat ja klubit',
  'Siltanen','',1,['late'],'The summer series and the club that follows it.'),

 # ---- theatre, opera, film ----
 ('16:00','18:00','Diivat studiossa','Diivat studiossa','Aleksanterin teatteri','49 €',1,[],''),
 ('17:00','20:00','Myrskyluodon Maija','Myrskyluodon Maija','Kivinokan kesäteatteri','44,10 €',1,
  ['out'],'Open-air summer theatre at Kivinokka -- check the sky before you commit to it.'),
 ('15:00','17:00','Torpantie 3','Torpantie 3','Kupla Tapiola','',0,[],''),
 ('14:00','16:00','Poetry afternoon','Runoiltapäivä','Herttoniemen siirtolapuutarha','',0,['out'],
  'Poetry among the allotment huts at Herttoniemi.'),
 ('21:00','23:00','Kesäkino Engel','Kesäkino Engel','Cafe Engel','',1,['out'],
  'Open-air cinema in the courtyard, and by nine the rain has cleared.'),
 ('09:00','23:00','Espoo Ciné International Film Festival','Espoo Ciné','Kino Tapiola','',1,[],
  'The festival runs all day at Kino Tapiola.'),

 # ---- outdoors and sport ----
 ('10:00','15:00','Helsinki Gran Fondo','Helsinki Gran Fondo','Velodromi','',1,['out'],
  'The mass-participation ride starts and finishes at the velodrome.'),
 ('09:00','11:00','ROOTS: Yoga & Sauna','ROOTS: jooga & sauna','Löyly','',0,[],
  'Booking required.'),
 ('11:00','13:00','Sunday Trail by Juoksut','Sunday Trail by Juoksut','Keskuspuisto','free',1,
  ['out','free'],'A free group run into the central park.'),
 ('11:00','12:30','Landscape yoga','Maisemajooga','Vallisaari','',1,['out'],
  'On the island, which means a ferry each way.'),

 # ---- one-offs and oddities ----
 ('11:00','17:00','Futuro House','Futuro-talo','Kaisaniemen kasvitieteellinen puutarha','',1,[],
  'The 1968 plastic flying-saucer house, parked in the botanic garden.'),
 ('12:00','14:00','Aino Ackté theatre walk','Aino Ackté -teatterikävely',
  'Tullisaaren kartanonpuisto','',0,['out'],''),
 ('12:00','17:00','Kallio Computer Museum','Kallion tietokonemuseo','Kallion tietokonemuseo','',1,
  [],'A working computer shop of 1984, kept running. Small, indoors and genuinely odd.'),
 ('10:00','18:00','Lego Jurassic World','Lego Jurassic World','Malmin jäähalli','',0,[],''),
 ('10:00','16:00','David Loy: eco-zen workshop','David Loy: ekozen-työpaja',
  'Kulttuurikeskus Sofia','',0,[],'In English.'),
 ('11:00','15:00','Responsibly together!','Vastuullisesti yhdessä!','Seikkailupuisto Huippu','',0,
  ['out'],''),

 # ---- the weekly jazz that is always there on a Sunday ----
 ('18:30','22:00','Jazzy Jam Sunday','Jazzy Jam Sunday','Harju 8','free',2,['out','free'],
  'The weekly Sunday session on the Harju 8 terrace, where visiting players sit in with the '
  'local regulars. Free, outdoors, and the rain is forecast to have stopped by then.'),
]

# The same notes in the other two languages, keyed by the English title.
NOTES_FI = {
    'Aleksis Kivi Street Flea Market': 'Vallilan katukirppis Dallapénpuistossa. Ilmainen ja ulkona -- ja juuri sen päälle on ennustettu päivän kovimmat sateet.',
    'Konepaja Block Flea Market': 'Konepajan kortteli tyhjentää kaappinsa vanhalle veturitallialueelle. Ilmainen.',
    'Design Market': 'Pohjoismaiden suurin designin varastomyynti ja Helsinki Design Weekin avauspäivä: huonekaluja, astioita, vaatteita ja asusteita Merikaapelihallissa suoraan tekijöiltä. Ilmainen, sisällä, ja kahden päivän jälkimmäinen -- mikä sateisena sunnuntaina tekee tästä päivän helpoimman hyvän päätöksen.',
    "Children's Design Week": 'Lasten työpajoja Turbiinisalissa, samassa rakennuksessa Design Marketin kanssa ja samoina kahtena päivänä.',
    'Helsinki Indie': 'Ilmaisohjelmaa ja kirppis keskustakirjastossa.',
    'Kun Ilta Tummentuu': 'Iltapäiväkonsertti Tullisaaren huvilalla.',
    'Kiska Kii Festival': 'Pieni ilmainen festivaali Käpylän lippakioskin ympärillä. Ulkona, joten ennuste ratkaisee.',
    'Storyville Country Festival: closing day': 'Country-festivaali soittaa päätöspäivänsä Storyvillessä.',
    'On The Rocks 25 Years: Yona + Kanerva': 'Klubi täyttää 25 vuotta ja tuo lavalle Yonan ja Kanervan.',
    'Siltanen summer gigs and club': 'Kesäsarja ja sen jälkeen klubi.',
    'Myrskyluodon Maija': 'Kesäteatteria ulkona Kivinokassa -- katso taivaalle ennen kuin lupaat mitään.',
    'Poetry afternoon': 'Runoutta Herttoniemen siirtolapuutarhan mökkien keskellä.',
    'Kesäkino Engel': 'Ulkoilmaelokuva sisäpihalla, ja yhdeksään mennessä sade on ohi.',
    'Espoo Ciné International Film Festival': 'Festivaali pyörii koko päivän Kino Tapiolassa.',
    'Helsinki Gran Fondo': 'Yleisölenkki lähtee ja päättyy velodromille.',
    'ROOTS: Yoga & Sauna': 'Vaatii ilmoittautumisen.',
    'Sunday Trail by Juoksut': 'Ilmainen porukkalenkki Keskuspuistoon.',
    'Landscape yoga': 'Saarella, eli lautta molempiin suuntiin.',
    'Futuro House': 'Vuoden 1968 muovinen lentävä lautanen, pysäköitynä kasvitieteelliseen puutarhaan.',
    'Kallio Computer Museum': 'Toimiva vuoden 1984 tietokonekauppa, yhä käynnissä. Pieni, sisällä ja aidosti omalaatuinen.',
    'David Loy: eco-zen workshop': 'Englanniksi.',
    'Jazzy Jam Sunday': 'Viikoittainen sunnuntaisessio Harju 8:n terassilla, jossa vierailevat soittajat pääsevät lavalle paikallisten vakiokasvojen kanssa. Ilmainen, ulkona, ja sateen pitäisi olla siihen mennessä ohi.',
}

NOTES_ZH = {
    'Aleksis Kivi Street Flea Market': 'Vallila 的街头跳蚤市场，就在 Dallapénpuisto 公园。免费、露天——而预报里全天最大的雨正好压在这段时间。',
    'Konepaja Block Flea Market': 'Konepaja 街区把家里的柜子搬到旧机车厂空地上卖。免费。',
    'Design Market': '北欧最大的设计品仓库特卖，也是 Helsinki Design Week 的开幕日：家具、家居、服饰与配件，在 Merikaapelihalli 由制作者本人摆摊。免费、室内，为期两天的最后一天——在下雨的周日，这是今天最省心的好选择。',
    "Children's Design Week": 'Turbiinisali 里的儿童手作工作坊，与 Design Market 同一栋楼、同样两天。',
    'Helsinki Indie': '中央图书馆里的免费节目加跳蚤市场。',
    'Kun Ilta Tummentuu': 'Tullisaari 别墅里的下午音乐会。',
    'Kiska Kii Festival': 'Käpylä 报刊亭周边的小型免费音乐节。露天，所以要看天。',
    'Storyville Country Festival: closing day': '乡村音乐节在 Storyville 打完最后一场。',
    'On The Rocks 25 Years: Yona + Kanerva': '俱乐部二十五周年，请来 Yona 和 Kanerva。',
    'Siltanen summer gigs and club': '夏季演出系列，之后接夜场。',
    'Myrskyluodon Maija': 'Kivinokka 的露天夏季剧场——答应去之前先看看天。',
    'Poetry afternoon': '在 Herttoniemi 市民农园的小屋之间读诗。',
    'Kesäkino Engel': '内院里的露天电影，到九点雨已经停了。',
    'Espoo Ciné International Film Festival': '影展在 Kino Tapiola 全天放映。',
    'Helsinki Gran Fondo': '大众骑行赛，从自行车馆出发也在那里结束。',
    'ROOTS: Yoga & Sauna': '需要报名。',
    'Sunday Trail by Juoksut': '免费的中央公园跑团。',
    'Landscape yoga': '在岛上，来回都要坐渡轮。',
    'Futuro House': '1968 年的塑料飞碟屋，停在植物园里。',
    'Kallio Computer Museum': '一间还能开机的 1984 年电脑店。小、室内，而且是真的有意思。',
    'David Loy: eco-zen workshop': '英语进行。',
    'Jazzy Jam Sunday': 'Harju 8 露台上的每周日爵士即兴场，客座乐手与本地常客同台。免费、露天，按预报那时雨已经停了。',
}

# Photographs for events no API carries one for. Instagram is out -- its image
# URLs are signed and expire, and it serves nothing to a logged-out fetch -- so
# these come from Wikimedia Commons, which is freely licensed and stable. The
# credit is shown on the picture, which is what the licence asks for.
PHOTOS = {
}

# One official page per event, checked at build time and dropped if it 404s.
# Anything not here gets no "official listing" button rather than a dead one.
LINKS = {
    'Design Market':'https://helsinkidesignweek.com/events/design-market/',
    'Jazzy Jam Sunday':'https://www.stadissa.fi/tapahtumat/111262/jazzy-jam-sunday',
}

# Linked Events carries no editorial weight -- everything it returns arrives as
# rank 0, and the festival feed as rank 2 -- so the things worth planning a day
# around are named here by a fragment of their title and given a rank. Matching
# is on the folded title, so a fragment in either language will do.
PROMOTE = {
    # the two the day is really built around
    'finland - sweden athletics': 3,
    'ruotsi-ottelu':              3,
    'cloud gate':                 3,
    # strong, and each one anchors a part of the afternoon or evening
    'poppaavali':                 2,
    'kaivopuisto observatory':    2,
    'kaivopuiston tahtitornin':   2,
    'pretty woman':               2,
    'egotrippi':                  2,
    # worth it if you are passing
    'hietsu flea market':         1,
    'hietsun kirpputori':         1,
    'epidermis circus':           1,
    'espan lava':                 1,
    'espa stage':                 1,
    'sampo festival':             1,
    'nukketeatteri sampo':        1,
}
