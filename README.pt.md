# Velocidade inicial e alvos circulares: dois problemas na análise de dados de queda livre por aprendizado de máquina

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24180985.svg)](https://doi.org/10.5281/zenodo.24180985)

*English version: [README.md](README.md)*

Pacote de reprodutibilidade (versão 2.0.0) do estudo **Velocidade inicial e alvos circulares: dois problemas na análise de dados de queda livre por aprendizado de máquina** (A. Brito, M. X. Amorim, E. N. Lima, Instituto de Física, UFMT).

## Sobre o estudo

Experimentos de queda livre com duas fotoportas são um exercício comum nos laboratórios de graduação, e seus dados vêm sendo usados como porta de entrada para o aprendizado de máquina. O estudo pergunta o que esses dados de fato revelam sobre a aceleração da gravidade e sobre o aparato, primeiro quando analisados com o estimador cinemático simplificado e depois quando usados para treinar um modelo de aprendizado de máquina.

Um único conjunto de dados, registrado em dois blocos sequenciais de aquisição, expõe dois problemas:

- **Físico.** O estimador simplificado supõe que a esfera inicia o intervalo cronometrado em repouso, mas ela cruza a primeira fotoporta já em movimento. Ao incluir essa velocidade de entrada no ajuste cinemático, recupera-se o valor esperado a partir da geometria de liberação medida. Ainda assim, a aceleração ajustada fica abaixo da referência local, muda entre os blocos e é fortemente acoplada à velocidade de entrada. Os dados sustentam o diagnóstico, mas não uma calibração instrumental.
- **Metodológico.** Um alvo residual definido a partir da estimativa simplificada e de um valor de referência fixo pode ser reconstruído exatamente a partir das entradas e da mesma referência. As métricas de validação passam a medir a aproximação de uma identidade algébrica conhecida, e não uma correção física aprendida dos dados.

Os scripts deste repositório reproduzem todos os números e figuras dos dois diagnósticos.

## Versões arquivadas

A versão 2.0.0 está arquivada no Zenodo: [10.5281/zenodo.24180985](https://doi.org/10.5281/zenodo.24180985). Versão 1.0.0: [10.5281/zenodo.21694213](https://doi.org/10.5281/zenodo.21694213). A versão 2.0.0 corrige a geometria de liberação e o valor de referência da gravidade; ver `CHANGELOG.md`.

## Dados

`data/free_fall_measurements.csv` contém 119 lançamentos individuais, com as colunas:

- `run_index`: ordem de aquisição;
- `block`: bloco sequencial de aquisição;
- `h(m)`: separação entre os feixes das fotoportas, em metros;
- `t(s)`: tempo de trânsito medido, em segundos.

O Bloco 1 tem 75 lançamentos. Depois que a separação entre as fotoportas foi reposicionada para um valor menor, o Bloco 2 tem 44 lançamentos. A mesma esfera, as mesmas fotoportas, o mesmo cronômetro e o mesmo sistema de liberação foram usados em toda a campanha. Antes de cada lançamento, a superfície inferior da esfera foi posicionada a 7 mm acima do feixe da fotoporta 1, com uma régua graduada em 1 mm (ver `ACQUISITION_PROTOCOL.md`).

## Como reproduzir a análise

É necessário Python 3.10 ou mais recente.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
./run_all.sh
```

Os resultados numéricos são gravados em `results/`, e as figuras são regeneradas em `figures/`, em PDF e PNG. As figuras saem em inglês e em português; as versões em português têm o sufixo `_pt`, rótulos traduzidos e vírgula decimal. Para gerar apenas as figuras em português:

```bash
cd src
python3 05_generate_figures.py --lang pt
```

## O que o pacote reproduz

- estimativas clássicas com `g = 2H/t^2`;
- ajustes cinemáticos com velocidade de entrada livre e com geometria fixa (h0 = 7 mm);
- regressões dos resíduos e testes entre blocos;
- ajustes de atraso temporal restritos pela geometria e diagnósticos da correlação entre g e o atraso;
- um limite para o viés em g causado por arrasto e empuxo;
- os modelos diagnósticos de aprendizado de máquina e o baseline algébrico exato do alvo;
- testes de ablação e de permutação de variáveis redundantes;
- todas as figuras derivadas dos dados.

O alvo de aprendizado de máquina pode ser reconstruído exatamente a partir das variáveis de entrada e do valor de referência fixo. As métricas de ML informadas quantificam, portanto, a aproximação de uma identidade algébrica conhecida, e não uma correção física aprendida de forma independente.

## Uso em sala de aula

Os dados e o código podem ser usados diretamente em disciplinas de laboratório:

1. prever a velocidade de entrada a partir da distância de liberação medida e compará-la com o coeficiente linear do ajuste cinemático;
2. ajustar cada bloco separadamente e discutir a correlação entre a velocidade de entrada e g;
3. antes de qualquer exercício de aprendizado de máquina, escrever o alvo em função das entradas brutas e verificar se a expressão se fecha.

## Citação

Cite o pacote arquivado como:

> Brito, A., Amorim, M. X., & Lima, E. N. (2026). *Free-fall model misspecification and algebraic target circularity: reproducibility package* (Version 2.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.24180985

Uma citação em formato legível por máquina está em `CITATION.cff`.

## Autoria

Auiri Brito e Matheus Xavier Amorim contribuíram igualmente para este trabalho. Erika N. Lima é a autora correspondente.
