# Veille Tech — Semaine 2025w48 (2025-11-24 → 2025-12-01)

## 🏛️ Warehouses & Query Engines

- [Run Apache Spark and Iceberg 4.5x faster than open source Spark with Amazon EMR](https://aws.amazon.com/blogs/big-data/run-apache-spark-and-iceberg-4-5x-faster-than-open-source-spark-with-amazon-emr/) — Redshift / AWS Big Data · 2025-11-27
  - This post shows how Amazon EMR 7.12 can make your Apache Spark and Iceberg workloads up to 4.5x faster performance.
- [Apache Spark encryption performance improvement with Amazon EMR 7.9](https://aws.amazon.com/blogs/big-data/apache-spark-encryption-performance-improvement-with-amazon-emr-7-9/) — Redshift / AWS Big Data · 2025-11-27
  - In this post, we analyze the results from our benchmark tests comparing the Amazon EMR 7.9 optimized Spark runtime against Spark 3.5.5 without encryption optimizations. We walk through a detailed cost analysis and provide step-by-step instr…
- [Run Apache Spark and Apache Iceberg write jobs 2x faster with Amazon EMR](https://aws.amazon.com/blogs/big-data/run-apache-spark-and-apache-iceberg-write-jobs-2x-faster-with-amazon-emr/) — Redshift / AWS Big Data · 2025-11-27
  - In this post, we demonstrate the write performance benefits of using the Amazon EMR 7.12 runtime for Spark and Iceberg compares to open source Spark 3.5.6 with Iceberg 1.10.0 tables on a 3TB merge workload.
- [DuckDB on AWS Lambda: The Easy Way with Layers](https://blog.zenika.com/2025/11/26/duckdb-on-aws-lambda-the-easy-way-with-layers/) — Zenika Tech Blog · 2025-11-26
  - This article shows how I used DuckDB in AWS Lambda in an easy way. I'll explain how my pre-built Lambda layers bypass complex build processes, allowing you to use DuckDB for efficient serverless analytics with ease.
- [Save up to 24% on Amazon Redshift Serverless compute costs with Reservations](https://aws.amazon.com/blogs/big-data/save-up-to-24-on-amazon-redshift-serverless-compute-costs-with-reservations/) — Redshift / AWS Big Data · 2025-11-24
  - In this post, you learn how Amazon Redshift Serverless Reservations can help you lower your data warehouse costs. We explore ways to determine the optimal number of RPUs to reserve, review example scenarios, and discuss important considerat…
- [Claude Opus 4.5 Is Here](https://www.databricks.com/blog/claude-opus-45-here) — Databricks Blog · 2025-11-24
  - Customers process exabytes of data daily on Databricks, and generative AI is already...
- [Building the Future of AI Agents and Intelligence Apps: Celebrating 4 years of Databricks Seattle R&D](https://www.databricks.com/blog/building-future-ai-agents-and-intelligence-apps-celebrating-4-years-databricks-seattle-rd) — Databricks Blog · 2025-11-24
  - In November 2021, we announced the opening of our Seattle R&D site and our plan to...

## 🔄 Orchestration, ETL & Data Movement

- [Build Pipelines 10x faster with workspace workflow](https://dlthub.com/blog/workspace-video-tutorial) — dlt Blog · 2025-11-26
  - dltHub Workspace: A frictionless LLM-native approach designed to help data developers build, run, and analyze complete pipelines.
- [Continuous batching from first principles](https://huggingface.co/blog/continuous_batching) — Hugging Face Blog · 2025-11-25
  - Continuous batching
TL;DR: in this blog post, starting from attention mechanisms and KV caching, we derive continuous batching by optimizing for throughput.
If you've ever used Qwen, Claude, or any other AI chatbot, you've probably noticed …
- [How to Orchestrate dbt with Dagster](https://dagster.io/blog/orchestrating-dbt-with-dagster) — Dagster Blog · 2025-11-24
  - With Dagster’s dbt integration, run and monitor dbt models as part of a larger, asset-driven pipeline for improved lineage and scheduling.
- [Why We Built Dagster for the Data Decade](https://dagster.io/blog/decade-of-data) — Dagster Blog · 2025-11-24
  - Our $14M Series A is just the start. Learn how Dagster is positioned for long-term success in the next decade of data.

## 📐 Data Modeling, Governance & Quality

- [Accelerate data lake operations with Apache Iceberg V3 deletion vectors and row lineage](https://aws.amazon.com/blogs/big-data/accelerate-data-lake-operations-with-apache-iceberg-v3-deletion-vectors-and-row-lineage/) — Redshift / AWS Big Data · 2025-11-26
  - In this post, we walk you through the new capabilities in Iceberg V3, explain how deletion vectors and row lineage address these challenges, explore real-world use cases across industries, and provide practical guidance on implementing Iceb…
- [A Year of Interoperability: How Enterprises Are Scaling Governance with Unity Catalog](https://www.databricks.com/blog/year-interoperability-how-enterprises-are-scaling-governance-unity-catalog) — Databricks Blog · 2025-11-26
  - The Era of Open GovernanceA year after we open-sourced Unity Catalog (UC), the results...
- [How SoftBank Scaled an AI Agent-Powered Sales Model, Saving 250K Hours a Year](https://www.dataiku.com/stories/blog/softbank) — Dataiku Blog · 2025-11-25
  - SoftBank Corp. is transforming sales with AI agents in Dataiku, capturing every conversation as insight, boosting data quality, and delivering various insights while working to reclaim a quarter-million hours a year for selling. 90% of sell…

## 🗄️ Data Lakes, Storage & Formats

- [Medidata’s journey to a modern lakehouse architecture on AWS](https://aws.amazon.com/blogs/big-data/medidatas-journey-to-a-modern-lakehouse-architecture-on-aws/) — Redshift / AWS Big Data · 2025-11-27
  - In this post, we show you how Medidata created a unified, scalable, real-time data platform that serves thousands of clinical trials worldwide with AWS services, Apache Iceberg, and a modern lakehouse architecture.
- [Achieve 2x faster data lake query performance with Apache Iceberg on Amazon Redshift](https://aws.amazon.com/blogs/big-data/achieve-2x-faster-data-lake-query-performance-with-apache-iceberg-on-amazon-redshift/) — Redshift / AWS Big Data · 2025-11-26
  - In 2025, Amazon Redshift delivered several performance optimizations that improved query performance over twofold for Iceberg workloads on Amazon Redshift Serverless, delivering exceptional performance and cost-effectiveness for your data l…
- [Introducing catalog federation for Apache Iceberg tables in the AWS Glue Data Catalog](https://aws.amazon.com/blogs/big-data/introducing-catalog-federation-for-apache-iceberg-tables-in-the-aws-glue-data-catalog/) — Redshift / AWS Big Data · 2025-11-26
  - AWS Glue now supports catalog federation for remote Iceberg tables in the Data Catalog. With catalog federation, you can query remote Iceberg tables, stored in Amazon S3 and cataloged in remote Iceberg catalogs, using AWS analytics engines …
- [Getting started with Apache Iceberg write support in Amazon Redshift](https://aws.amazon.com/blogs/big-data/getting-started-with-apache-iceberg-write-support-in-amazon-redshift/) — Redshift / AWS Big Data · 2025-11-26
  - In this post, we show how you can use Amazon Redshift to write data directly to Apache Iceberg tables stored in Amazon S3 and S3 Tables for seamless integration between your data warehouse and data lake while maintaining ACID compliance.

## ☁️ Cloud, Infra & Observability

- [How Octus achieved 85% infrastructure cost reduction with zero downtime migration to Amazon OpenSearch Service](https://aws.amazon.com/blogs/big-data/how-octus-achieved-85-infrastructure-cost-reduction-with-zero-downtime-migration-to-amazon-opensearch-service/) — Redshift / AWS Big Data · 2025-11-26
  - This post highlights how Octus migrated its Elasticsearch workloads running on Elastic Cloud to Amazon OpenSearch Service. The journey traces Octus’s shift from managing multiple systems to adopting a cost-efficient solution powered by Open…
- [Manage your secrets through OVHcloud Secret Manager thanks to External Secrets Operator (ESO) on OVHcloud Managed Kubernetes Service (MKS)](https://blog.ovhcloud.com/manage-your-secrets-through-ovhcloud-secret-manager-thanks-to-external-secrets-operator-eso-on-ovhcloud-managed-kubernetes-service-mks/) — OVHcloud Blog · 2025-11-25
  - The Secrets resources in Kubernetes allow us to store sensitive information like login, passwords, tokens, credentials and certificates. But be careful, when creating a Secret in Kubernetes, it is encoded in base64, it is not encrypted so e…
- [Introducing Claude Opus 4.5 in Microsoft Foundry](https://azure.microsoft.com/en-us/blog/introducing-claude-opus-4-5-in-microsoft-foundry/) — Azure Blog · 2025-11-24
  - Announcing Anthropic's newest model, Claude Opus 4.5, in Microsoft Foundry. Opus 4.5 is now available in public preview in Microsoft Foundry, GitHub Copilot paid plans, and Microsoft Copilot Studio. The post Introducing Claude Opus 4.5 in M…

## 🤖 AI for Data Engineering

- [Quand la génération synthétique permet de voir ce qui n’existe pas](https://blog.octo.com/quand-la-generation-synthetique-permet-de-voir-ce-qui-n'existe-pas-1) — OCTO Talks! · 2025-11-27
  - Comment entraîner une IA à détecter des défauts qu'elle ne voit presque jamais ? En industrie, les anomalies graves sont si rares qu'elles privent les modèles de matière d'apprentissage. La donnée synthétique offre une réponse inattendue : …
- [School of Product 2025 : les 5 notions à retenir](https://blog.octo.com/octo-school-of-product-2025--les-5-notions-a-retenir) — OCTO Talks! · 2025-11-27
  - La 8ème édition de la conférence Produit et Design organisée par OCTO Technology s'est déroulée le mardi 18 novembre,  à Paris. On avait rendez-vous comme l’an passé avec le caméléon, notre mascotte Produit, et le thème cette année était : …
- [“Le handicap, c’est l’affaire de tous.”](https://blog.octo.com/le-handicap-c'est-l'affaire-de-tous.) — OCTO Talks! · 2025-11-27
  - Rencontre avec notre chef d’orchestre, Vincent Mathon, référent handicap, qui nous explique d’où vient son engagement et comment il se matérialise au quotidien.
- [Using skills with Deep Agents](https://blog.langchain.com/using-skills-with-deep-agents/) — LangChain Blog · 2025-11-25
  - tl;dr: Anthropic recently introduced the idea of agent skills . Skills are simply folders containing a SKILL.md file along with any associated files (e.g., documents or scripts) that an agent can discover and load dynamically to perform bet…
- [🤖 Gemini dans votre terminal avec Gemini CLI](https://blog.zenika.com/2025/11/25/%f0%9f%a4%96-gemini-dans-votre-terminal-avec-gemini-cli/) — Zenika Tech Blog · 2025-11-25
  - 👉 CLI, Kezako? Les Command Line Interface (CLI) sont  des outils en ligne de commande qui permettent d’interagir avec une
- [Diffusers welcomes FLUX-2](https://huggingface.co/blog/flux-2) — Hugging Face Blog · 2025-11-25
  - Welcome FLUX.2 - BFL’s new open image generation model 🤗
FLUX.2 is the recent series of image generation models from Black Forest Labs, preceded by the
Flux.1
series. It is an entirely new model with a
new architecture
and pre-training done…
- [Partnering with Black Forest Labs to bring FLUX.2 [dev] to Workers AI](https://blog.cloudflare.com/flux-2-workers-ai/) — Cloudflare Engineering · 2025-11-25
  - FLUX.2 [dev] by Black Forest Labs is now on Workers AI! This advanced open-weight image model offers superior photorealism, multi-reference inputs, and granular control with JSON prompting.
- [Get better visibility for the WAF with payload logging](https://blog.cloudflare.com/waf-payload-logging/) — Cloudflare Engineering · 2025-11-24
  - The WAF provides ways for our customers to gain insight into why it takes certain actions. The more granular and precise the insight, the more reproducible and understandable it is. Revamped payload logging is one such method.

## 📰 Tech / Cloud / IA News

- [From Blind Spots to Real-Time Intelligence: How Location Data from O2 Motion is Transforming Business Decision-Making](https://www.databricks.com/blog/blind-spots-real-time-intelligence-how-location-data-o2-motion-transforming-business-decision) — Databricks Blog · 2025-11-26
  - A media buyer launches a £50,000 digital billboard campaign, only to discover later...
- [Data security shouldn't be an afterthought](https://blog.dataexpert.io/p/how-to-secure-your-data-a-practical) — DataEngineer.io · 2025-11-26
  - A practical guide for Data Engineers
- [Orchestrating data processing tasks with a serverless visual workflow in Amazon SageMaker Unified Studio](https://aws.amazon.com/blogs/big-data/orchestrating-data-processing-tasks-with-a-serverless-visual-workflow-in-amazon-sagemaker-unified-studio/) — Redshift / AWS Big Data · 2025-11-25
  - In this post, we show how to use the new visual workflow experience in SageMaker Unified Studio IAM-based domains to orchestrate an end-to-end machine learning workflow. The workflow ingests weather data, applies transformations, and genera…
- [🤖 Déployer son agent sur Google Vertex AI Agent Engine](https://blog.zenika.com/2025/11/25/%f0%9f%a4%96-deployer-son-agent-sur-google-vertex-ai-agent-engine/) — Zenika Tech Blog · 2025-11-25
  - Simplifiez le déploiement de vos agents IA sur Google Cloud avec Vertex AI Agent Engine à travers le framework Agent Development Kit (ADK) ou avec le SDK Vertex AI pour intégrer des frameworks comme LangChain, LangGraph et CrewAI.
