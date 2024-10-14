import re
import logging
from spellchecker import SpellChecker

logger = logging.getLogger(__name__)

class MarkdownHandler:
    def __init__(self):
        self.spell = SpellChecker()
        known_words = ['Markdown', 'ibm', 'github', 'watsonx', 'llm','llms', 'pr', 'prs', 'app', 'codebase', 'multi', 'golang', 'postgres',
                       'postgresql', 'api', 'apis', 'webhook', 'webhooks', 'json', 'yaml', 'yml', 'cli', 'docker', 'github', 'git',
                       'jenkins', 'kubernetes', 'slack', 'python', 'java', 'javascript', 'nodejs', 'node', 'js', 'ruby', 'rails', 'php',
                       'csharp', 'c#', 'dotnet', 'dot', 'net', 'c++', 'cpp', 'objective-c', 'swift', 'go', 'golang', 'rust', 'scala', 'kotlin', 'typescript',
                       'html', 'css', 'scss', 'sass', 'less', 'elasticsearch', 'elk', 'logstash', 'kibana', 'prometheus', 'grafana', 'influxdb', 'telegraf', 'mongodb',
                       'cloudant', 'couchdb', 'cassandra', 'redis', 'rabbitmq', 'kafka', 'activemq', 'nats', 'mqtt', 'mqtt', 'postgresql', 'mysql', 'mariadb', 'sqlite',
                       'mssql', 'oracle', 'db2', 'sybase', 'informix', 'teradata', 'snowflake', 'redshift', 'bigquery', 'athena', 'dynamodb', 'cosmosdb', 'couchbase', 'riak',
                       'hbase', 'cassandra', 'neo4j', 'arangodb', 'orientdb', 'dgraph', 'fauna', 'faunadb', 'cockroachdb', 'spanner', 'firestore', 'firebasedb', 'firebase', 'realm',
                       'etc', 'py', 'md', 'yaml', 'yml', 'json', 'toml', 'ini', 'xml', 'html', 'css', 'scss', 'sass', 'less', 'src', 'dist', 'build', 'bin', 'lib', 'node_modules',
                       'db', 'config', 'metadata', 'plaintext', 'watson', 'sql', 'api', 'apis', 'cli', 'sdk', 'dev', 'prod', 'test', 'qa', 'uat', 'prod','txt','readme','utils','util',
                       'ruamel', 'subfolder', 'subfolders', 'subdirectory', 'subdirectories', 'submodule', 'submodules', 'subrepo', 'subrepos', 'subrepository', 'subrepositories',
                       'runtime', 'runtimes', 'env', 'envs', 'environment', 'environments', 'config', 'configs', 'configuration', 'configurations', 'param', 'params', 'parameter',
                       'hardcoded', 'hardcode', 'hardcoding', 'hardcodes', 'softcoded', 'softcode', 'softcoding', 'softcodes', 'variable', 'variables', 'var', 'vars', 'constant',]
        for word in known_words:
            self.spell.word_frequency.add(word)

    def review(self, file_content):
        """
        Perform a spell check on the provided Markdown file content.

        :param file_content: The content of the Markdown file.
        :return: List of review comments.
        """
        logger.info("Starting Markdown review")
        comments = []
        lines = file_content.splitlines()

        for line_number, line in enumerate(lines, start=1):
            words = re.findall(r'\b\w+\b', line)
            split_words = []
            for word in words:
                split = False
                # Split snake_case words
                if '_' in word:
                    split_words.extend(word.split('_'))
                    split = True
                # Split kebab-case words
                if '-' in word:
                    split_words.extend(word.split('-'))
                    split = True
                # Split CamelCase words
                if re.search(r'[A-Z]', word):
                    split = True
                    split_words.extend(re.findall(r'[A-Z]+(?=[A-Z][a-z]|[A-Z]$|$)|[A-Z]?[a-z]+', word))
                # Add the original word only if it wasn't split
                if not split:
                    split_words.append(word)

            misspelled = self.spell.unknown(split_words)
            for word in misspelled:
                if len(word) == 1 and word.lower() not in ('a', 'i'):
                    continue  # Skip single-letter words like 's', 'P', 'R'

                correction = self.spell.correction(word)
                if correction != None:
                    comments.append({
                        'line': line_number,
                        'comment': f"Possible spelling mistake: '{word}'. Did you mean '{correction}'?"
                    })
                else:
                    comments.append({
                        'line': line_number,
                        'comment': f"Is this a spelling mistake?: '{word}'"
                    })

        logger.info(f"Markdown review found {len(comments)} issues.")
        for comment in comments:
            logger.debug(f"Comment: {comment}")
        logger.debug(f"Markdown review complete.")
        return comments