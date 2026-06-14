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

    def __init__(self, term : str, size : int, use_lemma : bool = False, max_samples_size : int = 0) -> None:
        """
        """
        self.term = term
        self.size = size
        self.use_lemma = use_lemma
        self.max_samples_size = max_samples_size

        self.workspace_path = Path(__file__).parent.parent / 'workspace'
        self.w2v_workspace_path = self.workspace_path / 'word2vec'
        if self.use_lemma:
            self.model = Word2Vec.load(str((self.w2v_workspace_path / 'word2vec_lemmata.model').absolute()))
        else:
            self.model = Word2Vec.load(str((self.w2v_workspace_path / 'word2vec_forms.model').absolute()))

    def nearest_neighbours(self, sentence : list[str]):
        """
        """
        result = []
        for candidate in sentence:
            if candidate != self.term and candidate in self.model.wv:
                result.append([candidate, self.model.wv.similarity(candidate, self.term)])
        return [ candidate for candidate, _ in sorted(result, reverse=True, key=lambda item: item[1])[:self.size] ]

    def pairwise_distance(self, s1 : list[str], s2 : list[str]) :
        """
        """

        # Step 1
        # Using model.wv.similarity, find the n most similar words (!= term) in each sentence
        nearest_neighbours_1 = self.nearest_neighbours(s1)
        nearest_neighbours_2 = self.nearest_neighbours(s2)

        # Step 2
        # For each list of neighbours, calculate the n most similar
        most_similar_1 = [key for key, _ in self.model.wv.most_similar(nearest_neighbours_1, topn=self.size+1) if key != self.term][:self.size]
        most_similar_2 = [key for key, _ in self.model.wv.most_similar(nearest_neighbours_2, topn=self.size+1) if key != self.term][:self.size]

        # Step 3
        # Compute the cross-wise similarity between neighpours
        distance = fmean([self.model.wv.n_similarity(nearest_neighbours_1, most_similar_2), self.model.wv.n_similarity(nearest_neighbours_2, most_similar_1)])

        # distance = np.sqrt(2 * distance) # convert to euclidean
        print (f'Mean distance {distance} between {nearest_neighbours_1} and {most_similar_2} and between {nearest_neighbours_2} and {most_similar_1}')
        return distance

    def condensed_distance_matrix(self, sentences : list[list[str]]):
        """
        """
        result = []
        for index, s1 in enumerate(sentences):
            for s2 in sentences[index+1:]:
                result.append(self.pairwise_distance(s1, s2))
        return result
    
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
        sentences = []
        context_max_size = 9 # the left and right context to show in concordances
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
                    sentences.append(sentence)
                    left_context = sentence[max(term_index-context_max_size,0):term_index]
                    right_context = sentence[term_index+1:min(term_index+context_max_size+1,len(sentence))]
                    plot_labels.append(f'{sample_uid:<16}:  {" ".join(left_context)} *{self.term}* {" ".join(right_context)}')
                    # print (sentence)
                    # print (max(term_index-context_max_size,0),term_index)
                    # print (left_context)
                    # print (term_index+1,min(term_index+context_max_size+1,len(sentence)))
                    # print (right_context)
                    
                # print (len(sentences), end='\n\n')

        return (sentences, plot_labels)
    
    def plot_clusters(self):

        sentences = []
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
            (sentences_thd, plot_labels_thd) = future.result()
            sentences.extend(sentences_thd)
            plot_labels.extend(plot_labels_thd)
        
        print (f'Documents traversal done, retrived {len(sentences)} - {len(plot_labels)} sentences.')
        for i, s in enumerate(sentences[:100]):
            print (plot_labels[i], s)

        if self.max_samples_size and (len(sentences) > self.max_samples_size):
            indices = np.random.choice(len(sentences), self.max_samples_size, replace=False)
            sentences = [sentences[index] for index in indices]
            plot_labels = [plot_labels[index] for index in indices]
            print (f'downsampled to {len(sentences)}.')
            for i, s in enumerate(sentences):
                print (plot_labels[i], s)

        condensed_distance_matrix = self.condensed_distance_matrix(sentences)

        plot_title = f'Agglomerative Clustering Dendrogram - {self.term}'
        Z = linkage(condensed_distance_matrix, method='complete', optimal_ordering=True)
        plt.figure(figsize=(20, 12))
        dendrogram(Z, orientation='left', labels=plot_labels)
        plt.title(plot_title)
        plt.xlabel("Sample Index")
        plt.ylabel("Distance")
        plt.tight_layout()
        # plt.savefig(f'{base}plots/{prefix}{suffix}.svg')
        # plt.savefig(f'{base}plots/{prefix}{suffix}.png', dpi = 300)
        plt.show()

if __name__ == "__main__":
    c = HierarchicalClustering("appositio", 1, use_lemma=False, max_samples_size=50)
    c.plot_clusters()

