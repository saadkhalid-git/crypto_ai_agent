from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from sentence_transformers import CrossEncoder

# Load and preprocess data
def prepare_rag():
    loader = TextLoader("data/crypto_banter_content.txt")
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()
    vector_db = Chroma.from_documents(texts, embeddings)

    # Hybrid retriever (BM25 + Semantic)
    bm25_retriever = BM25Retriever.from_documents(texts)
    semantic_retriever = vector_db.as_retriever()
    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, semantic_retriever], weights=[0.4, 0.6])

    # Re-ranking with CrossEncoder
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank_documents(query, documents):
        scores = cross_encoder.predict([(query, doc.page_content) for doc in documents])
        ranked_docs = [doc for _, doc in sorted(zip(scores, documents), reverse=True)]
        return ranked_docs

    return ensemble_retriever, rerank_documents