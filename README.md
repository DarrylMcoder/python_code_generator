# GenerativeBase

`GenerativeBase` is a Python base class that uses
 AI to dynamically generate undefined methods and
 attributes at runtime. It commits the generated
 code to the `ai-assistant` Git branch
 automatically.

## How to Use

1. **Extend the `GenerativeBase` class**:
   ```python
   from generative_base import GenerativeBase

   class MyDynamicClass(GenerativeBase):
       pass


2. **Access undefined methods or attributes**:
   ```python
   obj = MyDynamicClass()
   obj.some_method() # AI generates and commits
 the method.
   obj.some_attribute # AI generates and commits
 the attribute.


## Requirements

- **CLI Tools**:
 - `git`: For committing changes.
 - `tgpt`: For AI-based code generation (uses GPT
).

- **Python Dependencies**:
 - Minimal dependencies: Uses `inspect` and `sub
process`.

## License

This project is licensed under the MIT License.
 Feel free to use and modify it as needed.
