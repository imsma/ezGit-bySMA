import re
from urllib.parse import urlparse

def is_valid_git_url(url):
    """Checks if the given URL is a valid Git URL.

    Args:
        url: The URL to check.

    Returns:
        True if the URL is valid, False otherwise.
    """

    # Regular expressions for different Git URL schemes:
    github_ssh_regex = r"^git@([^/\s]+)\.com:(?:[^/]+)?(/[^/\s]+)+\.git$"  # Updated for GitHub SSH
    azure_ssh_regex = r"^git@ssh\.dev\.azure\.com:v3/([^/]+)/([^/]+)/([^/]+)$"
    azure_https_regex = r"^https://([^/]+)@dev\.azure\.com/([^/]+)/([^/]+)/_git/([^/]+)$"
    git_url_regex = r"^(?:git|https?|ssh)://([^/\s]+@)?([^/\s]+)(:[\d]+)?(/[^/\s]+)*(?:\.git|\.git@{[\w.]+})?$"

    # Check in the preferred order (specific to generic)
    if re.match(github_ssh_regex, url):
        return True
    elif re.match(azure_ssh_regex, url):
        return True
    elif re.match(azure_https_regex, url):
        return True
    elif re.match(git_url_regex, url):
        return True
    else:
        return False
    

def extract_repo_name(url):
    """Extracts the plain Git repository name from a given URL.

    Args:
        url: The Git URL to process.

    Returns:
        The extracted repository name, or None if the URL is invalid.
    """

    # Regular expressions for different Git URL schemes
    github_ssh_regex = r"^git@([^/\s]+)\.com:(?:[^/]+)?(/[^/\s]+)\.git$"
    azure_ssh_regex = r"^git@ssh\.dev\.azure\.com:v3/([^/]+)/([^/]+)/([^/]+)$"
    azure_https_regex = r"^https://([^/]+)@dev\.azure\.com/([^/]+)/([^/]+)/_git/([^/]+)$"
    git_url_regex = r"^(?:git|https?|ssh)://([^/\s]+@)?([^/\s]+)(:[\d]+)?(/[^/\s]+)+\.git$"

    # Check for different URL formats and extract the repository name
    if re.match(github_ssh_regex, url):
        return re.search(r"/([^/\s]+)\.git$", url).group(1)
    elif re.match(azure_ssh_regex, url):
        return re.search(r"/([^/]+)$", url).group(1)
    elif re.match(azure_https_regex, url):
        return re.search(r"/_git/([^/]+)$", url).group(1)
    elif re.match(git_url_regex, url):
        return re.search(r"/([^/\s]+)\.git$", url).group(1)
    else:
        return None


# Test cases:
test_cases = [
    "git@ssh.dev.azure.com:v3/company/PROJECT/REPO",
    "https://user@dev.azure.com/company/PROJECT/_git/REPO",
    "https://github.com/user/repo.git",
    "git://user:password@host:1234/path/to/repo.git",
    "invalid_url",
    "https://invobyte@dev.azure.com/invobyte/ARISTO/_git/aristo_db_init",
    "git@ssh.dev.azure.com:v3/invobyte/ARISTO/aristo_db_init",
    "https://github.com/ezarko/opendlp",
    "git@github.com:ezarko/opendlp.git",
    "https://github.com/ezarko/opendlp.git",
    "git@github.com:vercel/next.js.git"
]

# for url in test_cases:
#     print(f"Testing URL: {url}")
#     if is_valid_git_url(url):
#         print("Valid Git URL")
#     else:
#         print("Invalid Git URL")


for url in test_cases:
    print(f"normalize_git_url URL: {url}")
    repo_name = extract_repo_name(url)
    print(repo_name)