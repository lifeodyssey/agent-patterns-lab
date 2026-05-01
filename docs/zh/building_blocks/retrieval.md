# Retrieval（离线检索基建）

## 解决的问题

RAG 系列模式离不开检索。为了学习与回归，我们希望：

- 离线、确定性的检索
- 小语料可复现实验

本仓库内置一个极简的词频索引。

## 本仓库对应代码

- 实现： [`src/agent_patterns_lab/runtime/retrieval.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/src/agent_patterns_lab/runtime/retrieval.py)
- 语料：`data/mini_corpus.jsonl`
- 测试： [`tests/test_retrieval.py`](https://github.com/lifeodyssey/agent-patterns-lab/blob/main/tests/test_retrieval.py)

