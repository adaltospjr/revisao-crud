# app/data_structures/arvore_binaria.py
from typing import Optional, Any

class NoArvore:
    def __init__(self, chave_id: int, valor_conteudo: Any):
        self.id: int = chave_id
        self.produto: Any = valor_conteudo
        self.esquerda: Optional[NoArvore] = None
        self.direita: Optional[NoArvore] = None


class ArvoreProdutosCache:
    _instance = None

    def __new__(cls):
        """Padrão Singleton: Mantém a árvore e a sua raiz persistidas na memória global da API."""
        if cls._instance is None:
            cls._instance = super(ArvoreProdutosCache, cls).__new__(cls)
            cls._instance.raiz = None
        return cls._instance

    def inserir(self, chave_id: int, produto: Any) -> None:
        if self.raiz is None:
            self.raiz = NoArvore(chave_id, produto)
        else:
            self._inserir_recursivo(self.raiz, chave_id, produto)

    def _inserir_recursivo(self, no_atual: NoArvore, chave_id: int, produto: Any) -> None:
        if chave_id == no_atual.id:
            no_atual.produto = produto  # Atualiza caso o ID já exista
            return
        if chave_id < no_atual.id:
            if no_atual.esquerda is None:
                no_atual.esquerda = NoArvore(chave_id, produto)
            else:
                self._inserir_recursivo(no_atual.esquerda, chave_id, produto)
        else:
            if no_atual.direita is None:
                no_atual.direita = NoArvore(chave_id, produto)
            else:
                self._inserir_recursivo(no_atual.direita, chave_id, produto)

    def buscar(self, chave_id: int) -> Optional[Any]:
        return self._buscar_recursivo(self.raiz, chave_id)

    def _buscar_recursivo(self, no_atual: Optional[NoArvore], chave_id: int) -> Optional[Any]:
        if no_atual is None:
            return None
        if chave_id == no_atual.id:
            return no_atual.produto
        if chave_id < no_atual.id:
            return self._buscar_recursivo(no_atual.esquerda, chave_id)
        return self._buscar_recursivo(no_atual.direita, chave_id)

    def deletar(self, chave_id: int) -> None:
        self.raiz = self._deletar_recursivo(self.raiz, chave_id)

    def _deletar_recursivo(self, no_atual: Optional[NoArvore], chave_id: int) -> Optional[NoArvore]:
        if no_atual is None:
            return None

        if chave_id < no_atual.id:
            no_atual.esquerda = self._deletar_recursivo(no_atual.esquerda, chave_id)
        elif chave_id > no_atual.id:
            no_atual.direita = self._deletar_recursivo(no_atual.direita, chave_id)
        else:
            # Caso 1: Nó folha ou apenas um filho
            if no_atual.esquerda is None:
                return no_atual.direita
            elif no_atual.direita is None:
                return no_atual.esquerda

            # Caso 2: Nó com dois filhos (Encontra o menor valor do lado direito)
            sucessor = no_atual.direita
            while sucessor.esquerda is not None:
                sucessor = sucessor.esquerda
                
            no_atual.id = sucessor.id
            no_atual.produto = sucessor.produto
            no_atual.direita = self._deletar_recursivo(no_atual.direita, sucessor.id)

        return no_atual
