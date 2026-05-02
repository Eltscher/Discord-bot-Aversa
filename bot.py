import discord
from discord import app_commands
from discord.ext import commands
from better_profanity import profanity
from dotenv import load_dotenv
import os
import random
import asyncio
import requests
 
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
NASA_API_KEY = os.getenv("NASA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
 
# ── Konfiguration ──────────────────────────────────────────────
NEW_MEMBER_ROLE_NAME = "Bekannte von Bekannten"
WELCOME_CHANNEL_NAME = "frischfleisch"
MAX_WARNINGS = 5
# ───────────────────────────────────────────────────────────────
 
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
 
bot = commands.Bot(command_prefix="/", intents=intents)
 
profanity.load_censor_words()
profanity.load_censor_words_from_file("boese_woerter.txt")
 
# Warnungs-Speicher { user_id: anzahl_warnungen }
warnings: dict[int, int] = {}
 
# ── Fakten & Witze ─────────────────────────────────────────────
 
FACTS = [
    "Die Goth-Subkultur entstand Ende der 1970er Jahre aus der Post-Punk-Bewegung in Großbritannien, angeführt von Bands wie Siouxsie and the Banshees.",
    "Der Begriff 'Gothic' bezieht sich ursprünglich auf die Goten, einen ostgermanischen Volksstamm – später wurde er auf mittelalterliche Kathedralen und dann auf düstere Ästhetik übertragen.",
    "Das Batcave-Nachtclub in London (1982) gilt als Geburtsort der Goth-Szene und versammelte frühe Ikonen des Genres.",
    "Schwarze Kleidung dominiert in der Goth-Kultur, weil Schwarz als Symbol der Trauer, des Geheimnisses und der Ablehnung gesellschaftlicher Normen gilt.",
    "Viktorianische Goth-Mode orientiert sich an der Trauerkultur des 19. Jahrhunderts, als Königin Victoria Jahrzehnte Schwarz nach dem Tod von Prinz Albert trug.",
    "Haie sind älter als Bäume – sie existieren seit über 400 Millionen Jahren.",
    "Studien zeigen, dass Goths überdurchschnittlich hohe Werte in Empathie und kreativem Denken aufweisen.",
    "Die Nibelungensage, ein germanisches Heldenepos, schildert Drachen, Flüche und den tragischen Untergang des Burgundenstammes – sie inspirierte Wagners Opernzyklus Der Ring des Nibelungen.",
    "Der Werwolf-Mythos hat seine Wurzeln in mittelalterlichen Gerichtsprozessen: Zwischen 1400 und 1700 wurden in Europa Hunderte Menschen als Werwölfe angeklagt.",
    "Melusine, eine Wasserfee aus französischen Sagen, verwandelte sich jeden Samstag in eine Schlangenfrau – ihr Bild ziert noch heute das Starbucks-Logo.",
    "Der Heilige Gral, Kernstück der Artussagen, wurde von über 30 verschiedenen mittelalterlichen Autoren erwähnt – ohne je eine einheitliche Beschreibung zu erhalten.",
    "In nordischen Sagen bewacht Ratatoskr, ein Eichhörnchen, den Weltbaum Yggdrasil und trägt Klatsch zwischen dem Adler oben und der Schlange unten.",
    "Die Sage der Lorelei beschreibt eine Nixe auf einem Felsen am Rhein, die Schiffer mit ihrem Gesang in den Tod lockt – erst im 19. Jahrhundert von Clemens Brentano verschriftlicht.",
    "Drachen galten im europäischen Mittelalter als reale Wesen – Kartographen zeichneten sie auf unbekannte Meeresregionen als Warnung für Seefahrer.",
    "Der Pied Piper (Rattenfänger von Hameln) basiert möglicherweise auf historischen Ereignissen von 1284, als 130 Kinder aus Hameln spurlos verschwanden.",
    "Spinnen produzieren bis zu sieben verschiedene Arten von Seide aus unterschiedlichen Drüsen – jede Seide hat andere Eigenschaften wie Klebrigkeit, Elastizität oder Festigkeit.",
    "Spinnenseide ist gewichtsbezogen fünfmal stärker als Stahl und dabei dreimal dehnbarer als Nylon – Wissenschaftler erforschen sie für kugelsichere Westen.",
    "Die Krabbenspinne (Thomisus) kann ihre Farbe ähnlich wie ein Chamäleon anpassen, um sich auf Blüten zu tarnen und Insekten zu jagen.",
    "Spinnen haben blaues Blut – ihr Blutfarbstoff Hämocyanin enthält Kupfer statt Eisen und transportiert Sauerstoff effizienter bei niedrigen Temperaturen.",
    "Die Arachne der griechischen Mythologie war eine Weberin, die sich anmaßte, besser als Athene zu weben – zur Strafe wurde sie in eine Spinne verwandelt, daher Arachnida.",
    "Die australische Trichternetzspinne (Atrax robustus) besitzt Chelizeren, die Schutzkleidung durchdringen können – ihr Gift wirkt beim Menschen innerhalb von Minuten.",
    "Forschungen der Universität Oxford zeigten 2023, dass Spinnen durch ihr Bein-Nervensystem träumen und ähnliche Schlafphasen wie Säugetiere durchlaufen.",
    "Tee ist das meistkonsumierte Getränk der Welt nach Wasser – täglich werden weltweit schätzungsweise 3,7 Milliarden Tassen getrunken.",
    "Alle Teesorten – Grüntee, Schwarztee, Weißtee, Oolong – stammen von derselben Pflanze: Camellia sinensis. Der Unterschied liegt im Verarbeitungsgrad.",
    "Der chinesische Kaiser Shen Nong soll Tee zufällig 2737 v. Chr. entdeckt haben, als Blätter in sein heißes Wasser fielen – eine Legende, die sich bis heute hält.",
    "Lapsang Souchong, ein chinesischer Räuchertee, wird über Kiefernholzfeuer getrocknet – sein rauchiges Aroma macht ihn zu einem Lieblingstee in der Goth-Community.",
    "L-Theanin, eine Aminosäure im Tee, fördert Entspannung ohne Schläfrigkeit und dämpft die stimulierende Wirkung des Koffeins – ein sogenannter ruhiger Fokus.",
    "Die britische Tradition des Afternoon Tea wurde 1840 von Anna, der 7. Herzogin von Bedford, eingeführt – um den langen Hunger zwischen Mittag- und Abendessen zu überbrücken.",
]
 
JOKES = [
    "Warum können Geister so schlecht lügen?\nWeil man durch sie hindurchsieht!",
    "Was sagt ein Bauer, wenn er seinen Traktor sucht?\n'Wo ist mein Traktor?'",
    "Was ist braun und klebrig?\nEin Stock.",
    "Warum nehmen Programmierer immer eine Brille mit?\nWeil sie C# brauchen!",
    "Wie nennt man einen Bumerang, der nicht zurückkommt?\nEinen Stock.",
    "Was macht ein Pixel allein auf weiter Flur?\nEs fühlt sich ein bisschen verloren!",
    "Warum hat das Skelett keinen Freund?\nWeil es kein Herz hat!",
    "Ich habe meinem Sohn gesagt, er soll seine Träume verfolgen. Er hat sich hingelegt.",
    "Ich wollte einen Witz über Papier machen... Aber der ist reißerisch.",
    "Was sagt ein Bäcker, wenn er das Brot aus dem Ofen holt? 'Das ist eine Laib-lingsbeschäftigung'.",
    "Ich habe aufgehört, Witze über Arbeitslosen zu machen. Keiner von denen lacht sowieso.",
]
 
 
# ── Events ─────────────────────────────────────────────────────
 
@bot.event
async def on_ready():
    # Slash Commands bei Discord registrieren
    await bot.tree.sync()
    print(f"✅ Bot ist online als {bot.user} (ID: {bot.user.id})")
    print(f"✅ Slash Commands wurden synchronisiert!")
    await bot.change_presence(activity=discord.Game("/help für Befehle"))
 
 
@bot.event
async def on_member_join(member: discord.Member):
    """Neue Mitglieder begrüßen & Rolle vergeben."""
 
    # 1. Automatische Rolle vergeben
    role = discord.utils.get(member.guild.roles, name=NEW_MEMBER_ROLE_NAME)
    if role:
        await member.add_roles(role)
        print(f"Rolle '{NEW_MEMBER_ROLE_NAME}' an {member} vergeben.")
    else:
        print(f"⚠️  Rolle '{NEW_MEMBER_ROLE_NAME}' nicht gefunden!")
 
    # 2. Willkommensnachricht
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        embed = discord.Embed(
            title="Willkommen auf dem Server!",
            description=(
                f"Hallo {member.mention}. Wilkommen!\n\n"
                f"Du bist unser **{member.guild.member_count}. Mitglied**.\n"
                f"Bitte verhalte dich vernünftig!\n"
            ),
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)
 
 
@bot.event
async def on_message(message: discord.Message):
    """Nachrichten auf unangemessene Inhalte prüfen."""
    if message.author.bot:
        return
 
    if profanity.contains_profanity(message.content):
        await message.delete()
 
        user_id = message.author.id
        warnings[user_id] = warnings.get(user_id, 0) + 1
        count = warnings[user_id]
 
        if count >= MAX_WARNINGS:
            try:
                await message.author.kick(reason="Mehrfach unangemessene Sprache verwendet.")
                await message.channel.send(
                    f"RIP. {message.author.mention} wurde nach **{MAX_WARNINGS} Verwarnungen** gekickt."
                )
                warnings.pop(user_id, None)
            except discord.Forbidden:
                await message.channel.send("Ich habe keine Berechtigung, diesen Nutzer zu kicken. Glück gehabt.")
        else:
            remaining = MAX_WARNINGS - count
            warn_embed = discord.Embed(
                title="Verwarnung",
                description=(
                    f"{message.author.mention}, deine Nachricht wurde entfernt.\n"
                    f"**Grund:** Unangemessene Sprache\n"
                    f"**Verwarnungen:** {count}/{MAX_WARNINGS} "
                    f"(noch {remaining} bis zum Kick)"
                ),
                color=discord.Color.red(),
            )
            warn_msg = await message.channel.send(embed=warn_embed)
            await warn_msg.delete(delay=30)
 
    await bot.process_commands(message)
 
 
# ── Slash Commands ─────────────────────────────────────────────
 
@bot.tree.command(name="wetter", description="Zeigt das aktuelle Wetter einer Stadt.")
@app_commands.describe(stadt="Die Stadt für die du das Wetter sehen möchtest")
async def wetter(interaction: discord.Interaction, stadt: str):
    await interaction.response.defer()
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": stadt,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "de"
    }
    response = requests.get(url, params=params)
    data = response.json()
 
    if response.status_code != 200:
        await interaction.followup.send(f"Stadt **{stadt}** nicht gefunden!")
        return
 
    name         = data["name"]
    temp         = data["main"]["temp"]
    feels_like   = data["main"]["feels_like"]
    humidity     = data["main"]["humidity"]
    beschreibung = data["weather"][0]["description"].capitalize()
    wind         = data["wind"]["speed"]
    icon_code    = data["weather"][0]["icon"]
    icon_url     = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
 
    embed = discord.Embed(
        title=f"Wetter in {name}",
        description=beschreibung,
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name="Temperatur",       value=f"{temp}°C",       inline=True)
    embed.add_field(name="Gefühlt wie",      value=f"{feels_like}°C", inline=True)
    embed.add_field(name="Luftfeuchtigkeit", value=f"{humidity}%",    inline=True)
    embed.add_field(name="Wind",             value=f"{wind} m/s",     inline=True)
    await interaction.followup.send(embed=embed)
 
 
