from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r', encoding='UTF-8') as f:
    return f.read()


setup(
  name='autofaq_api',
  version='0.0.7',
  author='AzatXafizof',
  author_email='hafizov.azat.m@gmail.com',
  description='Этот модуль умеет работать с 3-мя API AutoFaq: External API, CRUD API, QUERY API. Как синхронно так и асинхронно',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/azatkhafizov/autofaq-api',
  packages=find_packages(),
  install_requires=['aiohttp>=2.25.1', 'aiohttp>=3.12.13', 'aiofiles==24.1.0', 'requests-toolbelt==1.0.0', 'pydantic>=2.9.2'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='AutoFaq AutoFAQ autofaq kb',
  project_urls={
    'GitHub': 'https://github.com/azatkhafizov/autofaq-api'
  },
  python_requires='>=3.10'
)