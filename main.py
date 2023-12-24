import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from config import *
from parser import Parser
from database import Database

bot = telebot.TeleBot(TOKEN)

database = Database()

urls = {
    "civil code": "https://i.factor.ua/ukr/law-54",
    "criminal code": "https://i.factor.ua/law-455/",
    "family code": "https://i.factor.ua/law-470/",
    "budget code": "https://i.factor.ua/ukr/law-52/",
    "tax code": "https://i.factor.ua/ukr/law-24/",
    "administrative judge code": "https://i.factor.ua/ukr/law-345/"
}

civil_code_parser = Parser(urls["civil code"])
criminal_code_parser = Parser(urls["criminal code"])
family_code_parser = Parser(urls["family code"])
budget_code_parser = Parser(urls["budget code"])
tax_code_parser = Parser(urls["tax code"])
administrative_judge_code_parser = Parser(urls["administrative judge code"])

table_name = "user_current_links"

database.create_table(table_name)

def create_markup():
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton("Civil code"), KeyboardButton("Criminal code"),
               KeyboardButton("Family code"), KeyboardButton("Budget code"),
               KeyboardButton("Tax code"), KeyboardButton("Administrative judge code"))
    markup.resize_keyboard = True
    markup.rows = 2
    return markup


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    markup = create_markup()
    bot.send_message(message.chat.id,
                     "Hello! \nI know all of ukrainian laws. You can find here every article you want. \nChoose a code",
                     reply_markup=markup)


parser = None
@bot.message_handler()
def code(message):
    global current_link, parser
    match message.text:
        case "Civil code":
            parser = civil_code_parser
            create_bot_code_message(message, parser, "first_or_final_part_of_civ_cod", "civil")

        case "Criminal code":
            parser = criminal_code_parser
            create_bot_code_message(message, parser, "first_or_final_part_of_crim_cod", "criminal")

        case "Family code":
            parser = family_code_parser
            create_bot_code_message(message, parser, "first_or_final_part_of_fam_cod", "family")

        case "Budget code":
            parser = budget_code_parser
            create_bot_code_message(message, parser, "first_or_final_part_of_bud_cod", "budget")

        case "Tax code":
            parser = tax_code_parser
            create_bot_code_message(message, parser, "first_or_final_part_of_tx_cod", "tax")

        case "Administrative judge code":
            parser = administrative_judge_code_parser
            create_bot_code_message(message, parser, "first_or_final_part_of_admj_cod", "administrative_judge")

    if message.text.isdigit():
        try:
            print(message.text)
            condition = f"user_name = '{message.from_user.username}'"
            content = send_article_content(parser, int(message.text), "https://i.factor.ua" +
                                           database.select_data(table_name, "current_link", condition)[0][0])
            text = write_bot_text(content)
            bot.send_message(message.chat.id, text)
        except TypeError:
            bot.send_message(message.chat.id, "Choose a chapter!")

current_link = ""


@bot.callback_query_handler(func=lambda message: True)
def callback(call):
    global current_link
    parsers = {
        "civil": civil_code_parser,
        "criminal": criminal_code_parser,
        "family": family_code_parser,
        "budget": budget_code_parser,
        "tax": tax_code_parser,
        "administrative_judge": administrative_judge_code_parser
    }

    if "civil" in call.data or "criminal" in call.data or "family" in call.data or "budget" in call.data \
            or "tax" in call.data or "administrative_judge" in call.data:
        parser = parsers[call.data.split(" ")[0]]
        link = get_current_link(parser, call.data)
        insert_current_link_in_database(link, call)
        send_article_listener(parser, call)
    else:
        parser = civil_code_parser
        if "civ_cod" in call.data:
            link = get_current_link(parser, call.data)
            insert_current_link_in_database(link, call)
            send_introduction_or_conclusion(parser, call)

        parser = criminal_code_parser
        if "crim_cod" in call.data:
            link = get_current_link(parser, call.data)
            insert_current_link_in_database(link, call)
            send_introduction_or_conclusion(parser, call)

        parser = family_code_parser
        if "fam_cod" in call.data:
            link = get_current_link(parser, call.data)
            insert_current_link_in_database(link, call)
            send_introduction_or_conclusion(parser, call)

        parser = budget_code_parser
        if "bud_cod" in call.data:
            link = get_current_link(parser, call.data)
            insert_current_link_in_database(link, call)
            send_introduction_or_conclusion(parser, call)

        parser = tax_code_parser
        if "tx_cod" in call.data:
            link = get_current_link(parser, call.data)
            insert_current_link_in_database(link, call)
            send_introduction_or_conclusion(parser, call)

        parser = administrative_judge_code_parser
        if "admj_cod" in call.data:
            link = get_current_link(parser, call.data)
            insert_current_link_in_database(link, call)
            send_introduction_or_conclusion(parser, call)

def send_article_content(parser: Parser, article_number: int, link: str):
    return parser.get_article_content(article_number, link)


def write_bot_text(content):
    text = ""
    for i in content:
        text += i + "\n"
    return text


def create_bot_code_message(message, parser: Parser, conclusion_id: str, code_id: str):
    markup = InlineKeyboardMarkup()
    titles = parser.get_chapters_titles()
    button_names = titles["texts"]
    not_articles = [button_names[0], button_names[-1]]

    data = f"{conclusion_id}: 0"
    markup.add(InlineKeyboardButton(not_articles[0], callback_data=data))

    for name_index, name in enumerate(button_names[1:-1]):
        data = f"{code_id} {name_index + 1}"
        markup.add(InlineKeyboardButton(name, callback_data=data))

    data = f"{conclusion_id}: -1"
    markup.add(InlineKeyboardButton(not_articles[1], callback_data=data))

    bot.send_message(message.chat.id, "Choose the chapter you want", reply_markup=markup)


def get_current_link(parser: Parser, data: str) -> str:
    link_index = int(data.split(" ")[1])
    titles = parser.get_chapters_titles()
    print(len(titles["hrefs"]))
    link = titles["hrefs"][link_index]
    return link


def insert_current_link_in_database(link, call):
    global table_name
    username = call.from_user.username
    if get_current_link_from_database(username) == 0:
        database.insert_data(table_name, ["user_name", "current_link"],
                             [call.from_user.username, link])
    else:
        database.update_data(table_name, "current_link", link, condition=f"user_name = '{call.from_user.username}'")


def send_article_listener(parser: Parser, call):
    link_index = int(call.data.split(" ")[1])
    titles = parser.get_chapters_titles()
    bot.send_message(call.message.chat.id, f"You've chosen {titles['texts'][link_index]}. Send article number")


def send_introduction_or_conclusion(parser: Parser, call):
    link = get_current_link_from_database(call.from_user.username)
    not_formatted_text = parser.get_content_from_inclusion_and_conclusion(
        "https://i.factor.ua" + link)
    formatted_text = write_bot_text(not_formatted_text)
    formatted_texts = []
    if len(formatted_text) > 4096:
        for x in range(0, len(formatted_text), 4096):
            formatted_texts.append(formatted_text[x:x+4096])
        [bot.send_message(call.message.chat.id, text) for text in formatted_texts]
    else:
        bot.send_message(call.message.chat.id, formatted_text)


def get_current_link_from_database(username: str):
    current_link =  database.select_data("user_current_links", "current_link", f"user_name = '{username}'")[0][0]
    return current_link

bot.infinity_polling()
