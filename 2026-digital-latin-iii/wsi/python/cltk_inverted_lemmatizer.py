from pathlib import Path
import json, csv

# Tnx Claude for the naming suggestion: "inverted lemmatizer"

def inflect(lemma : str, pos : str):

    workspace_path = Path(__file__).parent / 'workspace'
    cache_path = workspace_path / 'cltk_inverted_lemmatizer_cache.json'
    cache = {}
    if cache_path.exists():
        with cache_path.open('r') as cache_fp:
            cache = json.load(cache_fp)

    lemma = lemma.strip().lower()
    pos = pos.strip().upper()

    if lemma in cache:
        lemma_obj = cache[lemma]
        if pos in lemma_obj:
            return lemma_obj[pos]

    lemma_pos_obj = {'found' : False, 'forms' : {}}
    for document_dir_path in (workspace_path / 'alim').iterdir():
        if document_dir_path.is_dir():
            cltk_conllu_path = document_dir_path / 'cltk_conllu.txt'
            if cltk_conllu_path.exists():
                with cltk_conllu_path.open('r') as cltk_conllu_fp:
                    reader = csv.reader(cltk_conllu_fp, delimiter='\t', quoting=csv.QUOTE_NONE)
                    for row in reader:
                        if len(row) < 4:
                            continue
                        if row[2].lower() == lemma and row[3] == pos:
                            lemma_pos_obj['found'] = True
                            if not row[1] in lemma_pos_obj['forms']:
                                lemma_pos_obj['forms'][row[1]] = 0
                            lemma_pos_obj['forms'][row[1]] += 1

    if not lemma in cache:
        cache[lemma] = {}
    cache[lemma][pos] = lemma_pos_obj
    with cache_path.open('w') as cache_fp:
        json.dump(cache,cache_fp)

    return lemma_pos_obj

print(inflect('rosa', 'NOUN'))

"""
Ecco intanto altri termini che hanno anche un'accezione retorica

Einchiridion (esempio, formulario)
sciscitatio (ricerca, approfondimento)
mutatio (riguarda le variazionimorfologiche o sintattiche)
terminatio (al plurale: terminationes: la parte finale delle parole, utile al ritmo della frase)
dispositio (ordine delle parole)
prologus (come salutatio)
Maneries (sinonimo di modo)
Modus (come in italiano, ma usato spesso per indicare la sezione di una materia di un testo retorico)
Cause redditio (cause non si declina, è una tipologia di exordium o caopotatio benivolentie)
hortatorius (l'accezione retorica riguarda la petitio hortatoria, cioè una richiesta esorttativa)
dictamen (vale anche discorso in generale
color (al plurale colores sono le figure retoriche)
Bastano?
"""

for lemma in ['Einchiridion','sciscitatio','mutatio','terminatio','dispositio','prologus','modus','hortatorius','dictamen','color']:
    lemma_pos_obj = inflect(lemma, 'NOUN')
    for form, freq in sorted(lemma_pos_obj['forms'].items(), reverse = True, key=lambda item: item[1]):
        print (f'\'{form}\',', end='')
    print()
    for form, freq in sorted(lemma_pos_obj['forms'].items(), reverse = True, key=lambda item: item[1]):
        print (f'{freq},', end='')
    print()
