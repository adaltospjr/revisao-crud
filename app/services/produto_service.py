import json
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.domain.interfaces import ICache, IEventPublisher, IProdutoRepository
from app.domain.models import ProdutoModel
from app.domain.schemas import ProdutoCreate
from app.repositories.produto_repository import ProdutoRepository
from app.core.cache import RedisCacheConnection
from app.core.queue import KafkaProducerConnection
from app.use_cases.produto_use_cases import CriarProdutoUseCase


class ProdutoService:
    def __init__(
        self,
        repo: Optional[IProdutoRepository] = None,
        cache: Optional[ICache] = None,
        event_publisher: Optional[IEventPublisher] = None,
        db_session: Optional[Session] = None,
    ):
        if repo is None:
            if db_session is None:
                raise ValueError("db_session é obrigatório quando repo não for fornecido")
            repo = ProdutoRepository(db_session)

        self.repo = repo
        self.cache = cache or RedisCacheConnection()
        self.event_publisher = event_publisher or KafkaProducerConnection()
        self.criar_produto_use_case = CriarProdutoUseCase(
            repo=self.repo,
            cache=self.cache,
            event_publisher=self.event_publisher,
        )

    def criar_produto(self, schema_produto: ProdutoCreate) -> ProdutoModel:
        return self.criar_produto_use_case.executar(schema_produto)

    def obter_por_id(self, id_produto: int) -> ProdutoModel:
        dados_redis = self.cache.buscar(f"produto:{id_produto}")
        if dados_redis:
            dados = json.loads(dados_redis)
            return ProdutoModel(**dados)

        produto_db = self.repo.buscar_por_id(id_produto)
        if not produto_db:
            raise HTTPException(status_code=404, detail=f"Produto com ID {id_produto} não localizado.")

        payload_db = self._montar_payload(produto_db)
        self.cache.definir(f"produto:{id_produto}", json.dumps(payload_db))
        return produto_db

    def listar_todos_produtos(self) -> List[ProdutoModel]:
        return self.repo.listar_todos()

    def deletar_produto(self, id_produto: int) -> None:
        deletado = self.repo.deletar(id_produto)
        if not deletado:
            raise HTTPException(status_code=404, detail=f"Produto com ID {id_produto} não existe.")

        self.cache.deletar(f"produto:{id_produto}")
        self.event_publisher.disparar_evento(
            topico="eventos-produtos",
            chave=str(id_produto),
            payload={"evento": "PRODUTO_DELETADO", "id_produto": id_produto},
        )

    def _montar_payload(self, produto: ProdutoModel) -> dict:
        return {
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco,
            "descricao": produto.descricao,
        }
