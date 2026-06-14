import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import json
import re
from pathlib import Path

def plot_clusters(terms : list[str], max_samples_size : int = 0, use_cls : bool = False):

    base = str((Path(__file__).parent.parent / 'workspace/bert/').absolute()) + '/'
    prefix = f'bert_search_term__{"-".join(terms)}'
    suffix = '_use_cls' if use_cls else ''
    suffix = f'_{max_samples_size}-sample' if max_samples_size else ''

    if Path(f'{base}plots/{prefix}{suffix}.svg').exists():
        print (f'Skipping {prefix}')
        return

    print (f'Plotting for {prefix}')
    bert_result_json_path = Path(__file__).parent / f'{base}{prefix}.json'
    with bert_result_json_path.open('r') as fp:
        bert_result = json.load(fp)

    embeddings = []

    plot_labels = []
    context_max_size = 9 # the left and right context to show in concordances
    for document_key, document in sorted(bert_result.items(), key = lambda tuple: int(re.search(r'\d+', tuple[0]).group())):
        for sentence in document['sentences']:
            for term_index in sentence['term_indexes']:

                sample_uid = re.search(r'\d+', document_key).group() + '_' + str(sentence['index']) + '_' + str(term_index)

                if use_cls:
                    bert = sentence['embeddings'][0]
                    if not bert['token'] == '[CLS]':
                        raise Exception('assertion error: ' + bert['token'] + ' != \'[CLS]\'')
                else:
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
                plot_labels.append(f'{sample_uid:<16}:   {" ".join(left_context)} *{sentence['embeddings'][term_index]['token']}* {" ".join(right_context)}')
                # print(f'{sample_uid:<16}:   {" ".join(left_context)} *{sentence['embeddings'][term_index]['token']}* {" ".join(right_context)}')

    X = np.array(embeddings)
    # print(len(X))
    # for index, sample in enumerate(X):
    #     print (index, sample[:5])
    # print (len(X), max_samples_size)
    if max_samples_size and (len(X) > max_samples_size):
        indices = np.random.choice(len(X), max_samples_size, replace=False)
        X = X[indices]
        # print(plot_labels)
        plot_labels = np.array(plot_labels)[indices].tolist() # to avoid "only integer scalar arrays can be converted to a scalar index"
        # print(plot_labels)
        # print()
        # print(len(X))
        # for index, sample in enumerate(X):
            # print (index, sample[:5])
    else:
        # orribile ma ora non ho tempo
        suffix = '_use_cls' if use_cls else '' 
        if Path(f'{base}plots/{prefix}{suffix}.svg').exists():
            print (f'Skipping {prefix}')
            return

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
    plt.savefig(f'{base}plots/{prefix}{suffix}.svg')
    plt.savefig(f'{base}plots/{prefix}{suffix}.png', dpi = 300)
    # plt.show()

max_samples_size = 30
use_cls = False
for term in ['appositio','appositione','appositionem','appositiones','appositionibus',
             'maneries','maneriei','maneriebus',
             'mutatio','mutatione','mutationem','mutationes',
             'terminatio','terminationes','terminatione','terminationem','terminationibus','terminationis',
             'dispositio','dispositione','dispositionem','dispositionis','dispositiones','dispositionibus',
             'prologus','prologum','prologi',
             'dictamen','dictaminis','dictamine','dictaminum','dictaminibus',
             'color','colore','colores','coloris','coloribus','colorem','colorum',
            #  'modo','modum','modis','modus','modi','modos','modorum',
             ]:
    try:
        plot_clusters([term], max_samples_size, use_cls)
    except Exception as e:
        print (e)
# plot_clusters(['dispositio'], 50)
