# import package
from datetime import datetime, timedelta
from discord.ext import commands
import json 
import discord
import re
import os
import asyncio
from discord.ui import View, Button

# intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

# prefix 
client = commands.Bot(command_prefix='/', intents=intents)

# Create a dictionary to store the number of wins rr for each user
scores = {}
wins_file = 'wins.json'

if not os.path.exists(wins_file):
    with open(wins_file, 'w') as f:
        json.dump({}, f)
reward_roles = {}

# Event to indicate the bot is ready
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.tree.sync()  # Sync the command tree
    activity = discord.Activity(type=discord.ActivityType.playing, name="/help | CodeWithViktor")
    await client.change_presence(activity=activity)

# Create a dictionary to store the number of wins for each user
wins_file = 'wins.json'
guild_rewardroles = {}
if not os.path.exists(wins_file):
    with open(wins_file, 'w') as f:
        json.dump({}, f)

# Slash command for /help
class HelpView(View):
    def __init__(self):
        super().__init__()
        self.page = 1

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.blurple)
    async def previous(self, interaction, button):
        if self.page > 1:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple)
    async def next(self, interaction, button):
        if self.page < 3:
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    def get_embed(self):
        if self.page == 1:
            embed = discord.Embed(title=':mailbox_with_mail: Need help? Here\'s my information and my commands:', description='**:busts_in_silhouette: About Me**\nYour ultimate companion for all things Discord! Whether you’re managing a community or just hanging out with friends, I am here to enhance your server experience with a suite of powerful features and tools!\n\nKeep your server in top shape with our comprehensive moderation tools, versatile commands. From automated warnings to ban and kick commands, IND Clan Bot helps you maintain a friendly and respectful environment effortlessly!')
            return embed
        elif self.page == 2:
            embed = discord.Embed(title='**:video_game: GAME COMMANDS**', description='`/add`: register points to your balance!\n`/remove`: De-register points from your balance!\n`/points`: Check your or someone else\'s points!\n`/wins`: Check your or someone else\'s wins!\n`/leaderboard`: Check out the leaderboard!\n\n**:detective: MODERATOR GAME COMMANDS**\n`/botadmin`: Use this to set a role as the Bot Manager role, person with this role will have access to the bot\'s mod commands!\n`/removebotadmin:` Removes the selected role for Bot Manager!\n`/addpoints:` Register points in someone else\'s balance!\n`/removepoints:` De-Register points in someone else\'s balance!\n`/addwin:` Register a win for someone!\n`/removewin:` De-Register a win from someone!')
            return embed
        elif self.page == 3:
            embed = discord.Embed(title='**:tools: MODERATION COMMANDS**', description='`/warn`: Warns a user! 3 warns = 5 mins __timeout__ and 6 warns = __Kick__ from server. After 6 warnings all warns will be reset!\n`/clearwarns`: Clears all the warnings a user has!\n`/mute`: Gives a muted role to a user, creates one if there is no muted role!\n`/unmute`: Removes muted role from the user!\n`/addrole`: Add role(s) to a user!\n`/removerole`: Remove a role from a user!')
            return embed

@client.tree.command(name='help', description='Need help? Here\'s my information and my commands!')
async def help(interaction: discord.Interaction):
    view = HelpView()
    await interaction.response.send_message(embed=view.get_embed(), view=view)

