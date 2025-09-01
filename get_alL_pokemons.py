import time
from requests_html import HTMLSession
URL_INFO = "https://pokemondb.net/pokedex/all"

URL_SPRITES_GEN_5 = ""
NUM_POKEMONS = 5
RETRYING_MESSAGE = "Reintentando..."
TIME_SLEEP = 1

POKEMON_INFO = {
    "name": "",
    "pokemon_type": [],
    "HP": 0,
    "attack": 0,
    "defense": 0,
    "sp_attack": 0,
    "sp_defense": 0,
    "speed": 0,
}

POKEMON_SPRITES = {
    "sprites": {
        "front": "",
        "back": "",
        "shiny_front": "",
        "shiny_back": ""
    }
}

POKEMON_MOVES = {
    "MoveName": {
        "lvl": 0,
        "type": "",
        "damage": 0,
        "precision": 0
        
    }
}

def get_session_for_info(session, URL_INFO):
    succes = False
    while succes == False:
        try:
            info_all_pokemons = session.get(URL_INFO)
            return info_all_pokemons
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_session_for_sprites(session, URL_SPRITES_GEN_5):
    succes = False
    while succes == False:
        try:
            sprites_all_pokemons = session.get(URL_SPRITES_GEN_5)
            succes = True
            return sprites_all_pokemons
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_url_attacks(first_pokemon_name_list):
    success = False
    while success == False:
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
    succes = False
    while succes == False:
        try:
            attacks_all_pokemons = []
            URL_MOVES = get_url_attacks(first_pokemon_name_list)
            for url in URL_MOVES:
                print(url)
                response = session.get(url)
                attacks_all_pokemons.append(response)
            return attacks_all_pokemons
        except Exception as e:
            print("Error: {}".format(e))
            print(RETRYING_MESSAGE)
            time.sleep(TIME_SLEEP)

def get_pokemon_info (info_all_pokemons):
    first_pokemon_name_list = []
    row = info_all_pokemons.html.find("tr")
    for pokemon in row[:NUM_POKEMONS]:
        name_place = pokemon.find(".cell-name", first=True)
        if not name_place:
            continue
        # Primer nombre
        first_name = name_place.find("a", first=True)
        # Nombre secundario (ej: "Mega Mewtwo Y")
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

        print(
            f" No: {number} /Name: {pokemon_name} / Types: {types} / HP: {hp} / Attack: {attack} / Defense: {defense} / Sp. Atk: {sp_attack} / Sp. Def: {sp_defense} / Speed: {speed}")

    return first_pokemon_name_list

def get_pokemon_moves(attacks_all_pokemons):
    for pokemon_response in attacks_all_pokemons:
        title = pokemon_response.html.find("h1", first=True)
        print(f"\n=== MOVIMIENTOS DE {title.text.upper()} ===")
        h3_sections = pokemon_response.html.find("h3")
        tables = pokemon_response.html.find("table.data-table")
        seen = set()
        for table in range(min(len(h3_sections), len(tables))):
            section = h3_sections[table]
            table = tables[table]
            if section.text in seen:
                continue
            seen.add(section.text)
            print(f"\n=== SECCION: {section.text.upper()} ===")
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
                print(f" LVL: {move_lvl} /Name: {move_name} / Type: {move_type} / Damage: {move_damage} / Precision: {move_precision}")

    #return move_lvl, move_name, move_type, move_damage, move_precision

def get_table_titles(pokemon_response):
    # Buscar todos los encabezados h2 y h3 que contienen las secciones de movimientos
    sections = pokemon_response.html.find("h2, h3")
    
    print("\n=== SECCIONES DE MOVIMIENTOS ===")
    for section in sections:
        section_text = section.text.strip()
        if section_text:  # Solo mostrar si el texto no está vacío
            # Determinar el nivel de la sección por la etiqueta HTML
            level = "=" if section.tag == "h2" else "-"
            print(f"\n{level * 5} {section_text.upper()} {level * 5}")
    
    return sections  # Devolvemos las secciones encontradas


def main():
    session = HTMLSession()
    info_all_pokemons = get_session_for_info(session, URL_INFO)
    first_pokemon_name_list = get_pokemon_info(info_all_pokemons)
    attacks_all_pokemons = get_session_for_attacks(session, first_pokemon_name_list)
    pokemon_moves = get_pokemon_moves(attacks_all_pokemons)

if __name__ == "__main__":
    main()