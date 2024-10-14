import logging
from github.PullRequest import PullRequest
from github.Repository import Repository
from unidiff.patch import PatchSet
from src.language_handlers.markdown_handler import MarkdownHandler
from src.agents.base_agent import BaseAgent
from difflib import SequenceMatcher
from src.agents.markdown_llm_agent import MarkdownLLMAgent

logger = logging.getLogger(__name__)

class PRReviewAgent(BaseAgent):
    def __init__(self, github_api):
        super().__init__(github_api, "pr_review_agent")
        self.markdown_handler = MarkdownHandler()
        self.markdown_llm_agent = MarkdownLLMAgent(github_api)

    def perform_code_review(self, repo_name: str, pr_number: int):
        """
        Perform an code review for the specified pull request in the given repository.

        Args:
            repo_name (str): The name of the repository in the format 'owner/repo'.
            pr_number (int): The number of the pull request to review.

        Returns:
            dict: The result of the review, including status and a message.
        """
        logger.info(f"Starting code review for PR #{pr_number} in repo '{repo_name}'")
        try:
            pull_request: PullRequest = self.github_api.get_pull_request(repo_name, pr_number)
            repo: Repository = self.github_api.get_repository(repo_name)
            commit_id = pull_request.head.sha

            review_comments = []

            # Collect existing comments from all commits in the PR
            existing_comments_dict = {}
            existing_comments = self.get_all_review_comments(pull_request)
            for comment in existing_comments:
                key = (comment.commit_id, comment.diff_hunk, comment.body)
                existing_comments_dict[key] = True

            for file in self.get_all_files(pull_request):
                filename = file.filename
                logger.info(f"Reviewing file: {filename}")

                # Handle Markdown files
                if filename.endswith('.md'):
                    logger.info(f"Delegating review of Markdown file: {filename}")

                    file_content = repo.get_contents(filename, ref=commit_id)
                    content_str = file_content.decoded_content.decode('utf-8')

                    diff_text = file.patch
                    changed_line_numbers = self.get_changed_line_numbers(diff_text, filename)

                    markdown_comments = self.markdown_handler.review(content_str)
                    for comment in markdown_comments:
                        original_line_number = comment['line']
                        if original_line_number in changed_line_numbers:
                            diff_hunk = file.patch
                            comment_key = (commit_id, diff_hunk, comment['comment'])
                            if comment_key in existing_comments_dict:
                                logger.info(f"Skipping duplicate comment on line {original_line_number} in file {filename}")
                                continue

                            review_comments.append({
                                'path': filename,
                                'line': original_line_number,
                                'side': 'RIGHT',
                                'body': comment['comment']
                            })

                    # Send to LLM for review
                    logger.info(f"Sending changes to LLM for further analysis for file: {filename}")
                    llm_comments = self.markdown_llm_agent.review(
                        full_text=content_str,
                        changed_text=diff_text,
                        existing_comments=list(existing_comments_dict.keys())
                    )
                    for llm_comment in llm_comments:
                        if (commit_id, diff_text, llm_comment['comment']) not in existing_comments_dict:
                            review_comments.append({
                                'path': filename,
                                'line': llm_comment['line'],
                                'side': 'RIGHT',
                                'body': llm_comment['comment']
                            })

            # Post the comments back to the pull request
            if review_comments:
                post_result = self.github_api.post_review_comment(repo_name, pr_number, review_comments)
                if post_result['status'] == 'success':
                    return {'status': 'success', 'message': 'Review comments posted successfully'}
                else:
                    logger.error(f"Failed to post review comments: {post_result['message']}")
                    return {'status': 'failure', 'message': f"Failed to post review comments: {post_result['message']}"}
            else:
                return {'status': 'success', 'message': 'No issues found'}

        except Exception as e:
            logger.error(f"Exception occurred during review: {str(e)}")
            return {'status': 'failure', 'message': f'Exception occurred: {str(e)}'}

    @staticmethod
    def get_changed_line_numbers(diff_text, filename):
        # Prepend file header
        header = f'--- a/{filename}\n+++ b/{filename}\n'
        diff_text_with_header = header + diff_text

        changed_lines = set()
        patch_set = PatchSet(diff_text_with_header)
        for patched_file in patch_set:
            for hunk in patched_file:
                for line in hunk:
                    if line.is_added:
                        changed_lines.add(line.target_line_no)
        return changed_lines

    @staticmethod
    def get_changed_lines(diff_text, filename):
        """
        Extract the lines added or modified in the diff text.

        Args:
            diff_text (str): The diff text for the file.
            filename (str): The filename that was modified.

        Returns:
            str: A string containing only the changed lines.
        """
        # Add file headers to the diff text
        header = f'--- a/{filename}\n+++ b/{filename}\n'
        diff_text_with_header = header + diff_text

        changed_lines = []
        try:
            patch_set = PatchSet(diff_text_with_header)
            for patched_file in patch_set:
                for hunk in patched_file:
                    for line in hunk:
                        if line.is_added:
                            changed_lines.append(line.value)
        except Exception as e:
            logger.error(f"Error parsing diff for file '{filename}': {e}")
            raise e

        return ''.join(changed_lines)

    @staticmethod
    def get_all_review_comments(pull_request: PullRequest):
        """
        Get all review comments for a given pull request, handling pagination.

        Args:
            pull_request (PullRequest): The pull request object to retrieve comments from.

        Returns:
            list: A list of all review comments.
        """
        all_comments = []
        comments = pull_request.get_review_comments()
        while True:
            all_comments.extend(comments)
            if comments.totalCount == len(all_comments):
                break
            comments = pull_request.get_review_comments().get_page(len(all_comments))

        return all_comments

    @staticmethod
    def get_all_files(pull_request: PullRequest):
        """
        Get all files for a given pull request, handling pagination.

        Args:
            pull_request (PullRequest): The pull request object to retrieve files from.

        Returns:
            list: A list of all files in the pull request.
        """
        all_files = []
        files = pull_request.get_files()
        while True:
            all_files.extend(files)
            if files.totalCount == len(all_files):
                break
            files = pull_request.get_files().get_page(len(all_files))

        return all_files

    @staticmethod
    def _normalize_diff_hunk(diff_hunk):
        """
        Normalize the diff hunk text to improve matching for duplicate comments.
        This will strip leading/trailing spaces and reduce the content to the
        essential part that identifies the change.
        """
        if diff_hunk:
            # Strip leading and trailing whitespace and limit to significant lines
            return diff_hunk.strip().split('\n', 1)[0]  # Consider only the first line for consistency
        return diff_hunk

    @staticmethod
    def get_changed_parts(diff_text, filename):
        """
        Extract the changed parts of each modified line in the diff text.

        Args:
            diff_text (str): The diff text for the file.
            filename (str): The filename that was modified.

        Returns:
            list: A list of dictionaries containing the line number and the specific changed parts.
        """
        # Add file headers to the diff text
        header = f'--- a/{filename}\n+++ b/{filename}\n'
        diff_text_with_header = header + diff_text

        changed_parts = []
        try:
            patch_set = PatchSet(diff_text_with_header)
            for patched_file in patch_set:
                for hunk in patched_file:
                    removed_lines = []
                    added_lines = []
                    for line in hunk:
                        if line.is_removed:
                            removed_lines.append((line.value.rstrip('\n'), line.source_line_no))
                        elif line.is_added:
                            added_line = line.value.rstrip('\n')
                            target_line_no = line.target_line_no

                            if removed_lines:
                                # Pair the added line with the first removed line
                                prev_line, source_line_no = removed_lines.pop(0)
                                # Compare the lines word by word
                                prev_words = prev_line.split()
                                added_words = added_line.split()
                                # Identify changed words
                                matcher = SequenceMatcher(None, prev_words, added_words)
                                changes = []
                                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                                    if tag in ('insert', 'replace', 'delete'):
                                        # Include entire words that have changed
                                        changed_words = added_words[j1:j2]
                                        changes.extend(changed_words)
                                # Reconstruct the line with changes highlighted
                                if changes:
                                    changed_text = ' '.join(changes)
                                    changed_parts.append({
                                        'line': target_line_no,
                                        'changes': added_line.strip()
                                    })
                            else:
                                # New line added, include the entire line
                                changed_parts.append({
                                    'line': target_line_no,
                                    'changes': added_line.strip()
                                })
                        else:
                            # Reset if we encounter context lines
                            removed_lines = []
        except Exception as e:
            logger.error(f"Error parsing diff for file '{filename}': {e}")
            raise e

        return changed_parts