# Slash command for /add
@client.tree.command(name='add', description='Add to your score!')
async def add(interaction: discord.Interaction, amount: float):

    try:
        if amount <= 0:
            await interaction.response.send_message('You can only add positive numbers!')
            return

        user_id = interaction.user.id
        scores_file = 'scores.json'
        wins_file = 'wins.json'

        if not os.path.exists(scores_file):
            with open(scores_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(wins_file):
            with open(wins_file, 'w') as f:
                json.dump({}, f)

        with open(scores_file, 'r+') as f:
            try:
                scores = json.load(f)
            except json.JSONDecodeError:
                scores = {}
                f.seek(0)
                json.dump(scores, f, indent=4)
                f.truncate()

        with open(wins_file, 'r+') as f:
            try:
                wins = json.load(f)
            except json.JSONDecodeError:
                wins = {}
                f.seek(0)
                json.dump(wins, f, indent=4)
                f.truncate()

        if str(user_id) in scores:
            scores[str(user_id)] += amount
            new_balance = scores[str(user_id)]
        else:
            scores[str(user_id)] = amount
            new_balance = amount

        if str(user_id) not in wins:
            wins[str(user_id)] = {'added': 0, 'removed': 0}

        wins[str(user_id)]['added'] += 1

        with open(scores_file, 'w') as f:
            json.dump(scores, f, indent=4)

        with open(wins_file, 'w') as f:
            json.dump(wins, f, indent=4)

        embed = discord.Embed(description=f"Registered **{amount}** points to your balance, your new balance is **{new_balance}**")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /remove
@client.tree.command(name='remove', description='Remove points from your score!')
async def remove(interaction: discord.Interaction, amount: float):
    try:
        if amount <= 0:
            await interaction.response.send_message('You can only remove positive numbers!')
            return

        user_id = interaction.user.id
        scores_file = 'scores.json'
        wins_file = 'wins.json'

        if not os.path.exists(scores_file):
            with open(scores_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(wins_file):
            with open(wins_file, 'w') as f:
                json.dump({}, f)

        with open(scores_file, 'r+') as f:
            try:
                scores = json.load(f)
            except json.JSONDecodeError:
                scores = {}
                f.seek(0)
                json.dump(scores, f, indent=4)
                f.truncate()

        with open(wins_file, 'r+') as f:
            try:
                wins = json.load(f)
            except json.JSONDecodeError:
                wins = {}
                f.seek(0)
                json.dump(wins, f, indent=4)
                f.truncate()

        if str(user_id) in scores:
            if scores[str(user_id)] < amount:
                await interaction.response.send_message('You do not have enough points to remove!')
                return
            scores[str(user_id)] -= amount
            new_balance = scores[str(user_id)]
        else:
            await interaction.response.send_message('You do not have any points to remove!')
            return

        if str(user_id) not in wins:
            wins[str(user_id)] = {'added': 0, 'removed': 0}

        wins[str(user_id)]['removed'] += 1

        with open(scores_file, 'w') as f:
            json.dump(scores, f, indent=4)

        with open(wins_file, 'w') as f:
            json.dump(wins, f, indent=4)

        embed = discord.Embed(description=f"Removed **{amount}** points from your balance, your new balance is **{new_balance}**")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /points
@client.tree.command(name='points', description='Check your or someone else\'s points!')
async def points(interaction: discord.Interaction, user: discord.Member):
    try:
        scores_file = 'scores.json'

        if not os.path.exists(scores_file):
            with open(scores_file, 'w') as f:
                json.dump({}, f)

        with open(scores_file, 'r+') as f:
            try:
                scores = json.load(f)
            except json.JSONDecodeError:
                scores = {}
                f.seek(0)
                json.dump(scores, f, indent=4)
                f.truncate()

        user_id = str(user.id)
        if user_id in scores:
            total_points = scores[user_id]

            embed = discord.Embed(title=f'**__Points Data__ :money_with_wings:**', description=f'**{user.mention}** has **{total_points}** total points in their balance', color=0x00ff00)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f'{user.mention} doesn\'t have any points!')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /wins
@client.tree.command(name='wins', description='Check your or someone else\'s wins!')
async def wins(interaction: discord.Interaction, user: discord.Member):
    try:
        wins_file = 'wins.json'

        if not os.path.exists(wins_file):
            with open(wins_file, 'w') as f:
                json.dump({}, f)

        with open(wins_file, 'r+') as f:
            try:
                wins = json.load(f)
            except json.JSONDecodeError:
                wins = {}
                f.seek(0)
                json.dump(wins, f, indent=4)
                f.truncate()

        user_id = str(user.id)
        if user_id in wins:
            total_wins = wins[user_id]

            embed = discord.Embed(title=f'**__Wins Data__ :trophy:**', description=f'**{user.mention}** has total **{total_wins["added"]}** wins in their record!', color=0x00ff00)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f'{user.mention} doesn\'t have any wins!')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /leaderboard
