import argparse
import getopt
import logging
import os
from tkinter import *
from tkinter import font
from tkinter import ttk
from io import BytesIO
import requests
import gamelist_xml_io
from PIL import Image, ImageTk
from scrapers import KLOVScraper
from xml.etree import ElementTree

ES_BASE_DIR = "G:/frontends/Emulation Station/"


class GameInformationPane(object):
    def __init__(self, frame):
        self.name = StringVar()
        self.rating = StringVar()
        self.developer = StringVar()
        self.publisher = StringVar()
        self.genre = StringVar()
        self.players = StringVar()
        self.description = StringVar()
        self.photo = None   # see http://stackoverflow.com/questions/17760871/python-tkinter-photoimage

        self.scraper = KLOVScraper()

        # Create widgets
        self.snapshot = ttk.Label(frame, image=self.photo)
        self.snapshot.grid(row=1, column=0, rowspan=20, sticky=N+W)
        ttk.Label(frame, textvariable=self.name, font=appTitleFont).grid(row=1, column=1, sticky=N+W)
        Button(frame, text="Scrape", command=self.get_game_info).grid(row=2, column=1, sticky=N+W)
        ttk.Label(frame, textvariable=self.description, wraplength=600, justify=LEFT, anchor=W).grid(row=3, column=1, sticky=N+W)

        game_properties_frame = ttk.Frame(frame)
        game_properties_frame.grid(row=4, column=1, sticky=N+W)

        ttk.Label(game_properties_frame, text="Rating:").grid(row=0, column=0)
        ttk.Label(game_properties_frame, textvariable=self.rating).grid(row=0, column=1)

        ttk.Label(game_properties_frame, text="Developer:").grid(row=1, column=0)
        ttk.Label(game_properties_frame, textvariable=self.developer).grid(row=1, column=1)

        ttk.Label(game_properties_frame, text="Publisher:").grid(row=2, column=0)
        ttk.Label(game_properties_frame, textvariable=self.publisher).grid(row=2, column=1)

        ttk.Label(game_properties_frame, text="Genre:").grid(row=3, column=0)
        ttk.Label(game_properties_frame, textvariable=self.genre).grid(row=3, column=1)

        ttk.Label(game_properties_frame, text="Players:").grid(row=4, column=0, sticky=N+W)
        ttk.Label(game_properties_frame, textvariable=self.players).grid(row=4, column=1)

        for _child in game_info_frame.winfo_children():
            _child.grid_configure(sticky=N+W)   # Doesn't seem to do anything.

        # Set data to first game in tree list
        game_list_tree.selection_set(game_list_tree.get_children()[0])

    def update_to_selected_game(self, event):
        index = game_list_tree.item(game_list_tree.selection()[0], 'text')
        self.name.set(games[index]['name'])
        self.rating.set(games[index]['rating'])
        self.developer.set(games[index]['developer'])
        self.publisher.set(games[index]['publisher'])
        self.genre.set(games[index]['genre'])
        self.players.set(games[index]['players'])
        self.description.set(games[index]['desc'])

        if not games[index]['image'] is None:
            file_path = games[index]['image'].replace("~/", "")
        else:
            # TODO: show "no screenshot
            pass
        image = Image.open(ES_BASE_DIR + file_path)
        image.thumbnail((256, 256), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(image)
        self.snapshot['image'] = self.photo

    def _select_game(self, links):
        t = Toplevel(root)
        t.transient(root)   # Don't show 2 windows in taskbar
        t.grab_set()    # No mouse/kb events on root anymore

        selection = IntVar()
        ttk.Label(t, text="Select game:").pack()
        for idx, link in enumerate(links):
            Radiobutton(t, indicatoron=0, text=links[idx].string, variable=selection, value=idx, command=t.destroy).pack(anchor=W, fill=X)
        root.wait_window(t)
        return links[selection.get()]['href']

    def _enter_url_manually(self):
        t = Toplevel(root)
        t.transient(root)   # Don't show 2 windows in taskbar
        t.grab_set()    # No mouse/kb events on root anymore

        ttk.Label(t, text="Game not found... Perhaps you know the URL? ").grid(columnspan=2)
        entry_frame = ttk.Frame(t)
        entry_frame.grid(columnspan=2)
        ttk.Label(entry_frame, text=self.scraper.BASE_URL + '/').pack(side=LEFT)

        url = StringVar()
        e = Entry(entry_frame, textvariable=url)
        e.pack(side=LEFT)
        e.focus_set()
        button_frame = ttk.Frame(t)
        button_frame.grid(columnspan=2)
        Button(button_frame, text="Cancel", command=t.destroy).pack(side=LEFT)
        Button(button_frame, text="OK", command=t.destroy).pack(side=LEFT)
        root.wait_window(t)
        return url.get()


    def get_game_info(self):
        index = game_list_tree.item(game_list_tree.selection()[0], 'text')
        game_title = games[index]['name']
        links = self.scraper.get_links_to_game_page(game_title)
        if len(links) > 1:
            game_url = self._select_game(links)
        elif links == []:
            game_url = self._enter_url_manually()
        else:
            game_url = links[0]['href']

        game_info = self.scraper.scrape_game_info(game_url)
        print(game_info)


def get_games_from_xml():
    tree = gamelist_xml_io.open_gamelist_xml()
    return gamelist_xml_io.get_games(tree)


def gui():
    root = Tk()


    root.title("ES scraper")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.resizable(True, True)

    appTitleFont = font.Font(size=16, weight="bold")

    treeview_frame = ttk.Frame(root)
    treeview_frame.grid(row=0, column=0)

    game_info_frame = ttk.Frame(root)
    game_info_frame.grid(row=1, column=0)

    # Build game list tree
    game_list_tree = ttk.Treeview(treeview_frame, columns=tuple(gamelist_xml_io.REQUIRED_GAME_FIELDS))
    game_list_tree['show'] = 'headings'
    for heading in gamelist_xml_io.REQUIRED_GAME_FIELDS:
        game_list_tree.heading(heading, text=heading)

    games = get_games_from_xml()

    for g in games:
        game_list_tree.insert('', 'end', text=g['index'], values=tuple(g[key] for key in gamelist_xml_io.REQUIRED_GAME_FIELDS if key in g.keys()))

    game_info_window = GameInformationPane(game_info_frame)

    game_list_tree.bind("<<TreeviewSelect>>", game_info_window.update_to_selected_game)
    game_list_tree.pack(fill=BOTH, expand=1)

    for child in root.winfo_children(): child.grid_configure(padx=5, pady=5, sticky=N+W)

    root.mainloop()


def select_image(base_url, images):
    root = Tk()
    root.title("Select image:")
    frame = ttk.Frame(root)
    frame.pack()

    photos = []
    selection = IntVar()

    for idx, img in enumerate(images):
        r = requests.get(base_url + img)
        image = Image.open(BytesIO(r.content))
        image.thumbnail((256, 256), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        photos.append(photo)
    # for photo in photos:
        # snapshot = ttk.Label(frame, image=photo)
        snapshot = Radiobutton(frame, indicatoron=0, image=photo, variable=selection, value=idx, command=root.destroy)
        snapshot.pack(side=LEFT)

    root.mainloop()
    return images[selection.get()]


def main(command_line_options):
    scraper = KLOVScraper()
    es_settings_dir = "."
    gamelist_xml_path = 'gamelists/mame/gamelist.xml'

    if args.dir:
        es_settings_dir = args.dir
    else:
        es_settings_dir = '.\.emulationstation'
        while not os.path.exists(os.path.join(es_settings_dir, gamelist_xml_path)):
            es_settings_dir = input("Please provide the path to the .emulationstation directory (leave blank to cancel): ")
            if es_settings_dir == '':
                sys.exit()

    fp = os.path.join(es_settings_dir, gamelist_xml_path)
    logging.info("Opening " + fp)
    games_db = gamelist_xml_io.GameListXML(fp)

    def process_game(game):
        logging.info('Scraping information for %(game)s' % {'game': game})
        search_results = scraper.get_links_to_game_page(game)
        if len(search_results) > 1:
            print("Found {results} results for '{game}'.".format(results=len(search_results), game=game))
            print(search_results)
            for idx, result in enumerate(search_results):
                print('{counter}. {title}'.format(counter=int(idx)+1, title=result['title']))
            selection = input("Select game to look up: ")
            game_url = search_results[int(selection)-1]['url']
        elif len(search_results) == 1:
            game_url = search_results[0]['url']
        elif not search_results:
            print("Can't find game page for '%(game)s'..." % {'game': game})
            game_url = '/game_detail.php?game_id=' + input("Enter URL (leave blank to skip): %(base_url)s/game_detail.php?game_id=" % {'base_url': scraper.BASE_URL})
            if not game_url:
                sys.exit()

        game_info = scraper.scrape_game_info(game_url)

        if len(game_info['image']) > 1:
            # Select image
            game_info['image'] = select_image(scraper.base_url, game_info['image'])

        # Show diff
        games_db.show_diff(game_info)

        # Save?
        save = input("Do you want to save the updated information (Y/n)? ")
        if save in ("Y", "y", ""):
            # Download image
            image_filename = game_info['image'].split('/')[-1]
            r = requests.get(scraper.base_url + game_info['image'])
            image = Image.open(BytesIO(r.content))
            image_fp = os.path.join(es_settings_dir, 'downloaded_images/mame/' + image_filename)
            logging.info("Saving screenshot to {fp}".format(fp=image_fp))
            image.save(image_fp)
            game_info['image'] = '~/.emulationstation/downloaded_images/mame/' + image_filename
            games_db.save(game_info)
        else:
            sys.exit()

    if not args.game:
        # Scrape all games
        for game in games_db.games:
            process_game(game['name'])
    else:
        # Scrape for a specific game only
        process_game(args.game)


def usage():
    print("Usage:")
    pass    # TODO

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)    # TODO: settable via commmand line
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='.emulationstation directory path')
    parser.add_argument('-g', '--game', help='game you want to retrieve information for (put between "" if name contains spaces).')

    args = parser.parse_args()
    main(args)


