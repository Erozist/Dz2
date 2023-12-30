from setuptools import setup

setup(name='folder_order',
      version='0.0.1',
      description='Very useful code',
      author='Andriy Mandrik',
      author_email='Erozist87@gmail.com',
      url='https://github.com/Erozist/Dz2',
      license='MIT',
      packages=['clean_folder'],
      entry_points={'console_scripts': ['clean-folder=clean_folder.clean:main']})
