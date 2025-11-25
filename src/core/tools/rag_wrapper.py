def rag_retriever_wrapper(context_engine):
    def retrieve(query, k=None):
        res = context_engine.retrieve(query)
        if k: res = res[:k]
        return res, [{"source": "context"}] * len(res)
    return retrieve