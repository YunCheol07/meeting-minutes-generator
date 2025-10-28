"""패키지 설치 설정"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="meeting-minutes-generator",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI 기반 회의록 자동 생성 시스템",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.3.0",
        "langchain-community>=0.3.0",
        "langgraph>=0.2.16",
        "python-docx>=1.1.2",
        "typing-extensions>=4.9.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "generate-minutes=scripts.run_generation:main",
        ],
    },
)
