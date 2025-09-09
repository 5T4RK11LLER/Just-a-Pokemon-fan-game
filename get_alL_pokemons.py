import time
from requests_html import HTMLSession
import os

URL_INFO = "https://pokemondb.net/pokedex/all"
NUM_POKEMONS = 3
RETRYING_MESSAGE = "Reintentando..."
TIME_SLEEP = 1
FOLDER_SPRITES_NAME = "sprites"

POKEMON_SPRITES = {
        "front": "",
        "back": "",
        "shiny_front": "",
        "shiny_back": ""
}

POKEMON_MOVES = {}

POKEMON_INFO = {
    "name": "",
    "No": 0,
    "pokemon_type": [],
    "HP": 0,
    "attack": 0,
    "defense": 0,
    "sp_attack": 0,
    "sp_defense": 0,
    "speed": 0,
    "moves": POKEMON_MOVES,
    "sprites": POKEMON_SPRITES
}

def get_session_for_info(session, URL_INFO):
    success = False
    while not success:
        try:
            info_all_pokemons = session.get(URL_INFO)
            success = True
            return info_all_pokemons
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_url_sprites(first_pokemon_name_list):
    success = False
    while not success:
        try:
            URL_SPRITES_GEN_5_TEMPLATE = "https://pokemondb.net/sprites/{}"
            URL_SPRITES = []
            for name in first_pokemon_name_list:
                URL_SPRITES_GEN_5 = URL_SPRITES_GEN_5_TEMPLATE.format(name)
                URL_SPRITES.append(URL_SPRITES_GEN_5)
            success = True
            return URL_SPRITES
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_session_for_sprites(session,first_name_pokemon_list):
    success = False
    while not success:
        try:
            sprites_all_pokemon = []
            URL_SPRITES_GEN_5 = get_url_sprites(first_name_pokemon_list)
            for url in URL_SPRITES_GEN_5:
                print(url)
                response = session.get(url)
                sprites_all_pokemon.append(response)
            success = True
            return sprites_all_pokemon
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_url_attacks(first_pokemon_name_list):
    success = False
    while not success:
        try:
            URL_ATTACKS_TEMPLATE = "https://pokemondb.net/pokedex/{}/moves/1"
            URLS_MOVES = []
            for name in first_pokemon_name_list:
                URL_ATTACKS = URL_ATTACKS_TEMPLATE.format(name)
                URLS_MOVES.append(URL_ATTACKS)
            success = True
            return URLS_MOVES
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_session_for_attacks(session, first_pokemon_name_list):
    success = False
    while not success:
        try:
            attacks_all_pokemons = []
            URL_MOVES = get_url_attacks(first_pokemon_name_list)
            for url in URL_MOVES:
                print(url)
                response = session.get(url)
                attacks_all_pokemons.append(response)
            success = True
            return attacks_all_pokemons
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_pokemon_info (info_all_pokemons):
    first_pokemon_name_list = []
    success = False
    while not success:
        try:
            row = info_all_pokemons.html.find("tr")
            for pokemon in row[:NUM_POKEMONS]:
                name_place = pokemon.find(".cell-name", first=True)
                if not name_place:
                    continue

                first_name = name_place.find("a", first=True)
                second_name = name_place.find("small", first=True)
                first_pokemon_name = first_name.text
                first_pokemon_name_list.append(first_pokemon_name)
                pokemon_name = " / ".join([first_name.text, second_name.text]) if second_name else first_name.text

                types_block = pokemon.find(".cell-icon", first=True)
                first_second_type = [type.text for type in types_block.find("a")]
                types = " / ".join(first_second_type)

                stats = pokemon.find(".cell-num")
                number = stats[0].text if len(stats) > 0 else ""
                hp = stats[2].text if len(stats) > 2 else ""
                attack = stats[3].text if len(stats) > 3 else ""
                defense = stats[4].text if len(stats) > 4 else ""
                sp_attack = stats[5].text if len(stats) > 5 else ""
                sp_defense = stats[6].text if len(stats) > 6 else ""
                speed = stats[7].text if len(stats) > 7 else ""

                URL_ATTACKS = get_url_attacks(first_pokemon_name_list)
                all_pokemon_data = save_info_in_dicc_info(stats,first_name, second_name,types,types_block,number,
                      hp, attack, defense, sp_attack, sp_defense, speed)
                #print(f" No: {number} /Name: {pokemon_name} / Types: {types} / HP: {hp} / Attack: {attack} / Defense: {defense} / Sp. Atk: {sp_attack} / Sp. Def: {sp_defense} / Speed: {speed}")
                success = True
            return first_pokemon_name_list,types,types_block,stats, first_name, second_name, number, types, hp, attack, defense, sp_attack, sp_defense, speed
        except Exception as e:
            print("Error:{}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_pokemon_moves(attacks_all_pokemons):
    success = False
    while not success:
        try:
            for pokemon_response in attacks_all_pokemons:
                title = pokemon_response.html.find("h1", first=True)
                #print(f"\n=== MOVIMIENTOS DE {title.text.upper()} ===")
                h3_sections = pokemon_response.html.find("h3")
                tables = pokemon_response.html.find("table.data-table")
                seen = set()
                for table in range(min(len(h3_sections), len(tables))):
                    section = h3_sections[table]
                    table = tables[table]
                    if section.text in seen:
                        continue
                    seen.add(section.text)
                    #print(f"\n=== SECCION: {section.text.upper()} ===")
                    rows = table.find("tr")
                    for moves in rows:
                        move_name_cell = moves.find(".cell-name", first=True)
                        move_type_cell = moves.find(".cell-icon", first=True)
                        if not move_name_cell or not move_type_cell:
                            continue
                        move_name = move_name_cell.text
                        move_type = move_type_cell.text

                        stats = moves.find(".cell-num")
                        if len(stats) >= 3:
                            move_lvl = stats[0].text if stats[0].text else "--"
                            move_damage = stats[1].text if stats[1].text else "--"
                            move_precision = stats[2].text if stats[2].text else "--"
                        all_pokemon_moves = save_info_in_dicc_moves(move_lvl, move_name, move_type, move_damage, move_precision)
                        #print(f" LVL: {move_lvl} /Name: {move_name} / Type: {move_type} / Damage: {move_damage} / Precision: {move_precision}")
            
            success = True
            return all_pokemon_moves
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_table_titles(pokemon_response):
    # Buscar todos los encabezados h2 y h3 que contienen las secciones de movimientos
    sections = pokemon_response.html.find("h2, h3")
    
    print("\n=== SECCIONES DE MOVIMIENTOS ===")
    for section in sections:
        section_text = section.text.strip()
        if section_text:  # Solo mostrar si el texto no está vacío
            # Determinar el nivel de la sección por la etiqueta HTML
            level = "=" if section.tag == "h2" else "-"
            #print(f"\n{level * 5} {section_text.upper()} {level * 5}")
    
    return sections  # Devolvemos las secciones encontradas

def get_pokemon_sprites(sprites_all_pokemon):
    success = False
    while not success:
        url_sprites_pokemon = []
        for pokemon_response in sprites_all_pokemon:
            try:
                resp_scroll_div = pokemon_response.html.find(".resp-scroll")[5]  # Selecciona el sexto div con clase 'resp-scroll'
                if resp_scroll_div:
                    tr_elements = resp_scroll_div.find("tr")
                    if len(tr_elements) > 1:
                        resp_tr = tr_elements[2]  # Tercera fila
                        for td in resp_tr.find("td"):
                            a_elements = td.find("a")
                            for a in a_elements:
                                href_gif_pokemon = a.attrs.get('href', '')
                                #print(href_gif_pokemon)
                                url_sprites_pokemon.append(href_gif_pokemon)
                                success = True
            except Exception as e:
                print("Error: {}".format(e))
                print(RETRYING_MESSAGE)
                time.sleep(TIME_SLEEP)
    return url_sprites_pokemon


def download_sprite(session, url_sprites_pokemon):
    sprite_name = []
    for url in url_sprites_pokemon:
        success = False
        while not success:
            try:
                response = session.get(url)
                if response.status_code == 200:
                    if not os.path.exists(FOLDER_SPRITES_NAME):
                        os.makedirs(FOLDER_SPRITES_NAME)
                        #print("Carpeta creada: {}".format(FOLDER_SPRITES_NAME))
                    """
                    else:
                        print("Carpeta existente: {}".format(FOLDER_SPRITES_NAME))
                    """
                    parts = url.split("/")
                    file_name = "{}_{}".format(parts[-2], parts[-1])
                    file_path = os.path.join(FOLDER_SPRITES_NAME, file_name)

                    if os.path.exists(file_path):
                        #print("Ya existe, se omite: {}".format(file_name))
                        sprite_name.append(file_name) 
                        success = True  # ya no necesitamos reintentar
                        continue

                    with open(file_path, "wb") as file:
                        file.write(response.content)
                        sprite_name.append(file_name)
                    #print("Sprite descargado: {}".format(file_name))
                    success = True
            except Exception as e:
                print("Error: {}".format(e))
                print(RETRYING_MESSAGE)
                time.sleep(TIME_SLEEP)
    if sprite_name:
        save_info_in_dicc_sprites(sprite_name)
    return sprite_name

def save_info_in_dicc_info(stats,first_name, second_name,types,types_block,number,
                      hp, attack, defense, sp_attack, sp_defense, speed,
                      ):
    all_pokemon_data = []
    POKEMON_INFO["No"] = number
    POKEMON_INFO["name"] = first_name.text
    if second_name:
        POKEMON_INFO["name"] += f" {second_name.text}"
    POKEMON_INFO["pokemon_type"] = [type.text for type in types_block.find("a")]
    if len(stats) > 6:
        POKEMON_INFO["HP"] = int(stats[2].text) if stats[2].text.isdigit() else 0
        POKEMON_INFO["attack"] = int(stats[3].text) if stats[3].text.isdigit() else 0
        POKEMON_INFO["defense"] = int(stats[4].text) if stats[4].text.isdigit() else 0
        POKEMON_INFO["sp_attack"] = int(stats[5].text) if stats[5].text.isdigit() else 0
        POKEMON_INFO["sp_defense"] = int(stats[6].text) if stats[6].text.isdigit() else 0
        POKEMON_INFO["speed"] = int(stats[7].text) if len(stats) > 7 and stats[7].text.isdigit() else 0
    all_pokemon_data.append(POKEMON_INFO)
    all_pokemon_data.append(POKEMON_MOVES)
    #print(POKEMON_INFO)
    return all_pokemon_data

def save_info_in_dicc_moves(move_lvl, move_name, move_type, move_damage, move_precision):
    all_pokemon_moves = []
    POKEMON_MOVES[move_name] = {
        "lvl": int(move_lvl) if move_lvl.isdigit() else 0,
        "type": move_type,
        "damage": int(move_damage) if move_damage.isdigit() else 0,
        "precision": int(move_precision) if move_precision.isdigit() else 0
    }
    POKEMON_INFO["moves"] = POKEMON_MOVES.copy()
    all_pokemon_moves.append(POKEMON_MOVES)
    #print(POKEMON_MOVES)
    return all_pokemon_moves


def save_info_in_dicc_sprites(sprite_name):
    for file_name in sprite_name:
        file_path = os.path.join(FOLDER_SPRITES_NAME, file_name)
        if "back" in file_name and "shiny" in file_name:
            POKEMON_INFO["sprites"]["shiny_back"] = file_path
        elif "back" in file_name:
            POKEMON_INFO["sprites"]["back"] = file_path
        elif "shiny" in file_name:
            POKEMON_INFO["sprites"]["shiny_front"] = file_path
        else:
            POKEMON_INFO["sprites"]["front"] = file_path

def main():
    session = HTMLSession()
    info_all_pokemons = get_session_for_info(session, URL_INFO) 
    first_pokemon_name_list,*_ = get_pokemon_info(info_all_pokemons) #*_ to ignore the other returned values
    
    attacks_all_pokemons = get_session_for_attacks(session, first_pokemon_name_list)
    pokemon_moves = get_pokemon_moves(attacks_all_pokemons)
    POKEMON_INFO["moves"] = POKEMON_MOVES.copy()

    sprites_all_pokemon = get_session_for_sprites(session,first_pokemon_name_list)
    url_sprites_pokemon = get_pokemon_sprites(sprites_all_pokemon)
    sprite_name = download_sprite(session,url_sprites_pokemon)

    print("\n" + "="*50)
    print("POKEMON_INFO FINAL:")
    print("="*50)
    print(POKEMON_INFO)
    print("\n" + "="*50)

if __name__ == "__main__":
    main()