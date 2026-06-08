from env import *
from pathlib import Path
from saxonche import PySaxonProcessor
from cltk import NLP
from cltk.utils.file_outputs import doc_to_conllu
import mariadb
import unicodedata, re

connection_properties = {
        'user' : mariadb_alim_php7_user,
        'password' : mariadb_alim_php7_psw,
        'host' : mariadb_alim_php7_host,
        'port' : int(mariadb_alim_php7_port),
        'database' : mariadb_alim_php7_db
}
# print (connection_properties)

workspace_path = Path(__file__).parent / 'workspace/alim'
processor = PySaxonProcessor()
xslt_processor = processor.new_xslt30_processor()
executable = xslt_processor.compile_stylesheet(stylesheet_file = str(Path(__file__).parent / 'tei-to-text.xsl'))

def detox(filename: str) -> str:
    return re.sub(r'\s+', '_', filename.strip().lower())

query = '''
  -- The query use windows functions to get the last version of each book with not empty XML
  WITH agora_book_version_last AS (
    SELECT DISTINCT id, MAX(version) OVER (PARTITION BY id) AS max_version FROM agora_book_version WHERE length(n7tra_xml_content) > 0
  )
  SELECT
    b1.id
  , b1.title
  , b1.author
  , b1.is_document
  , b1.consistenza
  , b1.metadata
  , b1.n7tra_xml_content 
  FROM agora_book_version b1
  JOIN agora_book_version_last b2 ON b2.id = b1.id AND b2.max_version = b1.version
  WHERE NOT b1.alim_plus AND NOT b1.is_document
  -- WHERE b1.id = 13147
  -- LIMIT 1
  '''

nlp = NLP("lati1261", backend="stanza", suppress_banner=True)
paragraph_separator_re = re.compile(r'\.|\n\n+', flags=re.MULTILINE)

with mariadb.connect(**connection_properties) as conn:
    with conn.cursor() as cur:
        cur.execute(query)
        for (id, title, author, is_document, consistenza, metadata, xml) in cur:
            document_path = workspace_path / f"{id}-{detox(title)}"
            document_path.mkdir(exist_ok=True)
            tei_path = document_path / 'tei.xml'
            text_path = document_path / 'text.txt'
            cltk_conllu_path = document_path / 'cltk_conllu.txt'
            paragraphs_path = document_path / 'paragraphs'

            if not tei_path.exists():
              xml = bytes(xml,"utf-8").decode("utf-8-sig") # Remove UTF BOM, avoiding "Content is not allowed in prolog" error during XML parsing
              with tei_path.open('w') as tei_fp:
                  tei_fp.write(xml)
            else:
              with tei_path.open('r') as tei_fp:
                  xml = tei_fp.read()

            if not text_path.exists():
              try:
                  document = processor.parse_xml(xml_text = xml)
              except Exception as e:
                  print ('ERRORE!!!')
                  print (title)
                  print (author)
                  print ('https://alim.unisi.it/dl/resource/' + str(id))
                  print ('---')
                  print (e)
                  print ('\n')
                  continue
              text = executable.transform_to_string(xdm_node = document)
              with text_path.open('w') as text_fp:
                  text_fp.write(text)
            else:
              with text_path.open('r') as text_fp:
                 text = text_fp.read()

            if not cltk_conllu_path.exists():
              doc = nlp.analyze(text = text) 
              with cltk_conllu_path.open('w') as cltk_conllu_fp:
                  cltk_conllu_fp.write(doc_to_conllu(doc, include_provenance=False, include_confidence=True))

            if not paragraphs_path.exists():
              paragraphs_path.mkdir()
              paragraph_count = 0
              sents = paragraph_separator_re.split(text.strip())
              for sent in sents:
                sent = sent.strip()
                if len(sent) > 0:
                  paragraph_count += 1
                  with (paragraphs_path / f'paragraph_{paragraph_count:06}.txt').open('w') as paragraph_fp:
                    paragraph_fp.write(sent)


