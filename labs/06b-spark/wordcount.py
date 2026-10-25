"""Counts the words of a set of text files with Spark and writes the count as one CSV file.

The same script runs on your computer and on a Spark cluster: only the paths change.

    spark-submit --master 'local[*]' labs/06b-spark/wordcount.py \\
        --input "datasets/gutenberg-en/*.txt" --output labs/shared/output/lab06b/wordcount-en
"""
import argparse
from operator import add

from pyspark.sql import SparkSession


def words(line):
    """The words of a line, in lowercase: every character that is not a letter splits two words."""
    letters = "".join(char if char.isalpha() else " " for char in line.lower())
    return letters.split()


def main():
    parser = argparse.ArgumentParser(
        description="Count the words of text files with Spark.")
    parser.add_argument(
        "--input",
        default="datasets/gutenberg-en/*.txt",
        help=
        "files to read: a path, a folder or a pattern (default: %(default)s)")
    parser.add_argument(
        "--output",
        default="labs/shared/output/lab06b/wordcount-en",
        help=
        "folder of the CSV with the count, replaced if it exists (default: %(default)s)"
    )
    parser.add_argument("--top",
                        type=int,
                        default=10,
                        help="words to print (default: %(default)s)")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("lab06b-wordcount").getOrCreate()
    lines = spark.sparkContext.textFile(args.input)
    counts = lines.flatMap(words).map(lambda word: (word, 1)).reduceByKey(add)

    result = spark.createDataFrame(counts, "word string, count long").orderBy(
        ["count", "word"], ascending=[False, True])
    result.coalesce(1).write.mode("overwrite").csv(args.output, header=True)

    total = counts.values().sum()
    print(
        f"Lines: {lines.count()}, words: {total}, distinct words: {counts.count()}"
    )
    for row in result.take(args.top):
        print(f"{row['word']:>12} {row['count']:>8}")
    print(f"Wrote the count to {args.output}")
    spark.stop()


if __name__ == "__main__":
    main()
