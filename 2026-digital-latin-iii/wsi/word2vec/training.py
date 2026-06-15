import csv
import re
from gensim.models import Word2Vec
from pathlib import Path

workspace_path = Path(__file__).parent.parent / 'workspace'

discarding_poses = set()
discarding_poses.add('PUNCT')
discarding_poses.add('X')

def path_key_function_for_comp(path : Path):
    m = re.search(r'\d+', path.name)
    if m:
        return int(m.group())
    return -1

class ALIMSentencesRestartableGenerator:

    def __init__(self, use_lemmas : bool = False, complete_output : bool = False) -> None:
        self.use_lemmas = use_lemmas
        self.complete_output = complete_output
        pass

    def __iter__(self):

        for document_dir_path in sorted((workspace_path / 'alim').iterdir(), key=path_key_function_for_comp):
            if document_dir_path.is_dir():
                cltk_conllu_path = document_dir_path / 'cltk_conllu.txt'
                sentence_count = 0
                if cltk_conllu_path.exists():
                    tokens = []
                    lemma_tokens = []
                    with cltk_conllu_path.open('r') as cltk_conllu_fp:
                        reader = csv.reader(cltk_conllu_fp, delimiter='\t', quoting=csv.QUOTE_NONE)
                        for row in reader:

                            if len(row) < 4:
                                continue
                            
                            id = int(row[0])
                            form, lemma, upos = row[1:4]
                            
                            if upos in discarding_poses:
                                continue

                            if id == 1 and len(tokens) > 0:
                                sentence_count += 1
                                if self.complete_output:
                                    yield {'dir' : document_dir_path, 'sentence_number' : sentence_count, 'tokens' : tokens, 'lemma_tokens' : lemma_tokens}
                                elif self.use_lemmas:
                                    yield lemma_tokens
                                else:
                                    yield tokens
                                tokens = []
                                lemma_tokens = []

                            lemma_tokens.append(lemma)
                            tokens.append(form.lower())
                    
                    if len(tokens) > 0: # last sentence
                        sentence_count += 1
                        if self.complete_output:
                            yield {'dir' : document_dir_path, 'sentence_number' : sentence_count, 'tokens' : tokens, 'lemma_tokens' : lemma_tokens}
                        elif self.use_lemmas:
                            yield lemma_tokens
                        else:
                            yield tokens

if __name__ == "__main__":
    # for tokens in ALIMSentencesRestartableGenerator(use_lemmas=False):
    #     print (tokens)

    # model = Word2Vec(sentences=ALIMSentencesRestartableGenerator(use_lemmas=False), vector_size=100, window=20, sample=1e-3, workers=8, sg=1)
    # model.save(str((workspace_path / "word2vec/word2vec_forms.model").absolute()))
    # model = Word2Vec(sentences=ALIMSentencesRestartableGenerator(use_lemmas=True), vector_size=100, window=20, sample=1e-3, workers=8, sg=1)
    # model.save(str((workspace_path / "word2vec/word2vec_lemmata.model").absolute()))
    model = Word2Vec(sentences=ALIMSentencesRestartableGenerator(use_lemmas=True), vector_size=200, window=20, sample=1e-3, workers=8, sg=0)
    model.save(str((workspace_path / "word2vec/word2vec_cbow_lemmata.model").absolute()))
