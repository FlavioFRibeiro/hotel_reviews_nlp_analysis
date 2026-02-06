# Booking.com Reviews ? NLP Multil?ngue (Estudo de Caso)

Este projeto analisa avalia??es do Booking.com para entender **como h?spedes em diferentes idiomas (EN/DE/FR)**
expressam o que valorizam e o que criticam. O foco ? transformar texto livre em **insights acion?veis** para
opera??o, produto e marketing.

## Contexto de neg?cio
Hot?is recebem avalia??es em m?ltiplos idiomas. A forma de express?o pode variar e gerar vieses na interpreta??o.
Ao analisar separadamente **reviews positivas e negativas por idioma**, conseguimos identificar padr?es culturais
ou expectativas espec?ficas que impactam decis?es de servi?o e comunica??o.

## Perguntas respondidas
- Quais temas aparecem com mais frequ?ncia em reviews **positivas** e **negativas** por idioma?
- Existem diferen?as de ?nfase entre ingl?s, alem?o e franc?s?
- Onde est?o os principais drivers de satisfa??o/insatisfa??o?

## Dados
- Fonte: dataset de reviews coletadas para fins educacionais.
- Campos principais: `reviewTextParts/Liked`, `reviewTextParts/Disliked`, `reviewOriginalLanguage`.
- Observa??o: `reviewOriginalLanguage` possui valores faltantes. O pipeline aplica **fallback** de detec??o por stopwords.

## Metodologia (resumo)
1. Normaliza??o de texto preservando acentos.
2. Detec??o de idioma (campo original + fallback por stopwords).
3. Lemmatiza??o com spaCy por idioma.
4. Filtro de POS (ADJ/NOUN/PROPN) e stopwords.
5. Extra??o de **trigramas** e frequ?ncia por idioma e sentimento.

## Entreg?veis
- `outputs/<cidade>/top_trigrams_summary.csv`: ranking de trigramas por idioma e sentimento.
- `outputs/<cidade>/summary_counts.csv`: volume de reviews por idioma/sentimento.
- `outputs/<cidade>/good/`: trigramas de reviews positivas por idioma.
- `outputs/<cidade>/bad/`: trigramas de reviews negativas por idioma.
- `reports/insights_<cidade>.md`: relat?rio de insights (gerado por script).

## Como executar
1. Instale depend?ncias:
   - `pip install -r requirements.txt`
2. Baixe os modelos do spaCy:
   - `python -m spacy download en_core_web_sm`
   - `python -m spacy download de_core_news_sm`
   - `python -m spacy download fr_core_news_sm`
3. Execute o pipeline:
   - `python src/pipeline.py --config config/config.json`
4. Gere o relat?rio:
   - `python src/report.py --config config/config.json`

## Execu??o por cidade
Para manter outputs separados por cidade, use os arquivos de configura??o dedicados:
- Berlim: `python src/pipeline.py --config config/config_berlin.json`
  - Relat?rio: `python src/report.py --config config/config_berlin.json`
- Creta: `python src/pipeline.py --config config/config_crete.json`
  - Relat?rio: `python src/report.py --config config/config_crete.json`

## Estrutura do projeto
Estrutura atual do reposit?rio:

```
hotel_reviews_nlp_analysis
|-- config
|   |-- config.json
|   |-- config_berlin.json
|   `-- config_crete.json
|-- data
|   `-- raw
|       |-- Berlim_All_Reviews.csv
|       `-- dataset_booking-review.csv
|-- legacy
|   |-- outputs
|   |   |-- Berlin_Bad_Reviews.xlsx
|   |   |-- Berlin_Good_Reviews.xlsx
|   |   |-- Berlin_Reviews.jpg
|   |   |-- Crete_Bad_Reviews.xlsx
|   |   |-- Crete_Good_Reviews.xlsx
|   |   `-- Crete_Reviews.jpg
|   |-- Berlin_Reviews.ipynb
|   `-- Crete_Reviews.ipynb
|-- outputs
|   |-- berlin
|   |   |-- bad
|   |   |-- good
|   |   |-- summary_counts.csv
|   |   `-- top_trigrams_summary.csv
|   `-- crete
|       |-- bad
|       |-- good
|       |-- summary_counts.csv
|       `-- top_trigrams_summary.csv
|-- reports
|   |-- insights_berlin.md
|   |-- insights_by_language.md
|   `-- insights_crete.md
|-- src
|   |-- pipeline.py
|   `-- report.py
|-- main.ipynb
|-- README.md
`-- requirements.txt
```

Principais pastas:
- `data/raw/`: dados brutos (Berlim e Creta).
- `config/`: arquivos de configura??o por cidade.
- `src/`: pipeline NLP e gera??o de relat?rio.
- `outputs/`: resultados organizados por cidade e sentimento.
- `reports/`: relat?rios executivos gerados.
- `legacy/`: notebooks e outputs antigos.

Arquivos principais:
- `main.ipynb`: estudo de caso com narrativa executiva e uso do pipeline.
- `requirements.txt`: depend?ncias do projeto.

## Nota de ?tica e conformidade
Este projeto ? educacional. Sempre respeite as pol?ticas de uso e termos de servi?o das fontes ao coletar dados.
