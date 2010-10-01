from setuptools import setup, find_packages
import sys, os

from pyallocine  import VERSION

setup(name='pyallocine',
      version=".".join(map(str, VERSION)),
      description="Parser for allocine.fr",
      long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ], 
      keywords='parser allocine',
      author='Guillaume Boué',
      author_email='guillaumeboue@gmail.com',
      url='http://github.com/gboue/pyallocine',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      )


