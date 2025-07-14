from setuptools import setup, find_packages

setup(
    name="knowledge-gpt-api",
    version="1.0.0",
    description="Knowledge_GPT API - Natural language to behavioral data converter",
    author="Chris Anzalone",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.28.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.11",
) 