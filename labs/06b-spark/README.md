# Apache Spark in Google Colab, AWS EMR, Databricks

## 1. Python interactive: 'pyspark'

    $ pyspark
    >>> files = sc.textFile("s3://usernamedatalake/datasets/gutenberg-es/*.txt")
    >>> wc = files.flatMap(lambda line: line.split(" ")).map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)
    >>> wc.saveAsTextFile("hdfs:///tmp/wcout1")

    * save wc file by rdd
    * join all data at the same file:
    
    $ pyspark
    >>> files = sc.textFile("s3://usernamedatalake/datasets/gutenberg-es/*.txt")
    >>> wc = files.flatMap(lambda line: line.split(" ")).map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)
    >>> wc.coalesce(1).saveAsTextFile("hdfs:///tmp/wcout2")

## 2. python files: [wc-pyspark.py](wc-pyspark.py)

* run:

    $ spark-submit --master yarn --deploy-mode cluster wc-pyspark.py

## 3.  Zeppelin Nodebook:

    * Open the browser a: http://ip-or-name-amazon-host:9995
    * On AWS EMR, by default does not have login/pass

### Wordcount  python:

```python
    %spark2.pyspark
    files = sc.textFile("s3://usernamedatalake/datasets/gutenberg-es/*.txt")
    wc = files.flatMap(lambda line: line.split(" ")).map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)
    wc.coalesce(1).saveAsTextFile("hdfs:///tmp/wcout1")
```

### wordcount with spark.sql in zeppelin

    %spark2.sql
    SHOW tables

    %spark2.sql
    SHOW database

    %spark2.sql    
    USE <user_vpn>

    %spark2.sql   
    CREATE EXTERNAL TABLE <user_vpn>.docs2 (line STRING) stored as textfile location '/datasets/gutenberg-small/*.txt'

    %spark2.sql
    SELECT word, count(1) AS count FROM (SELECT explode(split(line,' ')) AS word FROM docs2) w GROUP BY word ORDER BY word

## 4. Jupyter Notebooks

### Wordcount [wordcount-spark.ipynb](wordcount-spark.ipynb)

### Dataframes and dataprep with pyspark

* notebook: [Data_processing_using_PySpark.ipynb](Data_processing_using_PySpark.ipynb)
* datos ejemplo: [sample_data.csv](../datasets/spark/sample_data.csv)

### Managed notebooks with AWS EMR

* options:

    ** jupyterhub included with EMR
    ** Notebooks as a service in EMR
    
Managed notebooks: packages and version could query:

    https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-managed-notebooks-scoped-libraries.html

* Options:

** change python version

    %%configure -f
    { "conf":{
    "spark.pyspark.python": "python3",
    "spark.pyspark.virtualenv.enabled": "true",
    "spark.pyspark.virtualenv.type":"native",
    "spark.pyspark.virtualenv.bin.path":"/usr/bin/virtualenv"
    }}

** Example – Listing Current Libraries

    sc.list_packages()

** Example – Installing the NLTK Library

    sc.install_pypi_package("nltk")

** Example – Uninstalling a Library

    sc.uninstall_package("nltk")