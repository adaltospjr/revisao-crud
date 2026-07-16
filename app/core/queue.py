from confluent_kafka import Producer
from app.core.config import settings
import json
import logging

class KafkaProducerConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KafkaProducerConnection, cls).__new__(cls)
            configuracao = {
                'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
                'client.id': 'api-produtos-enterprise'
            }
            
            cls._instance.producer = Producer(configuracao)
        return cls._instance

    def _callback_entrega(self, erro, mensagem):
        if erro is not None:
            logging.error(f"Falha ao entregar evento no Kafka: {erro}")
        else:
            logging.info(f"Evento entregue com sucesso no tópico {mensagem.topic()}")

    def disparar_evento(self, topico: str, chave: str, payload: dict) -> None:
        dados_json = json.dumps(payload)
        
        try:
            self.producer.produce(
                topic=topico,
                key=str(chave),
                value=dados_json,
                callback=self._callback_entrega
            )
            self.producer.flush()
        except BufferError:
            logging.warning("Fila interna do Kafka cheia, aguardando liberação...")
            self.producer.poll(0.1)