@bot.tree.command(name="nasa", description="Zeigt das NASA Bild des Tages.")
async def nasa(interaction: discord.Interaction):
    await interaction.response.defer()
    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": NASA_API_KEY}
 
    response = requests.get(url, params=params)
    data = response.json()
 
    if response.status_code != 200:
        await interaction.followup.send("NASA API nicht erreichbar, versuche es später nochmal.")
        return
 
    titel        = data.get("title", "Kein Titel")
    beschreibung = data.get("explanation", "Keine Beschreibung")
    datum        = data.get("date", "")
    media_type   = data.get("media_type", "image")
    url_bild     = data.get("url", "")
 
    if len(beschreibung) > 500:
        beschreibung = beschreibung[:500] + "..."
 
    embed = discord.Embed(
        title=f"🔭 {titel}",
        description=beschreibung,
        color=discord.Color.dark_blue()
    )
    embed.set_footer(text=f"📅 {datum} • NASA Astronomy Picture of the Day")
 
    if media_type == "image":
        embed.set_image(url=url_bild)
    else:
        embed.add_field(name="📹 Video", value=url_bild)
 
    await interaction.followup.send(embed=embed)
 
 
@bot.tree.command(name="reminder", description="Setzt einen Reminder.")
@app_commands.describe(
    zeit="Zeit z.B. 10s, 5m, 2h",
    nachricht="Woran soll ich dich erinnern?"
)
async def reminder(interaction: discord.Interaction, zeit: str, nachricht: str):
    einheiten = {"s": 1, "m": 60, "h": 3600}
    einheit = zeit[-1].lower()
 
    if einheit not in einheiten or not zeit[:-1].isdigit():
        await interaction.response.send_message("❌ Ungültiges Format! Beispiel: `10m` oder `2h`")
        return
 
    sekunden = int(zeit[:-1]) * einheiten[einheit]
 
    if sekunden > 86400:
        await interaction.response.send_message("❌ Maximale Zeit ist 24 Stunden!")
        return
 
    embed = discord.Embed(
        title="Reminder gesetzt!",
        description=f"Ich erinnere dich in **{zeit}** an:\n> {nachricht}",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)
    await asyncio.sleep(sekunden)
 
    remind_embed = discord.Embed(
        title="Erinnerung!",
        description=f"{interaction.user.mention}, wakey wakey:\n> {nachricht}",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=remind_embed)
 
 
