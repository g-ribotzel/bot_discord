import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
import threading
import pika

############ CONEXION RABBITMQ ##############

HOST = os.environ['RABBITMQ_HOST']
print("rabbit:"+HOST)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=HOST,heartbeat=3600,blocked_connection_timeout=1800))
channelMQ = connection.channel()

#Creamos el exchange 'cartero' de tipo 'fanout'
channelMQ.exchange_declare(exchange='cartero', exchange_type='topic', durable=True)

#############################################

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

print(TOKEN+" "+GUILD)
bot = commands.Bot(command_prefix='#')

bot.updown = 0

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )
	
    for server in bot.guilds: 
        print("Server name: "+str(server)+" "+str(server.id))
        for channel in server.channels: 
            print(str(channel)+" "+str(channel.id))
            if channel.permissions_for(server.me).send_messages and type(channel) is discord.TextChannel:
                ch = bot.get_channel(channel.id)
                #await ch.send('Bot listo.')
                print("can send message!")
                break
        members = '\n - '.join([member.name for member in server.members])
        print(f'Guild Members:\n - {members}')
        print("\n")
    print("KawaiiOgreBot listo para recibir comandos.")



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == 'pizza' or message.content == 'cerveza' or message.content == 'donuts':
        response = "!mmm..."+message.content+"!"
        await message.channel.send(response)
    if message.content == 'sube':
        bot.updown += 1
        response = "Sube un peldaño... \\[`A´]/ \nPeldaño numero: "+ str(bot.updown)
        await message.channel.send(response)
    if message.content == 'baja':
        bot.updown -= 1
        response = "Baja un peldaño... /[´-`]\\  \nPeldaño numero: "+ str(bot.updown)
        await message.channel.send(response)
    await bot.process_commands(message)
    
@bot.command(name='birthday', help='Muestra la fecha de cumpleaño del miembro de la GUILD que se pasa en parámetro. Ejemplo: !birthday MatthieuVernier')
async def birthday(ctx):
    message =  ctx.message.content + " " + str(ctx.channel.id)
    print("send a new mesage to rabbitmq: "+message)
    channelMQ.basic_publish(exchange='cartero', routing_key="birthday", body=message)

@bot.command(name='add-birthday', help='Permite añadir el cumpleaño de un nuevo miembro de la GUILD que se pasa en parámetro. Ejemplo: !birthday MatthieuVernier 1985-02-13')
async def birthday(ctx):
    message =  ctx.message.content
    print("send a new mesage to rabbitmq: "+message)
    channelMQ.basic_publish(exchange='cartero', routing_key="birthday", body=message)

@bot.command(name='redditimg', help='Una imagen aleatoria de una pequeña seleccion de subreddits definidos')
async def post_image(ctx):
    message = ctx.message.content + " " + str(ctx.channel.id)
    print("send a new message to rabbitmq: " + message)
    channelMQ.basic_publish(exchange='cartero', routing_key="reddit", body=message)


############ CONSUMER ###############

import threading
import asyncio

def writer(bot):
    """thread worker function"""
    print('Worker')

    HOST = os.environ['RABBITMQ_HOST']

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=HOST,heartbeat=3600,blocked_connection_timeout=1800))
    channelMQ = connection.channel()

    #Creamos el exchange 'cartero' de tipo 'fanout'
    channelMQ.exchange_declare(exchange='cartero', exchange_type='topic', durable=True)

    #Se crea un cola temporaria exclusiva para este consumidor (búzon de correos)
    result = channelMQ.queue_declare(queue="discord_writer", exclusive=True, durable=True)
    queue_name = result.method.queue

    #La cola se asigna a un 'exchange'
    channelMQ.queue_bind(exchange='cartero', queue=queue_name, routing_key="discord_writer")


    print(' [*] Waiting for messages. To exit press CTRL+C')

    async def write(message, id):
        channel = bot.get_channel(id)#913706828502814760
        await channel.send(message)

    def callback(ch, method, properties, body):
        message=body.decode("UTF-8").split("\nCH_ID:")
        front_msg = message[0]
        back_id = int(message[1]);
        print(message)
        bot.loop.create_task(write(front_msg, back_id))

    channelMQ.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channelMQ.start_consuming()

t = threading.Thread(target=writer, args=[bot])
t.start()

########################################


bot.run(TOKEN)
