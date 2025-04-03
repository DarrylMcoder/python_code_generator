import inspect
import subprocess
from .exceptions import CodeGenerationException

class CodeGenerator:
    def generate_method(self, cls, method_name, args, kwargs, frozen_stack):
        code_context = self.get_default_code_context(cls, method_name, frozen_stack)

        prompt = f"Implement the method {cls.__name__}.{method_name} in the class {cls.__name__} with the arguments {args} and the keyword arguments {kwargs}.\n"
        prompt += f"This method was called on an instance of the class {cls.__name__} but it was not defined in the class.\n"
        prompt += "The method was called with the arguments {args} and the keyword arguments {kwargs}.\n"
        prompt += "Do not generate the class definition, only the method implementation.\n"
        prompt += "Your job is to define the method.\n"

        code = self.generate_code(prompt, code_context)
        return code

    def generate_method_for_attribute(self, cls, attribute_name, stack):
        # Implement a new method to set the attribute
        code_context = self.get_default_code_context(cls, attribute_name, stack)

        prompt = f"Implement a new method to set the attribute {cls.__name__}.{attribute_name} in the class {cls.__name__}.\n"
        prompt += f"This attribute was accessed on an instance of the class {cls.__name__} but it was not defined in the class.\n"
        prompt += "We have determined that there should be a new method to set the attribute.\n"
        prompt += "Your job is to define the method.\n"
        prompt += "The method may or may not have arguments.\n"
        prompt += "The method may or may not perform any other operations.\n"
        prompt += "Return only the code for the method.\n"
        prompt += "Do not generate the class definition, only the method implementation.\n"

        code = CodeGenerator().generate_code(prompt, code_context)
        return code

    def generate_class_attribute(self, cls, attribute_name, stack):
        # Add the attribute to the class source as a class attribute
        code_context = self.get_default_code_context(cls, attribute_name, stack)

        prompt = f"Add the attribute {cls.__name__}.{attribute_name} to the class {cls.__name__} as a class attribute.\n"
        prompt += f"This attribute was accessed on an instance of the class {cls.__name__} but it was not defined in the class.\n"
        prompt += "We have determined that the attribute should be defined as a class attribute.\n"
        prompt += "Your job is to define the attribute.\n"
        prompt += "Return the line or lines of code where the attribute is defined.\n"
        prompt += "Do not generate the class definition (the class ClassName line), only the attribute definition (attribute_name = value).\n"

        code = self.generate_code(prompt, code_context)
        return code

    def modify_method_for_attribute(self, cls, attribute_name, stack, existing_method_name):
        # Modify an existing method to set the attribute
        code_context = self.get_default_code_context(cls, attribute_name, stack)
        existing_method_source = inspect.getsource(cls.__dict__[existing_method_name])

        prompt = f"Modify the method {cls.__name__}.{existing_method_name} to set the attribute {cls.__name__}.{attribute_name} in the class {cls.__name__}.\n"
        prompt += f"This attribute was accessed on an instance of the class {cls.__name__} but it was not defined in the class.\n"
        prompt += "We have determined that the attribute should be set by modifying an existing method to set the attribute.\n"
        prompt += "Your job is to modify the method.\n"
        prompt += "The method must retain its original functionality.\n"
        prompt += "Return only the source code of the modified method.\n"
        prompt += "Do not generate the class definition, only the modified method.\n"

        code = self.modify_code(prompt, code_context, existing_method_source)
        return code

    def generate_return_value(self, code, attribute_name, special_method_name, args=[], kwargs={}):
        prompt = f"The above code is the definition of the attribute {attribute_name}.\n"
        if args:
            prompt += f"The method was called with the arguments {args}.\n"
        if kwargs:
            prompt += f"The method was called with the keyword arguments {kwargs}.\n"
        prompt += f"Your job is to return code that can be run with eval to return the value of the attribute {attribute_name} or its return value if it is a function.\n"
        prompt += f"The code you return will be run in the {special_method_name} method of the attribute {attribute_name}.\n"
        prompt += f"The code you return will need to define the method or attribute {attribute_name}, then return its value or its return value, depending on whether it is a function.\n"
        prompt += f"Return only the code that can be run with eval to return a value compatible with the special method {special_method_name}.\n"

        return_code = self.generate_code(prompt, code)
        return eval(return_code)

    def generate_commit_message(self, old_code, new_code):
        if old_code == "":
            prompt = f"The following new code was generated by the code generator: {new_code}\n"
        else:
            prompt = f"The following new code was generated by the code generator: {new_code}\n"
            prompt += f"The following old code was replaced by the new code: {old_code}\n"
        prompt += "Return a commit message for the changes.\n"
        commit_message = self.generate_info(prompt)
        commit_message = f"AI generated {commit_message}"
        return commit_message

    def generate_info(self, prompt, code_context=""):
        prompt = f"{code_context}\n\n{prompt}"
        prompt += "- Based on the code above, and the instructions, generate a valid response.\n"
        prompt += "- Do not generate any additional text aside from the response that is requested.\n"

        info = self.prompt_ai(prompt)
        return info

    def generate_code(self, prompt, code_context=""):
        prompt = f"{code_context}\n\n{prompt}"
        prompt += "- Generate Python code as described.\n"
        prompt += "- If appropriate, document the code clearly and concisely with comments to explain what the code does.\n"
        prompt += "- If it is a function, add a docstring to the function.\n"
        prompt += "- Do not generate any additional code beside the code that is described.\n"
        prompt += "- Generate only Python code. Do not generate any explaining text aside from code comments.\n"
        prompt += "- Do not generate any import statements, they will be added later.\n"
        prompt += "- Do not include the text ```python.\n"

        code = self.prompt_ai(prompt)
        # Remove the Markdown formatting
        code = code.strip()
        code = code.replace("```python", "")
        code = code.replace("```", "")
        return code

    def modify_code(self, prompt, code_context, code):
        prompt = f"{code_context}\n\n{prompt}"
        prompt += f"- The following code is the existing code: {code}\n"
        prompt += "- Generate Python code as described.\n"
        prompt += "- Document the code clearly and concisely with comments to explain what the code does.\n"
        prompt += "- If it is a function, add a docstring to the function.\n"
        prompt += "- Do not generate any additional code beside the code that is described.\n"
        prompt += "- Generate only Python code. Do not generate any explaining text aside from code comments.\n"
        prompt += "- Do not generate any import statements, they will be added later.\n"
        prompt += "- Do not include the text ```python.\n"

        code = self.prompt_ai(prompt)
        # Remove the Markdown formatting
        code = code.strip()
        code = code.replace("```python", "")
        code = code.replace("```", "")
        return code

    def generate_imports(self, code):
        prompt = f"The following code was generated by the code generator: {code}\n"
        prompt += "- Generate the Python import statements that are required for the code.\n"
        prompt += "- Do not generate any additional code beside the import statements.\n"
        prompt += "- Generate only Python import statements. Do not generate any explaining text aside from import statements.\n"
        prompt += "- If no import statements are required, return 'None'.\n"
        prompt += "- Do not include any other text beside the import statements or the text 'None'.\n"
        prompt += "- Do not include the text ```python.\n"

        imports = self.prompt_ai(prompt)
        if imports == "None":
            imports = ""
        return imports

    def decide_which_method_sets_attribute(self, cls, attribute_name, stack):
        code_context = self.get_default_code_context(cls, attribute_name, stack)
        prompt = f"The attribute {attribute_name} was accessed on an instance of the class {cls.__module__}.{cls.__name__} but it was not defined in the class.\n"
        prompt += "Your job is to determine if it is a class attribute or an instance attribute.\n"
        prompt += "If the attribute should be defined as a class attribute, return 'class'. In this case, the attribute will be added to the class source as a class attribute.\n"
        prompt += "If the attribute should be defined as an instance attribute, and there is a method that can be sensibly modified to set the attribute, return the name of the method.\n"
        prompt += "If the attribute should be defined as an instance attribute, but there is no existing method that can be sensibly modified to set the attribute, return 'None'.\n"
        prompt += "Return only 'class' or 'None' or the name of the method that should be modified to set the attribute.\n"

        method = self.generate_info(prompt, code_context)

        return method

    def get_default_code_context(self, cls, method_name, frozen_stack):
        # Get the default code context
        # Get the parent classes
        parent_classes = self.get_all_parent_classes(cls)
        parent_class_sources = self.get_class_sources(parent_classes, method_name)

        # Get other related classes, siblings, cousins, etc
        other_related_classes = self.get_all_related_classes(cls, excluded_classes=parent_classes)
        other_related_class_sources = self.get_class_sources(other_related_classes, method_name)
        caller_source = self.get_calling_code(stack=frozen_stack, stack_depth=1)
        stack_trace = self.get_stack_trace(frozen_stack, start_depth=1)
        self_source = self.get_class_source(cls, method_name, full=True)
        
        code_context = f"Parent classes of {cls.__module__}.{cls.__name__}:\n {parent_class_sources}\n"
        code_context += f"Other related classes:\n {other_related_class_sources}\n"
        code_context += f"Code of around the call:\n {caller_source}\n"
        code_context += f"Stack trace: Most recent frame first:\n {stack_trace}\n"
        code_context += f"Code of class {cls.__module__}.{cls.__name__}:\n {self_source}\n"

        return code_context

    def add_line_numbers(self, code_lines, start=1) -> str:
        source = ""
        for line in code_lines:
            source += f"{start}: {line.strip()}\n"
            start += 1
        return source

    def get_class_source(self, cls, name, full=False):
        if full:
            try:
                source = f"{cls.__module__}.{cls.__name__}:\n"
                source_lines, lineno = inspect.getsourcelines(cls)
                source += self.add_line_numbers(source_lines, start=lineno)
                return source
            except (OSError, TypeError):
                return f"{cls.__module__}.{cls.__name__} source unavailable"

        # full=False, retrieve the source of the class with some code removed
        source = f"{cls.__module__}.{cls.__name__}:\n"
        # Add the class def line and the method implementation to the source
        try:
            class_source, lineno = inspect.getsourcelines(cls)
            source += f"{lineno}: {class_source[0]}\n"
        except (OSError, TypeError):
            # Class source could not be found
            # No use in continuing
            return f"{cls.__module__}.{cls.__name__} source unavailable"

        # Add the source of the __init__ method
        if "__init__" in cls.__dict__:
            source_lines, lineno = inspect.getsourcelines(cls.__dict__["__init__"])
            source += self.add_line_numbers(source_lines, start=lineno)

        # Add the source of the method
        if name in cls.__dict__:
            if inspect.isfunction(cls.__dict__[name]):
                source_lines, lineno = inspect.getsourcelines(cls.__dict__[name])
                source += self.add_line_numbers(source_lines, start=lineno)
            else:
                source += f"{name}={cls.__dict__[name]}\n"

        # Add the def line of all the other methods
        for attr_name, attr in cls.__dict__.items():
            if attr_name != "__init__" \
            and attr_name != name:
                if inspect.isfunction(attr):
                    method_source, lineno = inspect.getsourcelines(attr)
                    source += f"{lineno}: {method_source[0]}\n"
                    source += "...\n"
                else:
                    # Exclude stuff like __dict__ and __weakref__
                    if not attr_name.startswith("__"):
                        source += f"{lineno}: {attr_name}={attr}\n"
        return source

    def get_class_sources(self, classes, name):
        sources = ""
        for cls in classes:
            sources += self.get_class_source(cls, name)
        return sources

    def get_all_related_classes(self, cls, excluded_classes=None):
        subclass_families = []
        parent_classes = self.get_all_parent_classes(cls)
        for parent in parent_classes:
            parent_subclasses = self.get_all_subclasses(parent)
            # Has to be for loop here instead of list comprehension so we can get subclasses of excluded classes
            if excluded_classes is not None and parent not in excluded_classes:
                parent_subclasses.append(parent)

            # Remove all in excluded_classes
            if excluded_classes is not None:
                parent_subclasses = [c for c in parent_subclasses if c not in excluded_classes]
            subclass_families.append(parent_subclasses)
        # Combine the freundshachts into generations so the 'ages' are closer together in the list
        zipped_subclass_families = zip(*subclass_families)
        subclass_generations = [list(gen) for gen in zipped_subclass_families]
        # Flatten the generations
        classes = [cls for gen in subclass_generations for cls in gen]
        return classes

    def get_all_parent_classes(self, cls, excluded_classes=None):
        parent_classes = []
        for parent in cls.__mro__:
            if excluded_classes is not None and parent in excluded_classes:
                continue
            if parent.__name__ == "GenerativeBase"\
            or parent is object\
            or parent is cls:
                continue
            parent_classes.append(parent)
        # Closest ancestors first
        parent_classes.reverse()
        return parent_classes

    def get_all_subclasses(self, cls, excluded_classes=None):
        subclasses = []
        for subclass in cls.__subclasses__():
            if excluded_classes is not None and subclass not in excluded_classes:
                subclasses.append(subclass)
            subclasses.extend(self.get_all_subclasses(subclass, excluded_classes))
        return subclasses

    def get_calling_code(self, stack=None, stack_depth=0, slice_pre=10, slice_post=10):
        caller_source = ""
        if stack is None:
            caller_frame = inspect.stack()[stack_depth]
        else:
            caller_frame = stack[stack_depth]
        frame_info = inspect.getframeinfo(caller_frame[0])
        # If caller is a method, get the source of the method
        # If caller is module, only get the source immediately around the call
        if frame_info.function != "<module>":
            try:
                caller_source_lines, lineno = inspect.getsourcelines(caller_frame[0])
                caller_source = self.add_line_numbers(caller_source_lines, start=lineno)
            except (OSError, TypeError):
                caller_source = ""
        else:
            try:
                caller_source_lines, lineno = inspect.getsourcelines(caller_frame[0])
                source_we_need = caller_source_lines[frame_info.lineno - slice_pre:frame_info.lineno + slice_post]
                caller_source = self.add_line_numbers(source_we_need, start=frame_info.lineno - slice_pre + 1)
            except (OSError, TypeError):
                caller_source = ""
            except IndexError:
                caller_source = self.get_calling_code(stack=stack, stack_depth=stack_depth, slice_pre=slice_pre - 1, slice_post=slice_post - 1)

        return caller_source

    def get_stack_trace(self, frozen_stack, start_depth=1):
        stack_trace = ""
        for frame in frozen_stack[start_depth:]:
            frame_info = inspect.getframeinfo(frame[0])
            stack_trace += f"File: {frame_info.filename}, Line: {frame_info.lineno}, Function: {frame_info.function}\n"
        return stack_trace

    def prompt_ai(self, prompt, try_count=0):
        try:
            print("AI prompt:", prompt, "\n")
            # Escape the prompt to avoid special characters
            prompt = prompt.replace('"', '\\"')
            response = subprocess.run(["tgpt", "-q", "--provider", "pollinations", prompt], stdout=subprocess.PIPE, check=True, text=True).stdout.strip()
            print("AI response:", response, "\n")
            return response
        except subprocess.CalledProcessError as e:
            if try_count > 3:
                raise CodeGenerationException(f"AI prompt failed too many times. {e.stderr}")
            return self.prompt_ai(prompt, try_count + 1)