@bot.tree.command(name="ssp", description="Spiele Schere-Stein-Papier gegen den Bot!")
@app_commands.describe(wahl="Wähle deine Waffe")
@app_commands.choices(wahl=[
    app_commands.Choice(name="✂️ Schere", value="schere"),
    app_commands.Choice(name="🪨 Stein",  value="stein"),
    app_commands.Choice(name="📄 Papier", value="papier"),
])
async def ssp(interaction: discord.Interaction, wahl: str):
    optionen = ["schere", "stein", "papier"]
    emojis   = {"schere": "✂️", "stein": "🪨", "papier": "📄"}
    bot_wahl = random.choice(optionen)
 
    if wahl == bot_wahl:
        ergebnis = "🟡 Unentschieden!"
        farbe = discord.Color.yellow()
    elif (
        (wahl == "schere" and bot_wahl == "papier") or
        (wahl == "stein"  and bot_wahl == "schere") or
        (wahl == "papier" and bot_wahl == "stein")
    ):
        ergebnis = "🟢 Du gewinnst!"
        farbe = discord.Color.green()
    else:
        ergebnis = "🔴 Ich gewinne :D!"
        farbe = discord.Color.red()
 
    embed = discord.Embed(title="✂️🪨📄 Schere-Stein-Papier", color=farbe)
    embed.add_field(name="Deine Wahl", value=f"{emojis[wahl]} {wahl.capitalize()}",         inline=True)
    embed.add_field(name="Bot Wahl",   value=f"{emojis[bot_wahl]} {bot_wahl.capitalize()}", inline=True)
    embed.add_field(name="Ergebnis",   value=ergebnis, inline=False)
    await interaction.response.send_message(embed=embed)
 
 
