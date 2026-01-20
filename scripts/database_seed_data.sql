-- ========================================
-- AI-First Software Engineering Maturity Assessment Framework
-- Database Seed Data (DML Script)
-- ========================================

-- ========================================
-- Sections Data
-- ========================================
-- New 7-Section Structure (AI Security Assessment) -- INSERT OR IGNORE for compatibility
INSERT OR IGNORE INTO sections VALUES('ETSI','Ethics, Trust and Societal Impact','Ethics, explainability, fairness and societal impact of AI systems',1,'#1e3a8a','fas fa-scale-balanced',datetime('now'),datetime('now'));
INSERT OR IGNORE INTO sections VALUES('GSA','Governance, Strategy and Accountability','Strategy, compliance, accountability and organizational culture for AI',2,'#065f46','fas fa-gavel',datetime('now'),datetime('now'));
INSERT OR IGNORE INTO sections VALUES('IAA','Identity, Autonomy and Access Control for AI','Identity governance, secrets, and autonomous agent privilege',3,'#7c2d12','fas fa-user-shield',datetime('now'),datetime('now'));
INSERT OR IGNORE INTO sections VALUES('DPR','Data and Provenance','Data inventory and provenance of information',4,'#0f766e','fas fa-database',datetime('now'),datetime('now'));
INSERT OR IGNORE INTO sections VALUES('PUT','Privacy, User Rights and Operational Transparency','Privacy, user control and operational transparency for AI',5,'#7e22ce','fas fa-user-lock',datetime('now'),datetime('now'));
INSERT OR IGNORE INTO sections VALUES('TSA','Technical Security, Architecture and AI Operations','Threats, secure deployment, monitoring and harmful content handling',6,'#b45309','fas fa-network-wired',datetime('now'),datetime('now'));
INSERT OR IGNORE INTO sections VALUES('QEI','Quality, Evaluation, Incident Handling and Resilience','Testing, evaluation, incidents and operational resilience',7,'#0ea5e9','fas fa-clipboard-check',datetime('now'),datetime('now'));
-- INSERT OR IGNORE INTO sections VALUES('FC','FOUNDATIONAL CAPABILITIES','Core building blocks for AI-driven development, including infrastructure, team skills, code generation processes, and knowledge management systems that enable basic AI integration into software engineering workflows',1,'#3b82f6','fas fa-foundation','2025-09-04 16:06:55','2025-09-04 16:06:55');
-- INSERT OR IGNORE INTO sections VALUES('TC','TRANSFORMATION CAPABILITIES','Advanced capabilities that fundamentally transform how software is built, including intelligent architecture translation, autonomous testing, smart CI/CD, monitoring systems, and legacy modernization using AI',2,'#10b981','fas fa-magic','2025-09-04 16:06:55','2025-09-04 16:06:55');
-- INSERT OR IGNORE INTO sections VALUES('EI','ENTERPRISE INTEGRATION','Enterprise-scale capabilities for integrating AI development practices across the organization, including data governance, vendor management, system integration, cost optimization, scalability, and business continuity',3,'#f59e0b','fas fa-building','2025-09-04 16:06:55','2025-09-04 16:06:55');
-- INSERT OR IGNORE INTO sections VALUES('SG','STRATEGIC GOVERNANCE','Leadership and governance frameworks for responsible, compliant, and strategically aligned AI adoption, including ethics, performance measurement, IP management, risk management, change management, and future readiness',4,'#8b5cf6','fas fa-shield-alt','2025-09-04 16:06:55','2025-09-04 16:06:55');

-- Additional Sections (Draft Set)
-- INSERT OR IGNORE INTO sections VALUES('SE','AI SAFETY ENGINEERING','Engineering practices to ensure safe, robust, and trustworthy AI-enabled software, including safety cases, adversarial resilience, red-teaming, and human oversight',5,'#ef4444','fas fa-exclamation-triangle','2025-12-10 10:00:00','2025-12-10 10:00:00');
-- INSERT OR IGNORE INTO sections VALUES('HC','HUMAN-AI EXPERIENCE DESIGN','Designing effective human-AI interaction, usability, accessibility, and trust, including prompt UX, explainability, and feedback loops',6,'#06b6d4','fas fa-users','2025-12-10 10:00:00','2025-12-10 10:00:00');

