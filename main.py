import discord
from discord.ext import commands

permissoes = discord.Intents.default()
permissoes.message_content = True
permissoes.members = True

bot = commands.Bot(command_prefix=".", intents=permissoes)

@bot.command()
async def teste(ctx: commands.Context):
    usuario = ctx.author
    canal = ctx.channel
    await ctx.reply(f'{usuario.display_name} \n{canal.name}')

@bot.command()
async def img(ctx: commands.Context):
    meu_embed = discord.Embed(title="CARALHOOOOOOOO", description="Caralinho voador", )
    img_embed = discord.File('imgs/buseta.jpg', 'buseta.jpg')
    meu_embed.set_image(url='attachment://buseta.jpg')

    await ctx.reply(file=img_embed, embed=meu_embed)

@bot.event
async def on_member_join(membro:discord.Member):
    canal = bot.get_channel(1009289951474614323)
    await canal.send(f'{membro.mention} Mais um fudido kkkkkkkkkkkkk')

@bot.event
async def on_member_remove(membro:discord.Member):
    canal = bot.get_channel(1009289951474614323)
    await canal.send(f'{membro.display_name} Não aguentou ser fudido kkkkkkkkkkkk')







bot.run("MTI1Nzc4NjE3MzI1MDg2MzE3NA.GeexZv.n4HohzyNBGssroLdZ7w3y6OnCZPKbclUxVhiXo")