@bot.tree.command(name="orb", description="Stell eine Frage an den magischen Orb!")
@app_commands.describe(frage="Deine Frage an den Orb")
async def orb(interaction: discord.Interaction, frage: str):
    antworten = [
        "🟢 Ja, definitiv!",
        "🟢 Ohne Zweifel!",
        "🟢 Ganz sicher!",
        "🟢 Ja, du kannst dich darauf verlassen!",
        "🟡 Frag später nochmal.",
        "🟡 Frag mal Leon.",
        "🟡 Nicht vorhersehbar.",
        "🟡 Konzentriere dich und frag nochmal.",
        "🔴 Glaub nicht daran.",
        "🔴 Meine Quellen sagen Nein.",
        "🔴 Sehr zweifelhaft.",
        "🔴 Nein, auf keinen Fall!",
    ]
    embed = discord.Embed(
        title="Orb der Wahrheit",
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="Deine Frage", value=frage,                    inline=False)
    embed.add_field(name="Antwort",     value=random.choice(antworten), inline=False)
    await interaction.response.send_message(embed=embed)
 
 
@bot.tree.command(name="fakt", description="Zeigt einen zufälligen interessanten Fakt.")
async def fakt(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Ich lehre dich etwas Neues...",
        description=random.choice(FACTS),
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)
 
 
@bot.tree.command(name="witz", description="Erzählt einen lustigen Witz von Sophie.")
async def witz(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Witz des Tages",
        description=random.choice(JOKES),
        color=discord.Color.yellow(),
    )
    await interaction.response.send_message(embed=embed)
 
 
