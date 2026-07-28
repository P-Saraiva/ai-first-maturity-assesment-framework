# Tabela de Testes Funcionais — AFS Maturity Assessment Framework

Formato: **Teste Funcional | Objetivo do Teste | Resultado esperado**  
Escopo: validação ponta‑a‑ponta do fluxo **criar → responder → finalizar → relatório → PDF**, incluindo i18n, health checks e persistência.

| Teste Funcional | Objetivo do Teste | Resultado esperado |
|---|---|---|
| Acesso à home (`/`) | Verificar que a aplicação inicia e renderiza a página principal | Página carrega com layout esperado e, se houver dados, exibe estatísticas; sem erro 500 |
| Health check básico (`/health`) | Validar readiness/liveness e conectividade com banco | Retorna JSON com `status=healthy` e `components.database=healthy` |
| Health check detalhado (`/health/detailed`) | Validar disponibilidade de componentes (DB e cache) | Retorna JSON com `status` (healthy/degraded) e status por componente sem erro 500 |
| Health check escrita DB (`/health/write`) | Garantir que o banco é gravável no ambiente | Retorna `status=healthy`; se falhar, retorna `unhealthy` com mensagem de erro |
| Troca de idioma (`/set-language/pt`) | Validar i18n por sessão | UI passa a exibir strings em PT; `current_lang` refletido em templates |
| Troca de idioma (`/set-language/en`) | Validar fallback e mudança de locale | UI passa a exibir strings em EN; chaves faltantes exibem fallback (EN) ou key |
| Carregar tela de criação (`/assessment/create` GET) | Validar entrada do fluxo “create” | Página de criação renderiza sem erros e permite iniciar assessment |
| Criar assessment (form legacy) (`/assessment/create` POST) | Validar criação de registro em `assessments` e redirecionamento | Assessment criado com `status=IN_PROGRESS`; redireciona para primeira seção ativa |
| Validação de campos obrigatórios (form legacy) | Garantir robustez do fluxo de criação | Falta de campos obrigatórios exibe mensagem e não cria assessment |
| Criar assessment via JSON (`/assessment/submit-assessment`) | Validar fluxo client-driven (criação + respostas em lote) | Retorna JSON `status=success`, `assessment_id` e `redirect` para o relatório |
| Validação de payload JSON (campos obrigatórios) | Evitar criação incompleta via API JSON | Retorna 400 com mensagem de campos faltantes; não persiste assessment |
| Seleção de áreas vazia (JSON) | Evitar assessment sem escopo | Retorna 400 `No areas selected`; não persiste responses |
| Acesso a seção válida (`/assessment/<id>/section/<section_id>`) | Validar render do questionário por seção | Página da seção carrega com áreas/perguntas e respostas previamente salvas (se existirem) |
| Acesso a seção inexistente | Validar fallback para primeira seção ativa | Redireciona para a primeira seção disponível (sem erro 500) |
| Persistir respostas por seção (submit) | Garantir upsert de responses (criar/atualizar) | Respostas são gravadas/atualizadas em `responses` (unicidade por assessment+question) |
| Persistência de `notes_` (submit) | Validar armazenamento de observações por pergunta | Campo notes é persistido e reaparece ao reabrir a seção |
| Imutabilidade pós-conclusão (edição bloqueada) | Evitar alteração de assessment finalizado | Se status `COMPLETED/LOCKED`, rota de seção redireciona para `/report` com aviso |
| Progresso de assessment (`/assessment/api/<id>/progress`) | Validar cálculo de progresso e retorno JSON | Retorna `status=success` com total/respondidas/% e status atual |
| Final review (`/assessment/<id>/final-review`) | Validar cálculo de cobertura e prontidão para gerar relatório | Página exibe total/respondidas/%; `can_generate_report` true quando >=80% |
| Geração de relatório com <80% (sem force) | Validar regra de cobertura mínima | Não conclui; redireciona para final review com warning |
| Geração de relatório com force completion | Validar override de cobertura mínima | Assessment é marcado `COMPLETED` e redireciona para `/report` |
| Conclusão padrão (>=80%) | Validar finalização normal | Atualiza `assessments` (status, completion_date, scores e results_json) |
| Acesso ao relatório sem concluir (`/assessment/<id>/report`) | Validar proteção de rota de relatório | Exibe warning e redireciona para detalhe/fluxo de conclusão |
| Relatório HTML (assessment concluído) | Validar cálculo de scoring e render de visões | Página carrega com scores por seção/área, contagens, gráficos e insights |
| Relatório HTML com i18n de perguntas | Validar overlay de tradução do texto das perguntas | Em PT/EN, gaps/strengths e textos exibem tradução quando disponível; fallback para texto do DB |
| Download PDF (`/assessment/<id>/download-pdf`) com Playwright | Validar exportação PDF ponta‑a‑ponta | Retorna `application/pdf` com header `Content-Disposition` e conteúdo do relatório |
| Download PDF sem Playwright instalado | Validar tratamento de dependência ausente | Exibe flash de erro e redireciona para relatório, sem crash |
| Persistência de SQLite em Docker (volume `instance/`) | Garantir durabilidade de dados no container | Após reiniciar container, assessments/responses permanecem no banco |
| Consistência `ACTIVE_SECTION_IDS` | Garantir que seções ativas filtram fluxo e scoring | UI mostra apenas seções ativas; scoring considera apenas seções ativas; relatório reflete o filtro |
| Estatísticas da home com dados reais | Validar agregações (count, completion, média) | Contadores e médias refletem assessments existentes; sem exceções em DB |
| Exclusão de assessment (`/assessment/<id>/delete`) | Validar limpeza de dados associados | Assessment e responses associadas são removidos; lista e estatísticas atualizam |

## Observações de execução
- Recomenda-se rodar o setup do banco antes: [scripts/setup_database.py](../scripts/setup_database.py)
- Para teste de PDF em ambiente Linux/Container: garantir Playwright instalado e browsers disponíveis (ver [Dockerfile](../Dockerfile)).
