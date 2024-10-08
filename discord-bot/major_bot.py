#!/bin/env python3

"""
Majority Judgment Bar Chart Distribution Discord Bot
"""
import asyncio
import sys
import os

# Add the parent directory to the Python path, to get majority_judgment.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import disnake
from disnake.ext import commands
import logging
import majority_judgment as mj
import csv
import uuid
import re

# One only MJ opened allowed (for now)
OPENED = False

# Unique ID for any new question
UUID = uuid.uuid4()

# Keep questions, choices and grades in global scope
QUESTION = ""
CHOICES = []
GRADES = ["Nul", "Bof", "Okay", "Bien", "Top"]

# Results are stored globally as follows:
#   {{"user" : ["QUESTION[0]" : "value", ...]}}
RESULTS = {}

# Unfortunately Discord API do not separate buttons per user, so you have to keep
# in memory any button depending on user, 'custom_id' is defined as follows:
#   custom_id => str(UUID) + "button_" + GRADES[i] + "_" + str(user) + "_" + choice
BUTTONS = {}

# Keep the original interaction to edit (ephemeral trick)
# ORIGINAL_INTER {"user1": inter, "user2": inter...}
ORIGINAL_INTER = {}

# Validations storage allow a global button deactivation
# Keep in memory [user1, user2 ...]
VALIDATIONS = []

# Configure logging with date and time
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("Starting Major-Bot...")

# Fetch the MAJOR_BOT_GUILDS environment variable
guilds = os.getenv('MAJOR_BOT_GUILDS', '')
# Convert the string of guild IDs into a list of integers
test_guilds = [int(guild_id.strip()) for guild_id in guilds.split(',') if guild_id.strip().isdigit()]
if not test_guilds:
    logging.warning("MAJOR_BOT_GUILDS not found, bot is running as a global discord bot, any server is able to call him!")
else:
    logging.info("MAJOR_BOT_GUILDS=%s", guilds)

# Initialize your bot with these guilds
bot = commands.InteractionBot(test_guilds=test_guilds)

bot_is_ready = False
is_first_creation = True

@bot.event
async def on_ready():
    global bot_is_ready
    bot_is_ready = True
    print(f"Bot is ready. Logged in as {bot.user}")

# The slash command that responds with a message.
@bot.slash_command(description="Création d'un jugement majoritaire")
async def major_create(inter: disnake.ApplicationCommandInteraction,
                       question: str = commands.Param(description="Intitulé de la question"),
                       choices: str = commands.Param(description="Choix séparés par un `\";\" (ex : A;B;C)"),
):

    if not bot_is_ready:
        await inter.response.send_message(
            "Le bot est en cours de démarrage. Veuillez réessayer dans quelques secondes.",
            ephemeral=True,
        )
        return

    global is_first_creation
    global OPENED
    global QUESTION
    global CHOICES
    global UUID

    user = inter.author.id
    user_name = inter.author.name
    logging.info("User %s launched /major_create [%s] [%s]", user_name, question, choices)

    if not is_first_creation:
        await inter.response.defer(ephemeral=False)  # Defer the response to avoid timeouts

    if OPENED:
        await inter.response.send_message(
            "Err: Il y a déjà un jugement majoritaire en cours, lancez `/major_delete` pour l'arrêter.", ephemeral=True)
        return

    # Choices unique verification
    _choices = [x.strip() for x in choices.split(';')]
    if len(_choices) != len(set(_choices)):
        await inter.response.send_message("Err: Tous les choix doivent être différents !\n" + "choices: " + str(_choices), ephemeral=True)
        return

    QUESTION = question
    CHOICES = _choices
    UUID = uuid.uuid4()
    OPENED = True

    participate_button = disnake.ui.Button(label=QUESTION, style=disnake.ButtonStyle.primary, custom_id=str(UUID) + "participate")
    reset_button = disnake.ui.Button(label="Recommencer", style=disnake.ButtonStyle.secondary,
                      custom_id=str(UUID) + "button_reset_" + str(user))

    if not is_first_creation:
        await inter.followup.send("Un nouveau jugement majoritaire est créé, cliquez sur le bouton ci-dessous pour participer !",
            components=[participate_button, reset_button])
    else:
        await inter.response.send_message("Un nouveau jugement majoritaire est créé, cliquez sur le bouton ci-dessous pour participer !",
            components=[participate_button, reset_button])
        is_first_creation = False

