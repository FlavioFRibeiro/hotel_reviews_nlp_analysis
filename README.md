# Booking.com Reviews — NLP Multilíngue (Estudo de Caso)

Este projeto analisa avaliações do Booking.com para entender **como hóspedes em diferentes idiomas (EN/DE/FR)**
expressam o que valorizam e o que criticam. O foco é transformar texto livre em **insights acionáveis** para
operação, produto e marketing.

## Contexto de negócio
Hotéis recebem avaliações em múltiplos idiomas. A forma de expressão pode variar e gerar vieses na interpretação.
Ao analisar separadamente **reviews positivas e negativas por idioma**, conseguimos identificar padrões culturais
ou expectativas específicas que impactam decisões de serviço e comunicação.

## Perguntas respondidas
- Quais temas aparecem com mais frequência em reviews **positivas** e **negativas** por idioma?
- Existem diferenças de ênfase entre inglês, alemão e francês?
- Onde estão os principais drivers de satisfação/insatisfação?

## Dados
- Fonte: dataset de reviews coletadas para fins educacionais.
- Campos principais: `reviewTextParts/Liked`, `reviewTextParts/Disliked`, `reviewOriginalLanguage`.
- Observação: `reviewOriginalLanguage` possui valores faltantes. O pipeline aplica **fallback** de detecção por stopwords.

## Metodologia (resumo)
1. Normalização de texto preservando acentos.
2. Detecção de idioma (campo original + fallback por stopwords).
3. Lemmatização com spaCy por idioma.
4. Filtro de POS (ADJ/NOUN/PROPN) e stopwords.
5. Extração de **trigramas** e frequência por idioma e sentimento.

## Entregáveis
- `outputs/<cidade>/top_trigrams_summary.csv`: ranking de trigramas por idioma e sentimento.
- `outputs/<cidade>/summary_counts.csv`: volume de reviews por idioma/sentimento.
- `outputs/<cidade>/good/`: trigramas de reviews positivas por idioma.
- `outputs/<cidade>/bad/`: trigramas de reviews negativas por idioma.
- `reports/insights_<cidade>.md`: relatório de insights (gerado por script).

## Como executar
1. Instale dependências:
   - `pip install -r requirements.txt`
2. Baixe os modelos do spaCy:
   - `python -m spacy download en_core_web_sm`
   - `python -m spacy download de_core_news_sm`
   - `python -m spacy download fr_core_news_sm`
3. Execute o pipeline:
   - `python src/pipeline.py --config config/config.json`
4. Gere o relatório:
   - `python src/report.py --config config/config.json`

## Execução por cidade
Para manter outputs separados por cidade, use os arquivos de configuração dedicados:
- Berlim: `python src/pipeline.py --config config/config_berlin.json`
  - Relatório: `python src/report.py --config config/config_berlin.json`
- Creta: `python src/pipeline.py --config config/config_crete.json`
  - Relatório: `python src/report.py --config config/config_crete.json`

## Estrutura do projeto
Estrutura atual do repositório:

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
- `config/`: arquivos de configuração por cidade.
- `src/`: pipeline NLP e geração de relatório.
- `outputs/`: resultados organizados por cidade e sentimento.
- `reports/`: relatórios executivos gerados.
- `legacy/`: notebooks e outputs antigos.

Arquivos principais:
- `main.ipynb`: estudo de caso com narrativa executiva e uso do pipeline.
- `requirements.txt`: dependências do projeto.

## Nota de ética e conformidade
Este projeto é educacional. Sempre respeite as políticas de uso e termos de serviço das fontes ao coletar dados.
