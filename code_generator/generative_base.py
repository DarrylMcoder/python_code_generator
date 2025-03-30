import inspect
from .code_generator import CodeGenerator
from .code_writer import CodeWriter

class LazyAttribute:
    """
    This class is used to delay the generation of the code for a method until it is called.
    This lets us distinguish between methods and attributes.
    """
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def __call__(self, *args, **kwargs):
        print("LazyAttribute: __call__ called")
        # Remove the attribute from the queue since it has been called and is therefore not a variable
        del self.owner.generation_queue[self.name]

        # Generate the method
        code = CodeGenerator().generate_method(self.owner.__class__, self.name, args, kwargs, inspect.stack())
        class_source = CodeWriter().insert_code(cls=self.owner.__class__, code=code)
        imports = CodeGenerator().generate_imports(code)
        class_source = CodeWriter().insert_code(main_source=class_source, code=imports)
        commit_message = CodeGenerator().generate_commit_message(old_code="", new_code=code)
        CodeWriter().commit_changes(self.owner.__class__, class_source, commit_message)

class GenerativeBase:
    def __init__(self):
        print("GenerativeBase: __init__ called")
        # The queue of attributes that need to be generated
        self.generation_queue = {}

    def __getattr__(self, name):
        print(f"GenerativeBase: __getattr__ called for {name}")

        # Generate the attributes in the queue
        self._generate_attributes()

        # Add the attribute to the queue to be generated if it isn't called
        code_context = CodeGenerator().get_default_code_context(self.__class__, name, inspect.stack())
        self.generation_queue[name] = code_context

        return LazyAttribute(name, self)

    def _generate_attributes(self):
        # If there are attributes in the queue, commit them as they must not have been called 
        for name, code_context in self.generation_queue.items():
            method = CodeGenerator().decide_which_method_sets_attribute(cls=self.__class__, attribute_name=name, code_context=code_context)
            if method == "None":
                # Implement a new method to set the attribute
                prompt = f"Implement a new method to set the attribute {self.__class__.__name__}.{name} in the class {self.__class__.__name__}.\n"
                prompt += f"This attribute was accessed on an instance of the class {self.__class__.__name__} but it was not defined in the class.\n"
                prompt += "We have determined that there should be a new method to set the attribute.\n"
                prompt += "Your job is to define the method.\n"
                prompt += "The method may or may not have arguments.\n"
                prompt += "The method may or may not perform any other operations.\n"
                prompt += "Return only the code for the method.\n"
                prompt += "Do not generate the class definition, only the method implementation.\n"

                code = CodeGenerator().generate_code(prompt, code_context)
                class_source = CodeWriter().insert_code(cls=self.__class__, code=code)
                imports = CodeGenerator().generate_imports(code)
                class_source = CodeWriter().insert_code(main_source=class_source, code=imports)
                commit_message = CodeGenerator().generate_commit_message(old_code="", new_code=code)
                CodeWriter().commit_changes(self.__class__, class_source, commit_message)
            elif method == "class":
                # Add the attribute to the class source as a class attribute
                prompt = f"Add the attribute {self.__class__.__name__}.{name} to the class {self.__class__.__name__} as a class attribute.\n"
                prompt += f"This attribute was accessed on an instance of the class {self.__class__.__name__} but it was not defined in the class.\n"
                prompt += "We have determined that the attribute should be defined as a class attribute.\n"
                prompt += "Your job is to define the attribute.\n"
                prompt += "Return the line or lines of code where the attribute is defined.\n"
                prompt += "Do not generate the class definition, only the attribute definition.\n"

                code = CodeGenerator().generate_code(prompt, code_context)
                class_source = CodeWriter().insert_code(cls=self.__class__, code=code)
                # Probably unnecessary to add imports for class attributes
                imports = CodeGenerator().generate_imports(code)
                class_source = CodeWriter().insert_code(main_source=class_source, code=imports)
                commit_message = CodeGenerator().generate_commit_message(old_code="", new_code=code)
                CodeWriter().commit_changes(self.__class__, class_source, commit_message)
            else:
                # Modify an existing method to set the attribute
                existing_method_source = inspect.getsource(self.__class__.__dict__[method])

                prompt = f"Modify the method {self.__class__.__name__}.{method} to set the attribute {self.__class__.__name__}.{name} in the class {self.__class__.__name__}.\n"
                prompt += f"This attribute was accessed on an instance of the class {self.__class__.__name__} but it was not defined in the class.\n"
                prompt += "We have determined that the attribute should be set by modifying an existing method to set the attribute.\n"
                prompt += "Your job is to modify the method.\n"
                prompt += "The method must retain its original functionality.\n"
                prompt += "Return only the source code of the modified method.\n"
                prompt += "Do not generate the class definition, only the modified method.\n"

                code = CodeGenerator().modify_code(prompt, code_context, existing_method_source)
                class_source = CodeWriter().insert_code(cls=self.__class__, code=code)
                imports = CodeGenerator().generate_imports(code)
                class_source = CodeWriter().insert_code(main_source=class_source, code=imports)
                commit_message = CodeGenerator.generate_commit_message(old_code=existing_method_source, new_code=code)
                CodeWriter().commit_changes(self.__class__, class_source, commit_message)

        # Clear the queue after generating all attributes
        self.generation_queue = {}


