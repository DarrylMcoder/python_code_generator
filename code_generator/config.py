git_branch = 'ai-assistant'
"""
The git branch to commit AI-generated code to.
Default: "ai-assistant"
"""

after_generation = "raise"
"""
What to do after code generation.
Possible values:
    "continue" - Continue execution of the program
        This will cause the AI-generated code to be executed
        so that no exception is raised. Be careful! AI-generated code
        could contain bugs. It's up to you to validate the code.
    "raise" - Raise AttributeError. This will raise an AttributeError
    like usual, but with a custom message indicating that the
    attribute did not exist and was generated by the code generator.
    This is the default value.
"""

auto_merge = True
"""
Whether to automatically merge AI-generated code into the main branch.
Default: True
"""
