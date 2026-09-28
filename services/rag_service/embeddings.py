from fastembed import TextEmbedding


MODEL_NAME = "BAAI/bge-small-en-v1.5"

embedding_model = TextEmbedding(
    model_name=MODEL_NAME
)


def generate_embedding(text: str):
    embedding = list(
        embedding_model.embed([text])
    )[0]

    return embedding.tolist()