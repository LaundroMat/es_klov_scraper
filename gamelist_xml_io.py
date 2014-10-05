from xml.etree import ElementTree
PATH_TO_FILE = "G:/frontends/Emulation Station/.emulationstation/gamelists/mame/gamelist.xml"

GAME_FIELDS = [
    'name',
    'desc',
    'image',
    'rating',
    'releasedate',
    'developer',
    'publisher',
    'genre',
    'players'
]

REQUIRED_GAME_FIELDS = [
    'name',
    'desc',
    'image'
]


def open_gamelist_xml(path_to_file=PATH_TO_FILE):
    with open(path_to_file, mode="r", encoding="utf-8") as game_list:
        return ElementTree.parse(game_list)


def save_gamelist_xml(tree, path_to_file=PATH_TO_FILE):
    with open(path_to_file, mode="wb") as f:
        print("Writing to file")
        tree.write(f, encoding="utf-8")


def get_games(tree, fields=GAME_FIELDS):
    games = []
    for idx, game_node in enumerate(tree.findall('.//game')):
        game = {'index': idx}
        for field in GAME_FIELDS:
            try:
                game[field] = game_node.find(field).text
            except AttributeError:
                game[field] = None
        games.append(game)
    return games

    #
    # for game_node in tree.findall('.//game'):
    # # check for missing tags
    # missing_fields = [field for field in required_game_fields if field not in [child.tag for child in game_node]]
    # if missing_fields:
    #     game = game_node.find('name').text
    #     print(game + " is missing:")
    #     print(missing_fields)
    #     fill_in_missing_fields = input("Do you want to look for them on KLOV (Y/n)?")
    #     if fill_in_missing_fields not in ["n", "N"]:
    #         game_url = find_link_to_game_page(game)
    #         if game_url:
    #             r = requests.get(base_url+"/"+game_url)
    #
    #             soup = BeautifulSoup(r.content)
    #
    #             game_title = soup.find(attrs={"style": "font-size:32px;text-align:center"})
    #             print("Title:", game_title.string)
    #
    #             cabinet_picture_url = soup.findAll('table')[2].findAll("td")[1].find("img")['src']
    #             print("Cab picture source:", base_url+cabinet_picture_url)
    #
    #             start_desc = soup.findAll('table')[3].h2.next.next
    #             end_desc = start_desc.find_next("h2")
    #
    #             def loop_until_h2(text, first_element):
    #                 if first_element.string is not None:
    #                     text += first_element.string
    #                 if first_element.next == end_desc:
    #                     return text
    #                 else:
    #                     return loop_until_h2(text, first_element.next)
    #
    #             description = loop_until_h2('', start_desc)
    #             print("Description: ")
    #             print(description)
    #
    #             desc_node = ElementTree.SubElement(game_node, 'desc')
    #             desc_node.text = description
    #
    #             # Get screenshot(s)
    #             #col_screenshots = soup.findAll('td', attrs={'valign': 'top'})[-1]
    #             screenshots = soup.findAll("img", alt=re.compile("Title screen image"))
    #             print("Screenshots:")
    #             for s in screenshots:
    #                 print(base_url + s['src'])