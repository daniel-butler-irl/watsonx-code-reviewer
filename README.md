adsadadsdas# watsonx-code-reviewer

watsonx-code-reviewer is an AI-powered application designed to review GitHub pull requests (PRs), post automated change requests, and respond to user comments about code. The app leverages multiple agents using IBM WatsonX LLMs to review code not only within the PR but also in the broader context of the entire codebase and dependencies. This app provides continuous learning, building a knowledge database for each repository to speed up future reviews.

### Key Features

- **Multi-Agent Approach**:
    - One agent analyzes the code in PRs and suggests changes.
    - Another agent responds to comments about the code, fetching relevant data from the codebase for accurate replies.

- **Multi-Language Support**:
    - Initially, the app supports Python and will expand to include Golang, Terraform, and shell scripts. Language-specific handlers are modular, making it easy to extend functionality.

- **Contextual Code Analysis**:
    - The app not only reviews the code in the PR but also performs static analysis of the entire codebase to retrieve function signatures, dependencies, and relevant documentation.
    - Uses both structural (function signatures) and semantic (code comments) analysis to improve review quality.

- **Database Architecture**:
    - **PostgreSQL** (via IBM Cloud Databases for PostgreSQL) is used to store structured data, such as repository metadata, function signatures, and pull request details. PostgreSQL provides reliable, transactional storage for core application data.
    - **Elasticsearch**: For semantic similarity search and full-text search capabilities, allowing quick search across the codebase and historical data. Elasticsearch is used as both a vector database for semantic search and a full-text search engine for efficient querying.

- **RAG for LLM Operations**:
    - When reviewing code or responding to a comment, the system uses RAG techniques to retrieve semantically similar code snippets from the knowledge base. This is enhanced by vector search capabilities using Elasticsearch.

- **IBM Cloud Code Engine**:
    - The app is triggered by webhooks from GitHub and runs on demand in IBM Cloud Code Engine, providing scalable and efficient processing without needing to manage the infrastructure directly.

- **Integration with IBM Cloud Services**:
    - The app prioritizes IBM Cloud services where possible, using **IBM Cloud Databases**, **IBM Cloudant**, **Elasticsearch** for search, and **watsonx.data** for handling vector embeddings.

- **LLM Customization**:
    - Custom prompts and WatsonX LLM configurations are designed to tailor the review and comment responses based on the language (Python, Golang, etc.) and context (function signatures, dependencies).

### Repository Layout

The repository layout is structured to ensure maintainability, modularity, and scalability for supporting multiple languages and IBM Cloud integration. Below is a suggested directory and file structure for the watsonx-code-reviewer project:

### Root Directory Structure

```plaintext
watsonx-code-reviewer/
├── requirements.txt
├── README.md
├── LICENSE
├── config/
│   ├── config.yaml
│   ├── db_config.yaml
│   └── watsonx_models.yaml
├── docs/
│   ├── architecture.md
│   ├── usage.md
│   └── contributing.md
├── src/
│   ├── main.py
│   ├── github/
│   │   ├── webhook_handler.py
│   │   └── github_api.py
│   ├── agents/
│   │   ├── pr_review_agent.py
│   │   ├── comment_response_agent.py
│   │   └── base_agent.py
│   ├── language_handlers/
│   │   ├── python_handler.py
│   │   ├── golang_handler.py
│   │   ├── terraform_handler.py
│   │   └── shell_script_handler.py
│   ├── database/
│   │   ├── postgres_connector.py
│   │   └── elasticsearch_connector.py
│   ├── utils/
│   │   ├── logger.py
│   │   ├── config_loader.py
│   │   └── embedding_utils.py
│   └── cloud/
│       ├── code_engine.py
│       └── ibm_cloud_services.py
└── tests/
    ├── test_agents/
    │   ├── test_pr_review_agent.py
    │   └── test_comment_response_agent.py
    ├── test_language_handlers/
    │   ├── test_python_handler.py
    │   ├── test_golang_handler.py
    ├── test_database/
    │   ├── test_postgres_connector.py
    │   └── test_elasticsearch_connector.py
    └── test_utils/
        └── test_logger.py
```

### Description of Key Components

- **Root Files**:
    - `README.md`: Provides project overview, setup instructions, and usage guidelines.
    - `LICENSE`: Contains the licensing information for the project.

- **`requirements.txt`**: Specifies the Python dependencies for the project, including `ruamel.yaml` for configuration file parsing.

**`config/`**: Configuration files for various components, including database setup (`db_config.yaml`), WatsonX models (`watsonx_models.yaml`), and general app configuration (`config.yaml`). Default configurations are set in these files but can be overridden at runtime using environment variables for seamless integration with IBM Cloud Code Engine.

- `db_config.yaml`: Contains configurations for database connections:
    - **PostgreSQL**: Used to store structured data, such as repository metadata, function signatures, and pull request details. PostgreSQL provides reliable, transactional storage for core application data.
    - **Elasticsearch**: Used for semantic similarity search and full-text search capabilities, allowing quick search across the codebase and historical data. Elasticsearch serves both as a vector database for semantic embeddings and a full-text search engine.

- **`docs/`**: Documentation for architecture (`architecture.md`), app usage (`usage.md`), and contribution (`contributing.md`).

- **`src/`**: Main application code:
    - `main.py`: Entry point for the application.
    - `github/`: Handles GitHub interactions and webhook events.
        - `webhook_handler.py`: Manages GitHub webhook requests.
        - `github_api.py`: Interfaces with the GitHub API.
    - `agents/`: Implements agents for reviewing PRs and responding to comments.
        - `pr_review_agent.py`: Agent responsible for analyzing pull requests.
        - `comment_response_agent.py`: Agent that provides responses to user comments.
        - `base_agent.py`: Base class for all agents.
    - `language_handlers/`: Language-specific analysis modules.
        - `python_handler.py`, `golang_handler.py`, etc.: Modules for handling specific languages, each responsible for extracting relevant code insights.
    - `database/`: Database interaction code.
        - `postgres_connector.py`: Handles interactions with PostgreSQL.
        - `elasticsearch_connector.py`: Manages connections to Elasticsearch for vectorized searches and full-text search capabilities.
    - `utils/`: Helper utilities.
        - `logger.py`: Custom logging functionality.
        - `config_loader.py`: Loads configuration files and overrides them with environment variables if available.
        - `embedding_utils.py`: Functions for generating and processing embeddings.
    - `cloud/`: Manages cloud interactions.
        - `code_engine.py`: Code to deploy and manage workloads on IBM Cloud Code Engine.
        - `ibm_cloud_services.py`: Interfaces with other IBM Cloud services like Cloudant or Elasticsearch.

- **`tests/`**: Unit and integration tests:
    - Organized similarly to the main `src/` directory to ensure all components have corresponding tests.
    - Contains subfolders for testing agents, handlers, database connections, and utility functions.

### Additional Suggestions
- **Modular Language Handlers**: The structure allows easy addition of new language handlers to extend language support.
- **Cloud Integration**: The `cloud/` directory centralizes IBM Cloud-specific interactions, simplifying cloud-related changes.
- **Testing**: Each major component has corresponding unit tests to ensure reliability and maintainability.

### Runtime Configuration
Since the application will run in IBM Cloud Code Engine, configuration values (such as database credentials and API keys) should be supplied at runtime. Default configurations are defined in the `config/` files but can be overridden by **environment variables** for more flexibility. This approach allows efficient and secure management of runtime configurations without the need for hardcoding sensitive information, and it integrates well with IBM Cloud Secrets Manager.
