from training import ALIMSentencesRestartableGenerator
from gensim.models import Word2Vec
import matplotlib.pyplot as plt
import numpy as np
from statistics import fmean
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import json
import re
from pathlib import Path
import threading
from concurrent.futures import ProcessPoolExecutor

# print(model.wv.similarity('sanctus','petrum'))
# print(model.wv.similarity('sanctus','prologus'))
# print(model.wv.most_similar('sanctus', topn=13))

class HierarchicalClustering:

    def __init__(self, term : str, max_samples_size : int = 0, use_lemma : bool = False, neighbours_similarity_threshold_ratio : float = 0.85) -> None:
        """
        """
        self.term = term
        self.max_samples_size = max_samples_size
        self.use_lemma = use_lemma
        self.neighbours_similarity_threshold_ratio = neighbours_similarity_threshold_ratio

        self.workspace_path = Path(__file__).parent.parent / 'workspace'
        self.w2v_workspace_path = self.workspace_path / 'word2vec'
        if self.use_lemma:
            self.model = Word2Vec.load(str((self.w2v_workspace_path / 'word2vec_cbow_lemmata.model').absolute()))
        else:
            self.model = Word2Vec.load(str((self.w2v_workspace_path / 'word2vec_cbow_forms.model').absolute()))

    def nearest_neighbours(self, sentence : list[str]):
        """
        """
        result = []
        for candidate in sentence:
            if candidate != self.term and candidate in self.model.wv:
                result.append([candidate, self.model.wv.similarity(candidate, self.term)])
        sorted_candidates = [(candidate, similarity) for candidate, similarity in sorted(result, reverse=True, key=lambda item: item[1])]
        if len(sorted_candidates) > 0:
            best_similarity = sorted_candidates[0][1]
            min_similarity = best_similarity * self.neighbours_similarity_threshold_ratio
            print (best_similarity, min_similarity, sorted_candidates)
            return [ candidate for candidate, similarity in sorted_candidates if similarity >= min_similarity]
        return []

    def find_index(self, ss : list[str], s : str):
        """
        list.index() throws an exception if doesn'find the element:
        I need a method which returns -1 instead, because that's why
        """
        for index, item in enumerate(ss):
            if item == s:
                return index
        return -1
    
    def read_document(self, items : list[dict]):
        plot_labels = []
        X = []
        alim_id_pattern = re.compile(r'^\d+')

        for item in items:
            document_dir_path : Path = item['dir']
            m = alim_id_pattern.search(document_dir_path.name)
            if m:
                sample_uid = f'{int(m.group())}_{item["sentence_number"]}'
                # print (sample_uid)
                sentence = []
                if self.use_lemma:
                    sentence = item['lemma_tokens']
                else:
                    sentence = item['tokens']

                term_index = self.find_index(sentence, self.term)
                if (term_index > -1):
                    nearest_neighbours = self.nearest_neighbours(sentence)
                    if (len(nearest_neighbours) > 0):
                        X.append(self.model.wv.get_mean_vector(nearest_neighbours))

                        sent_label_max_size = 21 
                        # always using tokens, not not sentence, because I want to show the actual sentence in label, not the lemmatized one
                        sentence_label = ['*' + item["tokens"][term_index] + '*']
                        distance = 1
                        count = 1
                        while count < sent_label_max_size and distance < sent_label_max_size:
                            if (term_index - distance) >= 0:
                                sentence_label.insert(0, item["tokens"][term_index - distance])
                                count += 1
                            if (term_index + distance) < len(item["tokens"]):
                                sentence_label.append(item["tokens"][term_index + distance])
                                count += 1
                            distance += 1
                        plot_labels.append(f'{sample_uid:<16}:  {" ".join(sentence_label)}')

                        # print (sentence)
                        # print (max(term_index-context_max_size,0),term_index)
                        # print (left_context)
                        # print (term_index+1,min(term_index+context_max_size+1,len(sentence)))
                        # print (right_context)
                    
                # print (len(sentences), end='\n\n')

        return (X, plot_labels)
    
    def plot_clusters(self):

        X = []
        plot_labels = []
        futures = []

        with ProcessPoolExecutor(max_workers=8) as executor:
            slice_size = 4096
            slice = []
            slice_count = 0
            for item in ALIMSentencesRestartableGenerator(self.use_lemma, True):
                slice.append(item)
                slice_count += 1
                if slice_count == slice_size:
                    futures.append(executor.submit(self.read_document, slice))
                    slice = []
                    slice_count = 0
            if len(slice) > 0:
                futures.append(executor.submit(self.read_document, slice))

        for future in futures:
            (X_thd, plot_labels_thd) = future.result()
            X.extend(X_thd)
            plot_labels.extend(plot_labels_thd)
        
        # print (f'Documents traversal done, retrived {len(sentences)} - {len(plot_labels)} sentences.')
        # for i, s in enumerate(sentences[:100]):
        #     print (plot_labels[i], s)

        sampled = False
        if self.max_samples_size and (len(X) > self.max_samples_size):
            sampled = True
            indices = np.random.choice(len(X), self.max_samples_size, replace=False)
            X = [X[index] for index in indices]
            plot_labels = [plot_labels[index] for index in indices]


        plot_title = f'Agglomerative Clustering Dendrogram - {self.term}'
        Z = linkage(X)
        plt.figure(figsize=(20, 12))
        dendrogram(Z, orientation='left', labels=plot_labels)
        plt.title(plot_title)
        plt.xlabel("Sample Index")
        plt.ylabel("Distance")
        plt.tight_layout()
        base = str(self.w2v_workspace_path.absolute() / 'plots')
        prefix = 'word2vec_cbow_' + self.term
        if self.use_lemma:
            prefix += '_lemma'
        if sampled:
            prefix += '_' + str(self.max_samples_size) + '-sampled'
        plt.savefig(f'{base}/{prefix}.svg')
        plt.savefig(f'{base}/{prefix}.png', dpi = 300)
        # plt.show()

if __name__ == "__main__":
    # for term in ['appositio','color','terminatio','dispositio']:
    for term in ['dispositio']:
        for max_samples_size in [0, 50, 30]:
            c = HierarchicalClustering(term, max_samples_size=max_samples_size, use_lemma=True)
            c.plot_clusters()

