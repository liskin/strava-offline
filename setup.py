import setuptools


def slurp_lines(filename):
    with open(filename, "r") as f:
        return f.readlines()


setuptools.setup(
    use_scm_version=True,
    setup_requires=slurp_lines("setup-requirements.txt"),
    install_requires=slurp_lines("install-requirements.txt"),
    tests_require=slurp_lines("tests-requirements.txt"),
    extras_require={
        "dev": slurp_lines("dev-requirements.txt"),
        "test": slurp_lines("tests-requirements.txt"),
    },
)