@bot.listen("on_button_click")
async def major_update(inter: disnake.MessageInteraction):
    global QUESTION
    global CHOICES
    global RESULTS
    global VALIDATIONS
    global ORIGINAL_INTER

    user = inter.author.id
    user_name = inter.author.name

    # Validate button, disable any interaction
    if user in VALIDATIONS:
        return

    # Validation button scope
    if inter.component.custom_id == str(UUID) + "button_validate_" + str(user):

        # Do not allow Validation if results are not done
        # could happen if a user click on reset then validate
        for choice in CHOICES:
            if RESULTS[user][choice] == None:
                return

        logging.info("User %s clicked on validate '%s' button", user_name, QUESTION)
        VALIDATIONS.append(user)
        await inter.response.send_message("@" + user_name + " a validé ses choix!")
        return

    # Reset button, remove results from user
    if inter.component.custom_id == str(UUID) + "button_reset_" + str(user):
        logging.info("User %s clicked on reset '%s' button", user_name, QUESTION)
        if user not in RESULTS:
            # The user clicked on reset button but never have make any choice, just ignore
            return
        else:
            del RESULTS[user]

    # Init at participation button click
    if (inter.component.custom_id == str(UUID) + "participate"
            or inter.component.custom_id == str(UUID) + "button_reset_" + str(user)):
        logging.info("User %s asks for '%s' participation", user_name, QUESTION)
        if user not in RESULTS:
            logging.info("User %s is participating to '%s'", user_name, QUESTION)
            RESULTS[user] = {}
            BUTTONS[user] = {}
            for choice in CHOICES:
                RESULTS[user][choice] = None
                BUTTONS[user][choice] = []
                for i in range(0, 5):
                    BUTTONS[user][choice].append(
                        disnake.ui.Button(label=GRADES[i], style=disnake.ButtonStyle.secondary,
                            custom_id=str(UUID) + "button_" + GRADES[i] + "_" + str(user) + "_" + choice)
                    )
        else:
            # Ignore if the user click again on participation button
            return

    # Ignore if the user already have all results
    results_are_done = True
    for choice in CHOICES:
        try:
            if RESULTS[user][choice] is None:
                results_are_done = False
        except KeyError:
            logging.error("User tried %s an invalid RESULTS[%s][%s] call, maybe he clicked on an old button?", user_name, user, choice)
            return
    if results_are_done:
        return

    # Using c_index to be able to access to the next choice
    for c_index in range(0, len(CHOICES) + 1):
        choice = CHOICES[c_index]
        next_choice = choice
        if RESULTS[user][choice] is None:
            for i in range(0, 5):
                if inter.component.custom_id == str(UUID) + "button_" + GRADES[i] + "_" + str(user) + "_" + choice:
                    RESULTS[user][choice] = GRADES[i]
                    try:
                        next_choice = CHOICES[c_index + 1]
                    except:
                        logging.info("User %s has finished '%s'", user_name, QUESTION)
                        await ORIGINAL_INTER[user].edit_original_response(
                            content="Vous avez répondu à toutes les questions, merci pour votre participation !\n\n Résume de vos choix :\n"
                            + str(RESULTS[user]) + "\n"
                            + "\nCommande pour afficher les résultats : **/major_display**\n"
                            + "\nVoulez-vous valider vos choix ou recommencer le jugement majoritaire ?",
                            components=[disnake.ui.Button(label="Valider", style=disnake.ButtonStyle.success,
                                            custom_id=str(UUID) + "button_validate_" + str(user)),
                                       disnake.ui.Button(label="Recommencer", style=disnake.ButtonStyle.primary,
                                            custom_id=str(UUID) + "button_reset_" + str(user))]
                        )
                        await inter.response.defer()
                        return
            break  # do not continue, break loop for the next "choice"

    # Display buttons
    content_msg = "Que pensez-vous de **" + next_choice + "** ?"
    if ORIGINAL_INTER.get(user) is not None:
        await ORIGINAL_INTER[user].edit_original_response(content=content_msg, components=BUTTONS[user][next_choice])
        await inter.response.defer()
    else:
        await inter.response.send_message(
        content_msg,
        ephemeral=True,
        components=BUTTONS[user][next_choice])
        ORIGINAL_INTER[user] = inter

