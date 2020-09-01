# csc648-sp19-Team104 - Project Pegasus

# This base repo is for Dr. HyoJung Song's class.

# Coding and Git Requirements



The intention for this document is to serve as a reference for all coding and git practices for Team Pegasus.

### Python Coding Requirements
Any and all IDE or text editors can be used, provided they allow you to maintain the following requirements:
  - Whitespace should be only indented with spaces, not tabs.
  - Indent should be set to 4 spaces.
  - Variable, function and class names should align with PEP8, i.e. **'variable_name'**, **'function_name'**, **'ClassName'**.

Though not required, it is suggested to align as closely with PEP8 suggestions as possible. Certain tools can be configured to allow this, such as the PyCharm IDE.

### Git Requirements
  - Pull requests can be submitted to any branch _except_ **master**. **Master** will be merged from **dev** during a separate process.
  - Branch names should describe the feature the branch is for, rather than who started the branch. Examples of good branch names: _google-maps-feature_, _side navbar_, etc.
  - All new code changes and features will be submitted to **dev** at least **5** days before milestone due date. Any pull requests for new features past then will be denied. This is to allow proper time for testing with **dev** on the remote server, as well as the update of **master**.

The general workflow with Github should be as follows, assuming the addition of a new feature:
  - Make sure your branch is up-to-date with all of the latest changes of the repository:
     ```sh
    $ git pull
    ```
  - Create your new branch:
    ```sh
    $ git checkout <your_new_branch_name>
    ```
    **NOTE**: It is suggested that a branch be set up to track your changes **before** you start working on your new feature.

  - Implement the new feature...
  - Add all of the new, updated and deleted files to the working tree:

    ```sh
    $ git add . -A
    ```

  - Commit your work upstream to the remote repository:

    ```sh
    $ git commit
    $ git push -u origin <your_branch_name>
    ```
