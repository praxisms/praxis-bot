import setuptools

setuptools.setup(
    name="praxis-bot",
    version="0.0.1",
    author="Mike Holler",
    author_email="mike@mikeholler.me",
    description="A command line utility used to run Praxis Motorsport's bot.",
    url="https://github.com/mikeholler/praxis-bot",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "praxisbot = praxisbot.entrypoint:main"
        ]
    },
    python_requires=">3.8",
    install_requires=[
        "requests>=2.24.0,<3",
        "tabulate>=0.8,<1",
        "pyracing@git+https://github.com/Esterni/pyracing@2c072619ae1ef84e6452b1e67f7e1d19b2e36f4c"
    ]
)