def dict_to_csv(data, filename="output.csv"):
    # Filter out any entries where a sub-dictionary contains None values
    filtered_data = [v.values() for v in data.values() if None not in v.values()]

    # Check if there is any data left after filtering
    if not filtered_data:
        logging.info("No data to write to CSV.")
        return

    # Write to CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Assuming all sub-dictionaries have the same keys, use the keys from the first item for the header
        header = list(data[next(iter(data))].keys())
        writer.writerow(header)

        # Write the filtered data
        writer.writerows(filtered_data)

    logging.info(f"CSV file '{filename}' created successfully.")

@bot.slash_command(description="Affichage des résultats du jugement courant")
async def major_display(inter, visibility: str = commands.Param(name="visibilité", description="Affichage privé ou publique", choices=["privé", "publique"])):

    global GRADES
    global RESULTS
    global CHOICES
    global QUESTION
    user_name = inter.author.name

    if not OPENED:
        await inter.response.send_message(
            "Aucun jugement majoritaire n'est actuellement ouvert, veuillez utiliser la commande **/major_create**",
            ephemeral=True,
        )
        return

    # Manage visibility of the results
    if visibility == "privé":
        ephemeral = True
    else:
        ephemeral = False

    await inter.response.defer(ephemeral=ephemeral)  # Defer the response to avoid timeouts

    csv_file = "major_bot.csv"
    dict_to_csv(RESULTS, csv_file)
    results = mj.read_and_aggregate_csv(csv_file, category_names=GRADES, ignore_first_column=False, values_type='str')
    # Remove special chars for Windows files
    png_file = re.sub(r'\W', '_', QUESTION) + '.png'
    mj.survey(results, category_names=GRADES, title=QUESTION, plot=False, display_major=False)
    await inter.send(file=disnake.File(png_file), ephemeral=ephemeral)
    logging.info("'%s' displayed by user %s", QUESTION, user_name)

@bot.slash_command(description="Suppression du jugement courant")
async def major_delete(inter: disnake.ApplicationCommandInteraction):
    global OPENED
    global QUESTION
    global CHOICES
    global RESULTS
    global BUTTONS
    global VALIDATIONS

    user_name = inter.author.name
    logging.info("'%s' has been reset by user %s", QUESTION, user_name)
    OPENED = False
    prev_question = QUESTION
    QUESTION = ""
    CHOICES = []
    RESULTS = {}
    BUTTONS = {}
    VALIDATIONS = []

    # defer + asyncio + followup is a workaround do delay Discord 3s timeout
    # fixes "disnake.errors.NotFound: 404 Not Found (error code: 10062): Unknown interaction"
    # fixes "NotFound: 404 Not Found (error code: 10062): Unknown interaction"
    await inter.response.defer(ephemeral=True)  # Defer the response to avoid timeouts
    await asyncio.sleep(1)
    await inter.followup.send("INFO: Vous avez supprimé le Jugement Majoritaire intitulé : " + prev_question,
                                      ephemeral=True)

# Fetch the bot token from environment variables
bot_token = os.getenv('MAJOR_BOT_TOKEN')
if bot_token is None:
    logging.fatal("No bot token found in environment variables, MAJOR_BOT_TOKEN is required!")
    exit(1)
else:
    logging.info("MAJOR_BOT_TOKEN=%s", bot_token)
bot.run(bot_token)

