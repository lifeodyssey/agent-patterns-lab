# Retrieval（离线检索基建）

## 解决的问题

RAG 系列模式离不开检索。但为了学习与回归，我们通常更希望检索是：

- 离线、确定性的检索
- 小语料可复现实验

本仓库内置一个极简的词频索引，让 examples/tests 永远不依赖网络或向量库。

## 它是如何运作的（本仓库实现）

- `Document(doc_id, text, meta?)`：最小文档容器。
- `SimpleSearchIndex(docs)`：对每个文档做一次简单 tokenize（只保留字母数字）。
- `search(query, k=5)`：按 **query term 的词频和** 打分（不区分大小写）。

它很原始。但优点是：你能一眼看懂“为什么命中”。

## 什么时候用 / 什么时候别用

适合用在：

- 想做离线 demo/test 的 RAG 系列模式
- 想要稳定的回归基线（deterministic）

不适合拿去做生产检索：

- 没有语义匹配（同义词不行）
- 排序质量没保证
- 没有 chunking / embeddings / 时效性策略

## 一个能对照的例子

```python
from agent_patterns_lab.runtime import Document, SimpleSearchIndex

docs = [
    Document(doc_id="rag", text="RAG retrieves relevant documents and uses them as context."),
    Document(doc_id="react", text="ReAct alternates reasoning and tool use."),
]

index = SimpleSearchIndex(docs)
hits = index.search("rag context", k=3)

for h in hits:
    print(h.doc.doc_id, h.score)
```

## 常见失败模式与对策

- **query 为空**：直接返回 `[]`（本仓库这么做）。
- **tokenize 太粗糙**：正常，这就是教学用检索器。
- **“测试里好用，线上就不行”**：升级到 embeddings 时，尽量保留接口不变，然后跑同一套 eval 做对比。

## 本仓库对应代码

- 实现： [`src/agent_patterns_lab/runtime/retrieval.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/retrieval.py)
- 语料：`data/mini_corpus.jsonl`
- 测试： [`tests/test_retrieval.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_retrieval.py)
