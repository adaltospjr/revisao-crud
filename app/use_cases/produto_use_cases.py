import json
from typing import Optional

from fastapi import HTTPException, status

from app.domain.interfaces import ICache, IEventPublisher, IProdutoRepository
from app.domain.models import ProdutoModel
from app.domain.schemas import ProdutoCreate


class CriarProdutoUseCase:
    def __init__(
        self,
        repo: IProdutoRepository,
        cache: Optional[ICache] = None,
        event_publisher: Optional[IEventPublisher] = None,
    ):
        self.repo = repo
        self.cache = cache
        self.event_publisher = event_publisher

    def executar(self, schema_produto: ProdutoCreate) -> ProdutoModel:
        produto_existente = self.repo.buscar_por_id(schema_produto.id)
        if produto_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produto com ID {schema_produto.id} já existe no banco.",
            )

        novo_model = ProdutoModel(
            id=schema_produto.id,
            nome=schema_produto.nome,
            preco=schema_produto.preco,
            descricao=schema_produto.descricao,
        )

        produto_salvo = self.repo.criar(novo_model)
        payload_dados = self._montar_payload(produto_salvo)

        if self.cache is not None:
            self.cache.definir(f"produto:{produto_salvo.id}", json.dumps(payload_dados), expiracao_segundos=1800)

        if self.event_publisher is not None:
            self.event_publisher.disparar_evento(
                topico="eventos-produtos",
                chave=str(produto_salvo.id),
                payload={"evento": "PRODUTO_CRIADO", "dados": payload_dados},
            )

        return produto_salvo

    def _montar_payload(self, produto: ProdutoModel) -> dict:
        return {
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco,
            "descricao": produto.descricao,
        }