@client.tree.command(name='leaderboard', description='Displays the leaderboard of top players with highest score')
async def leaderboard(interaction: discord.Interaction):
    try:
        scores_file = 'scores.json'

        if not os.path.exists(scores_file):
            with open(scores_file, 'w') as f:
                json.dump({}, f)

        with open(scores_file, 'r+') as f:
            try:
                scores = json.load(f)
            except json.JSONDecodeError:
                scores = {}
                f.seek(0)
                json.dump(scores, f, indent=4)
                f.truncate()

        # Sort scores by value in descending order
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Create the leaderboard embed
        embed = discord.Embed(title='Leaderboard', description='Top players with highest score', color=0x00ff00)

        # Create the leaderboard string
        leaderboard_str = ''
        for i, (user_id, score) in enumerate(sorted_scores[:10]):  # Show first 10 players
            user = client.get_user(int(user_id))
            if user:
                username = user.mention
            else:
                username = 'Unknown User'
            leaderboard_str += f'{i+1}. {username} - {score} points\n'

        embed.add_field(name='Leaderboard', value=leaderboard_str, inline=False)

        # Check if we need to display navigation buttons
        if len(sorted_scores) > 10:
            # Create the navigation buttons
            view = View()
            prev_button = Button(label='Previous', style=discord.ButtonStyle.blurple, custom_id='prev')
            next_button = Button(label='Next', style=discord.ButtonStyle.blurple, custom_id='next')
            view.add_item(prev_button)
            view.add_item(next_button)

            # Define the callback functions for the navigation buttons
            async def prev_callback(interaction):
                # Get the current page number
                page_num = int(interaction.message.embeds[0].footer.text.split(' ')[1])

                # Check if we're on the first page
                if page_num == 1:
                    return

                # Decrement the page number
                page_num -= 1

                # Update the leaderboard string
                leaderboard_str = ''
                for i, (user_id, score) in enumerate(sorted_scores[(page_num-1)*10:page_num*10]):
                    user = client.get_user(int(user_id))
                    if user:
                        username = user.mention
                    else:
                        username = 'Unknown User'
                    leaderboard_str += f'{(page_num-1)*10+i+1}. {username} - {score} points\n'

                # Update the embed
                embed.set_field_at(0, name='Leaderboard', value=leaderboard_str, inline=False)
                embed.set_footer(text=f'Page {page_num} of {len(sorted_scores)//10 + 1}')

                # Send the updated embed
                await interaction.response.edit_message(embed=embed)

            async def next_callback(interaction):
                # Get the current page number
                page_num = int(interaction.message.embeds[0].footer.text.split(' ')[1])

                # Check if we're on the last page
                if page_num == len(sorted_scores)//10 + 1:
                    return

                # Increment the page number
                page_num += 1

                # Update the leaderboard string
                leaderboard_str = ''
                for i, (user_id, score) in enumerate(sorted_scores[(page_num-1)*10:page_num*10]):
                    user = client.get_user(int(user_id))
                    if user:
                        username = user.mention
                    else:
                        username = 'Unknown User'
                    leaderboard_str += f'{(page_num-1)*10+i+1}. {username} - {score} points\n'

                # Update the embed
                embed.set_field_at(0, name='Leaderboard', value=leaderboard_str, inline=False)
                embed.set_footer(text=f'Page {page_num} of {len(sorted_scores)//10 + 1}')

                # Send the updated embed
                await interaction.response.edit_message(embed=embed)

            # Set the callback functions for the navigation buttons
            prev_button.callback = prev_callback
            next_button.callback = next_callback

            # Send the initial embed with navigation buttons
            await interaction.response.send_message(embed=embed, view=view)
        else:
            # Send the initial embed without navigation buttons
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /scorecard
@client.tree.command(name='scorecard', description='Gives a statistical data about a player!')
async def scorecard(interaction: discord.Interaction, user: discord.Member):
    try:
        scores_file = 'scores.json'
        wins_file = 'wins.json'

        if not os.path.exists(scores_file):
            with open(scores_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(wins_file):
            with open(wins_file, 'w') as f:
                json.dump({}, f)

        with open(scores_file, 'r+') as f:
            try:
                scores = json.load(f)
            except json.JSONDecodeError:
                scores = {}
                f.seek(0)
                json.dump(scores, f, indent=4)
                f.truncate()

        with open(wins_file, 'r+') as f:
            try:
                wins = json.load(f)
            except json.JSONDecodeError:
                wins = {}
                f.seek(0)
                json.dump(wins, f, indent=4)
                f.truncate()

        user_id = user.id

        if str(user_id) in scores:
            total_points = scores[str(user_id)]
        else:
            total_points = 0

        if str(user_id) in wins:
            total_wins = wins[str(user_id)]['added'] - wins[str(user_id)]['removed']
        else:
            total_wins = 0

        # Calculate the rank of the player
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        rank = [i for i, (uid, score) in enumerate(sorted_scores) if uid == str(user_id)]
        if rank:
            rank = rank[0] + 1
        else:
            rank = 'Not ranked'

        # Calculate points earned in last 15 days
        recent_points = 0  # TO DO: implement logic to calculate recent points

        # Calculate battle wins in last 15 days
        recent_wins = 0  # TO DO: implement logic to calculate recent wins

        embed = discord.Embed(title='**__Statistical User Scorecard :bar_chart:__**', color=0x00ff00)
        embed.add_field(name='**__USer Data__**', value=f'**1) Battle Wins: {total_wins}**\n'
                                                             f'**2) Battle Wins (last 15 days): {recent_wins}**\n'
                                                             f'**3) Total Points: {total_points}**\n'
                                                             f'**4) Total Points (last 15 days): {recent_points}**\n'
                                                             f'**5) Rank in leaderboard: {rank}**', inline=False)

        await interaction.response.send_message(f'{user.mention}', embed=embed)

    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /botadmin
@client.tree.command(name='botadmin', description='Set a role as Bot Manager role (Admin only)')
@commands.has_permissions(administrator=True)
async def botadmin(interaction: discord.Interaction, role: discord.Role):
    try:
        botadmin_file = 'botadmin.json'

        if not os.path.exists(botadmin_file):
            with open(botadmin_file, 'w') as f:
                json.dump({}, f)

        with open(botadmin_file, 'r+') as f:
            try:
                botadmin_data = json.load(f)
            except json.JSONDecodeError:
                botadmin_data = {}
                f.seek(0)
                json.dump(botadmin_data, f, indent=4)
                f.truncate()

        guild_id = interaction.guild.id
        role_id = role.id

        if str(guild_id) not in botadmin_data:
            botadmin_data[str(guild_id)] = role_id
        else:
            botadmin_data[str(guild_id)] = role_id

        with open(botadmin_file, 'w') as f:
            json.dump(botadmin_data, f, indent=4)

        await interaction.response.send_message(f'Set {role.mention} as Bot Manager role for this server.')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /removebotadmin
@client.tree.command(name='removebotadmin', description='Remove the Bot Manager role for the server (Admin only)')
@commands.has_permissions(administrator=True)
async def removebotadmin(interaction: discord.Interaction):
    try:
        botadmin_file = 'botadmin.json'

        if not os.path.exists(botadmin_file):
            with open(botadmin_file, 'w') as f:
                json.dump({}, f)

        with open(botadmin_file, 'r+') as f:
            try:
                botadmin_data = json.load(f)
            except json.JSONDecodeError:
                botadmin_data = {}
                f.seek(0)
                json.dump(botadmin_data, f, indent=4)
                f.truncate()

        guild_id = interaction.guild.id

        if str(guild_id) in botadmin_data:
            del botadmin_data[str(guild_id)]

            with open(botadmin_file, 'w') as f:
                json.dump(botadmin_data, f, indent=4)

            await interaction.response.send_message(f'Removed Bot Manager role for this server.')
        else:
            await interaction.response.send_message(f'Bot Manager role is not set for this server.')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /hi
@client.tree.command(name='hi', description='A test command for Bot Managers only')
async def hi(interaction: discord.Interaction):
    try:
        botadmin_file = 'botadmin.json'

        if not os.path.exists(botadmin_file):
            with open(botadmin_file, 'w') as f:
                json.dump({}, f)

        with open(botadmin_file, 'r+') as f:
            try:
                botadmin_data = json.load(f)
            except json.JSONDecodeError:
                botadmin_data = {}
                f.seek(0)
                json.dump(botadmin_data, f, indent=4)
                f.truncate()

        guild_id = interaction.guild.id
        role_id = botadmin_data.get(str(guild_id))

        if role_id:
            role = interaction.guild.get_role(role_id)
            if role in interaction.user.roles:
                await interaction.response.send_message('Hello, Bot Manager!')
            else:
                await interaction.response.send_message('You do not have permission to use this command.')
        else:
            await interaction.response.send_message('Bot Manager role is not set for this server.')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /addpoints
@client.tree.command(name='addpoints', description='Add points to someone\'s account (Bot Manager only)')
async def addpoints(interaction: discord.Interaction, user: discord.Member, amount: int):
    try:
        botadmin_file = 'botadmin.json'
        scores_file = 'scores.json'
        wins_file = 'wins.json'

        if not os.path.exists(botadmin_file):
            with open(botadmin_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(scores_file):
            with open(scores_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(wins_file):
            with open(wins_file, 'w') as f:
                json.dump({}, f)

        with open(botadmin_file, 'r+') as f:
            try:
                botadmin_data = json.load(f)
            except json.JSONDecodeError:
                botadmin_data = {}
                f.seek(0)
                json.dump(botadmin_data, f, indent=4)
                f.truncate()

        guild_id = interaction.guild.id
        role_id = botadmin_data.get(str(guild_id))

        if role_id:
            role = interaction.guild.get_role(role_id)
            if role in interaction.user.roles:
                with open(scores_file, 'r+') as f:
                    try:
                        scores = json.load(f)
                    except json.JSONDecodeError:
                        scores = {}
                        f.seek(0)
                        json.dump(scores, f, indent=4)
                        f.truncate()

                user_id = user.id
                if str(user_id) in scores:
                    scores[str(user_id)] += amount
                else:
                    scores[str(user_id)] = amount

                with open(scores_file, 'w') as f:
                    json.dump(scores, f, indent=4)

                with open(wins_file, 'r+') as f:
                    try:
                        wins = json.load(f)
                    except json.JSONDecodeError:
                        wins = {}
                        f.seek(0)
                        json.dump(wins, f, indent=4)
                        f.truncate()

                if str(user_id) in wins:
                    wins[str(user_id)]['added'] += 1
                else:
                    wins[str(user_id)] = {'added': 1, 'removed': 0}

                with open(wins_file, 'w') as f:
                    json.dump(wins, f, indent=4)

                await interaction.response.send_message(f'Added {amount} points to {user.mention}\'s account.')
            else:
                await interaction.response.send_message('You do not have permission to use this command.')
        else:
            await interaction.response.send_message('Bot Manager role is not set for this server.')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /removepoints
@client.tree.command(name='removepoints', description='Remove points from someone\'s account (Bot Manager only)')
async def removepoints(interaction: discord.Interaction, user: discord.Member, amount: int):
    try:
        botadmin_file = 'botadmin.json'
        scores_file = 'scores.json'
        wins_file = 'wins.json'

        if not os.path.exists(botadmin_file):
            with open(botadmin_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(scores_file):
            with open(scores_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(wins_file):
            with open(wins_file, 'w') as f:
                json.dump({}, f)

        with open(botadmin_file, 'r+') as f:
            try:
                botadmin_data = json.load(f)
            except json.JSONDecodeError:
                botadmin_data = {}
                f.seek(0)
                json.dump(botadmin_data, f, indent=4)
                f.truncate()

        guild_id = interaction.guild.id
        role_id = botadmin_data.get(str(guild_id))

        if role_id:
            role = interaction.guild.get_role(role_id)
            if role in interaction.user.roles:
                with open(scores_file, 'r+') as f:
                    try:
                        scores = json.load(f)
                    except json.JSONDecodeError:
                        scores = {}
                        f.seek(0)
                        json.dump(scores, f, indent=4)
                        f.truncate()

                user_id = user.id
                if str(user_id) in scores:
                    if scores[str(user_id)] >= amount:
                        scores[str(user_id)] -= amount
                    else:
                        await interaction.response.send_message(f'Cannot remove {amount} points from {user.mention}\'s account. They only have {scores[str(user_id)]} points.')
                        return
                else:
                    await interaction.response.send_message(f'{user.mention} does not have any points to remove.')
                    return

                with open(scores_file, 'w') as f:
                    json.dump(scores, f, indent=4)

                with open(wins_file, 'r+') as f:
                    try:
                        wins = json.load(f)
                    except json.JSONDecodeError:
                        wins = {}
                        f.seek(0)
                        json.dump(wins, f, indent=4)
                        f.truncate()

                if str(user_id) in wins:
                    wins[str(user_id)]['removed'] += 1
                else:
                    wins[str(user_id)] = {'added': 0, 'removed': 1}

                with open(wins_file, 'w') as f:
                    json.dump(wins, f, indent=4)

                await interaction.response.send_message(f'removeed {amount} points from {user.mention}\'s account.')
            else:
                await interaction.response.send_message('You do not have permission to use this command.')
        else:
            await interaction.response.send_message('Bot Manager role is not set for this server.')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /addwin
@client.tree.command(name='addwin', description='Add a win to someone\'s account (Bot Manager only)')
async def addwin(interaction: discord.Interaction, user: discord.Member):
    try:
        botadmin_file = 'botadmin.json'
        wins_file = 'wins.json'

        if not os.path.exists(botadmin_file):
            with open(botadmin_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(wins_file):
            with open(wins_file, 'w') as f:
                json.dump({}, f)

        with open(botadmin_file, 'r+') as f:
            try:
                botadmin_data = json.load(f)
            except json.JSONDecodeError:
                botadmin_data = {}
                f.seek(0)
                json.dump(botadmin_data, f, indent=4)
                f.truncate()

        guild_id = interaction.guild.id
        role_id = botadmin_data.get(str(guild_id))

        if role_id:
            role = interaction.guild.get_role(role_id)
            if role in interaction.user.roles:
                with open(wins_file, 'r+') as f:
                    try:
                        wins = json.load(f)
                    except json.JSONDecodeError:
                        wins = {}
                        f.seek(0)
                        json.dump(wins, f, indent=4)
                        f.truncate()

                user_id = user.id
                if str(user_id) in wins:
                    wins[str(user_id)]['added'] += 1
                else:
                    wins[str(user_id)] = {'added': 1, 'removed': 0}

                with open(wins_file, 'w') as f:
                    json.dump(wins, f, indent=4)

                await interaction.response.send_message(f'Added a win to {user.mention}\'s account.')
            else:
                await interaction.response.send_message('You do not have permission to use this command.')
        else:
            await interaction.response.send_message('Bot Manager role is not set for this server.')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /removewin
@client.tree.command(name='removewin', description='Remove a win from someone\'s account (Bot Manager only)')
async def removewin(interaction: discord.Interaction, user: discord.Member):
    try:
        botadmin_file = 'botadmin.json'
        wins_file = 'wins.json'

        if not os.path.exists(botadmin_file):
            with open(botadmin_file, 'w') as f:
                json.dump({}, f)

        if not os.path.exists(wins_file):
            with open(wins_file, 'w') as f:
                json.dump({}, f)

        with open(botadmin_file, 'r+') as f:
            try:
                botadmin_data = json.load(f)
            except json.JSONDecodeError:
                botadmin_data = {}
                f.seek(0)
                json.dump(botadmin_data, f, indent=4)
                f.truncate()

        guild_id = interaction.guild.id
        role_id = botadmin_data.get(str(guild_id))

        if role_id:
            role = interaction.guild.get_role(role_id)
            if role in interaction.user.roles:
                with open(wins_file, 'r+') as f:
                    try:
                        wins = json.load(f)
                    except json.JSONDecodeError:
                        wins = {}
                        f.seek(0)
                        json.dump(wins, f, indent=4)
                        f.truncate()

                user_id = user.id
                if str(user_id) in wins:
                    if wins[str(user_id)]['added'] > 0:
                        wins[str(user_id)]['added'] -= 1
                    else:
                        await interaction.response.send_message(f'Cannot remove a win from {user.mention}\'s account. They do not have any wins.')
                        return
                else:
                    await interaction.response.send_message(f'{user.mention} does not have any wins to remove.')
                    return

                with open(wins_file, 'w') as f:
                    json.dump(wins, f, indent=4)

                await interaction.response.send_message(f'Removed a win from {user.mention}\'s account.')
            else:
                await interaction.response.send_message('You do not have permission to use this command.')
        else:
            await interaction.response.send_message('Bot Manager role is not set for this server.')
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

# Slash command for /warn
@client.tree.command(name="warn")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    guild = interaction.guild
    warns_folder = "json"
    warns_file = "warns.json"
    warns_path = os.path.join(warns_folder, warns_file)

    if not os.path.exists(warns_path):
        with open(warns_path, "w") as f:
            json.dump({}, f)

    with open(warns_path, "r") as f:
        warns = json.load(f)

    if str(guild.id) not in warns:
        warns[str(guild.id)] = {}

    if str(user.id) not in warns[str(guild.id)]:
        warns[str(guild.id)][str(user.id)] = 0

    warns[str(guild.id)][str(user.id)] += 1

    with open(warns_path, "w") as f:
        json.dump(warns, f)

    await interaction.response.send_message(f"{user.mention} is warned, they now have {warns[str(guild.id)][str(user.id)]} warns.")

    await user.send(f"You have been warned for {reason}. You now have {warns[str(guild.id)][str(user.id)]} warns. Please review the server rules and refrain from breaking them.")

    if warns[str(guild.id)][str(user.id)] == 3:
        await user.timeout(timedelta(minutes=5))
        await interaction.response.send_message(f"{user.mention} has been timed out for 5 minutes due to receiving 3 warnings.")
        await user.send(f"You have been timed out for 5 minutes due to receiving 3 warnings. Please review the server rules and refrain from breaking them.")
    elif warns[str(guild.id)][str(user.id)] == 6:
        await user.kick(reason="6 warns")
        await interaction.response.send_message(f"{user.mention} has been kicked due to receiving 6 warnings.")
        await user.send(f"You have been kicked from the server due to receiving 6 warnings. Please review the server rules and refrain from breaking them if you wish to rejoin.")
        warns[str(guild.id)][str(user.id)] = 0  # Reset warns
    elif warns[str(guild.id)][str(user.id)] > 6:
        warns[str(guild.id)][str(user.id)] = 0  # Reset warns

# Slash command for /clearwarns
@client.tree.command(name="clearwarns")
async def clearwarns(interaction: discord.Interaction, user: discord.Member):
    guild = interaction.guild
    warns_folder = "json"
    warns_file = "warns.json"
    warns_path = os.path.join(warns_folder, warns_file)

    if not os.path.exists(warns_path):
        with open(warns_path, "w") as f:
            json.dump({}, f)

    with open(warns_path, "r") as f:
        warns = json.load(f)

    if str(guild.id) not in warns:
        warns[str(guild.id)] = {}

    if str(user.id) not in warns[str(guild.id)]:
        warns[str(guild.id)][str(user.id)] = 0

    warns[str(guild.id)][str(user.id)] = 0
    await user.timeout(timedelta(seconds=0))  # Remove timeout

    with open(warns_path, "w") as f:
        json.dump(warns, f)

    embed = discord.Embed(title="Member Warns Cleared", description=f"{user.mention}'s warns have been cleared.", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

# Slash command for /mute
@client.tree.command(name="mute")
async def mute(interaction: discord.Interaction, user: discord.Member):
    guild = interaction.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        muted_role = await guild.create_role(name="Muted", color=discord.Color.red())
        for channel in guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)

    if muted_role in user.roles:
        await interaction.response.send_message(f"{user.mention} is already muted.", ephemeral=True)
        return

    await user.add_roles(muted_role)

    embed = discord.Embed(title="Member Muted", description=f"{user.mention} has been muted.", color=0xff0000)
    await interaction.response.send_message(embed=embed)

# Slash command for /unmute
@client.tree.command(name="unmute")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    guild = interaction.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        await interaction.response.send_message("No muted role found.", ephemeral=True)
        return

    if muted_role not in user.roles:
        await interaction.response.send_message(f"{user.mention} is not muted.", ephemeral=True)
        return

    await user.remove_roles(muted_role)

    embed = discord.Embed(title="Member Unmuted", description=f"{user.mention} has been unmuted.", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

# Slash command for /addrole
@client.tree.command(name="addrole")
async def addrole(interaction: discord.Interaction, user: discord.Member, roles: str):
    role_mentions = [role.strip() for role in roles.split(",")]

    guild = interaction.guild
    roles_to_add = []
    for role_mention in role_mentions:
        if role_mention.startswith("<@&"):
            role_id = int(re.sub(r"[^0-9]", "", role_mention))
            role = guild.get_role(role_id)
            if role:
                roles_to_add.append(role)
            else:
                await interaction.response.send_message(f"Role '{role_mention}' not found.", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"Invalid role mention: '{role_mention}'. Please use the `@role` format.", ephemeral=True)
            return

    await user.add_roles(*roles_to_add)

    embed = discord.Embed(title="Role Assigned", description=f"Assigned {', '.join([r.mention for r in roles_to_add])} role to {user.mention}", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

# Slash command for /removerole
@client.tree.command(name="removerole")
async def removerole(interaction: discord.Interaction, user: discord.Member, roles: str):
    role_mentions = [role.strip() for role in roles.split(",")]

    guild = interaction.guild
    roles_to_remove = []
    for role_mention in role_mentions:
        if role_mention.startswith("<@&"):
            role_id = int(re.sub(r"[^0-9]", "", role_mention))
            role = guild.get_role(role_id)
            if role:
                roles_to_remove.append(role)
            else:
                await interaction.response.send_message(f"Role '{role_mention}' not found.", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"Invalid role mention: '{role_mention}'. Please use the `@role` format.", ephemeral=True)
            return

    await user.remove_roles(*roles_to_remove)

    embed = discord.Embed(title="Role Removed", description=f"Removed {', '.join([r.mention for r in roles_to_remove])} role from {user.mention}", color=0xff0000)
    await interaction.response.send_message(embed=embed)
# Token
client.run('')