import praw
import os, time, random
from dotenv import load_dotenv
import pika

#Gustavo Reyes Romero

print("inicializando reddit_img...")

HOST = os.environ['RABBITMQ_HOST']
print("rabbit:"+HOST)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST,heartbeat=3600,blocked_connection_timeout=1800))
channel = connection.channel()

channel.exchange_declare(exchange='cartero', exchange_type='topic', durable=True)

result = channel.queue_declare(queue="reddit", durable=True)
queue_name = result.method.queue

channel.queue_bind(exchange='cartero', queue=queue_name, routing_key="reddit")

# Credenciales para el acceso a reddit
load_dotenv()
CLIENT_ID=os.getenv('REDDIT_CLIENT_ID')
SECRET=os.getenv('REDDIT_CLIENT_SECRET')

reddit = praw.Reddit(client_id = CLIENT_ID,
                     client_secret = SECRET,
                     user_agent = 'img_searcher v0.1 by /u/ribotzel_e')

#Seleccion de subreddits. 
#Cambio futuro posible: Añadir o quitar subreddits de la lista.
subreddit_list = ["EarthPorn", "FoodPorn", "memes", "wholesomememes"]

print(' [*] Listo y esperando a recibir mensajes.')

def callback(ch, method, properties, body):
        print(body.decode("UTF-8"))
        arguments = body.decode("UTF-8").split(" ")
		
        #Elije un subreddit aleatorio de la lista
        sub = random.choice(subreddit_list)
        if (arguments[0]=="#redditimg"):
            subreddit = reddit.subreddit(sub)
            print("Getting image from subreddit: "+ sub)
            new_ep = subreddit.new(limit = 100)
            submissions = []

            #Se creara una lista con los enlaces de las publicaciones que contengan alguna imagen
            for posts in new_ep:
                if not posts.stickied:
                    url = posts.url
                    if url.endswith(('.jpg', '.png', '.jpeg')):
                        submissions.append(url)
						
            #Elije un enlace al azar y se le asigna el id del canal de discord al cual debe enviar el mensaje
            result = random.choice(submissions) +"\nCH_ID:"+ arguments[1]

            #Envia el mensaje a rabbitmq
            print("send a new message to rabbitmq: "+result)
            channel.basic_publish(exchange='cartero',routing_key="discord_writer",body=result)

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()



