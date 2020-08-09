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
)
