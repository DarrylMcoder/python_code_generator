import inspect
import subprocess
from .code_generator import CodeGenerator
from .exceptions import CodeWriterException

class CodeWriter(CodeGenerator):
    def insert_code(self, cls=None, main_source=None, code="") -> str:
        # Validate inputs
        if cls and main_source:
            raise ValueError("Cannot specify both cls and main_source")
        if cls:
            # Get the class source
            class_file = inspect.getsourcefile(cls)
            with open(class_file) as f:
                class_source = f.read()
        elif main_source:
            class_source = main_source
        else:
            raise ValueError("Must specify either cls or main_source")

        if not code.strip():
            # No code to insert; Nothing to do
            return class_source

        # Add line numbers to the class source
        lines = class_source.split("\n")
        class_source = "Class source:\n"
        for i, line in enumerate(lines):
            class_source += f"{i + 1}: {line}\n"

        prompt = f"Where in the {'class ' + cls.__name__ if cls else 'above source code'} should the following code be inserted?\n"
        prompt += f"Code to insert:\n{code}\n\n"
        prompt += "Please choose a line number from the class source above.\n"
        prompt += "Return the line number as a string.\n"
        prompt += "The line number must be between 1 and the number of lines in the class source and it must be a whole number.\n"
        prompt += "The code will be inserted in the class source immediately before the code at that line number.\n"

        line_number = self.generate_info(prompt, class_source)

        try:
            line_number = int(line_number)
        except ValueError:
            raise CodeWriterException(f"Invalid line number: {line_number}")

        if not (1 <= line_number <= len(lines)):
            raise CodeWriterException(f"Invalid line number: {line_number}")

        # Add AI watermark
        code = code.strip()
        code = f"""## AI GENERATED CODE; PLEASE REVIEW ##
{code}
## END OF AI GENERATED CODE ##
        """

        # Add indentation to the code
        # And define code_lines
        code_lines = code.split("\n")
        code_lines = [f"    {line}" for line in code_lines]

       # Insert the code at the line number
        lines_before = lines[:line_number]
        lines_after = lines[line_number:]
        new_lines = lines_before + code_lines + lines_after
        new_class_source = "\n".join(new_lines)
        return new_class_source

    def replace_code(self, cls=None, main_source=None, old_code="", new_code="") -> str:
        if cls and main_source:
            raise ValueError("Cannot specify both cls and main_source")

        if cls:
            # Get the class source
            class_file = inspect.getsourcefile(cls)
            with open(class_file) as f:
                class_source = f.read()
        elif main_source:
            class_source = main_source
        else:
            raise ValueError("Must specify either cls or main_source")

        if not new_code.strip():
            # No code to insert; Nothing to do
            return class_source

        if not old_code.strip():
            return self.insert_code(cls=cls, main_source=main_source, code=new_code)

        # Indent the new code
        new_code = new_code.replace("\n", "\n    ")

        replacement_str = f"""
## AI MODIFIED CODE; PLEASE REVIEW ##
{new_code}
## END OF AI MODIFIED CODE ##

## ORIGINAL CODE; REMOVE WHEN REVIEWED ##
\"\"\"
{old_code}
\"\"\"
## END OF ORIGINAL CODE ##
"""

        new_class_source = class_source.replace(old_code, replacement_str)

        return new_class_source


    def commit_changes(self, cls, class_source, commit_message):
        class_file = inspect.getsourcefile(cls)

        # Write to the class source file
        # Simpler than using git for now :)-
        with open(class_file, "w") as f:
            f.write(class_source)

    def git_stash(self):
        print("Stashing changes...")
        self.shell(["git", "stash"])

    def git_stash_pop(self):
        print("Popping changes...")
        self.shell(["git", "stash", "pop"])

    def git_current_branch(self):
        print("Getting current branch...")
        return self.shell(["git", "branch", "--show-current"])

    def git_switch(self, branch_name):
        print(f"Switching to branch {branch_name}...")
        try:
            subprocess.run(["git", "switch", branch_name], check=True)
        except subprocess.CalledProcessError as e:
            if e.stderr and e.stderr.contains("invalid reference: ai-assistant"):
                self.shell(["git", "branch", branch_name])
                self.shell(["git", "switch", branch_name])
            else:
                raise CodeWriterException(f"Error switching to branch {branch_name}: {e.stderr}")

    def git_add(self, filename):
        print(f"Adding {filename} to git...")
        self.shell(["git", "add", filename])

    def git_status(self):
        print("Getting git status...")
        return self.shell(["git", "status"])

    def git_commit(self, message):
        print("Committing changes...")
        self.shell(["git", "commit", "-m", message])

    def git_merge(self, branch):
        print(f"Merging branch {branch}...")
        self.shell(["git", "merge", branch])

    def shell(self, command):
        print(f"Running shell command: {' '.join(command)}")
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        except subprocess.CalledProcessError as e:
            raise CodeWriterException(f"Error running shell command: {e.stderr}")
        else:
            return result.stdout.strip()
