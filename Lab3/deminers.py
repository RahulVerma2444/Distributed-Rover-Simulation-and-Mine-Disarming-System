import time
import grpc
import rover_pb2_grpc
import rover_pb2
import hashlib
import pika
import json

def run():
    deminerNumber = input("Input deminer number:") #get rover number from user

    #Demine_Queue Channel Subscribe------------------------------------------
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()    

    queue = channel.queue_declare(queue='Demine_Queue_notify')
    queue = channel.queue_declare(queue='Defused_Mines2_notify')
    queue_name = queue.method.queue

    channel.queue_bind(
        exchange='Demine_Queue',
        queue=queue_name,
        routing_key='Demine_Queue.notify')
    
    

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        global pin
        payload = json.loads(body)
        print('[x] Demine_Queue information:')
        print(f"Deminer id: {deminerNumber}")
        print(f" [x] {body}")
        pin = payload['pin']
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Publishing to Defused_Mines2")
        body = str(pin)
        ch.basic_publish( #publish to Defused_Mines2 channel
            exchange = 'Defused_Mines2',
            routing_key='Defused_Mines2.notify',
            body=str(pin)
        )
        
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback)

    channel.start_consuming()
    connection.close()
    

if __name__ == "__main__":
    run()