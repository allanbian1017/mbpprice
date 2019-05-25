from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mbpprice',
    version='0.0.2',
    description="second hand macbook pro price in Taiwan.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url="https://github.com/allanbian1017/mbpprice",
    license='MIT',
    author="Allan Bian",
    install_requires=[
        'pyquery',
        'requests'
    ],
    python_requires='>=3.5'
)
