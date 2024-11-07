import streamlit as st
import subprocess
import os
import re
import pandas as pd
from urllib.parse import urlparse

class Repository:
    def __init__(self, repo_name, repo_url):
        self.repo_name = repo_name
        self.repo_url = repo_url

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

def render_list():
    # Render the repository table with st.data_editor
    if st.session_state.repo_list:
        repo_data = {
            "Repository Name": [repo.repo_name for repo in st.session_state.repo_list],
            "Repository URL": [repo.repo_url for repo in st.session_state.repo_list],
            "Select": [False for _ in st.session_state.repo_list]
        }
        repo_df = pd.DataFrame(repo_data)
        edited_df = st.data_editor(repo_df, use_container_width=True, num_rows="dynamic", key="repo_table")
        return edited_df

# Streamlit UI
st.title("Git Repository Cloner and Branch Fetcher")

# Input for target directory
target_directory = st.text_input("Enter the target directory to clone repositories:")

# Input and button to manage repository list
if 'repo_list' not in st.session_state:
    st.session_state.repo_list = []

new_repo_urls = st.text_area("Enter new Git repository URLs to add to the list (one URL per line):")

if st.button("Add Repositories"):
    for new_repo_url in new_repo_urls.strip().splitlines():
        new_repo_url = new_repo_url.strip()
        if new_repo_url:
            if is_valid_git_url(new_repo_url.strip()):
                repo_name = extract_repo_name(new_repo_url.strip())
                if repo_name and not any(repo.repo_name == repo_name for repo in st.session_state.repo_list):
                    st.session_state.repo_list.append(Repository(repo_name, new_repo_url.strip()))
                    st.success(f"Added repository: {new_repo_url.strip()}")
                else:
                    st.warning("The repository name is already in the list.")
            else:
                st.error("Please enter a valid Git SSH or HTTPS repository URL.")

edited_df = render_list()

# Update the repository list based on selected rows for deletion
if st.button("Remove Selected Repositories"):
    updated_repo_list = []
    for idx, selected in enumerate(edited_df["Select"]):
        if not selected:
            updated_repo_list.append(st.session_state.repo_list[idx])
    st.session_state.repo_list = updated_repo_list
    st.success("Selected repositories removed successfully.")
    st.experimental_rerun()


st.session_state.count = 0
def clone_and_fetch(repo_url, target_directory):
    progress_bar = st.progress(0)
    st.session_state.count  += 1
    md = "### {count}".format(count=st.session_state.count)
    st.markdown(md)
    progress = 0
    progress_step = 10
    # Change to the target directory
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    os.chdir(target_directory)

    # Clone the repository
    st.info(f"Cloning the repository from {repo_url} ...")
    progress += progress_step
    progress_bar.progress(min(progress, 100))
    result = subprocess.run(["git", "clone", repo_url], capture_output=True, text=True)
    progress += progress_step
    progress_bar.progress(min(progress, 100))
    
    if result.stdout:
        st.text(result.stdout)
    if result.stderr:
        st.text(result.stderr)


    progress += progress_step
    progress_bar.progress(min(progress, 100))

    # Extract the repository name from URL
    repo_name = os.path.basename(repo_url).replace('.git', '')

    # Check if the repository was cloned successfully
    if not os.path.exists(repo_name):
        st.error(f"Failed to clone the repository {repo_name}")
        return

    # Change directory to the cloned repository
    os.chdir(repo_name)

    # Fetch all remote branches locally
    st.info("Fetching all remote branches ...")
    progress += progress_step
    progress_bar.progress(min(progress, 100))
    result = subprocess.run(["git", "fetch", "--all"], capture_output=True, text=True)
    progress += progress_step
    progress_bar.progress(min(progress, 100))
    if result.stdout:
        st.text(result.stdout)
    if result.stderr:
        st.text(result.stderr)

    # Checkout to a new temporary branch
    result = subprocess.run(["git", "checkout", "-b", "temp_branch_for_fetch"], capture_output=True, text=True)
    progress += progress_step
    progress_bar.progress(min(progress, 100))
    if result.stdout:
        st.text(result.stdout)
    if result.stderr:
        st.text(result.stderr)
    else:
        st.success("Repository cloned and all remote branches fetched successfully.")
        progress = 100
        progress_bar.progress(min(progress, 100))        

    # Print success message


    # Move back to the original directory
    os.chdir("..")
    st.divider()

def clone():
    # Button to clone and fetch branches
    if st.button("Clone and Fetch Branches"):
        if target_directory and st.session_state.repo_list:
            for repo in st.session_state.repo_list:
                clone_and_fetch(repo.repo_url, target_directory)
            st.success("Done")
            st.balloons()            
        else:
            st.error("Please enter both the target directory and at least one repository URL.")    

clone()