-- ========================================
-- Areas Data
-- ========================================
-- ETSI Areas
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('ETSI-ESI','ETSI','Ethics, Social Impact and Transparency','Ethics, Social Impact and Transparency',1,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('ETSI-ETC','ETSI','Explainability, Transparency and Communication','Explainability, Transparency and Communication',2,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('ETSI-BFR','ETSI','Bias, Fairness and Responsible Use','Bias, Fairness and Responsible Use',3,NULL,NULL,NULL,datetime('now'),datetime('now'));

-- GSA Areas
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('GSA-GSC','GSA','Governance, Strategy and Compliance','Governance, Strategy and Compliance',1,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('GSA-PLA','GSA','Policies, Legal Compliance and Accountability','Policies, Legal Compliance and Accountability',2,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('GSA-CUL','GSA','AI Security Awareness and Culture','AI Security Awareness and Culture',3,NULL,NULL,NULL,datetime('now'),datetime('now'));

-- IAA Areas
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('IAA-IGO','IAA','Identity Governance for AI and Agents','Identity Governance for AI and Agents',1,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('IAA-CSM','IAA','Credential and Secret Management','Credential and Secret Management',2,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('IAA-AAP','IAA','Agents, Autonomy and Privilege','Agents, Autonomy and Privilege',3,NULL,NULL,NULL,datetime('now'),datetime('now'));

-- DPR Areas
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('DPR-IPU','DPR','Inventory and Provenance','Inventory and Provenance',1,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('DPR-DGM','DPR','Data Quality, Governance and Minimization','Data Quality, Governance and Minimization',2,NULL,NULL,NULL,datetime('now'),datetime('now'));
-- INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
-- VALUES('DPR-TDL','DPR','Third-Party Data, Ethics and Licensing','Third-Party Data, Ethics and Licensing',3,NULL,NULL,NULL,datetime('now'),datetime('now'));

-- PUT Areas
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('PUT-PUC','PUT','Privacy, User Transparency and Control','Privacy, User Transparency and Control',1,NULL,NULL,NULL,datetime('now'),datetime('now'));

-- TSA Areas
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('TSA-TRO','TSA','Threats, Risks and Operational Security','Threats, Risks and Operational Security',1,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('TSA-SDA','TSA','Secure Deployment and Architecture','Secure Deployment and Architecture',2,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('TSA-DMH','TSA','Defects, Monitoring and Harmful Content','Defects, Monitoring and Harmful Content',3,NULL,NULL,NULL,datetime('now'),datetime('now'));

-- QEI Areas
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('QEI-TEI','QEI','Testing, Evaluation and Independence','Testing, Evaluation and Independence',1,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('QEI-IEC','QEI','Incidents, Events and Continuity','Incidents, Events and Continuity',2,NULL,NULL,NULL,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO areas (id, section_id, name, description, display_order, timeline_l1_l2, timeline_l2_l3, timeline_l3_l4, created_at, updated_at)
VALUES('QEI-OCM','QEI','Operations, Continuous Monitoring and Improvement','Operations, Continuous Monitoring and Improvement',3,NULL,NULL,NULL,datetime('now'),datetime('now'));

-- ========================================
-- Questions Data (Binary Yes/No in Portuguese)
-- ========================================

-- Section 1: Ética, Impacto Social e Transparência (ETSI)
-- Área: Ética, Impacto Social e Transparência (ETSI-ESI)
INSERT OR IGNORE INTO questions (id, area_id, question, level_1_desc, level_2_desc, level_3_desc, level_4_desc, display_order, is_active, created_at, updated_at) VALUES('ETSI-ESI-01A','ETSI-ESI','Existe conscientização básica sobre impactos éticos e sociais do uso de IA na organização?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ESI-01B','ETSI-ESI','Questões éticas relacionadas ao uso de IA são discutidas de forma informal quando surgem?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ESI-01C','ETSI-ESI','Existem processos formais para avaliar impactos éticos e sociais antes ou durante o uso de sistemas de IA?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ESI-01D','ETSI-ESI','Existe um framework ou diretriz organizacional para apoiar decisões éticas relacionadas ao uso de IA?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ESI-01E','ETSI-ESI','Avaliações de impacto ético são aplicadas de forma consistente aos sistemas de IA e revisadas periodicamente?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ESI-01F','ETSI-ESI','As decisões éticas relacionadas à IA estão incorporadas aos processos organizacionais e de negócio?','Não','Sim',NULL,NULL,6,1,datetime('now'),datetime('now'));

-- Área: Explicabilidade, Transparência e Comunicação (ETSI-ETC)
INSERT OR IGNORE INTO questions VALUES('ETSI-ETC-01A','ETSI-ETC','Existem esforços informais para explicar decisões ou saídas de sistemas de IA quando solicitado?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ETC-01B','ETSI-ETC','A comunicação sobre como os sistemas de IA funcionam ocorre apenas de forma reativa ou pontual?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ETC-01C','ETSI-ETC','Existem mecanismos formais de explicabilidade para sistemas de IA considerados críticos?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ETC-01D','ETSI-ETC','Explicações e informações sobre decisões de IA são documentadas e compartilhadas internamente?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ETC-01E','ETSI-ETC','Técnicas de explicabilidade são aplicadas de forma consistente nos sistemas de IA relevantes?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-ETC-01F','ETSI-ETC','A organização realiza comunicação externa clara informando quando usuários interagem com IA?','Não','Sim',NULL,NULL,6,1,datetime('now'),datetime('now'));

-- Área: Viés, Equidade e Uso Responsável (ETSI-BFR)
INSERT OR IGNORE INTO questions VALUES('ETSI-BFR-01A','ETSI-BFR','Existe conscientização básica sobre riscos de viés em sistemas de IA utilizados pela organização?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-BFR-01B','ETSI-BFR','Medidas informais são adotadas para mitigar vieses quando identificados?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-BFR-01C','ETSI-BFR','Existem procedimentos sistemáticos para identificar e avaliar vieses em sistemas de IA?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-BFR-01D','ETSI-BFR','Estratégias formais de mitigação de viés são aplicadas e revisadas periodicamente?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-BFR-01E','ETSI-BFR','A avaliação e mitigação de viés ocorre ao longo do uso e operação dos sistemas de IA?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('ETSI-BFR-01F','ETSI-BFR','As práticas de mitigação de viés são monitoradas continuamente em sistemas de IA em produção?','Não','Sim',NULL,NULL,6,1,datetime('now'),datetime('now'));

-- Section 2: Governança, Estratégia e Accountability (GSA)
-- Área: Governança, Estratégia e Conformidade (GSA-GSC)
INSERT OR IGNORE INTO questions VALUES('GSA-GSC-01A','GSA-GSC','Existe uma estratégia inicial ou diretriz informal para o uso de IA na organização?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-GSC-01B','GSA-GSC','Existem métricas básicas para acompanhar iniciativas e uso de IA?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-GSC-01C','GSA-GSC','A estratégia de IA está formalmente definida e comunicada aos stakeholders?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-GSC-01D','GSA-GSC','As métricas relacionadas à IA são revisadas e utilizadas em decisões gerenciais?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-GSC-01E','GSA-GSC','A estratégia de IA está integrada à estratégia de negócio da organização?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));

-- Área: Políticas, Conformidade Legal e Accountability (GSA-PLA)
INSERT OR IGNORE INTO questions VALUES('GSA-PLA-01A','GSA-PLA','Existe conscientização básica sobre requisitos legais e regulatórios aplicáveis ao uso de IA (ex.: LGPD, GDPR)?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-PLA-01B','GSA-PLA','Existe uma política formal para uso de IA claramente comunicada internamente?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-PLA-01C','GSA-PLA','Requisitos de conformidade relacionados à IA são documentados e revisados periodicamente?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-PLA-01D','GSA-PLA','A conformidade com requisitos legais e éticos de IA é monitorada continuamente?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-PLA-01E','GSA-PLA','Existem políticas de denúncia que protegem colaboradores que reportam riscos ou problemas relacionados à IA?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));

-- Área: Capacitação e Cultura de Segurança em IA (GSA-CUL)
INSERT OR IGNORE INTO questions VALUES('GSA-CUL-01A','GSA-CUL','Existe conscientização ou treinamento informal sobre riscos de segurança associados ao uso de IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-CUL-01B','GSA-CUL','A comunicação sobre riscos de segurança de IA ocorre de forma esporádica ou ad hoc?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-CUL-01C','GSA-CUL','Existem programas formais de treinamento em segurança de IA para equipes relevantes?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-CUL-01D','GSA-CUL','A organização promove comunicação contínua sobre boas práticas de segurança em IA?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('GSA-CUL-01E','GSA-CUL','Existe uma cultura organizacional de conscientização contínua sobre riscos de IA?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));

-- Section 3: Identidade, Autonomia e Controle de Acesso (IAA)
-- Área: Governança de Identidade para IA e Agents (IAA-IGO)
INSERT OR IGNORE INTO questions VALUES('IAA-IGO-01A','IAA-IGO','Existe clareza formal sobre quem é responsável por identidades e acessos de sistemas de IA e agentes automatizados?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-IGO-01B','IAA-IGO','Sistemas de IA e agentes possuem identidades próprias, distintas de usuários humanos?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-IGO-01C','IAA-IGO','Existe segregação clara entre identidades usadas para: experimentação, operação, administração de sistemas de IA?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-IGO-01D','IAA-IGO','O uso de contas genéricas ou compartilhadas por sistemas de IA é proibido ou controlado?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));

-- Área: Gestão de Credenciais e Segredos (IAA-CSM)
INSERT OR IGNORE INTO questions VALUES('IAA-CSM-01A','IAA-CSM','Credenciais, tokens e chaves usadas por sistemas de IA são armazenadas de forma segura (ex.: vault, secret manager)?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-CSM-01B','IAA-CSM','Existe rotação automática de credenciais usadas por IA, agentes ou integrações remotas?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-CSM-01C','IAA-CSM','Sistemas de IA utilizam credenciais com privilégio mínimo, compatível com sua função operacional?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-CSM-01D','IAA-CSM','Existe monitoramento de uso indevido ou anômalo de credenciais associadas a IA?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-CSM-01E','IAA-CSM','Credenciais de IA são revogadas automaticamente quando sistemas, agentes ou integrações são desativados?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));

-- Área: Agents, Autonomia e Privilégio (IAA-AAP)
INSERT OR IGNORE INTO questions VALUES('IAA-AAP-01A','IAA-AAP','Existe limitação explícita de escopo de ação para agentes baseados em IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-AAP-01B','IAA-AAP','Agentes de IA executam ações administrativas ou sensíveis com aprovação humana?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-AAP-01C','IAA-AAP','Existem mecanismos de “human-in-the-loop” para ações privilegiadas executadas por agentes?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('IAA-AAP-01D','IAA-AAP','As ações executadas por agentes de IA são: autenticadas, registradas, auditáveis por identidade própria?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));

-- Section 4: Dados, Proveniência e Uso Responsável (DPR)
-- Área: Inventário e Proveniência (DPR-IPU)
INSERT OR IGNORE INTO questions VALUES('DPR-IPU-01A','DPR-IPU','O inventário de ativos identifica sistemas de IA, incluindo “Shadow AI” ou IA embutida em softwares corporativos?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('DPR-IPU-01B','DPR-IPU','A organização mantém registro dos componentes de IA utilizados (modelos, APIs, bibliotecas, fornecedores)?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('DPR-IPU-01C','DPR-IPU','Existem mecanismos técnicos para rastrear a proveniência do conteúdo gerado por IA?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));

-- Área: Qualidade, Governança e Minimização de Dados (DPR-DGM)
INSERT OR IGNORE INTO questions VALUES('DPR-DGM-01A','DPR-DGM','Existem práticas informais para garantir qualidade básica dos dados usados por sistemas de IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('DPR-DGM-01B','DPR-DGM','Verificações de integridade de dados são realizadas ocasionalmente?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('DPR-DGM-01C','DPR-DGM','Existem procedimentos formais para gestão da qualidade dos dados utilizados por IA?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('DPR-DGM-01D','DPR-DGM','Controles de integridade de dados são aplicados de forma consistente e revisados regularmente?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('DPR-DGM-01E','DPR-DGM','A governança de dados relacionados à IA está formalmente definida e integrada às operações?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));

-- Section 5: Privacidade, Direitos do Usuário e Transparência (PUT)
-- Área: Privacidade, Transparência ao Usuário e Controle (PUT-PUC)
INSERT OR IGNORE INTO questions VALUES('PUT-PUC-01A','PUT-PUC','Existe conscientização básica sobre privacidade no uso de IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('PUT-PUC-01B','PUT-PUC','Configurações padrão de privacidade (Privacy by Default) são consideradas no uso de sistemas de IA?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('PUT-PUC-01C','PUT-PUC','Existem procedimentos formais de privacidade por design aplicáveis ao uso de IA?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('PUT-PUC-01D','PUT-PUC','Usuários recebem informações claras sobre uso de dados e IA?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('PUT-PUC-01E','PUT-PUC','Existem mecanismos para que usuários exerçam controle sobre seus dados pessoais?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));

-- Section 6: Segurança Técnica, Arquitetura e Operações de IA (TSA)
-- Área: Ameaças, Riscos e Segurança Operacional (TSA-TRO)
INSERT OR IGNORE INTO questions VALUES('TSA-TRO-01A','TSA-TRO','Existe identificação informal de ameaças específicas relacionadas ao uso de IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('TSA-TRO-01B','TSA-TRO','Ameaças de IA são sistematicamente identificadas e documentadas?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('TSA-TRO-01C','TSA-TRO','Estratégias formais de mitigação de riscos de IA são aplicadas e revisadas?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('TSA-TRO-01D','TSA-TRO','Avaliações de risco são integradas ao ciclo operacional dos sistemas de IA?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));

-- Área: Implantação Segura e Arquitetura (TSA-SDA)
INSERT OR IGNORE INTO questions VALUES('TSA-SDA-01A','TSA-SDA','Existem práticas informais para implantação segura de sistemas de IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('TSA-SDA-01B','TSA-SDA','Existem procedimentos formais para implantação segura de IA em produção?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('TSA-SDA-01C','TSA-SDA','Controles técnicos de acesso e isolamento são aplicados a modelos e configurações em produção?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('TSA-SDA-01D','TSA-SDA','Existem critérios formais de risco (Go/No-Go) para autorizar implantações de IA?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));

-- Área: Defeitos, Monitoramento e Conteúdo Prejudicial (TSA-DMH)
INSERT OR IGNORE INTO questions VALUES('TSA-DMH-01A','TSA-DMH','Existe rastreamento informal de defeitos ou falhas em sistemas de IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('TSA-DMH-01B','TSA-DMH','Processos formais de gestão de defeitos em sistemas de IA estão implementados?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('TSA-DMH-01C','TSA-DMH','Existe detecção e bloqueio de geração de conteúdo sintético prejudicial na saída dos sistemas?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));

-- Section 7: Qualidade, Avaliação, Incidentes e Resiliência (QEI)
-- Área: Testes, Avaliação e Independência (QEI-TEI)
INSERT OR IGNORE INTO questions VALUES('QEI-TEI-01A','QEI-TEI','Testes básicos são realizados para verificar requisitos de segurança e uso adequado da IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-TEI-01B','QEI-TEI','Existe uma abordagem formal para testes baseados em requisitos aplicáveis ao uso de IA?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-TEI-01C','QEI-TEI','As equipes que avaliam sistemas de IA são independentes das equipes que os operam ou configuram?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));

-- Área: Incidentes, Eventos e Continuidade (QEI-IEC)
INSERT OR IGNORE INTO questions VALUES('QEI-IEC-01A','QEI-IEC','Existem procedimentos informais para resposta a incidentes envolvendo IA?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-IEC-01B','QEI-IEC','Existe um processo formal de resposta a incidentes específicos de IA?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-IEC-01C','QEI-IEC','Existe um procedimento documentado de desativação (“kill switch”) para sistemas de IA, incluindo revogação imediata de credenciais e desativação de identidade de agentes?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-IEC-01D','QEI-IEC','Existem playbooks específicos para comprometimento de identidades de IA?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-IEC-01E','QEI-IEC','Eventos e incidentes de IA são monitorados, registrados e analisados regularmente?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));

-- Área: Operação, Monitoramento Contínuo e Melhoria (QEI-OCM)
INSERT OR IGNORE INTO questions VALUES('QEI-OCM-01A','QEI-OCM','A operação de sistemas de IA é monitorada informalmente?','Não','Sim',NULL,NULL,1,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-OCM-01B','QEI-OCM','Existem processos operacionais formais para gestão contínua de IA?','Não','Sim',NULL,NULL,2,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-OCM-01C','QEI-OCM','O acesso de sistemas de IA a ambientes remotos (cloud, SaaS, APIs externas) é explicitamente autorizado e monitorado?','Não','Sim',NULL,NULL,3,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-OCM-01D','QEI-OCM','Existe segregação entre acessos de IA a ambientes produtivos e não produtivos?','Não','Sim',NULL,NULL,4,1,datetime('now'),datetime('now'));
INSERT OR IGNORE INTO questions VALUES('QEI-OCM-01E','QEI-OCM','A eficácia operacional dos sistemas de IA é medida e utilizada para melhoria contínua?','Não','Sim',NULL,NULL,5,1,datetime('now'),datetime('now'));


-- ========================================
-- Maturity Progression Data
-- ========================================

-- FOUNDATIONAL CAPABILITIES
INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-AIT', 2, 
'Team willingness to experiment with new tools|Basic development environment setup|Management approval for tool trials',
'Tool Selection & Setup: Evaluate and select primary AI assistant (GitHub Copilot / Cursor etc), Set up accounts and IDE integrations for 3-5 developers, Create shared team accounts where possible|Pilot Program: Select 2-3 volunteers for initial adoption, Start with simple code completion tasks, Document experiences and productivity gains|Basic Training: Conduct 2-hour workshop on prompt engineering basics, Share best practices for code generation, Create simple usage guidelines',
'80% of team members have AI tools installed and configured|At least 3 team members using AI tools daily|10+ documented use cases of successful AI assistance',
'6-8 weeks',
'Choosing tools without considering team needs or security; no usage guidelines established');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-AIT', 3,
'Positive pilot program results|Basic team familiarity with AI tools|Identified AI champions within the team',
'Standardization: Select 2-3 standardized AI tools for the entire team, Create procurement process for enterprise licenses, Establish consistent configurations and plugins|Training Program: Deliver comprehensive AI tool training to all team members, Create internal documentation and best practices guide, Establish peer mentoring system|Workflow Integration: Integrate AI tools into standard development workflows, Create templates for common AI prompts, Establish code review processes that include AI-generated code|Measurement System: Implement basic metrics tracking (usage / satisfaction / productivity), Set up regular feedback collection, Create monthly usage reports',
'90% team adoption rate|Standardized tool configurations across team|Documented productivity improvements (20-30%)|Established feedback and improvement processes',
'8-10 weeks',
'Scaling without standardization; inadequate enterprise integration; uncontrolled costs');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-AIT', 4,
'Proven ROI from team-wide adoption|Executive sponsorship and budget approval|IT/Security team engagement',
'Enterprise Architecture: Design enterprise AI development platform architecture, Select enterprise-grade AI tools and platforms, Plan integration with existing development infrastructure|Security & Governance: Implement security controls and data governance, Create AI usage policies and compliance frameworks, Set up monitoring and audit capabilities|Platform Implementation: Deploy centralized AI platform infrastructure, Integrate with LDAP / SSO and enterprise identity systems, Set up centralized logging and monitoring|Organization Rollout: Create organization-wide training programs, Establish center of excellence for AI development, Implement usage analytics and optimization',
'Enterprise platform serving 100+ developers|Integrated security and governance controls|Centralized analytics and optimization|50%+ productivity improvements across organization',
'16-20 weeks',
'Over-engineering platform complexity; vendor lock-in; building systems without clear ROI');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-ALS', 2,
'Team commitment to learning|Time allocation for training activities|Access to learning resources',
'Foundation Learning: Enroll team in basic AI/ML concepts course (Coursera / edX / LinkedIn Learning), Conduct weekly 1-hour AI literacy sessions, Create shared learning resources library|Hands-on Experience: Practice with different AI tools for 30 minutes daily, Complete guided exercises with AI-assisted coding, Share weekly learnings and discoveries|Basic Prompt Engineering: Learn fundamental prompt engineering techniques, Practice with different types of coding prompts, Create personal prompt libraries',
'100% team completion of basic AI concepts course|Each team member has personal AI tool usage examples|Basic prompt engineering competency demonstrated',
'6-8 weeks',
'One-size-fits-all training; no hands-on practice; underestimating resistance to change');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-ALS', 3,
'Completed basic AI literacy training|Regular AI tool usage experience|Management support for formal training programs',
'Formal Training Program: Design comprehensive AI-first development curriculum, Include advanced prompt engineering / AI tool mastery and AI-assisted architecture, Bring in external trainers or create internal certification|Practical Application Projects: Assign AI-focused development projects to each team member, Create mentorship pairs for knowledge transfer, Document and share successful AI implementation patterns|Knowledge Sharing System: Establish regular AI knowledge sharing sessions, Create internal wiki/documentation for AI best practices, Set up cross-team collaboration on AI techniques',
'Formal AI competency certification for team members|Multiple completed AI-focused projects|Active internal knowledge sharing community|40-50% improvement in AI-assisted development speed',
'10-12 weeks',
'Training without practical application; skill gaps between team members; no mentoring system');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-ALS', 4,
'Advanced AI tool proficiency|Successful AI project implementations|Recognition as internal AI experts',
'Advanced Specialization: Team members specialize in different AI domains (testing / architecture / monitoring), Pursue advanced certifications in AI/ML platforms, Contribute to open source AI development tools|Innovation Program: Establish innovation time for AI experimentation, Create proof-of-concepts for emerging AI technologies, Present at conferences and industry events|Thought Leadership: Publish internal and external content on AI-first development, Mentor other teams in AI adoption, Create reusable frameworks and tools for AI development',
'Team recognized as internal AI experts and consultants|Multiple innovations and POCs developed|External thought leadership activities|80%+ of development tasks AI-enhanced',
'20-24 weeks',
'Over-specialization without cross-functional knowledge; knowledge hoarding; neglecting human collaboration skills');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-CGR', 2,
'AI coding tools installed and configured|Basic prompt engineering skills|Code review process in place',
'Start Simple: Use AI for code completion and suggestions, Generate boilerplate code and templates, Ask AI to explain unfamiliar code patterns|Establish Patterns: Create templates for common AI coding prompts, Document successful AI-generated code examples, Share effective prompting techniques|Review Process Integration: Add AI-generated code identification to review checklist, Create guidelines for reviewing AI-generated code, Train reviewers on common AI code patterns and issues',
'50%+ of team using AI for daily coding tasks|Established templates and patterns for AI coding|Updated code review processes including AI considerations',
'6-8 weeks',
'Over-relying on AI without understanding output; no review processes for AI-generated code');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-CGR', 3,
'Comfort with AI-assisted coding|Established code review processes|Team experience with AI tools',
'Advanced Code Generation: Use AI for complex function and class generation, Generate comprehensive test cases with AI, Create AI-assisted refactoring workflows|Quality Assurance Integration: Implement AI-powered code quality checks, Use AI for automated code review comments, Set up AI-assisted documentation generation|Workflow Optimization: Integrate AI tools into IDE and development workflows, Create automated pipelines that include AI-generated code, Establish metrics for AI-assisted development productivity',
'70%+ of new code has AI assistance|Automated AI integration in development workflows|Measurable productivity improvements (30-40%)|Quality metrics maintained or improved',
'8-10 weeks',
'Inconsistent review standards; accumulating technical debt from poor AI suggestions; security vulnerabilities');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-CGR', 4,
'Mature AI-assisted development practices|Advanced team AI competency|Established quality and security processes',
'Intelligent Code Generation: Implement intent-to-code generation systems, Create AI-powered architecture generation tools, Develop context-aware code generation pipelines|Automated Review Systems: Deploy AI-powered automated code review, Implement intelligent code quality gates, Create self-improving code suggestion systems|Continuous Learning Integration: Set up systems that learn from team coding patterns, Implement personalized AI assistants for each developer, Create feedback loops that improve AI suggestions over time',
'85%+ of code has intelligent AI assistance|Automated code review catching 80%+ of issues|Self-improving AI systems showing continuous enhancement|Team velocity increased by 60%+ compared to manual development',
'16-20 weeks',
'Over-automation without human oversight; developer skill atrophy; blind trust in AI systems');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-DKM', 2,
'Basic documentation processes in place|AI tools available for text generation|Team awareness of documentation importance',
'AI Documentation Tools: Set up AI tools for documentation generation (GPT-4 / Claude etc.), Train team on using AI for documentation tasks, Create templates for common documentation types|Basic AI Integration: Use AI to generate README files and code comments, Create API documentation with AI assistance, Generate meeting summaries and project updates with AI|Quality Framework: Establish quality standards for AI-generated documentation, Create review processes for AI-assisted content, Develop guidelines for editing and improving AI output',
'60%+ of documentation has AI assistance|Established quality standards and review processes|Reduced time spent on documentation by 30%',
'5-6 weeks',
'AI content without quality control; no review processes; inconsistent formatting and style');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-DKM', 3,
'Experience with AI-assisted documentation|Established documentation quality standards|Integration capabilities with development tools',
'Automated Documentation Pipeline: Integrate AI documentation generation into CI/CD pipelines, Set up automated generation of API docs / changelogs and release notes, Create intelligent documentation templates based on code analysis|Knowledge Base Integration: Implement AI-powered search and discovery in documentation, Create intelligent linking between related documentation, Set up automated content updates based on code changes|Advanced Content Generation: Generate comprehensive user guides and tutorials with AI, Create context-aware help content, Implement AI-powered documentation maintenance and updates',
'80%+ of documentation automatically generated or updated|Intelligent search and discovery implemented|Documentation maintenance time reduced by 60%|Improved documentation quality and consistency scores',
'10-12 weeks',
'Automation without governance; content quality degradation; poor user adoption of new systems');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('FC-DKM', 4,
'Mature automated documentation systems|Advanced AI tool integration|Enterprise knowledge management infrastructure',
'Intelligent Knowledge Graph: Build knowledge graphs connecting code / documentation and business context, Implement semantic search across all knowledge assets, Create AI-powered knowledge discovery and recommendation systems|Context-Aware Documentation: Deploy AI that generates documentation based on user context and role, Implement personalized documentation experiences, Create intelligent onboarding and learning pathways|Predictive Knowledge Management: Implement AI that predicts documentation needs, Create systems that proactively update documentation based on code changes, Deploy intelligent content governance and lifecycle management',
'Intelligent knowledge graph serving all development content|Personalized documentation experiences for different user types|Proactive documentation updates with 95%+ accuracy|Knowledge discovery time reduced by 80%',
'20-24 weeks',
'Over-reliance on AI insights; loss of institutional domain knowledge; system complexity overwhelming users');

-- TRANSFORMATION CAPABILITIES
INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-IAT', 2,
'Established requirements gathering processes|Basic understanding of system architecture|AI tools capable of text analysis and generation',
'AI-Enhanced Requirements Gathering: Use AI to analyze and clarify business requirements, Generate initial user stories and acceptance criteria with AI, Create AI-assisted stakeholder interview summaries|Basic Architecture Suggestions: Prompt AI tools to suggest high-level architecture patterns, Use AI to generate component diagrams and system overviews, Create AI-assisted technology stack recommendations|Documentation and Validation: Generate architecture documentation with AI assistance, Use AI to validate requirements consistency and completeness, Create AI-powered requirements traceability matrices',
'50%+ of requirements analysis includes AI assistance|Basic architecture suggestions generated for all new projects|Improved requirements clarity and consistency scores',
'6-8 weeks',
'Unclear requirements input to AI; accepting suggestions without validation; no stakeholder buy-in');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-IAT', 3,
'Experience with AI-assisted requirements analysis|Architecture review processes in place|Advanced AI tools for technical design',
'Advanced Architecture Generation: Implement AI systems that generate detailed architecture from business goals, Create automated system design workflows, Build AI-powered architecture pattern libraries|Validation and Optimization: Develop AI-powered architecture validation against best practices, Implement automated compliance and security checks, Create AI-assisted architecture optimization recommendations|Integration with Development: Connect architecture generation to code scaffolding, Implement automated project setup based on generated architectures, Create feedback loops from implementation back to architecture',
'Complete architectures generated from business requirements|80%+ of generated architectures pass validation checks|Integrated architecture-to-implementation workflows|Architecture quality metrics improved by 40%',
'10-12 weeks',
'Generated architectures without feasibility analysis; no integration planning; scope and complexity creep');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-IAT', 4,
'Mature architecture generation capabilities|Established validation and quality processes|Enterprise architecture governance framework',
'Semantic Traceability System: Build complete traceability from business intent to implementation, Implement AI-powered impact analysis for requirement changes, Create intelligent architecture evolution and versioning|Automated Architecture Pipeline: Deploy fully automated intent-to-architecture-to-code pipelines, Implement continuous architecture optimization, Create self-healing architecture recommendations|Enterprise Integration: Integrate with enterprise architecture management tools, Implement organization-wide architecture pattern libraries, Create AI-powered architecture governance and compliance',
'Complete semantic traceability from intent to implementation|Fully automated architecture generation pipeline|Enterprise-wide architecture consistency and governance|Architecture delivery time reduced by 80%',
'20-24 weeks',
'Automation without business context; loss of architectural expertise; rigid system dependencies');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-ATQ', 2,
'Existing testing processes and frameworks|Basic understanding of test automation|AI tools capable of code analysis',
'AI Test Generation Setup: Implement AI tools for basic test case generation, Train team on AI-assisted testing techniques, Create templates for AI-generated test prompts|Basic Test Automation: Generate unit tests for existing code using AI, Create AI-assisted integration test scenarios, Implement AI-powered test data generation|Quality Integration: Integrate AI-generated tests into existing test suites, Set up basic test quality metrics and validation, Create processes for reviewing and maintaining AI-generated tests',
'25-50% of tests have AI assistance in generation|Established AI test generation templates and processes|Maintained or improved test coverage metrics',
'7-8 weeks',
'AI-generated tests without validation; coverage gaps; false confidence in AI testing capabilities');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-ATQ', 3,
'Experience with AI-assisted test generation|Established test automation infrastructure|Team competency in advanced testing practices',
'Advanced Test Generation: Implement AI-powered test case design from requirements, Create intelligent test scenario generation for complex workflows, Deploy AI-assisted performance and security test creation|Self-Healing Test Infrastructure: Implement AI-powered test maintenance and updates, Create intelligent test failure analysis and auto-correction, Deploy adaptive test execution based on code changes|Quality Intelligence: Build AI-powered quality prediction and risk assessment, Implement intelligent test prioritization and selection, Create automated quality gates with AI-driven decision making',
'50-85% of testing processes leverage AI automation|Self-healing test infrastructure reducing maintenance by 60%|Predictive quality metrics and intelligent test selection|Overall testing efficiency improved by 50%',
'10-12 weeks',
'Test automation without maintenance strategy; over-reliance degrading manual testing skills');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-ATQ', 4,
'Mature AI-driven testing capabilities|Advanced test automation infrastructure|Executive support for autonomous testing initiatives',
'Autonomous Test Systems: Deploy fully autonomous test generation / execution and maintenance, Implement AI systems that create comprehensive test strategies, Build predictive testing that prevents issues before they occur|Intelligent Quality Orchestration: Create AI that orchestrates all quality assurance activities, Implement autonomous quality decision-making systems, Deploy intelligent quality coaching and improvement recommendations|Continuous Learning Integration: Build systems that learn from production issues to improve testing, Implement AI that evolves testing strategies based on outcomes, Create predictive quality assurance that anticipates future issues',
'85%+ of testing fully autonomous with predictive capabilities|Zero-touch quality assurance for standard development workflows|Predictive issue prevention with 90%+ accuracy|Quality delivery time reduced by 75%',
'20-24 weeks',
'Autonomous systems without human oversight; missing critical edge cases; regulatory compliance gaps');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-CID', 2,
'Existing CI/CD infrastructure and processes|Basic monitoring and alerting in place|Team familiarity with pipeline management',
'AI-Enhanced Pipeline Analytics: Implement AI-powered build failure analysis, Add intelligent alerting and notification systems, Create AI-assisted pipeline optimization suggestions|Basic Intelligent Automation: Deploy AI-powered deployment risk assessment, Implement intelligent rollback decision support, Create AI-assisted pipeline troubleshooting|Performance Intelligence: Add AI-powered performance monitoring to pipelines, Implement intelligent resource allocation for builds, Create predictive pipeline capacity planning',
'AI-enhanced analytics covering all CI/CD processes|Intelligent alerting reducing noise by 50%|Basic AI-assisted decision making in deployments',
'6-8 weeks',
'AI insights without actionable responses; alert fatigue; poor integration with existing tools');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-CID', 3,
'AI-enhanced CI/CD capabilities|Advanced monitoring and observability|Team experience with AI-assisted development',
'Intelligent Pipeline Orchestration: Deploy AI systems that optimize pipeline workflows, Implement adaptive testing and deployment strategies, Create intelligent environment management and provisioning|Advanced Issue Detection: Build AI-powered code quality gates and assessments, Implement predictive failure detection and prevention, Create intelligent dependency management and conflict resolution|Automated Optimization: Deploy AI systems that continuously optimize pipeline performance, Implement intelligent resource scaling and management, Create adaptive deployment strategies based on AI analysis',
'Intelligent pipeline optimization reducing build times by 40%|AI-powered issue detection preventing 70% of potential failures|Automated optimization improving resource efficiency by 50%',
'10-12 weeks',
'Optimization without understanding business impact; over-complex pipelines; performance degradation');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-CID', 4,
'Advanced intelligent CI/CD capabilities|Mature DevOps culture and practices|Executive support for autonomous deployment',
'Autonomous Deployment Systems: Build fully autonomous deployment decision-making systems, Implement AI that manages complex multi-environment deployments, Create self-healing deployment infrastructure|Adaptive Strategy Management: Deploy AI systems that adapt deployment strategies in real-time, Implement autonomous canary and blue-green deployment management, Create intelligent disaster recovery and rollback systems|Predictive Operations: Build AI systems that predict and prevent operational issues, Implement autonomous capacity planning and scaling, Create intelligent compliance and governance automation',
'Fully autonomous deployment decisions for 90% of changes|Self-healing infrastructure resolving 85% of issues automatically|Predictive operations preventing 95% of potential incidents|Deployment velocity increased by 10x with improved reliability',
'20-24 weeks',
'Over-automation without fallback procedures; loss of operational knowledge; vendor dependencies');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-MOB', 2,
'Basic monitoring and alerting infrastructure in place|Access to system logs and performance metrics|Team understanding of observability principles',
'AI-Enhanced Alert Management: Implement AI-powered alert correlation and deduplication, Set up intelligent alert prioritization based on business impact, Create AI-assisted root cause analysis for common issues|Anomaly Detection Implementation: Deploy machine learning models for performance anomaly detection, Implement intelligent baseline establishment and drift detection, Create automated anomaly investigation and documentation|Enhanced Dashboards and Insights: Build AI-powered dashboards with intelligent insights, Implement predictive performance indicators, Create automated reporting with AI-generated summaries',
'AI-enhanced anomaly detection reducing false positives by 60%|Intelligent alert correlation decreasing alert noise by 50%|Automated insights and reporting saving 40% of manual analysis time',
'9-12 months',
'AI alerts without business context; false positives overwhelming teams; no root cause analysis');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-MOB', 3,
'AI-enhanced monitoring capabilities deployed|Historical performance and incident data available|Advanced observability tools and platforms',
'Intelligent Incident Classification: Build AI models that automatically classify and categorize incidents, Implement intelligent incident routing and assignment, Create automated incident impact assessment and escalation|Automated Initial Response: Deploy AI systems that provide initial incident response recommendations, Implement automated diagnostic data collection and analysis, Create intelligent runbook execution and decision support|Proactive Monitoring Intelligence: Build predictive models for system health and performance, Implement AI-powered capacity planning and resource optimization, Create intelligent maintenance scheduling and recommendation systems',
'Automated incident classification with 85% accuracy|AI-powered initial response reducing MTTR by 45%|Proactive monitoring preventing 70% of potential incidents',
'18-24 months',
'Automation without validation; incident classification errors; delayed response times');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-MOB', 4,
'Mature intelligent monitoring capabilities|Advanced AI and machine learning infrastructure|Executive support for autonomous operations',
'Predictive Issue Resolution: Deploy AI systems that predict and prevent issues before they impact users, Implement autonomous system optimization and tuning, Create self-healing infrastructure with minimal human intervention|Autonomous Operations Management: Build AI that manages complete operational workflows autonomously, Implement intelligent disaster recovery and business continuity, Create autonomous scaling and resource management systems|Continuous Learning and Optimization: Deploy AI systems that continuously learn from operational patterns, Implement self-improving monitoring and response capabilities, Create intelligent operational coaching and best practice recommendations',
'Predictive issue resolution preventing 95% of potential outages|Autonomous operations handling 90% of routine operational tasks|Self-improving systems showing continuous performance enhancement',
'30-36 months',
'Over-reliance on predictive models; loss of operational expertise; system becoming black boxes');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-LSM', 2,
'Inventory of legacy systems requiring modernization|Access to legacy system documentation and code|Basic understanding of target modern architectures',
'AI-Powered System Analysis: Use AI tools to analyze and document legacy system architectures, Generate comprehensive system maps and dependency analysis, Create AI-assisted business logic documentation and extraction|Code Analysis and Documentation: Deploy AI tools for legacy code analysis and understanding, Generate modernization feasibility assessments with AI, Create AI-assisted technical debt analysis and prioritization|Initial Migration Planning: Use AI to generate high-level modernization roadmaps, Create AI-assisted risk assessment for migration strategies, Generate preliminary effort estimates and resource planning',
'Complete legacy system analysis and documentation using AI|AI-generated modernization roadmaps for all target systems|Documented technical debt and risk assessments',
'12-15 months',
'AI analysis without domain expert validation; incomplete documentation; missed critical dependencies');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-LSM', 3,
'Completed AI-assisted legacy system analysis|Established modernization goals and target architectures|Migration methodology and tools selected',
'Advanced Migration Planning: Deploy AI systems that generate detailed migration strategies, Implement automated code transformation and refactoring suggestions, Create AI-powered data migration planning and validation|Intelligent Refactoring Support: Build AI tools that suggest optimal refactoring approaches, Implement automated code pattern recognition and modernization, Create AI-assisted API design and integration planning|Migration Validation and Testing: Deploy AI-powered migration testing and validation, Implement intelligent functional equivalence verification, Create automated performance and compatibility testing',
'AI-generated detailed migration plans with 80% accuracy|Automated refactoring suggestions reducing manual effort by 60%|AI-powered testing validating migration success with 90% coverage',
'18-24 months',
'Migration planning without comprehensive risk assessment; timeline optimism; insufficient testing');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('TC-LSM', 4,
'Mature AI-powered migration planning capabilities|Successful pilot migrations with AI assistance|Advanced automation and orchestration infrastructure',
'Autonomous Code Transformation: Deploy AI systems that autonomously transform legacy code, Implement intelligent modernization with minimal human intervention, Create self-validating transformation processes|Intelligent Migration Orchestration: Build AI systems that orchestrate complex multi-system migrations, Implement autonomous data migration with integrity validation, Create intelligent rollback and recovery capabilities|Continuous Modernization Systems: Deploy AI that continuously identifies modernization opportunities, Implement autonomous technical debt reduction programs, Create intelligent architecture evolution and optimization',
'Autonomous code transformation handling 85% of migration work|Intelligent orchestration managing complex migrations with 95% success rate|Continuous modernization systems preventing technical debt accumulation',
'30-36 months',
'Autonomous transformation without business validation; loss of tribal knowledge; system disruption');

-- ENTERPRISE INTEGRATION
INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-DGM', 2,
'Executive awareness of data governance needs|Basic understanding of data types used in AI development|Legal/Compliance team engagement',
'Data Discovery and Classification: Inventory all data sources used in AI development, Classify data by sensitivity and regulatory requirements, Create basic data handling policies for AI systems|Basic Governance Framework: Establish data governance committee with AI representation, Create initial policies for AI data usage and retention, Implement basic access controls and audit logging|Compliance Foundation: Assess regulatory requirements (GDPR / CCPA / industry-specific), Create basic compliance checklists for AI development, Implement initial data lineage tracking',
'Complete data inventory and classification system|Basic governance policies and procedures documented|Initial compliance framework implemented',
'12-15 months',
'Policy creation without enforcement mechanisms; compliance theater without real protection');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-DGM', 3,
'Basic data governance framework in place|Data classification and policies established|Team training on governance requirements',
'Automated Governance Controls: Implement automated data classification and tagging, Deploy policy enforcement in AI development workflows, Create automated compliance monitoring and reporting|Advanced Data Management: Build comprehensive data lineage and impact analysis, Implement data quality monitoring and validation, Create automated data lifecycle management|Integration and Orchestration: Integrate governance controls with AI development platforms, Create centralized data governance dashboard, Implement automated policy updates and distribution',
'Automated governance controls in all AI workflows|Comprehensive data lineage and quality monitoring|Integrated governance dashboard providing real-time insights',
'18-24 months',
'Automation without human validation; governance overhead hindering productivity; user resistance');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-DGM', 4,
'Mature automated governance capabilities|Advanced data management infrastructure|Organization-wide governance culture',
'AI-Powered Governance Intelligence: Deploy AI systems that continuously learn and improve governance, Implement intelligent data discovery and classification, Create predictive compliance risk assessment|Advanced Quality Management: Build AI-powered data quality prediction and remediation, Implement intelligent data lineage with semantic understanding, Create autonomous data lifecycle optimization|Strategic Governance Integration: Integrate with enterprise-wide data governance systems, Implement AI-powered policy recommendation and updates, Create intelligent governance coaching and improvement systems',
'AI-powered governance systems providing proactive insights|Autonomous data quality management with 95%+ accuracy|Intelligent policy evolution based on usage patterns and outcomes',
'30-36 months',
'AI governance without human judgment; over-compliance constraining innovation; system rigidity');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-VTS', 2,
'Executive awareness of AI tool proliferation and costs|Basic understanding of vendor landscape|IT procurement team engagement',
'Vendor Assessment Framework: Create evaluation criteria for AI tool selection, Assess current AI tool usage across teams, Establish basic vendor security and compliance requirements|Initial Standardization: Select 2-3 primary AI development platforms, Negotiate basic enterprise agreements, Create initial tool approval and procurement processes|Basic Governance: Establish AI tool governance committee, Create initial policies for tool evaluation and approval, Implement basic cost tracking and budgeting',
'Standardized evaluation framework for AI tools|Enterprise agreements for primary AI platforms|Basic governance processes and cost tracking implemented',
'12-15 months',
'Standardization without user input; vendor lock-in without alternatives; governance overhead slowing adoption');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-VTS', 3,
'Basic vendor standardization in place|Enterprise agreements established|Tool governance processes implemented',
'Strategic Vendor Partnerships: Develop strategic partnerships with key AI vendors, Negotiate volume discounts and enterprise features, Create vendor roadmap alignment and influence programs|Advanced Tool Integration: Integrate standardized tools with enterprise systems, Create centralized tool management and provisioning, Implement advanced usage analytics and optimization|Vendor Risk Management: Establish vendor risk assessment and management, Create backup vendor strategies and contingency plans, Implement vendor performance monitoring and SLA management',
'Strategic partnerships with key AI vendors|Integrated tool management with enterprise systems|Comprehensive vendor risk management and performance monitoring',
'18-24 months',
'Over-dependence on single vendors; complex integrations without clear benefits; vendor management overhead');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-VTS', 4,
'Mature vendor partnerships and tool integration|Advanced vendor risk management|Organization-wide tool standardization',
'Intelligent Vendor Orchestration: Deploy AI-powered vendor selection and management, Implement intelligent contract negotiation and optimization, Create autonomous vendor performance monitoring and optimization|Strategic Ecosystem Development: Build strategic AI vendor ecosystem partnerships, Create innovation partnerships and co-development programs, Implement vendor ecosystem intelligence and market analysis|Advanced Value Optimization: Deploy intelligent cost optimization and vendor value analysis, Implement predictive vendor performance and risk management, Create strategic vendor portfolio optimization and evolution',
'AI-powered vendor orchestration and optimization|Strategic ecosystem partnerships driving innovation|Advanced value optimization maximizing vendor ROI',
'30-36 months',
'Automation without strategic oversight; ecosystem complexity without clear value; optimization without innovation consideration');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-IES', 2,
'Inventory of enterprise systems requiring AI integration|Basic understanding of system APIs and integration patterns|IT architecture team engagement',
'Integration Assessment: Map current enterprise systems and integration requirements, Assess AI tool integration capabilities and APIs, Create initial integration architecture and design|Basic Integration Implementation: Implement basic API integrations with key enterprise systems, Create initial data flow and synchronization, Establish basic monitoring and error handling|Integration Governance: Create integration standards and guidelines, Establish integration testing and validation processes, Implement basic security and access controls',
'Basic API integrations with key enterprise systems|Initial data flow and synchronization established|Integration governance and standards implemented',
'12-15 months',
'Point-to-point integrations without architecture; data security gaps; insufficient error handling');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-IES', 3,
'Basic enterprise system integrations in place|Integration architecture and standards established|Integration governance processes implemented',
'Advanced Integration Platform: Deploy enterprise integration platform for AI systems, Implement advanced data transformation and orchestration, Create comprehensive integration monitoring and management|Intelligent Data Flow: Build intelligent data routing and transformation, Implement automated data quality validation and cleansing, Create real-time data synchronization and event processing|Integration Optimization: Deploy integration performance monitoring and optimization, Implement automated integration testing and validation, Create integration analytics and continuous improvement',
'Enterprise integration platform managing all AI system connections|Intelligent data flow with automated quality validation|Integration optimization with performance monitoring and analytics',
'18-24 months',
'Platform complexity without clear benefits; data quality issues; integration performance bottlenecks');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-IES', 4,
'Mature integration platform and data flow management|Advanced integration optimization|Organization-wide system integration',
'Autonomous Integration Management: Deploy AI-powered integration orchestration and management, Implement self-healing integration capabilities, Create autonomous integration optimization and scaling|Intelligent System Orchestration: Build AI systems that intelligently orchestrate enterprise workflows, Implement semantic understanding and intelligent data mapping, Create autonomous business process optimization|Strategic Integration Evolution: Deploy continuously evolving integration architecture, Implement intelligent integration strategy and roadmap development, Create autonomous integration innovation and advancement',
'Autonomous integration management with self-healing capabilities|Intelligent system orchestration optimizing enterprise workflows|Strategic integration evolution driving continuous business value',
'30-36 months',
'Autonomous integration without business oversight; system complexity without user value; evolution without strategic alignment');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-CMR', 2,
'Executive commitment to AI cost management|Basic understanding of AI tool costs and usage|Finance team engagement',
'Cost Discovery and Tracking: Inventory all AI tool costs and subscriptions, Implement basic cost tracking and allocation, Create initial budgeting and cost control processes|ROI Framework Development: Define AI development ROI metrics and KPIs, Create initial ROI measurement and tracking, Establish baseline productivity and efficiency metrics|Basic Financial Governance: Create AI cost governance committee, Establish initial cost approval and oversight processes, Implement basic cost reporting and analysis',
'Complete AI cost inventory and tracking system|ROI measurement framework with baseline metrics established|Basic financial governance processes implemented',
'12-15 months',
'Cost tracking without value attribution; ROI metrics without business context; governance overhead without clear benefits');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-CMR', 3,
'Basic cost tracking and ROI framework in place|Financial governance processes established|Baseline metrics and reporting implemented',
'Advanced Cost Analytics: Deploy comprehensive AI cost analytics and optimization, Implement predictive cost modeling and forecasting, Create automated cost allocation and chargeback systems|ROI Optimization: Build advanced ROI analysis with business value correlation, Implement automated productivity and efficiency measurement, Create ROI-driven investment decision support|Financial Intelligence: Deploy AI-powered financial analysis and insights, Implement intelligent cost optimization recommendations, Create automated financial reporting and dashboards',
'Advanced cost analytics with predictive modeling and optimization|ROI optimization with automated measurement and business value correlation|Financial intelligence providing AI-powered insights and recommendations',
'18-24 months',
'Analytics complexity without actionable insights; ROI optimization without strategic consideration; automation without financial oversight');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-CMR', 4,
'Mature cost analytics and ROI optimization|Advanced financial intelligence and automation|Organization-wide cost management culture',
'Autonomous Financial Management: Deploy AI systems that autonomously manage AI development costs, Implement self-optimizing budget allocation and resource management, Create autonomous ROI maximization and value optimization|Strategic Financial Intelligence: Build AI-powered strategic financial planning and analysis, Implement intelligent investment portfolio optimization, Create autonomous financial strategy and decision support|Value-Driven Financial Evolution: Deploy continuously evolving cost and value optimization, Implement intelligent financial innovation and advancement, Create autonomous financial excellence and competitive advantage',
'Autonomous financial management with self-optimizing resource allocation|Strategic financial intelligence driving AI investment decisions|Value-driven financial evolution maximizing business impact and competitive advantage',
'30-36 months',
'Autonomous management without strategic oversight; financial intelligence without business judgment; evolution without human financial wisdom');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-PSM', 2,
'Understanding of current AI adoption scale and performance|Basic performance metrics and monitoring|Team growth and scaling plans',
'Performance Baseline and Metrics: Establish baseline performance metrics for AI-enhanced development, Implement basic performance monitoring and tracking, Create initial performance improvement targets and goals|Scalability Assessment: Assess current AI tool and process scalability, Identify scalability bottlenecks and limitations, Create initial scaling strategies and plans|Basic Scaling Implementation: Implement basic scaling processes for AI tool adoption, Create initial team onboarding and training scalability, Establish basic resource allocation and capacity planning',
'Performance baseline metrics and monitoring established|Scalability assessment with identified bottlenecks and strategies|Basic scaling processes for AI adoption and team growth',
'12-15 weeks',
'Metrics without actionable insights; scalability planning without practical testing; scaling without quality control');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-PSM', 3,
'Performance monitoring and scalability assessment completed|Basic scaling processes implemented|Initial scaling experience and learnings',
'Advanced Performance Management: Deploy comprehensive performance analytics and optimization, Implement automated performance monitoring and alerting, Create performance-driven continuous improvement processes|Intelligent Scaling Systems: Build intelligent scaling automation and orchestration, Implement adaptive resource allocation and capacity management, Create predictive scaling and performance optimization|Scaling Excellence: Deploy scaling excellence programs and best practices, Implement scaling quality assurance and validation, Create scaling innovation and advancement capabilities',
'Advanced performance management with automated optimization|Intelligent scaling systems with adaptive resource management|Scaling excellence with quality assurance and innovation',
'15-18 weeks',
'Performance optimization without user experience focus; scaling automation without quality validation; excellence programs without practical benefits');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-PSM', 4,
'Mature performance management and intelligent scaling|Advanced scaling excellence and innovation|Organization-wide performance and scaling culture',
'Autonomous Performance Excellence: Deploy self-improving performance optimization throughout the organization, Implement autonomous performance innovation and advancement, Create intelligent performance ecosystem and platform development|Strategic Scaling Leadership: Establish organizational leadership in AI performance and scalability, Create industry partnerships and collaboration on scaling excellence, Implement performance advocacy and thought leadership|Performance-Driven Transformation: Build performance capabilities that create sustainable competitive advantage, Create performance-driven organizational evolution and transformation, Implement performance excellence as core organizational DNA',
'Autonomous performance excellence driving continuous optimization and innovation|Recognized industry leadership in AI performance and scalability|Performance-driven transformation creating sustainable competitive advantage',
'20-24 weeks',
'Autonomous performance without human insight; scaling leadership without practical innovation; transformation without cultural adaptation');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-BCD', 2,
'Understanding of AI system dependencies and risks|Basic business continuity planning experience|IT disaster recovery team engagement',
'Risk Assessment and Planning: Assess AI system dependencies and failure impact, Create initial business continuity plans for AI-dependent processes, Establish basic disaster recovery procedures for AI systems|Backup and Recovery Implementation: Implement basic backup strategies for AI tools and data, Create initial recovery procedures and documentation, Establish basic testing and validation processes|Continuity Governance: Create business continuity governance for AI systems, Establish initial continuity policies and procedures, Implement basic continuity training and awareness',
'Risk assessment and business continuity plans for AI systems|Basic backup and recovery implementation with testing|Continuity governance and policies established',
'7-8 weeks',
'Planning without practical testing; backup strategies without recovery validation; governance without operational integration');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-BCD', 3,
'Basic business continuity plans and backup systems in place|Continuity governance and policies established|Initial testing and validation experience',
'Advanced Continuity Systems: Deploy comprehensive business continuity management for AI systems, Implement automated backup and recovery processes, Create advanced continuity testing and validation|Intelligent Recovery Management: Build intelligent disaster detection and response systems, Implement automated failover and recovery orchestration, Create predictive continuity risk assessment and mitigation|Continuity Excellence: Deploy continuity excellence programs and capabilities, Implement continuity innovation and continuous improvement, Create continuity learning and knowledge management',
'Advanced continuity systems with automated backup and recovery|Intelligent recovery management with automated failover|Continuity excellence with innovation and continuous improvement',
'10-12 weeks',
'Automation without human oversight; recovery systems without business context; excellence programs without practical testing');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('EI-BCD', 4,
'Mature continuity systems and intelligent recovery|Advanced continuity excellence and innovation|Organization-wide continuity culture',
'Autonomous Continuity Excellence: Deploy self-improving continuity capabilities throughout the organization, Implement autonomous continuity adaptation and evolution, Create intelligent continuity ecosystem and platform development|Strategic Continuity Leadership: Establish organizational leadership in AI business continuity and resilience, Create industry partnerships and collaboration on continuity excellence, Implement continuity advocacy and thought leadership|Resilience-Driven Integration: Build continuity capabilities that create sustainable business resilience, Create continuity-driven organizational transformation and evolution, Implement continuity excellence as core organizational DNA',
'Autonomous continuity excellence with self-improving capabilities|Recognized industry leadership in AI business continuity and resilience|Resilience-driven integration creating sustainable business advantage',
'20-24 weeks',
'Autonomous continuity without business judgment; leadership without practical resilience; integration without adaptive capability');

