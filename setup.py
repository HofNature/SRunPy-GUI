from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
long_description = long_description.replace("./Show.png","https://github.com/HofNature/SRunPy-GUI/raw/main/Show.png")
setup(
    name="srunpy",
    version="1.0.6.0",
    author="HofNature",
    description="适用于深澜网关的校园网第三方登录器",
    long_description=long_description,
    long_description_content_type='text/markdown',    
    packages=find_packages(),
    install_requires=["pystray","pywebview","pywin32","requests","urllib3","win10toast","pycryptodome"],
    extras_require={
        'qt': ["pywebview[qt]"],
    },
    python_requires=">=3.7, <3.13",
    url="https://github.com/HofNature/SRunPy-GUI",
    license="GPL-3.0",
    keywords=["srun", "srunpy", "srun-client", "srun-gui", "srunpy-gui", "srun-client-gui","network","login","logout","gateway"],
    include_package_data=True,
    entry_points={
        "gui_scripts": [
            "srunpy-gui=srunpy.entry:Gui",
        ],
        "console_scripts": [
            "srunpy=srunpy.entry:Gui",
            "srunpy-cli=srunpy.entry:Cli",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
    ]
)