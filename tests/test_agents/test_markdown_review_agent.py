import unittest
from unittest.mock import MagicMock, patch
from language_handlers.markdown_handler import MarkdownReviewAgent

class TestMarkdownReviewAgent(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the MarkdownReviewAgent instance for testing.
        """
        self.agent = MarkdownReviewAgent()

    @patch('src.github.github_api.GitHubAPI')
    def test_review_no_issues(self, mock_github_api):
        """
        Test the review function with a markdown file that has no spelling mistakes.
        """
        # Mock the GitHubAPI to ensure it has the required label
        mock_pull_request = MagicMock()
        mock_pull_request.get_labels.return_value = [{'name': 'ready-to-review'}]
        mock_github_api.get_pull_request.return_value = mock_pull_request

        content = """
        # Markdown Header
        This is a test Markdown file with no spelling mistakes.
        """
        comments = self.agent.review(content)
        self.assertEqual(len(comments), 0, "Expected no comments for correct content.")

    @patch('src.github.github_api.GitHubAPI')
    def test_review_with_spelling_issues(self, mock_github_api):
        """
        Test the review function with a markdown file that contains spelling mistakes.
        """
        # Mock the GitHubAPI to ensure it has the required label
        mock_pull_request = MagicMock()
        mock_pull_request.get_labels.return_value = [{'name': 'ready-to-review'}]
        mock_github_api.get_pull_request.return_value = mock_pull_request

        content = """
        # Markdown Header
        This is a tesst Markdown file with sme spelling mistakes.
        """
        comments = self.agent.review(content)
        self.assertGreater(len(comments), 0, "Expected comments for incorrect content.")
        self.assertIn("Spelling mistake: 'tesst'", [c['comment'] for c in comments], "Expected 'tesst' to be flagged.")
        self.assertIn("Spelling mistake: 'sme'", [c['comment'] for c in comments], "Expected 'sme' to be flagged.")

    @patch('src.github.github_api.GitHubAPI')
    def test_review_multiple_lines(self, mock_github_api):
        """
        Test the review function with multiple lines of content containing spelling mistakes.
        """
        # Mock the GitHubAPI to ensure it has the required label
        mock_pull_request = MagicMock()
        mock_pull_request.get_labels.return_value = [{'name': 'ready-to-review'}]
        mock_github_api.get_pull_request.return_value = mock_pull_request

        content = """
        This is the frst line.
        This is the secnd line with an eror.
        """
        comments = self.agent.review(content)
        self.assertEqual(len(comments), 3, "Expected 3 spelling mistakes to be flagged.")
        self.assertIn("Spelling mistake: 'frst'", [c['comment'] for c in comments], "Expected 'frst' to be flagged.")
        self.assertIn("Spelling mistake: 'secnd'", [c['comment'] for c in comments], "Expected 'secnd' to be flagged.")
        self.assertIn("Spelling mistake: 'eror'", [c['comment'] for c in comments], "Expected 'eror' to be flagged.")

if __name__ == "__main__":
    unittest.main()