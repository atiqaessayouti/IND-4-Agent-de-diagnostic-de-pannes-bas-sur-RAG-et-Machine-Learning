# IND-4 — État de l'art de travail

Veille ciblée au 19 novembre 2026. Cette bibliographie de travail distingue les articles publiés et les prépublications. Les performances des publications ne sont pas des résultats du projet : leurs unités d'analyse, partitions, données et tâches ne sont pas toutes comparables.

## Positionnement

**Les résultats HDFS dépendent du protocole.** Xu et al. ont montré que la structuration des journaux aide à dégager des motifs de défaillance [1]. Loghub rend le benchmark accessible [2], mais les travaux sur le parsing à grande échelle documentent les limites des petits extraits annotés [4]. Sedláček et al. comparent plusieurs détecteurs et montrent que les scores changent entre versions d'HDFS [5]. Xiao et al. observent en outre des changements de performance et de classement lorsque les groupes ou le temps sont pris en compte [6]. D'où le classifieur réglé uniquement sur validation, la séparation disjointe des blocs et l'annonce explicite des limites du découpage aléatoire.

**La recherche peut améliorer l'explication sans améliorer la détection.** LogPrompt illustre la production d'explications par instruction, LogLLM entraîne un détecteur reposant sur des modèles préentraînés, tandis que LogRules introduit des règles validées [7–9]. RAPID récupère des motifs de journaux avec un modèle préentraîné [10]. Le RAG original combine une mémoire externe avec la génération [11] ; sa qualité doit être examinée séparément de celle des réponses produites [12,13]. Cela motive ici un contrôle sans recherche et deux mesures de traçabilité : existence des références et soutien effectif des affirmations.

**Le projet teste la documentation, pas la mémoire des incidents.** RCACopilot collecte des signaux puis prédit une catégorie de cause, et AIOpsLab sépare détection, localisation et cause racine [14,15]. Sun et al. étudient déjà HDFS et des récits fondés sur des preuves sur un sous-ensemble structuré [16]. TriCalRAG compare également des LLM locaux et un détecteur classique sur HDFS, mais son bras RAG recherche dans un historique d'incidents étiquetés [17]. Notre contraste est plus étroit : notices Apache seules, même LLM des deux côtés, comparaison appariée à une régression logistique et audit humain des justifications. Le choix de Qwen2.5-3B permet une inférence locale et limite la portée du résultat à cette configuration [18].

## Références

1. Xu, W., Huang, L., Fox, A., Patterson, D. et Jordan, M. I. (2009). *Detecting Large-Scale System Problems by Mining Console Logs*. SOSP. https://doi.org/10.1145/1629575.1629587
2. Zhu, J., He, S., He, P., Liu, J. et Lyu, M. R. (2023). *Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics*. ISSRE. https://arxiv.org/abs/2008.06448 ; dépôt de données : https://doi.org/10.5281/zenodo.8196385
3. Borthakur, D. (2008). *HDFS Architecture Guide*. Apache Software Foundation, documentation Hadoop 1.2.1. https://hadoop.apache.org/docs/r1.2.1/hdfs_design.pdf
4. Jiang, Z. et al. (2024). *A Large-Scale Evaluation for Log Parsing Techniques: How Far Are We?* ISSTA. https://arxiv.org/abs/2308.10828
5. Sedláček, O., Žádník, M. et Bartoš, V. (2025). *Anomaly Detection in Log Data: A Comparative Study*. CNSM. https://opendl.ifip-tc6.org/db/conf/cnsm/cnsm2025/1571164872.pdf
6. Xiao, H., Sung, J., Li, Z., Qian, I. et Xu, C. (2026). *Protocol-Sensitive Evaluation of Log Anomaly Detection: Component Costs and Target-Access Sensitivity on HDFS and BGL*. Notice de recherche avec résumé. https://research.google/pubs/protocol-sensitive-evaluation-of-log-anomaly-detection-component-costs-and-target-access-sensitivity-on-hdfs-and-bgl/
7. Liu, Y. et al. (2024). *Interpretable Online Log Analysis Using Large Language Models with Prompt Strategies*. ICPC. https://doi.org/10.1145/3643916.3644408
8. Guan, W., Cao, J., Qian, S., Gao, J. et Ouyang, C. (2024). *LogLLM: Log-based Anomaly Detection Using Large Language Models*. Prépublication. https://arxiv.org/abs/2411.08561
9. Huang, X., Zhang, T. et Zhao, W. (2025). *LogRules: Enhancing Log Analysis Capability of Large Language Models through Rules*. Findings of NAACL. https://doi.org/10.18653/v1/2025.findings-naacl.28
10. No, G., Lee, Y., Kang, H. et Kang, P. (2024). *Training-free retrieval-based log anomaly detection with pre-trained language model considering token-level information*. Engineering Applications of Artificial Intelligence, 133, 108613. https://doi.org/10.1016/j.engappai.2024.108613
11. Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS. https://arxiv.org/abs/2005.11401
12. Es, S., James, J., Espinosa-Anke, L. et Schockaert, S. (2024). *RAGAs: Automated Evaluation of Retrieval Augmented Generation*. EACL System Demonstrations. https://doi.org/10.18653/v1/2024.eacl-demo.16
13. Ma, Z., Yang, J. et Chen, T.-H. (2026). *LLM4Log: A Systematic Review of Large Language Model-based Log Analysis*. Prépublication. https://arxiv.org/abs/2604.16359
14. Chen, Y. et al. (2024). *Automatic Root Cause Analysis via Large Language Models for Cloud Incidents*. EuroSys. https://arxiv.org/abs/2305.15778
15. Chen, Y. et al. (2025). *AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds*. Prépublication. https://arxiv.org/abs/2501.06706
16. Sun, X., Zhong, Z. S. et Wu, Q. (2026). *Retrieval-Grounded HDFS Log Anomaly Detection and Deterministic Failure Narrative Generation*. Journal of Computational Systems and Applications. https://doi.org/10.64229/j6d7fr94
17. Patel, R., Mohanty, S. K. et Chaudhary, J. (2026). *TriCalRAG: A Three-Strategy, Retrieval-Augmented Benchmark for On-Premise LLM-Based Root Cause Analysis in AIOps*. Prépublication, v2 du 3 octobre. https://arxiv.org/abs/2609.14762v2
18. Yang, A. et al. (2024). *Qwen2.5 Technical Report*. Prépublication. https://arxiv.org/abs/2412.15115
