# Especificação do Projeto: Diário TCC Assistido por LLM

## 1. Visão Geral
Sistema para processar diários pessoais (escritos em Markdown no Obsidian) usando um LLM,
aplicando abordagem TCC (Terapia Cognitivo-Comportamental) para identificar distorções
cognitivas e estruturar registros no modelo ABC/ABCDE. Uso pessoal, com output também
aproveitável pelo psicólogo do usuário.

## 2. Objetivos
- Ajudar o usuário a registrar e refletir sobre pensamentos/eventos diários.
- Identificar automaticamente distorções cognitivas nos registros.
- Estruturar entradas livres no modelo ABC/ABCDE quando aplicável.
- Gerar relatórios periódicos consolidados para acompanhamento (próprio e/ou terapêutico).

## 3. Escopo

### Incluso (v1)
- Script/comando manual que lê arquivo(s) markdown do Obsidian.
- Processamento via API de LLM (agnóstico de provedor).
- Geração de:
  - Arquivo markdown de análise por entrada (distorções identificadas, estrutura ABC/ABCDE sugerida).
  - Relatório periódico consolidado (padrões recorrentes, evolução, distorções mais frequentes).
- Prompts guiados para orientar o registro (biblioteca de prompts TCC).

### Fora do escopo (v1)
- Automação/watch de pasta.
- App mobile/web dedicado.
- Modelo local (Ollama).
- Interface gráfica própria (usa Obsidian como front-end).

## 4. Requisitos Funcionais
| ID | Requisito |
|----|-----------|
| RF01 | O sistema deve ler um arquivo markdown de entrada (diário) via caminho informado pelo usuário. |
| RF02 | O sistema deve enviar o conteúdo ao LLM configurado via API, com prompt estruturado para análise TCC. |
| RF03 | O sistema deve identificar e listar distorções cognitivas presentes no texto. |
| RF04 | O sistema deve sugerir estruturação da entrada no modelo ABC/ABCDE quando aplicável. |
| RF05 | O sistema deve gerar um arquivo markdown de saída com a análise, salvo em local configurável. |
| RF06 | O sistema deve permitir gerar relatório consolidado a partir de múltiplas entradas (intervalo de datas configurável). |
| RF07 | O sistema deve oferecer prompts guiados (biblioteca pré-definida) para auxiliar o usuário a escrever a entrada. |
| RF08 | O provedor de LLM deve ser configurável (API key + endpoint/modelo), permitindo troca futura sem alterar o core. |

## 5. Requisitos Não-Funcionais
| ID | Requisito |
|----|-----------|
| RNF01 | Dados sensíveis (diários) não devem ser persistidos fora do ambiente local do usuário, exceto na chamada à API do LLM. |
| RNF02 | Arquitetura deve isolar a camada de LLM (adapter/interface) para permitir troca de provedor (API → modelo local) sem refatoração ampla. |
| RNF03 | Formato de entrada/saída deve ser markdown puro, compatível com Obsidian. |
| RNF04 | Execução via linha de comando (CLI), sem dependência de interface gráfica própria. |

## 6. Critérios de Aceite
- Rodar o comando sobre um arquivo de diário gera um markdown de análise coerente com TCC.
- Rodar o comando de relatório sobre um intervalo de datas consolida padrões de múltiplas entradas.
- Trocar o provedor de LLM (via config) não exige alteração no código core.

## 7. Riscos / Pontos de Atenção
- **Privacidade:** conteúdo sensível trafega para API externa — considerar aviso/consentimento explícito.
- **Qualidade clínica:** análise de LLM não substitui avaliação profissional — deixar isso explícito no output.
- **Migração para modelo local:** desenhar o adapter de LLM desde já pensando nessa troca.