@bot.tree.command(name="warnungen", description="Zeigt deine aktuellen Verwarnungen an.")
async def warnungen(interaction: discord.Interaction):
    count = warnings.get(interaction.user.id, 0)
    await interaction.response.send_message(
        f"📋 {interaction.user.mention} hat **{count}/{MAX_WARNINGS}** Verwarnungen."
    )
 
 
@bot.tree.command(name="clearwarn", description="[Admin] Setzt die Verwarnungen eines Nutzers zurück.")
@app_commands.describe(member="Der Nutzer dessen Verwarnungen zurückgesetzt werden sollen")
@app_commands.checks.has_permissions(administrator=True)
async def clearwarn(interaction: discord.Interaction, member: discord.Member):
    warnings.pop(member.id, None)
    await interaction.response.send_message(
        f"Verwarnungen von {member.mention} wurden zurückgesetzt. Sei dankbar."
    )
 
 
# ── Fehlerbehandlung ───────────────────────────────────────────

@bot.tree.command(name="help", description="Zeigt alle verfügbaren Befehle an.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Alle Befehle",
        description="Hier sind alle verfügbaren Slash Commands:",
        color=discord.Color.dark_purple()
    )

    embed.add_field(
        name="Spiele",
        value=(
            "`/ssp` – Schere-Stein-Papier gegen den Bot\n"
            "`/orb` – Stell eine Frage an den Orb der Wahrheit"
        ),
        inline=False
    )
    embed.add_field(
        name="Wissen",
        value=(
            "`/fakt` – Zufälliger interessanter Fakt\n"
            "`/witz` – Witz des Tages\n"
            "`/nasa` – NASA Bild des Tages"
        ),
        inline=False
    )
    embed.add_field(
        name="Stuff",
        value=(
            "`/wetter [stadt]` – Aktuelles Wetter einer Stadt\n"
            "`/reminder [zeit] [nachricht]` – Setzt einen Reminder (z.B. `10m` oder `2h`)\n"
            "`/warnungen` – Zeigt deine aktuellen Verwarnungen an"
        ),
        inline=False
    )
    embed.add_field(
        name="Admin",
        value=(
            "`/clearwarn [@nutzer]` – Verwarnungen eines Nutzers zurücksetzen"
        ),
        inline=False
    )

    embed.set_footer(text="Bei Fragen wende dich an Eltscher!")
    await interaction.response.send_message(embed=embed)
 
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Du hast leider keine Berechtigung für diesen Befehl.")
    else:
        await interaction.response.send_message("❌ Ein Fehler ist aufgetreten.")
        raise error
 
 
# ── Start ──────────────────────────────────────────────────────
bot.run(TOKEN)
