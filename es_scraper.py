import argparse
import difflib
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


def get_roms_directory(es_settings_dir):
    with open(os.path.join(es_settings_dir, 'es_systems.cfg'), mode="r", encoding="utf-8") as es_settings:
        settings = ElementTree.parse(es_settings)
        for system in settings.findall(".//system"):
            if system.find("fullname").text == "Arcade":
                rom_path = system.find("path").text
                if os.path.isabs(rom_path):
                    return rom_path
                else:
                    # TODO: currently only works if .emulationstation is in ES folder (and not $HOME or %HOMEPATH%)
                    return os.path.normpath(os.path.join(os.path.join(es_settings_dir, os.pardir), rom_path))


def get_roms(rom_path):
    return os.walk(rom_path)


def add_missing_roms_to_xml(games_db, roms):
    xml_updated = False
    for root, dirs, files in roms:
        for rom in files:
            if games_db.get_game_by_rom_name(rom) is None:
                # rom not found in XML
                print('{rom} not found in gamelist.xml!'.format(rom=rom))
                add_to_xml = input("Do you want to add it to your gamelist? (Y/n)")
                if add_to_xml in ('Y', 'y', ''):
                    xml_updated = True
                    games_db.add_game_by_rom_name(rom)
    if xml_updated:
        games_db.save()


def main(command_line_options):
    scraper = KLOVScraper()
    es_settings_dir = "."
    gamelist_xml_path = 'gamelists/mame/gamelist.xml'

    if args.dir:
        es_settings_dir = args.dir
    else:
        es_settings_dir = './.emulationstation'
        while not os.path.exists(os.path.join(es_settings_dir, gamelist_xml_path)):
            es_settings_dir = input("Please provide the path to the .emulationstation directory (leave blank to cancel): ")
            if es_settings_dir == '':
                sys.exit()

    es_settings_dir = os.path.normpath(es_settings_dir)
    fp = os.path.normpath(os.path.join(es_settings_dir, gamelist_xml_path))
    logging.info("Opening " + fp)
    game_list_xml = gamelist_xml_io.GameListXML(fp)

    if args.rom_check:
        rom_path = get_roms_directory(es_settings_dir)
        add_missing_roms_to_xml(game_list_xml, get_roms(rom_path))

    def process_game(title):
        original_game_data = game_list_xml.get_game_info(title)
        # Is a game with this name in the XML?
        if original_game_data is None:
            print("No game named {title} found in gamelist.xml.".format(title=title))
            matches = [t for t in game_list_xml.get_all_game_titles() if title in t]
            if len(matches) == 1:
                title = matches[0]
                print('I suppose you mean "{title}". Continuing.'.format(title=title))
            elif len(matches) > 1:
                print("Did you mean one of these?")
                for idx, matched_title in enumerate(matches):
                    print('{idx}. {matched_title}'.format(idx=idx, matched_title=matched_title))
                title_idx = input("Select game: ")
                title = matches[title_idx]
            elif len(matches) == 0:
                print('No titles resembling "{title}" found in gamelist XML either.'.format(title=title))
                sys.exit()

        original_game_data = game_list_xml.get_game_info(title)

        logging.info('Scraping information for %(game)s' % {'game': title})
        search_results = scraper.get_links_to_game_page(title)
        if len(search_results) > 1:
            print("Found {results} results for '{title}'.".format(results=len(search_results), title=title))
            for idx, result in enumerate(search_results):
                print('{counter}. {title}'.format(counter=int(idx)+1, title=result['title']))
            selection = input("Select game to look up: ")
            game_url = search_results[int(selection)-1]['url']
        elif len(search_results) == 1:
            game_url = search_results[0]['url']
        elif not search_results:
            print("Can't find game page for '%(game)s'..." % {'game': title})
            game_url = '/game_detail.php?game_id=' + input("Enter URL (leave blank to skip): %(base_url)s/game_detail.php?game_id=" % {'base_url': scraper.BASE_URL})
            if not game_url:
                sys.exit()

        scraped_game_data = scraper.scrape_game_info(game_url)

        if len(scraped_game_data['image']) > 1:
            # Select image
            scraped_game_data['image'] = select_image(scraper.base_url, scraped_game_data['image'])

        # Show diff
        game_list_xml.show_diff(original_game_data, scraped_game_data)

        # Save?
        save = input("Do you want to save the updated information (Y/n)? ")
        if save in ("Y", "y", ""):
            # Download image
            image_filename = scraped_game_data['image'].split('/')[-1]
            r = requests.get(scraper.base_url + scraped_game_data['image'])
            image = Image.open(BytesIO(r.content))
            image_fp = os.path.join(es_settings_dir, 'downloaded_images/mame/' + image_filename)
            logging.info("Saving screenshot to {fp}".format(fp=image_fp))
            image.save(image_fp)
            scraped_game_data['image'] = '~/.emulationstation/downloaded_images/mame/' + image_filename
            game_list_xml.save(scraped_game_data)

    if not args.game:
        # Scrape all games
        for title in game_list_xml.get_all_game_titles():
            process_game(title)
    else:
        # Scrape for a specific game only
        process_game(args.game)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)    # TODO: settable via commmand line
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='.emulationstation directory path')
    parser.add_argument('-g', '--game', help='game you want to retrieve information for (put between "" if name contains spaces).')
    parser.add_argument('-r', '--rom-check', action='store_true', help='Check rom directory for missing games.')

    args = parser.parse_args()
    main(args)


