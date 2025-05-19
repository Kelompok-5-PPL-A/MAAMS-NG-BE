from setuptools import setup, find_packages

setup(
    name="MAAMS-NG-BE",
    version="0.2.0",
    description="MAAMS-NG Backend",
    author="MAAMS Team",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 