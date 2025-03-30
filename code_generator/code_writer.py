import inspect
import traceback
import subprocess
from .code_generator import CodeGenerator
from .exceptions import CodeWriterException

class CodeWriter(CodeGenerator):
    def insert_code(self, cls=None, main_source=None, code="") -> str:
        # Add indentation to the code
        code_lines = code.split("\n")
        for i, line in enumerate(code_lines):
            code_lines[i] = f"    {line}"

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
        prompt += "The code will be inserted at that line number.\n"

        line_number = self.generate_info(prompt, class_source)

        try:
            line_number = int(line_number)
        except ValueError:
            raise CodeWriterException(f"Invalid line number: {line_number}")

        if not (1 <= line_number <= len(lines)):
            raise CodeWriterException(f"Invalid line number: {line_number}")

        # Insert the code at the line number
        lines_before = lines[:line_number - 1]
        lines_after = lines[line_number - 1:]
        new_lines = lines_before + code_lines + lines_after
        new_class_source = "\n".join(new_lines)
        return new_class_source

    def commit_changes(self, cls, class_source, commit_message):
        class_file = inspect.getsourcefile(cls)
        # Commit to git in the ai-assistant branch
        # Save the developer's changes
        self.git_stash()

        current_branch = self.git_current_branch()
        self.git_switch("ai-assistant")

        try:
            # Write to the class source file
            with open(class_file, "w") as f:
                f.write(class_source)

            self.git_add(class_file)
            self.git_commit(commit_message)
            self.git_switch(current_branch)
            self.git_stash_pop()
        except Exception as e:
            # Commit failed, restore the developer's changes
            # Reraise the exception
            self.git_switch(current_branch)
            self.git_stash_pop()
            raise

    def sanitize(self, message):
        # Sanitize the commit message
        message = message.replace("`", "")
        return message

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
        except subprocess.CalledProcessError:
            self.shell(["git", "branch", branch_name])
            self.shell(["git", "switch", branch_name])

    def git_add(self, filename):
        print(f"Adding {filename} to git...")
        self.shell(["git", "add", filename.strip()])

    def git_commit(self, message):
        print("Committing changes...")
        # Sanitize the commit message
        message = self.sanitize(message)
        self.shell(["git", "commit", "-m", message])

    def shell(self, command):
        print(f"Running shell command: {' '.join(command)}")
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        except subprocess.CalledProcessError as e:
            raise CodeWriterException(f"Error running shell command: {e}\n{traceback.format_exc()}")
        else:
            return result.stdout.strip()
