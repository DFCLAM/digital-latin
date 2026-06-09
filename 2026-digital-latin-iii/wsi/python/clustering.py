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

bert_result_json_path = Path(__file__).parent / 'workspace/bert/bert_search_term__maneries__paragraphs_context_window__7.json'
with bert_result_json_path.open('r') as fp:
    bert_result = json.load(fp)

embeddings = []
labels = []
for document_key, document in bert_result.items():
    for paragraph_key, paragraph in document.items():
        for bert in paragraph['bert']:
            if bert['token'] == term:
                embeddings.append(bert['embedding'])
                labels.append(re.search(r'\d+', document_key).group() + '_' + paragraph_key[10:16])

X = np.array(embeddings)

# 2. Scale the data (Crucial: distance metrics are sensitive to varying scales)
X_scaled = StandardScaler().fit_transform(X)

# 3. Fit Agglomerative Clustering
# n_clusters: The target number of clusters to find
# linkage: 'ward' minimizes variance of merged clusters. Other options: 'complete', 'average', 'single'
hierarchical_model = AgglomerativeClustering(n_clusters=2, linkage='ward')
cluster_labels = hierarchical_model.fit_predict(X_scaled)

# 4. Generate Linkage Matrix and Plot Dendrogram (Using Scipy)
# Note: 'ward' linkage in AgglomerativeClustering requires Euclidean distance
linkage_matrix = linkage(X_scaled, method='ward')

plt.figure(figsize=(12, 8))

# Plot 1: Dendrogram
plt.subplot(1, 1, 1)
dendrogram(linkage_matrix, labels=cluster_labels, show_leaf_counts=True, truncate_mode=None)
plt.title("Hierarchical Clustering Dendrogram")
plt.xlabel("Sample Index")
plt.ylabel("Distance Threshold")

# # Plot 2: Scatter Plot of Assignments (Visualizing 2 out of 4 features)
# plt.subplot(1, 2, 2)
# sns.scatterplot(x=X_scaled[:, 0], y=X_scaled[:, 1], hue=cluster_labels, palette='Set1', s=70)
# plt.title("Assigned Cluster Labels (First 2 Dimensions)")
# plt.xlabel("Feature 1 (Scaled)")
# plt.ylabel("Feature 2 (Scaled)")

plt.tight_layout()
plt.show()

