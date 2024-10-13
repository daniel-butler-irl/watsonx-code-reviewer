# 🚧 POC Work in Progress - Nothing Works 🚧

# WatsonX Code Reviewer Documentation

Welcome to the **WatsonX Code Reviewer** documentation! This project is an AI-powered code review tool that integrates with GitHub to automate code reviews, leveraging IBM WatsonX language models for advanced analysis.

## Overview

The **WatsonX Code Reviewer** helps streamline code review processes by providing automated suggestions, detecting issues, and enhancing the quality of your codebase. It supports multiple agents, including review and dependency analysis, and is capable of integrating with GitHub or GitHub Enterprise.

The application is designed to run in IBM Cloud using scalable services like IBM Code Engine, and it utilizes PostgreSQL and Elasticsearch for data storage and retrieval.

## Table of Contents

- [Getting Started](./setup_github_app.md)
- [Local Development](./local_dev_smee.md)
- [Webhook Handler Setup](./webhook_handler_setup.md)
- [Configuration](#configuration)
- [Agents Overview](#agents-overview)
- [License](#license)

## Getting Started

To get started, check out the [Getting Started guide](./setup_github_app.md) to set up the GitHub app and integrate it with your repository. This will help you configure the WatsonX Code Reviewer to begin analyzing pull requests and providing automated reviews.

## Local Development

If you want to run the application locally for testing and development, refer to the [Local Development guide](./local_dev_smee.md). This guide will show you how to use tools like **Smee.io** to handle webhooks while developing locally.

## Configuration

The project relies on several configuration files that help it connect to GitHub, IBM Cloud services, and manage settings for each agent:

- `config.yaml`: Main configuration file for app settings.
- `db_config.yaml`: Configuration for PostgreSQL and Elasticsearch databases.
- `watsonx_models.yaml`: Contains information about the WatsonX models used for code analysis.

## Agents Overview

WatsonX Code Reviewer uses multiple agents, each designed to handle specific aspects of the review process. The primary agent currently implemented is the **ReviewAgent**, which automatically reviews pull requests and posts comments on detected issues.

In future releases, we plan to add additional agents, such as a **DependencyAnalysisAgent** to provide insights on library usage and compatibility.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](../LICENSE) file for details.