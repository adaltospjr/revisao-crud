# app/services/produto_service.py
import json
from typing import List, Optional
from fastapi import HTTPException, status
from app.domain.interfaces import IProdutoRepository
from app.domain.models import ProdutoModel
from app.domain.schemas import ProdutoCreate
from app.data_structures.arvore_binaria import ArvoreProdutosCache
from app.core.cache import RedisCacheConnection
from app.core.queue import KafkaProducerConnection

class ProdutoService:
    def __init__(self, produto_repository: IProdutoRepository):
        self.repo = produto_repository
        self.arvore_cache = ArvoreProdutosCache()
        self.redis_cache = RedisCacheConnection()
        self.kafka_queue = KafkaProducerConnection()

    def criar_produto(self, schema_produto: ProdutoCreate) -> ProdutoModel:

        produto_existente = self.repo.buscar_por_id(schema_produto.id)
        if produto_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produto com ID {schema_produto.id} já existe no banco."
            )

        novo_model = ProdutoModel(
            id=schema_produto.id,
            nome=schema_produto.nome,
            preco=schema_produto.preco,
            descricao=schema_produto.descricao
        )
        
        produto_salvo = self.repo.criar(novo_model)
        self.arvore_cache.inserir(produto_salvo.id, produto_salvo)
        payload_dados = {"id": produto_salvo.id, "nome": produto_salvo.nome, "preco": produto_salvo.preco, "descricao": produto_salvo.descricao}
        self.redis_cache.definir(f"produto:{produto_salvo.id}", json.dumps(payload_dados), expiracao_segundos=1800)

        self.kafka_queue.disparar_evento(
            topico="eventos-produtos",
            chave=str(produto_salvo.id),
            payload={"evento": "PRODUTO_CRIADO", "dados": payload_dados}
        )

        return produto_salvo

    def obter_por_id(self, id_produto: int) -> ProdutoModel:
        """Fluxo Triplo de Busca de Alta Performance: Redis ➔ Árvore Binária ➔ Postgres"""
        
        # Camada de Cache 1: Tenta buscar no Redis
        dados_redis = self.redis_cache.buscar(f"produto:{id_produto}")
        if dados_redis:
            dados = json.loads(dados_redis)
            return ProdutoModel(**dados)

        # Camada de Cache 2: Se falhar o Redis, faz a varredura O(log n) na Árvore Binária
        dados_arvore = self.arvore_cache.buscar(id_produto)
        if dados_arvore:
            # Reabastece o Redis para manter a consistência mais rápida
            payload = {"id": dados_arvore.id, "nome": dados_arvore.nome, "preco": dados_arvore.preco, "descricao": dados_arvore.descricao}
            self.redis_cache.definir(f"produto:{id_produto}", json.dumps(payload))
            return dados_arvore

        # Camada Física 3: Se não achar em nenhum cache, faz a query estrutural no PostgreSQL
        produto_db = self.repo.buscar_por_id(id_produto)
        if not produto_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {id_produto} não localizado."
            )

        # Alimenta as duas camadas de cache com a resposta do banco de dados físico
        self.arvore_cache.inserir(produto_db.id, produto_db)
        payload_db = {"id": produto_db.id, "nome": produto_db.nome, "preco": produto_db.preco, "descricao": produto_db.descricao}
        self.redis_cache.definir(f"produto:{id_produto}", json.dumps(payload_db))

        return produto_db

    def listar_todos_produtos(self) -> List[ProdutoModel]:
        # Para listagem geral profissional, a leitura varre o banco físico diretamente
        return self.repo.listar_todos()

    def deletar_produto(self, id_produto: int) -> None:
        # 1. Tenta deletar fisicamente do Postgres
        deletado = self.repo.deletar(id_produto)
        if not deletado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Não foi possível deletar: Produto com ID {id_produto} não existe."
            )

        # 2. Invalida/Remove o produto da nossa Árvore Binária de Busca em memória RAM
        self.arvore_cache.deletar(id_produto)

        # 3. Remove a chave correspondente do Redis
        self.redis_cache.deletar(f"produto:{id_produto}")

        # 4. Dispara o evento de deleção para o barramento do Kafka
        self.kafka_queue.disparar_evento(
            topico="eventos-produtos",
            chave=str(id_produto),
            payload={"evento": "PRODUTO_DELETADO", "id_produto": id_produto}
        )
