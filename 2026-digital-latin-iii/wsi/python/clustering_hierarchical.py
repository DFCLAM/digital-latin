import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler

import json
import re
from pathlib import Path

def plot_clusters(terms : list[str]):
    prefix = f'workspace/bert/bert_search_term__{"-".join(terms)}'
    print (f'Plotting for {prefix}')
    bert_result_json_path = Path(__file__).parent / f'{prefix}.json'
    with bert_result_json_path.open('r') as fp:
        bert_result = json.load(fp)

    embeddings = []

    plot_labels = []
    context_max_size = 9 # the left and right context to show in concordances
    for document_key, document in sorted(bert_result.items(), key = lambda tuple: int(re.search(r'\d+', tuple[0]).group())):
        for sentence in document['sentences']:
            for term_index in sentence['term_indexes']:

                sample_uid = re.search(r'\d+', document_key).group() + '_' + str(sentence['index']) + '_' + str(term_index)

                bert = sentence['embeddings'][term_index]
                if not bert['token'] in terms:
                    raise Exception('assertion error: ' + bert['token'] + ' not in (' + ','.join(terms) + ')')
                embeddings.append(bert['embedding'])

                left_context = []
                right_context = []
                for index in range(max(0, term_index - context_max_size), term_index):
                    left_context.append(sentence['embeddings'][index]['token'])
                for index in range(term_index + 1, min(len(sentence['embeddings']), term_index + context_max_size + 1)):
                    right_context.append(sentence['embeddings'][index]['token'])
                plot_labels.append(f'{sample_uid:<16}:   {" ".join(left_context)} *{bert['token']}* {" ".join(right_context)}')

    X = np.array(embeddings)

    # setting distance_threshold=0 ensures we compute the full tree.
    plot_title = f'Agglomerative Clustering Dendrogram - {", ".join(terms)}'
    # model = AgglomerativeClustering(distance_threshold=0, n_clusters=None)
    # model = AgglomerativeClustering(n_clusters=2)
    # model = model.fit(X)

    Z = linkage(X, method='ward')
    plt.figure(figsize=(20, 12))
    dendrogram(Z, orientation='left', labels=plot_labels)
    plt.title(plot_title)
    plt.xlabel("Sample Index")
    plt.ylabel("Distance")
    plt.tight_layout()
    plt.savefig(f'{prefix}.svg')
    plt.savefig(f'{prefix}.png')
    # plt.show()

"""
labels = fcluster(Z, t=2, criterion='maxclust')
assert len(plot_labels) == len(labels)
for label_index, label in enumerate(labels):
    print (f'{plot_labels[label_index]} : {labels[label_index]}')
"""

# terms = ['appositio']
# terms = ['appositio','appositione','appositionem','appositiones','appositionibus']
# terms = ['maneries','maneriei','maneriebus']
for term in ['appositio','appositione','appositionem','appositiones','appositionibus','maneries','maneriei','maneriebus']:
    try:
        plot_clusters([term])
    except Exception as e:
        print (e)

plot_clusters(['appositio','appositione','appositionem','appositiones','appositionibus'])
