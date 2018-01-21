import os ,sys
from scrapy.cmdline import execute

base_dir=os.path.abspath(os.path.dirname(__file__))
print(base_dir)
sys.path.insert(0,base_dir)

execute("scrapy crawl tb".split())