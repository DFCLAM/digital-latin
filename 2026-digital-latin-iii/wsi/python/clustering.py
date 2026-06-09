import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler

import json
import re
from pathlib import Path

# 1. Generate synthetic high-dimensional data
# X, y = make_blobs(n_samples=50, centers=3, n_features=4, random_state=42)

term = 'maneries'

bert_result_json_path = Path(__file__).parent / 'workspace/bert/bert_search_term__maneries.json'
with bert_result_json_path.open('r') as fp:
    bert_result = json.load(fp)

embeddings = []
labels = []
for document_key, document in bert_result.items():
    for sentence in document['sentences']:
        for term_index in sentence['term_indexes']:
            bert = sentence['embeddings'][term_index]
            if bert['token'] != term:
                raise Exception('assertion error')
            embeddings.append(bert['embedding'])
            labels.append(re.search(r'\d+', document_key).group() + '_' + str(sentence['index']) + '_' + str(term_index))

X = np.array(embeddings)

# setting distance_threshold=0 ensures we compute the full tree.
# model = AgglomerativeClustering(distance_threshold=0, n_clusters=None)
model = AgglomerativeClustering(n_clusters=2)
model = model.fit(X)

Z = linkage(X, method='ward')
plt.figure(figsize=(12, 6))
dendrogram = dendrogram(Z, labels=labels)
plt.title("Agglomerative Clustering Dendrogram (One Leaf Per Sample)")
plt.xlabel("Sample Index")
plt.ylabel("Distance")
plt.show()