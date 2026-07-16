import json
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.domain.models import ProdutoModel
from app.domain.schemas import ProdutoCreate
from app.repositories.produto_repository import ProdutoRepository  # Importado para cá
from app.data_structures.arvore_binaria import ArvoreProdutosCache
from app.core.cache import RedisCacheConnection
from app.core.queue import KafkaProducerConnection

class ProdutoService:
    def __init__(self, db_session: Session):
        """O Service agora encapsula o repositório, recebendo apenas a sessão do banco."""
        self.repo = ProdutoRepository(db_session)
        
        # Injeta os Singletons internos
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
        dados_redis = self.redis_cache.buscar(f"produto:{id_produto}")
        if dados_redis:
            dados = json.loads(dados_redis)
            return ProdutoModel(**dados)

        dados_arvore = self.arvore_cache.buscar(id_produto)
        if dados_arvore:
            payload = {"id": dados_arvore.id, "nome": dados_arvore.nome, "preco": dados_arvore.preco, "descricao": dados_arvore.descricao}
            self.redis_cache.definir(f"produto:{id_produto}", json.dumps(payload))
            return dados_arvore

        produto_db = self.repo.buscar_por_id(id_produto)
        if not produto_db:
            raise HTTPException(status_code=404, detail=f"Produto com ID {id_produto} não localizado.")

        self.arvore_cache.inserir(produto_db.id, produto_db)
        payload_db = {"id": produto_db.id, "nome": produto_db.nome, "preco": produto_db.preco, "descricao": produto_db.descricao}
        self.redis_cache.definir(f"produto:{id_produto}", json.dumps(payload_db))
        return produto_db

    def listar_todos_produtos(self) -> List[ProdutoModel]:
        return self.repo.listar_todos()

    def deletar_produto(self, id_produto: int) -> None:
        deletado = self.repo.deletar(id_produto)
        if not deletado:
            raise HTTPException(status_code=404, detail=f"Produto com ID {id_produto} não existe.")

        self.arvore_cache.deletar(id_produto)
        self.redis_cache.deletar(f"produto:{id_produto}")
        self.kafka_queue.disparar_evento(
            topico="eventos-produtos",
            chave=str(id_produto),
            payload={"evento": "PRODUTO_DELETADO", "id_produto": id_produto}
        )