-- STRATEGIC GOVERNANCE
INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-AER', 2,
'Executive awareness of AI ethics and responsible AI importance|Basic understanding of ethical AI principles|Legal/Compliance team engagement on AI ethics',
'Ethical Framework Development: Establish basic AI ethics principles and guidelines, Create initial responsible AI development policies, Implement basic ethical review processes for AI projects|Ethics Training and Awareness: Conduct AI ethics training for development teams, Create awareness programs on responsible AI practices, Establish ethics champions within development teams|Basic Ethics Assessment: Implement basic ethical impact assessments for AI systems, Create simple checklists for ethical AI development, Establish initial bias detection and mitigation procedures',
'Established AI ethics framework and policies|100% team completion of AI ethics training|Basic ethical assessment processes for all AI projects',
'8-10 weeks',
'Ethics policies without enforcement; training without practical application; assessment checklists without real impact');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-AER', 3,
'Basic AI ethics framework and training completed|Established ethical review processes|Team understanding of responsible AI principles',
'Advanced Ethics Integration: Integrate ethical considerations into AI development workflows, Implement automated bias detection and mitigation tools, Create comprehensive ethical impact assessment procedures|Responsible AI Governance: Establish AI ethics committee with diverse representation, Create robust ethical review and approval processes, Implement continuous ethical monitoring and auditing|Stakeholder Engagement: Engage external stakeholders in ethical AI development, Create transparency and accountability reporting mechanisms, Implement ethical AI communication and education programs',
'Integrated ethical considerations in all AI development workflows|Established AI ethics committee with robust governance processes|Transparent ethical AI practices with stakeholder engagement',
'12-14 weeks',
'Ethics integration without workflow disruption balance; governance committee without decision-making authority; stakeholder engagement without meaningful participation');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-AER', 4,
'Mature ethical AI integration and governance|Advanced responsible AI capabilities|Organization-wide ethical AI culture',
'Autonomous Ethics Management: Deploy AI systems that continuously monitor and ensure ethical compliance, Implement self-improving ethical AI frameworks, Create intelligent ethical decision-making support systems|Strategic Ethics Leadership: Establish organizational leadership in AI ethics and responsible AI, Create industry partnerships and collaboration on ethical AI, Implement AI ethics innovation and research programs|Ethical AI Excellence: Build AI systems that exemplify ethical and responsible AI practices, Create ethical AI standards and best practices for industry adoption, Implement ethical AI coaching and consulting capabilities',
'Autonomous ethical AI compliance with 99%+ accuracy|Recognized industry leadership in AI ethics and responsible AI|Ethical AI excellence driving business value and social impact',
'18-20 weeks',
'Autonomous ethics without human oversight; ethics leadership without practical implementation; ethical AI excellence without business alignment');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-PMV', 2,
'Executive commitment to AI value measurement|Basic understanding of business value metrics|Finance and business stakeholder engagement',
'Value Framework Development: Define AI development value metrics and KPIs, Create initial value measurement and tracking systems, Establish baseline business performance and productivity metrics|Basic Measurement Implementation: Implement basic AI impact tracking and reporting, Create initial business value dashboards and analytics, Establish regular value review and assessment processes|Value Governance: Create AI value governance committee and processes, Establish initial value optimization and improvement procedures, Implement basic value communication and stakeholder engagement',
'Value measurement framework with defined metrics and KPIs|Basic AI impact tracking and business value dashboards|Value governance processes and stakeholder engagement established',
'6-8 weeks',
'Metrics without business context; measurement without action; governance overhead without clear value');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-PMV', 3,
'Basic value measurement and tracking systems in place|Value governance processes established|Initial value insights and learnings',
'Advanced Value Analytics: Deploy comprehensive AI value analytics and optimization, Implement predictive value modeling and forecasting, Create automated value analysis and insight generation|Value Optimization Programs: Build advanced value optimization and improvement initiatives, Implement value-driven decision support and prioritization, Create systematic value realization and scaling|Value Excellence: Deploy value excellence programs and capabilities, Implement value innovation and continuous improvement, Create value learning and knowledge management',
'Advanced value analytics with predictive modeling and optimization|Value optimization programs driving systematic improvement|Value excellence with innovation and continuous learning',
'10-12 weeks',
'Analytics complexity without actionable insights; optimization without strategic alignment; excellence programs without practical value creation');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-PMV', 4,
'Mature value analytics and optimization programs|Advanced value excellence and innovation|Organization-wide value-driven culture',
'Autonomous Value Excellence: Deploy self-improving value optimization throughout the organization, Implement autonomous value innovation and advancement, Create intelligent value ecosystem and platform development|Strategic Value Leadership: Establish organizational leadership in AI value realization and optimization, Create industry partnerships and collaboration on value excellence, Implement value advocacy and thought leadership|Value-Driven Transformation: Build value capabilities that create sustainable competitive advantage, Create value-driven organizational evolution and transformation, Implement value excellence as core organizational DNA',
'Autonomous value excellence driving continuous optimization and innovation|Recognized industry leadership in AI value realization|Value-driven transformation creating sustainable competitive advantage',
'20-24 weeks',
'Autonomous optimization without human judgment; value leadership without practical innovation; transformation without cultural evolution');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-IPM', 2,
'Legal team awareness of AI IP concerns|Basic understanding of AI-generated content risks|Executive support for IP protection',
'IP Risk Assessment: Assess AI-generated content IP risks and implications, Create initial IP policies for AI development, Establish basic IP review and validation processes|Basic IP Protection: Implement basic IP scanning and validation tools, Create initial IP documentation and attribution processes, Establish basic legal review and approval procedures|IP Governance: Create AI IP governance committee and processes, Establish initial IP training and awareness programs, Implement basic IP compliance and monitoring',
'IP risk assessment and initial policies for AI development|Basic IP protection with scanning and validation tools|IP governance processes and training programs established',
'8-10 weeks',
'Policies without practical enforcement; scanning tools without legal validation; governance without developer integration');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-IPM', 3,
'Basic IP protection and governance processes in place|IP risk assessment and policies established|Initial IP compliance experience',
'Advanced IP Management: Deploy comprehensive AI IP management and protection systems, Implement automated IP scanning and validation workflows, Create advanced IP documentation and audit capabilities|Intelligent IP Analysis: Build AI-powered IP originality and risk analysis, Implement intelligent IP portfolio management and optimization, Create predictive IP risk assessment and mitigation|IP Excellence: Deploy IP excellence programs and capabilities, Implement IP innovation and continuous improvement, Create IP learning and knowledge management',
'Advanced IP management with automated scanning and validation|Intelligent IP analysis with AI-powered originality assessment|IP excellence with innovation and continuous improvement',
'10-12 weeks',
'Automation without legal oversight; AI analysis without human judgment; excellence programs without practical protection');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-IPM', 4,
'Mature IP management and intelligent analysis systems|Advanced IP excellence and innovation|Organization-wide IP protection culture',
'Autonomous IP Excellence: Deploy self-improving IP protection throughout the organization, Implement autonomous IP innovation and advancement, Create intelligent IP ecosystem and platform development|Strategic IP Leadership: Establish organizational leadership in AI IP management and protection, Create industry partnerships and collaboration on IP excellence, Implement IP advocacy and thought leadership|IP-Driven Innovation: Build IP capabilities that create sustainable competitive advantage, Create IP-driven organizational innovation and transformation, Implement IP excellence as core organizational DNA',
'Autonomous IP excellence with self-improving protection capabilities|Recognized industry leadership in AI IP management|IP-driven innovation creating sustainable competitive advantage',
'20-24 weeks',
'Autonomous protection without legal oversight; IP leadership without practical innovation; innovation without strategic IP consideration');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-RMS', 2,
'Security team awareness of AI risks|Basic understanding of AI security threats|Executive support for AI risk management',
'Risk Assessment and Framework: Assess AI development security risks and vulnerabilities, Create initial AI risk management framework and policies, Establish basic risk monitoring and mitigation processes|Basic Security Implementation: Implement basic AI security controls and safeguards, Create initial security scanning and validation procedures, Establish basic incident response and recovery processes|Risk Governance: Create AI risk governance committee and processes, Establish initial risk training and awareness programs, Implement basic risk compliance and reporting',
'Risk assessment and management framework for AI development|Basic AI security controls and safeguards implemented|Risk governance processes and training programs established',
'8-10 weeks',
'Risk assessment without practical mitigation; security controls without operational integration; governance without developer engagement');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-RMS', 3,
'Basic risk management and security controls in place|Risk governance processes established|Initial security incident experience',
'Advanced Risk Management: Deploy comprehensive AI risk management and security systems, Implement automated risk monitoring and threat detection, Create advanced security analytics and incident response|Intelligent Security Operations: Build AI-powered security analysis and threat intelligence, Implement intelligent security orchestration and automated response, Create predictive security risk assessment and prevention|Security Excellence: Deploy security excellence programs and capabilities, Implement security innovation and continuous improvement, Create security learning and knowledge management',
'Advanced risk management with automated monitoring and threat detection|Intelligent security operations with AI-powered analysis|Security excellence with innovation and continuous improvement',
'10-12 weeks',
'Automation without human oversight; AI security without validation; excellence programs without practical security improvement');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-RMS', 4,
'Mature risk management and intelligent security operations|Advanced security excellence and innovation|Organization-wide security culture',
'Autonomous Security Excellence: Deploy self-improving security capabilities throughout the organization, Implement autonomous security adaptation and evolution, Create intelligent security ecosystem and platform development|Strategic Security Leadership: Establish organizational leadership in AI security and risk management, Create industry partnerships and collaboration on security excellence, Implement security advocacy and thought leadership|Security-Driven Innovation: Build security capabilities that create sustainable competitive advantage, Create security-driven organizational innovation and transformation, Implement security excellence as core organizational DNA',
'Autonomous security excellence with self-improving capabilities|Recognized industry leadership in AI security and risk management|Security-driven innovation creating sustainable competitive advantage',
'20-24 weeks',
'Autonomous security without human judgment; security leadership without practical innovation; innovation without comprehensive risk consideration');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-OCM', 2,
'Executive commitment to AI transformation|Change management expertise and resources|Understanding of organizational readiness for AI adoption',
'Change Assessment and Strategy: Assess organizational readiness for AI-first transformation, Create comprehensive change management strategy and roadmap, Establish change leadership and governance structures|Basic Change Implementation: Implement initial AI adoption and culture change programs, Create change communication and engagement strategies, Establish basic change metrics and feedback systems|Change Support Systems: Deploy change support and coaching capabilities, Implement change training and skill development programs, Create change resistance management and mitigation strategies',
'Change assessment and comprehensive transformation strategy|Basic AI adoption and culture change programs implemented|Change support systems with training and coaching established',
'8-10 weeks',
'Change strategy without cultural understanding; implementation without adequate support; support systems without practical change facilitation');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-OCM', 3,
'Basic change programs and support systems in place|Change strategy and governance established|Initial transformation experience and learnings',
'Advanced Change Orchestration: Deploy comprehensive change management and orchestration systems, Implement intelligent change analytics and optimization, Create advanced change acceleration and scaling capabilities|Change Excellence Programs: Build change excellence and continuous improvement initiatives, Implement change innovation and best practice development, Create change learning and knowledge management systems|Transformation Integration: Deploy integrated transformation capabilities across the organization, Implement change-driven business process optimization, Create sustainable change culture and operating models',
'Advanced change orchestration with intelligent analytics and optimization|Change excellence programs driving continuous improvement|Transformation integration with sustainable culture change',
'10-12 weeks',
'Orchestration complexity without human connection; excellence programs without practical change outcomes; integration without cultural authenticity');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-OCM', 4,
'Mature change orchestration and excellence programs|Advanced transformation integration|Organization-wide change culture',
'Autonomous Change Excellence: Deploy self-improving change capabilities throughout the organization, Implement autonomous change adaptation and evolution, Create intelligent change ecosystem and platform development|Strategic Change Leadership: Establish organizational leadership in AI transformation and change management, Create industry partnerships and collaboration on change excellence, Implement change advocacy and thought leadership|Change-Driven Innovation: Build change capabilities that create sustainable competitive advantage, Create change-driven organizational evolution and transformation, Implement change excellence as core organizational DNA',
'Autonomous change excellence with self-improving capabilities|Recognized industry leadership in AI transformation and change management|Change-driven innovation creating sustainable competitive advantage',
'20-24 weeks',
'Autonomous change without human connection; change leadership without authentic transformation; innovation without cultural evolution');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-CAC', 2,
'Understanding of cross-functional AI collaboration needs|Basic AI tool adoption across different functions|Leadership commitment to collaborative AI adoption',
'Collaboration Framework Development: Create cross-functional AI collaboration framework and guidelines, Assess current collaboration patterns and improvement opportunities, Establish basic collaboration governance and coordination processes|Initial Collaboration Implementation: Implement basic cross-functional AI collaboration initiatives, Create initial collaboration tools and platforms, Establish basic collaboration metrics and feedback systems|Collaboration Culture Development: Deploy collaboration culture development and training programs, Implement collaboration awareness and skill development, Create collaboration champions and support networks',
'Cross-functional AI collaboration framework and governance established|Basic collaboration initiatives and tools implemented|Collaboration culture development with training and support networks',
'7-8 weeks',
'Framework without practical implementation; collaboration tools without cultural adoption; culture development without sustained commitment');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-CAC', 3,
'Basic collaboration framework and initiatives in place|Collaboration tools and culture development established|Initial collaboration experience and learnings',
'Advanced Collaboration Orchestration: Deploy comprehensive collaboration management and orchestration systems, Implement intelligent collaboration analytics and optimization, Create advanced collaboration scaling and acceleration capabilities|Collaboration Excellence Programs: Build collaboration excellence and continuous improvement initiatives, Implement collaboration innovation and best practice development, Create collaboration learning and knowledge management systems|Integrated Collaboration Ecosystems: Deploy integrated collaboration ecosystems across the organization, Implement collaboration-driven workflow optimization, Create sustainable collaboration culture and operating models',
'Advanced collaboration orchestration with intelligent analytics|Collaboration excellence programs driving continuous improvement|Integrated collaboration ecosystems with sustainable culture',
'10-12 weeks',
'Orchestration without human relationships; excellence programs without authentic collaboration; ecosystems without cultural foundation');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-CAC', 4,
'Mature collaboration orchestration and excellence programs|Advanced integrated collaboration ecosystems|Organization-wide collaboration culture',
'Autonomous Collaboration Excellence: Deploy self-improving collaboration capabilities throughout the organization, Implement autonomous collaboration adaptation and evolution, Create intelligent collaboration ecosystem and platform development|Strategic Collaboration Leadership: Establish organizational leadership in cross-functional AI collaboration, Create industry partnerships and collaboration on collaboration excellence, Implement collaboration advocacy and thought leadership|Collaboration-Driven Innovation: Build collaboration capabilities that create sustainable competitive advantage, Create collaboration-driven organizational innovation and transformation, Implement collaboration excellence as core organizational DNA',
'Autonomous collaboration excellence with self-improving capabilities|Recognized industry leadership in cross-functional AI collaboration|Collaboration-driven innovation creating sustainable competitive advantage',
'20-24 weeks',
'Autonomous collaboration without human connection; collaboration leadership without practical innovation; innovation without authentic collaboration culture');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-REC', 2,
'Legal and compliance team awareness of AI regulations|Basic understanding of applicable AI laws and regulations|Executive support for AI compliance',
'Compliance Assessment and Framework: Assess applicable AI regulations and compliance requirements, Create initial AI compliance framework and policies, Establish basic compliance monitoring and validation processes|Basic Compliance Implementation: Implement basic AI compliance controls and safeguards, Create initial compliance documentation and audit procedures, Establish basic compliance training and awareness programs|Compliance Governance: Create AI compliance governance committee and processes, Establish initial compliance review and approval procedures, Implement basic compliance reporting and communication',
'Compliance assessment and framework for applicable AI regulations|Basic AI compliance controls and documentation implemented|Compliance governance processes and training programs established',
'8-10 weeks',
'Compliance assessment without practical implementation; controls without operational integration; governance without developer engagement');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-REC', 3,
'Basic compliance framework and controls in place|Compliance governance processes established|Initial compliance experience and learnings',
'Advanced Compliance Management: Deploy comprehensive AI compliance management and monitoring systems, Implement automated compliance scanning and validation workflows, Create advanced compliance analytics and reporting capabilities|Intelligent Compliance Operations: Build AI-powered compliance analysis and risk assessment, Implement intelligent compliance orchestration and automated response, Create predictive compliance risk assessment and prevention|Compliance Excellence: Deploy compliance excellence programs and capabilities, Implement compliance innovation and continuous improvement, Create compliance learning and knowledge management',
'Advanced compliance management with automated scanning and validation|Intelligent compliance operations with AI-powered analysis|Compliance excellence with innovation and continuous improvement',
'10-12 weeks',
'Automation without legal oversight; AI compliance without human judgment; excellence programs without practical compliance improvement');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-REC', 4,
'Mature compliance management and intelligent operations|Advanced compliance excellence and innovation|Organization-wide compliance culture',
'Autonomous Compliance Excellence: Deploy self-improving compliance capabilities throughout the organization, Implement autonomous compliance adaptation and evolution, Create intelligent compliance ecosystem and platform development|Strategic Compliance Leadership: Establish organizational leadership in AI regulatory compliance, Create industry partnerships and collaboration on compliance excellence, Implement compliance advocacy and thought leadership|Compliance-Driven Innovation: Build compliance capabilities that create sustainable competitive advantage, Create compliance-driven organizational innovation and transformation, Implement compliance excellence as core organizational DNA',
'Autonomous compliance excellence with self-improving capabilities|Recognized industry leadership in AI regulatory compliance|Compliance-driven innovation creating sustainable competitive advantage',
'20-24 weeks',
'Autonomous compliance without legal oversight; compliance leadership without practical innovation; innovation without comprehensive regulatory consideration');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-IFR', 2,
'Understanding of AI innovation landscape and future trends|Executive commitment to innovation and future readiness|Basic innovation processes and capabilities in place',
'Innovation Strategy Development: Create comprehensive AI innovation strategy and roadmap, Assess current innovation capabilities and future requirements, Establish initial innovation governance and investment frameworks|Basic Innovation Implementation: Implement basic AI innovation processes and experimentation, Create innovation project management and evaluation procedures, Establish initial future readiness assessment and planning|Innovation Culture Development: Train teams on AI innovation and future thinking, Create innovation awareness and skill development programs, Establish innovation champions throughout the organization',
'Comprehensive AI innovation strategy and roadmap established|Basic innovation implementation for systematic AI experimentation|Innovation culture development training for 100% of teams',
'10-12 weeks',
'Innovation strategy without practical implementation; basic processes without cultural support; culture development without sustained commitment');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-IFR', 3,
'Basic innovation strategy and implementation established|Innovation processes integrated into AI development workflows|Innovation culture development training completed',
'Advanced Innovation Orchestration: Implement intelligent innovation management and optimization, Deploy systematic innovation pipeline and portfolio management, Create advanced innovation evaluation and scaling capabilities|Future Readiness Intelligence: Build systematic future trend analysis and scenario planning, Implement predictive innovation and technology forecasting, Create adaptive innovation strategy and roadmap development|Innovation Excellence: Deploy innovation excellence programs and capabilities, Implement innovation acceleration and scaling systems, Create innovation learning and continuous improvement',
'Advanced innovation orchestration driving systematic breakthrough innovation|Future readiness intelligence informing strategic innovation decisions|Innovation excellence capabilities accelerating AI innovation and value creation',
'14-16 weeks',
'Innovation orchestration without creative freedom; future intelligence without practical application; excellence programs without authentic innovation culture');

INSERT OR IGNORE INTO maturity_progressions (area_id, target_level, prerequisites, action_items, success_metrics, timeline, common_pitfall) VALUES 
('SG-IFR', 4,
'Mature innovation orchestration and future readiness capabilities|Advanced innovation excellence and scaling systems|Organization-wide innovation culture and leadership',
'Autonomous Innovation Excellence: Deploy self-improving innovation capabilities throughout the organization, Implement continuous innovation adaptation and evolution, Create intelligent innovation ecosystem and platform development|Strategic Innovation Leadership: Establish organizational leadership in AI innovation and future readiness, Create industry partnerships and collaboration on innovation ecosystems, Implement innovation advocacy and thought leadership|Future Readiness Integration: Build innovation capabilities that create sustainable future advantage, Create innovation-driven organizational transformation and evolution, Implement innovation excellence as core organizational DNA',
'Autonomous innovation capabilities driving continuous breakthrough and evolution|Recognized industry leadership in AI innovation and future readiness|Innovation excellence creating sustainable future advantage and transformation',
'20-24 weeks',
'Autonomous innovation without human creativity; innovation leadership without practical breakthrough; future readiness without adaptive capability');
-- ========================================
-- End of Seed Data
-- ========================================
